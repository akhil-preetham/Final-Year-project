"""Locked exploratory leave-one-source-out transfer and OOD study.

The full target cohort is isolated from preprocessing, predictor fitting,
calibration, and OOD threshold selection. Run with the project virtualenv:

    .venv/Scripts/python.exe experiments/run_lodo_transfer.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import zipfile
from collections import Counter
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.optimize import minimize
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
PROTOCOL = ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105.md"
OUTPUT = ROOT / "results" / "transfer_20261105_lodo_final"
COHORT_FILES = {
    "cleveland": "processed.cleveland.data",
    "hungary": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va_long_beach": "processed.va.data",
}
FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]
TARGET_RAW = "num"
NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL = [name for name in FEATURES if name not in NUMERIC]
ZERO_SENTINEL_FIELDS = ["trestbps", "chol"]
BASE_SEED = 20261105
CALIBRATION_FRACTION = 0.20
BOOTSTRAP_REPLICATES = 1000
ECE_BINS = 10


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_cohorts(
    archive_path: Path, zero_as_missing: bool
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    columns = [*FEATURES, TARGET_RAW]
    cohort_data: dict[str, dict[str, Any]] = {}
    source_manifest: dict[str, Any] = {}
    with zipfile.ZipFile(archive_path) as archive:
        members = set(archive.namelist())
        for cohort, member in COHORT_FILES.items():
            if member not in members:
                raise FileNotFoundError(f"UCI archive is missing required member {member!r}")
            raw = archive.read(member)
            frame = pd.read_csv(
                BytesIO(raw),
                header=None,
                names=columns,
                na_values=["?"],
                keep_default_na=True,
            )
            if frame.shape[1] != len(columns):
                raise ValueError(f"Unexpected column count in {member}: {frame.shape[1]}")
            for column in columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")
            invalid_labels = frame[TARGET_RAW].notna() & ~frame[TARGET_RAW].isin([0, 1, 2, 3, 4])
            if invalid_labels.any():
                raise ValueError(f"Unexpected target values in {member}")
            frame = frame.loc[frame[TARGET_RAW].notna()].reset_index(drop=True)

            data = frame[FEATURES].copy()
            if zero_as_missing:
                for field in ZERO_SENTINEL_FIELDS:
                    data.loc[data[field] == 0, field] = np.nan
            labels = (frame[TARGET_RAW].astype(int) > 0).astype(np.int8)
            cohort_data[cohort] = {
                "X": data,
                "y": labels.to_numpy(),
                "num": frame[TARGET_RAW].astype(int).to_numpy(),
                "row_index": np.arange(len(frame)),
            }
            source_manifest[cohort] = {
                "archive_member": member,
                "member_sha256": sha256_bytes(raw),
                "rows": int(len(frame)),
                "raw_num_counts": {
                    str(k): int(v)
                    for k, v in sorted(Counter(frame[TARGET_RAW].astype(int)).items())
                },
                "binary_target_counts": {
                    str(k): int(v) for k, v in sorted(Counter(labels).items())
                },
                "feature_missing_counts_after_policy": {
                    name: int(count) for name, count in data.isna().sum().items()
                },
                "zero_values_recode_policy": "missing" if zero_as_missing else "retained",
            }
    return cohort_data, source_manifest


def equal_domain_weights(domains: np.ndarray) -> np.ndarray:
    domains = np.asarray(domains)
    weights = np.zeros(len(domains), dtype=float)
    unique_domains = np.unique(domains)
    for domain in unique_domains:
        indices = domains == domain
        weights[indices] = 1.0 / int(indices.sum())
    return weights


def weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ordered_values = values[order]
    ordered_weights = weights[order]
    cumulative = np.cumsum(ordered_weights) - 0.5 * ordered_weights
    cumulative /= ordered_weights.sum()
    return float(
        np.interp(
            quantile, cumulative, ordered_values, left=ordered_values[0], right=ordered_values[-1]
        )
    )


def expected_calibration_error(
    y: np.ndarray, probabilities: np.ndarray, bins: int = ECE_BINS
) -> float:
    y = np.asarray(y, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = len(y)
    error = 0.0
    for index in range(bins):
        if index == bins - 1:
            in_bin = (probabilities >= edges[index]) & (probabilities <= edges[index + 1])
        else:
            in_bin = (probabilities >= edges[index]) & (probabilities < edges[index + 1])
        if in_bin.any():
            error += (in_bin.sum() / total) * abs(
                float(probabilities[in_bin].mean()) - float(y[in_bin].mean())
            )
    return float(error)


def calibration_intercept_slope(
    y: np.ndarray, probabilities: np.ndarray
) -> dict[str, float | None]:
    y = np.asarray(y, dtype=float)
    if len(np.unique(y)) < 2:
        return {"intercept": None, "slope": None}
    logits = np.log(np.clip(probabilities, 1e-7, 1 - 1e-7) / np.clip(1 - probabilities, 1e-7, 1.0))

    def objective(parameters: np.ndarray) -> float:
        linear = parameters[0] + parameters[1] * logits
        return float(np.mean(np.logaddexp(0.0, linear) - y * linear))

    result = minimize(
        objective,
        x0=np.array([0.0, 1.0]),
        method="L-BFGS-B",
        bounds=[(-20.0, 20.0), (-10.0, 10.0)],
    )
    if not result.success or not np.all(np.isfinite(result.x)):
        return {"intercept": None, "slope": None}
    return {"intercept": float(result.x[0]), "slope": float(result.x[1])}


def predictive_metrics(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    y = np.asarray(y, dtype=int)
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-7, 1 - 1e-7)
    classes = np.unique(y)
    predicted = probabilities >= 0.5
    true_positive = int(np.sum((y == 1) & predicted))
    false_negative = int(np.sum((y == 1) & ~predicted))
    true_negative = int(np.sum((y == 0) & ~predicted))
    false_positive = int(np.sum((y == 0) & predicted))
    sensitivity = (
        float(true_positive / (true_positive + false_negative))
        if true_positive + false_negative
        else None
    )
    specificity = (
        float(true_negative / (true_negative + false_positive))
        if true_negative + false_positive
        else None
    )
    precision = (
        float(true_positive / (true_positive + false_positive))
        if true_positive + false_positive
        else None
    )
    balanced_accuracy = (
        float((sensitivity + specificity) / 2)
        if sensitivity is not None and specificity is not None
        else None
    )
    metrics: dict[str, Any] = {
        "n": int(len(y)),
        "class_counts": {str(k): int(v) for k, v in sorted(Counter(y).items())},
        "roc_auc": None,
        "average_precision": None,
        "brier_score": float(brier_score_loss(y, probabilities)),
        "log_loss": float(log_loss(y, probabilities, labels=[0, 1])),
        "ece_10_bins": expected_calibration_error(y, probabilities),
        "accuracy_at_0_5": float(np.mean(y == predicted)),
        "balanced_accuracy_at_0_5": balanced_accuracy,
        "sensitivity_at_0_5": sensitivity,
        "specificity_at_0_5": specificity,
        "precision_at_0_5": precision,
    }
    if len(classes) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y, probabilities))
        metrics["average_precision"] = float(average_precision_score(y, probabilities))
    metrics["calibration"] = calibration_intercept_slope(y, probabilities)
    return metrics


def percentile_interval(values: list[float]) -> dict[str, float | None]:
    finite = np.asarray([value for value in values if np.isfinite(value)], dtype=float)
    if len(finite) == 0:
        return {"lower_95": None, "upper_95": None}
    return {
        "lower_95": float(np.quantile(finite, 0.025)),
        "upper_95": float(np.quantile(finite, 0.975)),
    }


def bootstrap_predictive_intervals(
    y: np.ndarray,
    raw_probabilities: np.ndarray,
    calibrated_probabilities: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    y = np.asarray(y, dtype=int)
    rng = np.random.default_rng(seed)
    by_class = [np.flatnonzero(y == value) for value in (0, 1)]
    if any(len(indices) == 0 for indices in by_class):
        return {"status": "not estimable: target cohort contains a single class"}
    requested = ("roc_auc", "average_precision", "brier_score", "log_loss", "ece_10_bins")
    samples: dict[str, dict[str, list[float]]] = {
        "raw": {key: [] for key in requested},
        "platt": {key: [] for key in requested},
    }
    for _ in range(BOOTSTRAP_REPLICATES):
        indices = np.concatenate(
            [
                rng.choice(class_indices, size=len(class_indices), replace=True)
                for class_indices in by_class
            ]
        )
        for name, probabilities in (
            ("raw", raw_probabilities),
            ("platt", calibrated_probabilities),
        ):
            sampled_y = y[indices]
            sampled_probabilities = np.clip(probabilities[indices], 1e-7, 1 - 1e-7)
            metrics = {
                "roc_auc": roc_auc_score(sampled_y, sampled_probabilities),
                "average_precision": average_precision_score(sampled_y, sampled_probabilities),
                "brier_score": brier_score_loss(sampled_y, sampled_probabilities),
                "log_loss": log_loss(sampled_y, sampled_probabilities, labels=[0, 1]),
                "ece_10_bins": expected_calibration_error(sampled_y, sampled_probabilities),
            }
            for key in requested:
                value = metrics[key]
                if np.isfinite(value):
                    samples[name][key].append(float(value))
    return {
        name: {key: percentile_interval(values) for key, values in metric_values.items()}
        for name, metric_values in samples.items()
    }


def bootstrap_ood_auc_interval(
    source_scores: np.ndarray, target_scores: np.ndarray, seed: int
) -> dict[str, float | None]:
    source_scores = np.asarray(source_scores, dtype=float)
    target_scores = np.asarray(target_scores, dtype=float)
    if len(source_scores) < 2 or len(target_scores) < 2:
        return {"lower_95": None, "upper_95": None}
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        source_sample = rng.choice(source_scores, size=len(source_scores), replace=True)
        target_sample = rng.choice(target_scores, size=len(target_scores), replace=True)
        labels = np.concatenate([np.zeros(len(source_sample)), np.ones(len(target_sample))])
        scores = np.concatenate([source_sample, target_sample])
        values.append(float(roc_auc_score(labels, scores)))
    return percentile_interval(values)


def build_preprocessor() -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            ),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent", add_indicator=True, keep_empty_features=True
                ),
            ),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, NUMERIC),
            ("categorical", categorical_pipeline, CATEGORICAL),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def source_split(
    cohort_data: dict[str, dict[str, Any]], target: str
) -> tuple[
    pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame, np.ndarray, np.ndarray, dict[str, Any]
]:
    fit_frames: list[pd.DataFrame] = []
    fit_labels: list[np.ndarray] = []
    fit_domains: list[np.ndarray] = []
    cal_frames: list[pd.DataFrame] = []
    cal_labels: list[np.ndarray] = []
    cal_domains: list[np.ndarray] = []
    split_manifest: dict[str, Any] = {}
    outer_index = list(COHORT_FILES).index(target)
    for source_index, (cohort, data) in enumerate(cohort_data.items()):
        if cohort == target:
            continue
        row_indices = np.arange(len(data["y"]))
        fit_indices, cal_indices = train_test_split(
            row_indices,
            test_size=CALIBRATION_FRACTION,
            random_state=BASE_SEED + 100 * outer_index + source_index,
            stratify=data["y"],
        )
        fit_frames.append(data["X"].iloc[fit_indices].reset_index(drop=True))
        fit_labels.append(data["y"][fit_indices])
        fit_domains.append(np.full(len(fit_indices), cohort, dtype=object))
        cal_frames.append(data["X"].iloc[cal_indices].reset_index(drop=True))
        cal_labels.append(data["y"][cal_indices])
        cal_domains.append(np.full(len(cal_indices), cohort, dtype=object))
        split_manifest[cohort] = {
            "fit_row_indices": fit_indices.astype(int).tolist(),
            "calibration_row_indices": cal_indices.astype(int).tolist(),
            "fit_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][fit_indices]).items())
            },
            "calibration_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][cal_indices]).items())
            },
        }
    return (
        pd.concat(fit_frames, ignore_index=True),
        np.concatenate(fit_labels),
        np.concatenate(fit_domains),
        pd.concat(cal_frames, ignore_index=True),
        np.concatenate(cal_labels),
        np.concatenate(cal_domains),
        split_manifest,
    )


def run_outer_fold(
    cohort_data: dict[str, dict[str, Any]],
    target: str,
    zero_policy: str,
) -> tuple[dict[str, Any], pd.DataFrame]:
    # The target labels are kept separate until final scoring below.
    target_features = cohort_data[target]["X"].copy()
    target_labels_for_scoring = cohort_data[target]["y"].copy()
    target_raw_labels_for_scoring = cohort_data[target]["num"].copy()
    target_row_indices = cohort_data[target]["row_index"].copy()

    fit_X, fit_y, fit_domains, cal_X, cal_y, cal_domains, split_manifest = source_split(
        cohort_data, target
    )
    fit_weights = equal_domain_weights(fit_domains)
    cal_weights = equal_domain_weights(cal_domains)

    preprocessor = build_preprocessor()
    fit_matrix = preprocessor.fit_transform(fit_X)
    cal_matrix = preprocessor.transform(cal_X)
    target_matrix = preprocessor.transform(target_features)

    predictor = LogisticRegression(C=1.0, solver="liblinear", max_iter=5000, random_state=BASE_SEED)
    predictor.fit(fit_matrix, fit_y, sample_weight=fit_weights)
    raw_calibration_probabilities = predictor.predict_proba(cal_matrix)[:, 1]
    raw_target_probabilities = predictor.predict_proba(target_matrix)[:, 1]

    calibration_logits = np.log(
        np.clip(raw_calibration_probabilities, 1e-7, 1 - 1e-7)
        / np.clip(1 - raw_calibration_probabilities, 1e-7, 1.0)
    ).reshape(-1, 1)
    target_logits = np.log(
        np.clip(raw_target_probabilities, 1e-7, 1 - 1e-7)
        / np.clip(1 - raw_target_probabilities, 1e-7, 1.0)
    ).reshape(-1, 1)
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=5000, random_state=BASE_SEED)
    calibrator.fit(calibration_logits, cal_y, sample_weight=cal_weights)
    calibrated_probabilities = calibrator.predict_proba(target_logits)[:, 1]

    detector = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=BASE_SEED,
        n_jobs=1,
    )
    detector.fit(fit_matrix, sample_weight=fit_weights)
    cal_anomaly_scores = -detector.score_samples(cal_matrix)
    target_anomaly_scores = -detector.score_samples(target_matrix)
    ood_threshold = weighted_quantile(cal_anomaly_scores, cal_weights, 0.95)
    target_ood_flags = target_anomaly_scores > ood_threshold
    ood_domain_labels = np.concatenate(
        [np.zeros(len(cal_anomaly_scores)), np.ones(len(target_anomaly_scores))]
    )
    ood_domain_scores = np.concatenate([cal_anomaly_scores, target_anomaly_scores])
    ood_auc = float(roc_auc_score(ood_domain_labels, ood_domain_scores))

    # Target labels are first used here, after every model and alert threshold is frozen.
    raw_metrics = predictive_metrics(target_labels_for_scoring, raw_target_probabilities)
    calibrated_metrics = predictive_metrics(target_labels_for_scoring, calibrated_probabilities)
    accepted = ~target_ood_flags
    accepted_metrics = (
        predictive_metrics(target_labels_for_scoring[accepted], calibrated_probabilities[accepted])
        if accepted.any()
        else {"status": "no target rows accepted by source-calibrated OOD threshold"}
    )
    flagged_metrics = (
        predictive_metrics(
            target_labels_for_scoring[target_ood_flags], calibrated_probabilities[target_ood_flags]
        )
        if target_ood_flags.any()
        else {"status": "no target rows flagged by source-calibrated OOD threshold"}
    )
    bootstrap = bootstrap_predictive_intervals(
        target_labels_for_scoring,
        raw_target_probabilities,
        calibrated_probabilities,
        seed=BASE_SEED + 1000 + list(COHORT_FILES).index(target),
    )
    ood_interval = bootstrap_ood_auc_interval(
        cal_anomaly_scores,
        target_anomaly_scores,
        seed=BASE_SEED + 2000 + list(COHORT_FILES).index(target),
    )

    result = {
        "target_cohort": target,
        "zero_value_policy": zero_policy,
        "target_rows": int(len(target_labels_for_scoring)),
        "target_class_counts": {
            str(k): int(v) for k, v in sorted(Counter(target_labels_for_scoring).items())
        },
        "source_fit_rows": int(len(fit_y)),
        "source_calibration_rows": int(len(cal_y)),
        "source_fit_class_counts": {str(k): int(v) for k, v in sorted(Counter(fit_y).items())},
        "source_calibration_class_counts": {
            str(k): int(v) for k, v in sorted(Counter(cal_y).items())
        },
        "source_fit_domain_counts": {
            str(k): int(v) for k, v in sorted(Counter(fit_domains).items())
        },
        "source_calibration_domain_counts": {
            str(k): int(v) for k, v in sorted(Counter(cal_domains).items())
        },
        "source_splits": split_manifest,
        "raw_predictor_metrics": raw_metrics,
        "platt_calibrated_metrics": calibrated_metrics,
        "predictor_bootstrap_95_ci": bootstrap,
        "ood": {
            "score_definition": (
                "negative IsolationForest score_samples; larger means more anomalous"
            ),
            "threshold_source_calibration_weighted_q95": float(ood_threshold),
            "source_calibration_false_alert_rate": float(
                np.average(cal_anomaly_scores > ood_threshold, weights=cal_weights)
            ),
            "target_alert_rate": float(target_ood_flags.mean()),
            "target_flagged_rows": int(target_ood_flags.sum()),
            "target_accepted_rows": int(accepted.sum()),
            "target_coverage": float(accepted.mean()),
            "source_vs_target_ood_auroc": ood_auc,
            "source_vs_target_ood_auroc_bootstrap_95_ci": ood_interval,
            "accepted_target_calibrated_metrics": accepted_metrics,
            "flagged_target_calibrated_metrics": flagged_metrics,
        },
        "calibrator": {
            "method": "Platt logistic regression on source-only calibration logits",
            "C": 1e6,
            "intercept": float(calibrator.intercept_[0]),
            "slope": float(calibrator.coef_[0, 0]),
        },
        "model": {
            "family": "logistic_regression",
            "C": 1.0,
            "solver": "liblinear",
            "max_iter": 5000,
        },
        "preprocessor": {
            "numeric": (
                "source-fit median imputation with missing indicators, then standard scaling"
            ),
            "categorical": (
                "source-fit most-frequent imputation with missing indicators, then one-hot encoding"
            ),
            "encoded_feature_count": int(fit_matrix.shape[1]),
        },
    }
    predictions = pd.DataFrame(
        {
            "target_cohort": target,
            "zero_value_policy": zero_policy,
            "row_index": target_row_indices,
            "num_raw": target_raw_labels_for_scoring,
            "y_binary": target_labels_for_scoring,
            "raw_probability": raw_target_probabilities,
            "platt_probability": calibrated_probabilities,
            "ood_anomaly_score": target_anomaly_scores,
            "ood_threshold": ood_threshold,
            "ood_flag": target_ood_flags,
            "accepted": accepted,
        }
    )
    return result, predictions


def aggregate_macro(results: list[dict[str, Any]]) -> dict[str, Any]:
    fields = {
        "raw_roc_auc": lambda fold: fold["raw_predictor_metrics"]["roc_auc"],
        "raw_average_precision": lambda fold: fold["raw_predictor_metrics"]["average_precision"],
        "raw_brier_score": lambda fold: fold["raw_predictor_metrics"]["brier_score"],
        "platt_roc_auc": lambda fold: fold["platt_calibrated_metrics"]["roc_auc"],
        "platt_average_precision": lambda fold: fold["platt_calibrated_metrics"][
            "average_precision"
        ],
        "platt_brier_score": lambda fold: fold["platt_calibrated_metrics"]["brier_score"],
        "platt_log_loss": lambda fold: fold["platt_calibrated_metrics"]["log_loss"],
        "platt_ece_10_bins": lambda fold: fold["platt_calibrated_metrics"]["ece_10_bins"],
        "ood_auroc": lambda fold: fold["ood"]["source_vs_target_ood_auroc"],
        "ood_target_alert_rate": lambda fold: fold["ood"]["target_alert_rate"],
        "ood_target_coverage": lambda fold: fold["ood"]["target_coverage"],
        "accepted_target_platt_brier": lambda fold: fold["ood"][
            "accepted_target_calibrated_metrics"
        ].get("brier_score"),
    }
    summary: dict[str, Any] = {}
    for name, getter in fields.items():
        values = [
            float(value)
            for fold in results
            if (value := getter(fold)) is not None and np.isfinite(value)
        ]
        summary[name] = {
            "macro_mean": float(np.mean(values)) if values else None,
            "fold_min": float(np.min(values)) if values else None,
            "fold_max": float(np.max(values)) if values else None,
            "n_defined_folds": len(values),
        }
    return summary


def run_policy(zero_as_missing: bool) -> tuple[dict[str, Any], pd.DataFrame]:
    cohort_data, source_manifest = load_cohorts(ARCHIVE, zero_as_missing=zero_as_missing)
    policy = "impossible_zeros_as_missing" if zero_as_missing else "retain_zero_values_sensitivity"
    folds: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for target in COHORT_FILES:
        fold, predictions = run_outer_fold(cohort_data, target, policy)
        folds.append(fold)
        prediction_frames.append(predictions)
    return (
        {
            "zero_value_policy": policy,
            "cohort_audit": source_manifest,
            "macro_descriptive_summary": aggregate_macro(folds),
            "folds": folds,
        },
        pd.concat(prediction_frames, ignore_index=True),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Missing frozen UCI archive: {ARCHIVE}")
    if not PROTOCOL.is_file():
        raise FileNotFoundError(f"Missing frozen protocol: {PROTOCOL}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_runs: dict[str, Any] = {}
    all_predictions: list[pd.DataFrame] = []
    with threadpool_limits(limits=1):
        for zero_as_missing in (True, False):
            run, predictions = run_policy(zero_as_missing)
            all_runs[run["zero_value_policy"]] = run
            all_predictions.append(predictions)

    protocol_payload = PROTOCOL.read_bytes()
    script_payload = Path(__file__).read_bytes()
    manifest = {
        "study_id": "CD-XD-002",
        "status": "exploratory_retrospective_leave_one_source_out_pilot",
        "run_timestamp_utc": datetime.now(UTC).isoformat(),
        "archive_path": str(ARCHIVE.relative_to(ROOT)),
        "archive_sha256": sha256_file(ARCHIVE),
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": sha256_bytes(protocol_payload),
        "runner_path": str(Path(__file__).relative_to(ROOT)),
        "runner_sha256": sha256_bytes(script_payload),
        "code_artifacts_sha256": {
            str(Path(__file__).relative_to(ROOT)): sha256_bytes(script_payload)
        },
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scipy_version": scipy.__version__,
        "scikit_learn_version": sklearn.__version__,
        "cohort_order": list(COHORT_FILES),
        "feature_order": FEATURES,
        "numeric_features": NUMERIC,
        "categorical_features": CATEGORICAL,
        "seed": BASE_SEED,
        "source_calibration_fraction": CALIBRATION_FRACTION,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "ece_bins": ECE_BINS,
        "prior_project_exposure": (
            "All four component cohorts are represented in historical heart5.csv; "
            "this is not independent external validation."
        ),
        "runs": all_runs,
    }
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    pd.concat(all_predictions, ignore_index=True).to_csv(
        args.output_dir / "outer_predictions.csv", index=False
    )
    print(f"Wrote frozen-run manifest and predictions to {args.output_dir}")


if __name__ == "__main__":
    main()
