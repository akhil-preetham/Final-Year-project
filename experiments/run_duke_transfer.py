"""Run the source-only CD-XD-005 transport and abstention experiment."""

from __future__ import annotations

import hashlib
import json
import platform
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import numpy as np
import pandas as pd
import run_lodo_transfer as shared
import scipy
import sklearn
from matplotlib import pyplot as plt
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from threadpoolctl import threadpool_limits

from cardiodiag.domain_guard import DomainAwareSelectivePredictor
from cardiodiag.reliability import uncertainty_evidence
from cardiodiag.uncertainty import (
    conformal_prediction_sets,
    conformal_selective_summary,
    domain_robust_threshold,
)

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ARCHIVE = ROOT / "data" / "external" / "uci_heart_disease_45" / "heart_disease.zip"
DUKE_ARCHIVE = ROOT / "data" / "external" / "duke_acath" / "acath.xls.zip"
DUKE_WORKBOOK = ROOT / "data" / "external" / "duke_acath" / "raw" / "acath.xls"
SOURCE_MANIFEST = ROOT / "data" / "manifests" / "uci_heart_disease_transfer_study.json"
TARGET_MANIFEST = ROOT / "data" / "manifests" / "duke_acath_external.json"
PROTOCOL = ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_DUKE.md"
OUTPUT = ROOT / "results" / "transfer_20261105_duke_acath_final"
SEED = 20261105
PROBABILITY_CALIBRATION_FRACTION = 0.15
CONFORMAL_CALIBRATION_FRACTION = 0.15
CONFORMAL_ALPHA = 0.10
OOD_ALPHA = 0.05
K_NEIGHBORS = 10
FEATURES = ["age", "sex", "chol"]
NUMERIC = ["age", "chol"]
CATEGORICAL = ["sex"]
SOURCE_ORDER = tuple(shared.COHORT_FILES)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    cohorts, audit = shared.load_cohorts(SOURCE_ARCHIVE, zero_as_missing=True)
    mapped: dict[str, dict[str, Any]] = {}
    for name in SOURCE_ORDER:
        data = cohorts[name]
        frame = data["X"][FEATURES].copy()
        sex = pd.to_numeric(frame["sex"], errors="raise")
        if not set(sex.dropna().unique()).issubset({0, 1}):
            raise ValueError(f"Unexpected source sex encoding in {name}")
        frame["sex"] = sex.map({0: "female", 1: "male"})
        frame["age"] = pd.to_numeric(frame["age"], errors="raise")
        frame["chol"] = pd.to_numeric(frame["chol"], errors="raise")
        mapped[name] = {
            "X": frame[FEATURES].reset_index(drop=True),
            "y": data["y"].astype(np.int8),
            "row_index": data["row_index"].astype(int),
        }
    return mapped, audit


def load_duke() -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    frame = pd.read_excel(DUKE_WORKBOOK, engine="xlrd")
    expected_columns = ["sex", "age", "cad.dur", "choleste", "sigdz", "tvdlm"]
    if frame.shape != (3504, 6) or frame.columns.tolist() != expected_columns:
        raise ValueError(
            f"Unexpected Duke ACATH schema: shape={frame.shape}, columns={frame.columns}"
        )
    if not frame["sigdz"].isin([0, 1]).all():
        raise ValueError("Duke sigdz target must contain only binary 0/1 labels")
    if not frame["sex"].isin([0, 1]).all():
        raise ValueError("Duke sex must contain only source-documented values 0/1")
    features = pd.DataFrame(
        {
            "age": pd.to_numeric(frame["age"], errors="raise").astype(float),
            "sex": frame["sex"].map({0: "male", 1: "female"}),
            "chol": pd.to_numeric(frame["choleste"], errors="raise").astype(float),
        }
    )[FEATURES]
    labels = frame["sigdz"].astype(np.int8).to_numpy()
    audit = {
        "rows": int(len(frame)),
        "columns": frame.columns.tolist(),
        "target_counts": {str(k): int(v) for k, v in sorted(Counter(labels).items())},
        "predictor_missing_counts": {str(k): int(v) for k, v in features.isna().sum().items()},
        "sex_counts_after_mapping": {
            str(k): int(v) for k, v in sorted(Counter(features["sex"]).items())
        },
        "target_threshold": ">=75% diameter narrowing in at least one major coronary artery",
        "target_row_index_policy": (
            "Workbook row order; the public table has no patient identifier."
        ),
    }
    return features.reset_index(drop=True), labels, audit


def build_preprocessor(
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
) -> ColumnTransformer:
    numeric_features = NUMERIC if numeric_features is None else numeric_features
    categorical_features = CATEGORICAL if categorical_features is None else categorical_features
    numeric = Pipeline(
        [
            (
                "imputer",
                SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            ),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
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
            ("numeric", numeric, numeric_features),
            ("categorical", categorical, categorical_features),
        ],
        remainder="drop",
        sparse_threshold=0.0,
    )


def source_split(
    cohorts: dict[str, dict[str, Any]], source_names: tuple[str, ...]
) -> dict[str, Any]:
    fit_X: list[pd.DataFrame] = []
    fit_y: list[np.ndarray] = []
    fit_domains: list[np.ndarray] = []
    platt_X: list[pd.DataFrame] = []
    platt_y: list[np.ndarray] = []
    platt_domains: list[np.ndarray] = []
    conformal_X: list[pd.DataFrame] = []
    conformal_y: list[np.ndarray] = []
    conformal_domains: list[np.ndarray] = []
    splits: dict[str, Any] = {}
    for source_index, name in enumerate(source_names):
        data = cohorts[name]
        indices = np.arange(len(data["y"]))
        fit_indices, reserved_indices = train_test_split(
            indices,
            test_size=(PROBABILITY_CALIBRATION_FRACTION + CONFORMAL_CALIBRATION_FRACTION),
            random_state=SEED + 100 + source_index,
            stratify=data["y"],
        )
        platt_indices, conformal_indices = train_test_split(
            reserved_indices,
            test_size=CONFORMAL_CALIBRATION_FRACTION
            / (PROBABILITY_CALIBRATION_FRACTION + CONFORMAL_CALIBRATION_FRACTION),
            random_state=SEED + 200 + source_index,
            stratify=data["y"][reserved_indices],
        )
        fit_X.append(data["X"].iloc[fit_indices].reset_index(drop=True))
        fit_y.append(data["y"][fit_indices])
        fit_domains.append(np.full(len(fit_indices), name, dtype=object))
        platt_X.append(data["X"].iloc[platt_indices].reset_index(drop=True))
        platt_y.append(data["y"][platt_indices])
        platt_domains.append(np.full(len(platt_indices), name, dtype=object))
        conformal_X.append(data["X"].iloc[conformal_indices].reset_index(drop=True))
        conformal_y.append(data["y"][conformal_indices])
        conformal_domains.append(np.full(len(conformal_indices), name, dtype=object))
        splits[name] = {
            "fit_seed": int(SEED + 100 + source_index),
            "calibration_partition_seed": int(SEED + 200 + source_index),
            "fit_row_indices": data["row_index"][fit_indices].astype(int).tolist(),
            "probability_calibration_row_indices": data["row_index"][platt_indices]
            .astype(int)
            .tolist(),
            "conformal_calibration_row_indices": data["row_index"][conformal_indices]
            .astype(int)
            .tolist(),
            "fit_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][fit_indices]).items())
            },
            "probability_calibration_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][platt_indices]).items())
            },
            "conformal_calibration_class_counts": {
                str(k): int(v) for k, v in sorted(Counter(data["y"][conformal_indices]).items())
            },
        }
    return {
        "fit_X": pd.concat(fit_X, ignore_index=True),
        "fit_y": np.concatenate(fit_y),
        "fit_domains": np.concatenate(fit_domains),
        "platt_X": pd.concat(platt_X, ignore_index=True),
        "platt_y": np.concatenate(platt_y),
        "platt_domains": np.concatenate(platt_domains),
        "conformal_X": pd.concat(conformal_X, ignore_index=True),
        "conformal_y": np.concatenate(conformal_y),
        "conformal_domains": np.concatenate(conformal_domains),
        "splits": splits,
    }


def train_source_model(
    cohorts: dict[str, dict[str, Any]],
    source_names: tuple[str, ...],
    feature_names: list[str] | None = None,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
) -> dict[str, Any]:
    feature_names = FEATURES if feature_names is None else feature_names
    numeric_features = NUMERIC if numeric_features is None else numeric_features
    categorical_features = CATEGORICAL if categorical_features is None else categorical_features
    split = source_split(cohorts, source_names)
    fit_X = split["fit_X"]
    fit_y = split["fit_y"]
    fit_domains = split["fit_domains"]
    platt_X = split["platt_X"]
    platt_y = split["platt_y"]
    platt_domains = split["platt_domains"]
    cal_X = split["conformal_X"]
    cal_y = split["conformal_y"]
    cal_domains = split["conformal_domains"]
    split_info = split["splits"]
    fit_weights = shared.equal_domain_weights(fit_domains)
    platt_weights = shared.equal_domain_weights(platt_domains)
    cal_weights = shared.equal_domain_weights(cal_domains)
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    fit_matrix = preprocessor.fit_transform(fit_X)
    platt_matrix = preprocessor.transform(platt_X)
    cal_matrix = preprocessor.transform(cal_X)
    predictor = LogisticRegression(C=1.0, solver="liblinear", max_iter=5000, random_state=SEED)
    predictor.fit(fit_matrix, fit_y, sample_weight=fit_weights)
    raw_platt_p = predictor.predict_proba(platt_matrix)[:, 1]
    platt_logits = np.log(
        np.clip(raw_platt_p, 1e-7, 1 - 1e-7) / np.clip(1 - raw_platt_p, 1e-7, 1.0)
    )
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=5000, random_state=SEED)
    calibrator.fit(platt_logits.reshape(-1, 1), platt_y, sample_weight=platt_weights)
    raw_cal_p = predictor.predict_proba(cal_matrix)[:, 1]
    cal_logits = np.log(np.clip(raw_cal_p, 1e-7, 1 - 1e-7) / np.clip(1 - raw_cal_p, 1e-7, 1.0))
    calibrated_cal_p = calibrator.predict_proba(cal_logits.reshape(-1, 1))[:, 1]

    forest = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=SEED,
        n_jobs=1,
    )
    forest.fit(fit_matrix, sample_weight=fit_weights)
    forest_cal_scores = -forest.score_samples(cal_matrix)

    neighbor_count = min(K_NEIGHBORS, len(fit_matrix))
    neighbors = NearestNeighbors(n_neighbors=neighbor_count, metric="euclidean", n_jobs=1)
    neighbors.fit(fit_matrix)
    knn_cal_distances = neighbors.kneighbors(cal_matrix, return_distance=True)[0]
    knn_cal_scores = knn_cal_distances.mean(axis=1)

    conformal_scores = 1.0 - np.where(cal_y == 1, calibrated_cal_p, 1.0 - calibrated_cal_p)
    conformal_threshold, conformal_by_domain = domain_robust_threshold(
        conformal_scores, cal_domains, CONFORMAL_ALPHA
    )
    knn_threshold, knn_thresholds = domain_robust_threshold(knn_cal_scores, cal_domains, OOD_ALPHA)
    forest_threshold, forest_thresholds = domain_robust_threshold(
        forest_cal_scores, cal_domains, OOD_ALPHA
    )
    pooled_forest_threshold = shared.weighted_quantile(forest_cal_scores, cal_weights, 0.95)
    pooled_knn_threshold = shared.weighted_quantile(knn_cal_scores, cal_weights, 0.95)

    cal_frame = pd.DataFrame(
        {
            "cohort": cal_domains,
            "row_index": np.concatenate(
                [
                    np.asarray(split_info[name]["conformal_calibration_row_indices"])
                    for name in source_names
                ]
            ),
            "label": cal_y,
            "raw_probability": raw_cal_p,
            "calibrated_probability": calibrated_cal_p,
            "conformal_nonconformity": conformal_scores,
            "isolation_forest_score": forest_cal_scores,
            "knn_support_score": knn_cal_scores,
        }
    )
    platt_frame = pd.DataFrame(
        {
            "cohort": platt_domains,
            "row_index": np.concatenate(
                [
                    np.asarray(split_info[name]["probability_calibration_row_indices"])
                    for name in source_names
                ]
            ),
            "label": platt_y,
            "raw_probability": raw_platt_p,
            "calibrated_probability": calibrator.predict_proba(platt_logits.reshape(-1, 1))[:, 1],
        }
    )
    return {
        "preprocessor": preprocessor,
        "predictor": predictor,
        "calibrator": calibrator,
        "forest": forest,
        "neighbors": neighbors,
        "fit_X": fit_X,
        "fit_y": fit_y,
        "fit_domains": fit_domains,
        "fit_matrix": fit_matrix,
        "fit_weights": fit_weights,
        "platt_X": platt_X,
        "platt_y": platt_y,
        "platt_domains": platt_domains,
        "platt_matrix": platt_matrix,
        "platt_predictions": platt_frame,
        "cal_X": cal_X,
        "cal_y": cal_y,
        "cal_domains": cal_domains,
        "cal_matrix": cal_matrix,
        "calibrated_cal_p": calibrated_cal_p,
        "forest_cal_scores": forest_cal_scores,
        "knn_cal_scores": knn_cal_scores,
        "conformal_scores": conformal_scores,
        "conformal_threshold": conformal_threshold,
        "conformal_by_domain": conformal_by_domain,
        "knn_threshold": knn_threshold,
        "knn_thresholds": knn_thresholds,
        "forest_threshold": forest_threshold,
        "forest_thresholds": forest_thresholds,
        "pooled_forest_threshold": pooled_forest_threshold,
        "pooled_knn_threshold": pooled_knn_threshold,
        "calibration_predictions": cal_frame,
        "splits": split_info,
        "source_names": source_names,
        "features": feature_names,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }


def score_features(model: dict[str, Any], features: pd.DataFrame) -> dict[str, np.ndarray]:
    matrix = model["preprocessor"].transform(features[model["features"]])
    raw_p = model["predictor"].predict_proba(matrix)[:, 1]
    logits = np.log(np.clip(raw_p, 1e-7, 1 - 1e-7) / np.clip(1 - raw_p, 1e-7, 1.0))
    calibrated_p = model["calibrator"].predict_proba(logits.reshape(-1, 1))[:, 1]
    forest_scores = -model["forest"].score_samples(matrix)
    knn_scores = model["neighbors"].kneighbors(matrix, return_distance=True)[0].mean(axis=1)
    probabilities = np.column_stack([1.0 - calibrated_p, calibrated_p])
    sets = conformal_prediction_sets(probabilities, model["conformal_threshold"])
    singleton = sets.sum(axis=1) == 1
    set_prediction = np.where(singleton, sets.argmax(axis=1), -1)
    knn_flag = knn_scores > model["knn_threshold"]
    forest_flag = forest_scores > model["forest_threshold"]
    pooled_knn_flag = knn_scores > model["pooled_knn_threshold"]
    pooled_forest_flag = forest_scores > model["pooled_forest_threshold"]
    combined_abstain = ~singleton | knn_flag
    combined_prediction = np.where(combined_abstain, -1, set_prediction)
    return {
        "raw_probability": raw_p,
        "calibrated_probability": calibrated_p,
        "isolation_forest_score": forest_scores,
        "knn_support_score": knn_scores,
        "conformal_set_0": sets[:, 0],
        "conformal_set_1": sets[:, 1],
        "conformal_prediction": set_prediction,
        "conformal_abstain": ~singleton,
        "knn_ood_flag": knn_flag,
        "isolation_forest_ood_flag": forest_flag,
        "pooled_knn_ood_flag": pooled_knn_flag,
        "pooled_isolation_forest_ood_flag": pooled_forest_flag,
        "combined_abstain": combined_abstain,
        "combined_prediction": combined_prediction,
    }


def binary_metrics(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    return shared.predictive_metrics(y, probabilities)


def summarize_detector(
    source_scores: np.ndarray,
    target_scores: np.ndarray,
    target_threshold: float,
) -> dict[str, Any]:
    domain_y = np.concatenate([np.zeros(len(source_scores)), np.ones(len(target_scores))])
    scores = np.concatenate([source_scores, target_scores])
    source_alerts = source_scores > target_threshold
    target_alerts = target_scores > target_threshold
    return {
        "source_calibration_rows": int(len(source_scores)),
        "target_rows": int(len(target_scores)),
        "target_vs_source_auroc": float(roc_auc_score(domain_y, scores)),
        "source_false_alert_count": int(source_alerts.sum()),
        "source_false_alert_rate": float(source_alerts.mean()),
        "target_alert_count": int(target_alerts.sum()),
        "target_alert_rate": float(target_alerts.mean()),
        "threshold": float(target_threshold),
    }


def summarize_combined(
    y: np.ndarray, probabilities: np.ndarray, output: dict[str, np.ndarray]
) -> dict[str, Any]:
    accepted = ~output["combined_abstain"]
    accepted_prediction = output["combined_prediction"][accepted]
    accepted_y = y[accepted]
    errors = accepted_prediction != accepted_y
    return {
        "n": int(len(y)),
        "accepted_n": int(accepted.sum()),
        "coverage": float(accepted.mean()),
        "abstention_rate": float((~accepted).mean()),
        "accepted_error_count": int(errors.sum()),
        "accepted_error_rate": float(errors.mean()) if len(errors) else None,
        "accepted_accuracy": float(1.0 - errors.mean()) if len(errors) else None,
        "accepted_probability_metrics": (
            binary_metrics(accepted_y, probabilities[accepted])
            if len(accepted_y) and np.unique(accepted_y).size == 2
            else {"status": "not estimable: accepted set lacks both classes"}
        ),
    }


def score_lodo(
    cohorts: dict[str, dict[str, Any]],
    feature_names: list[str] | None = None,
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    feature_names = FEATURES if feature_names is None else feature_names
    numeric_features = NUMERIC if numeric_features is None else numeric_features
    categorical_features = CATEGORICAL if categorical_features is None else categorical_features
    folds: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for heldout in SOURCE_ORDER:
        train_domains = tuple(name for name in SOURCE_ORDER if name != heldout)
        model = train_source_model(
            cohorts,
            train_domains,
            feature_names=feature_names,
            numeric_features=numeric_features,
            categorical_features=categorical_features,
        )
        target = cohorts[heldout]
        output = score_features(model, target["X"])
        y = target["y"]
        probabilities = output["calibrated_probability"]
        sets = np.column_stack([output["conformal_set_0"], output["conformal_set_1"]])
        iso = summarize_detector(
            model["forest_cal_scores"], output["isolation_forest_score"], model["forest_threshold"]
        )
        knn = summarize_detector(
            model["knn_cal_scores"], output["knn_support_score"], model["knn_threshold"]
        )
        folds.append(
            {
                "heldout_source_domain": heldout,
                "training_domains": list(train_domains),
                "n": int(len(y)),
                "predictive_metrics": binary_metrics(y, probabilities),
                "conformal": conformal_selective_summary(y, sets),
                "combined_selective": summarize_combined(y, probabilities, output),
                "ood": {"knn": knn, "isolation_forest": iso},
                "source_calibration_false_alert": {
                    "knn": float(np.mean(model["knn_cal_scores"] > model["knn_threshold"])),
                    "isolation_forest": float(
                        np.mean(model["forest_cal_scores"] > model["forest_threshold"])
                    ),
                },
                "domain_registry_gate": {
                    "heldout_domain_registered": heldout in model["source_names"],
                    "action": "abstain" if heldout not in model["source_names"] else "continue",
                    "reason": (
                        "domain_not_in_source_registry"
                        if heldout not in model["source_names"]
                        else None
                    ),
                },
                "conformal_source_domain_thresholds": model["conformal_by_domain"],
                "ood_source_domain_thresholds": {
                    "knn": model["knn_thresholds"],
                    "isolation_forest": model["forest_thresholds"],
                },
            }
        )
        frame = pd.DataFrame(
            {
                "heldout_source_domain": heldout,
                "row_index": target["row_index"],
                "label": y,
                **output,
            }
        )
        prediction_frames.append(frame)
    return folds, pd.concat(prediction_frames, ignore_index=True)


def macro_summary(folds: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, list[float]] = {
        "roc_auc": [],
        "average_precision": [],
        "brier_score": [],
        "ece_10_bins": [],
        "conformal_coverage": [],
        "conformal_singleton_coverage": [],
        "conformal_selective_risk": [],
        "knn_ood_auroc": [],
        "knn_target_alert_rate": [],
        "knn_source_false_alert_rate": [],
        "isolation_forest_ood_auroc": [],
        "isolation_forest_target_alert_rate": [],
        "isolation_forest_source_false_alert_rate": [],
    }
    for fold in folds:
        pred = fold["predictive_metrics"]
        conformal = fold["conformal"]
        metrics["roc_auc"].append(float(pred["roc_auc"]))
        metrics["average_precision"].append(float(pred["average_precision"]))
        metrics["brier_score"].append(float(pred["brier_score"]))
        metrics["ece_10_bins"].append(float(pred["ece_10_bins"]))
        metrics["conformal_coverage"].append(float(conformal["empirical_set_coverage"]))
        metrics["conformal_singleton_coverage"].append(float(conformal["singleton_coverage"]))
        metrics["conformal_selective_risk"].append(float(conformal["selective_risk"]))
        for method in ("knn", "isolation_forest"):
            prefix = "knn" if method == "knn" else "isolation_forest"
            detector = fold["ood"][method]
            metrics[f"{prefix}_ood_auroc"].append(float(detector["target_vs_source_auroc"]))
            metrics[f"{prefix}_target_alert_rate"].append(float(detector["target_alert_rate"]))
            metrics[f"{prefix}_source_false_alert_rate"].append(
                float(detector["source_false_alert_rate"])
            )
    return {
        key: {
            "mean": float(np.mean(values)),
            "sd": float(np.std(values, ddof=1)),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "fold_values": values,
        }
        for key, values in metrics.items()
    }


def fairness_summary(y: np.ndarray, probabilities: np.ndarray, sex: pd.Series) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for group in ("female", "male"):
        mask = sex.to_numpy() == group
        if mask.sum() and np.unique(y[mask]).size == 2:
            output[group] = {
                "n": int(mask.sum()),
                "predictive_metrics": binary_metrics(y[mask], probabilities[mask]),
            }
        else:
            output[group] = {"n": int(mask.sum()), "status": "not estimable"}
    return output


def model_explanation(model: dict[str, Any]) -> list[dict[str, Any]]:
    names = model["preprocessor"].get_feature_names_out().tolist()
    coefficients = model["predictor"].coef_[0]
    return [
        {
            "transformed_feature": str(name),
            "standardized_log_odds_coefficient": float(coefficient),
            "odds_ratio_per_transformed_unit": float(np.exp(np.clip(coefficient, -30, 30))),
        }
        for name, coefficient in zip(names, coefficients, strict=True)
    ]


def create_deployment_bundle(model: dict[str, Any], target_definition: str) -> dict[str, Any]:
    categorical_processor = model["preprocessor"].named_transformers_["categorical"]
    imputer = categorical_processor.named_steps["imputer"]
    categories = categorical_processor.named_steps["onehot"].categories_
    imputed_names = imputer.get_feature_names_out(model["categorical_features"])
    allowed_categories = {
        str(name): [str(value) for value in categories[index]]
        for index, name in enumerate(imputed_names)
        if name in model["categorical_features"]
    }
    return {
        "preprocessor": model["preprocessor"],
        "predictor": model["predictor"],
        "calibrator": model["calibrator"],
        "neighbors": model["neighbors"],
        "source_domains": list(model["source_names"]),
        "conformal_thresholds_by_domain": model["conformal_by_domain"],
        "ood_thresholds_by_domain": model["knn_thresholds"],
        "features": model["features"],
        "numeric_features": model["numeric_features"],
        "categorical_features": model["categorical_features"],
        "allowed_categories": allowed_categories,
        "target_definition": target_definition,
    }


def make_figure(
    output_path: Path,
    y: np.ndarray,
    probabilities: np.ndarray,
    output: dict[str, np.ndarray],
    model: dict[str, Any],
) -> None:
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    curve = uncertainty_evidence(y, probabilities)
    risk = curve["selective_risk"]
    axes[0].plot(
        [item["coverage"] for item in risk],
        [item["risk"] for item in risk],
        marker="o",
        color="#286090",
    )
    axes[0].set(title="Confidence-ranked selective risk", xlabel="Coverage", ylabel="Error rate")
    axes[0].set_xlim(0.45, 1.01)
    axes[0].set_ylim(0, 1)
    axes[0].grid(alpha=0.25)

    cal_scores = model["knn_cal_scores"]
    test_scores = output["knn_support_score"]
    bins = np.histogram_bin_edges(np.concatenate([cal_scores, test_scores]), bins=35)
    axes[1].hist(cal_scores, bins=bins, density=True, alpha=0.6, label="Source calibration")
    axes[1].hist(test_scores, bins=bins, density=True, alpha=0.55, label="Duke target")
    axes[1].axvline(
        model["knn_threshold"], color="#a33", linestyle="--", label="Frozen 95% threshold"
    )
    axes[1].set(title="Source-support distance", xlabel="Mean 10-NN distance", ylabel="Density")
    axes[1].legend(fontsize=8)

    observed, predicted = calibration_curve(y, probabilities, n_bins=10, strategy="uniform")
    axes[2].plot([0, 1], [0, 1], linestyle="--", color="grey", label="Ideal")
    axes[2].plot(predicted, observed, marker="o", color="#397b46", label="Duke target")
    axes[2].set(
        title="External reliability diagram",
        xlabel="Mean predicted risk",
        ylabel="Observed event rate",
    )
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(0, 1)
    axes[2].legend(fontsize=8)
    figure.suptitle("CD-XD-005: source-only model on Duke ACATH", y=1.02)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def run_experiment(output_dir: Path) -> None:
    for path in (
        SOURCE_ARCHIVE,
        DUKE_ARCHIVE,
        DUKE_WORKBOOK,
        SOURCE_MANIFEST,
        TARGET_MANIFEST,
        PROTOCOL,
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Required frozen study input is missing: {path}")
    target_meta = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    source_meta = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    if source_meta["archive_sha256"] != sha256_file(SOURCE_ARCHIVE):
        raise ValueError("UCI source archive hash differs from its registered manifest")
    if target_meta["archive_sha256"] != sha256_file(DUKE_ARCHIVE):
        raise ValueError("Duke download archive hash differs from the registered manifest")
    if target_meta["workbook_sha256"] != sha256_file(DUKE_WORKBOOK):
        raise ValueError("Duke workbook hash differs from the registered manifest")
    if target_meta["workbook_sha256"] == "TO_BE_VERIFIED":
        raise ValueError("Duke workbook hash must be frozen before the experiment is run")
    with zipfile.ZipFile(DUKE_ARCHIVE) as archive:
        if (
            archive.namelist() != ["acath.xls"]
            or archive.read("acath.xls") != DUKE_WORKBOOK.read_bytes()
        ):
            raise ValueError("Extracted Duke workbook does not match the registered source archive")

    source_cohorts, source_audit = load_source()
    target_X, target_y, target_audit = load_duke()
    if target_audit["target_counts"] != target_meta["target_counts"]:
        raise ValueError("Duke target counts differ from the registered cohort manifest")
    lodo_folds, lodo_predictions = score_lodo(source_cohorts)
    model = train_source_model(source_cohorts, SOURCE_ORDER)
    prediction = score_features(model, target_X)
    target_p = prediction["calibrated_probability"]
    target_raw_p = prediction["raw_probability"]
    sets = np.column_stack([prediction["conformal_set_0"], prediction["conformal_set_1"]])

    knn_summary = summarize_detector(
        model["knn_cal_scores"], prediction["knn_support_score"], model["knn_threshold"]
    )
    iso_summary = summarize_detector(
        model["forest_cal_scores"], prediction["isolation_forest_score"], model["forest_threshold"]
    )
    pooled_knn_summary = summarize_detector(
        model["knn_cal_scores"], prediction["knn_support_score"], model["pooled_knn_threshold"]
    )
    pooled_iso_summary = summarize_detector(
        model["forest_cal_scores"],
        prediction["isolation_forest_score"],
        model["pooled_forest_threshold"],
    )
    target_metrics = binary_metrics(target_y, target_p)
    raw_metrics = binary_metrics(target_y, target_raw_p)
    conformal_summary = conformal_selective_summary(target_y, sets)
    combined_summary = summarize_combined(target_y, target_p, prediction)
    bootstrap = shared.bootstrap_predictive_intervals(
        target_y, target_raw_p, target_p, seed=SEED + 1000
    )
    ood_ci = shared.bootstrap_ood_auc_interval(
        model["knn_cal_scores"], prediction["knn_support_score"], seed=SEED + 2000
    )
    target_source_cal = model["calibration_predictions"]
    source_cal_summary = binary_metrics(
        target_source_cal["label"].to_numpy(),
        target_source_cal["calibrated_probability"].to_numpy(),
    )
    subgroup = fairness_summary(target_y, target_p, target_X["sex"])
    deploy_bundle = create_deployment_bundle(
        model, target_definition="UCI num > 0 (>50% stenosis); research only."
    )
    guarded_predictor = DomainAwareSelectivePredictor(deploy_bundle)
    domain_gate = guarded_predictor.predict(target_X, domain_id="duke_acath")
    gate_action_counts = dict(Counter(item["action"] for item in domain_gate))
    gate_reason_counts = dict(Counter(item["reason"] for item in domain_gate))

    metrics: dict[str, Any] = {
        "study_id": "CD-XD-005",
        "target_dataset": "Duke ACATH",
        "endpoint_compatibility": "Not identical: UCI source >50%; Duke target >=75% stenosis.",
        "target_rows": int(len(target_y)),
        "target_class_counts": target_audit["target_counts"],
        "source_calibration_metrics": source_cal_summary,
        "raw_source_model_metrics_on_target": raw_metrics,
        "source_platt_calibrated_metrics_on_target": target_metrics,
        "target_bootstrap_95_ci": bootstrap,
        "conformal": {
            "alpha": CONFORMAL_ALPHA,
            "source_domain_thresholds": model["conformal_by_domain"],
            "worst_source_threshold": float(model["conformal_threshold"]),
            "target_summary": conformal_summary,
            "interpretation": (
                "Empirical target coverage is measured; source split-conformal coverage is not "
                "assumed to transfer under dataset shift."
            ),
        },
        "combined_abstention": {
            "rule": (
                "abstain if the conformal set is not singleton or kNN support distance "
                "is above its threshold"
            ),
            "target_summary": combined_summary,
        },
        "domain_registry_gate": {
            "target_domain_id": "duke_acath",
            "registered_source_domains": list(SOURCE_ORDER),
            "action_counts": gate_action_counts,
            "reason_counts": gate_reason_counts,
            "coverage": float(gate_action_counts.get("classify", 0) / len(target_y)),
            "interpretation": (
                "The source registry gate rejects any site not identified as one of the "
                "development cohorts; site identity must come from trusted metadata."
            ),
        },
        "ood": {
            "primary_knn_domain_robust": {
                **knn_summary,
                "source_domain_thresholds": model["knn_thresholds"],
                "target_auroc_bootstrap_95_ci": ood_ci,
            },
            "knn_pooled_threshold_ablation": pooled_knn_summary,
            "isolation_forest_domain_robust": {
                **iso_summary,
                "source_domain_thresholds": model["forest_thresholds"],
            },
            "isolation_forest_pooled_threshold_baseline": pooled_iso_summary,
        },
        "lodo_source_domain_stress_test": {
            "folds": lodo_folds,
            "macro_summary": macro_summary(lodo_folds),
            "interpretation": (
                "Retrospective source-domain stress test: UCI components overlap the historical "
                "Heart5 project composite and are not independent external cohorts."
            ),
        },
        "supported_subgroup_metrics_by_sex": subgroup,
        "linear_model_explanation": model_explanation(model),
        "limitations": [
            "The Duke endpoint threshold is >=75%, versus >50% in UCI source cohorts.",
            "Cohort, referral, historical-era, endpoint, and measurement shifts are confounded.",
            (
                "Duke cholesterol is missing in 1,246 of 3,504 records and is imputed "
                "from source-fit rows."
            ),
            (
                "Target labels were not used for fitting, calibration, feature selection, "
                "or threshold selection."
            ),
            (
                "Prior cohort-level target counts were reviewed during schema validation, "
                "so this is exploratory rather than preregistered."
            ),
            (
                "The model and uncertainty layer are research outputs, not a clinically "
                "validated diagnostic system."
            ),
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(exist_ok=True)
    target_predictions = pd.DataFrame(
        {
            "target_row_index": np.arange(len(target_y)),
            "observed_label_for_scoring": target_y,
            "domain_gate_action": [item["action"] for item in domain_gate],
            "domain_gate_reason": [item["reason"] for item in domain_gate],
            "deployment_probability": [item["probability"] for item in domain_gate],
            "deployment_prediction": [item["prediction"] for item in domain_gate],
            **{f"exploratory_{name}": values for name, values in prediction.items()},
        }
    )
    calibration_predictions = model["calibration_predictions"].copy()
    calibration_predictions["conformal_include_0"] = (
        1.0 - (1.0 - calibration_predictions["calibrated_probability"])
        <= model["conformal_threshold"]
    )
    calibration_predictions["conformal_include_1"] = (
        1.0 - calibration_predictions["calibrated_probability"] <= model["conformal_threshold"]
    )
    (output_dir / "study_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    target_predictions.to_csv(output_dir / "target_predictions.csv", index=False)
    calibration_predictions.to_csv(output_dir / "source_calibration_predictions.csv", index=False)
    model["platt_predictions"].to_csv(output_dir / "platt_calibration_predictions.csv", index=False)
    lodo_predictions.to_csv(output_dir / "lodo_source_predictions.csv", index=False)
    joblib.dump(deploy_bundle, output_dir / "model_bundle.joblib", compress=3)
    make_figure(
        figure_dir / "duke_transport_reliability.png", target_y, target_p, prediction, model
    )

    code_paths = [
        Path(__file__),
        ROOT / "experiments" / "run_lodo_transfer.py",
        ROOT / "src" / "cardiodiag" / "uncertainty.py",
        ROOT / "src" / "cardiodiag" / "reliability.py",
        ROOT / "src" / "cardiodiag" / "domain_guard.py",
    ]
    generated_paths = [
        output_dir / "study_metrics.json",
        output_dir / "target_predictions.csv",
        output_dir / "source_calibration_predictions.csv",
        output_dir / "platt_calibration_predictions.csv",
        output_dir / "lodo_source_predictions.csv",
        output_dir / "model_bundle.joblib",
        figure_dir / "duke_transport_reliability.png",
    ]
    manifest = {
        "study_id": "CD-XD-005",
        "created_utc": datetime.now(UTC).isoformat(),
        "seed": SEED,
        "source_fit_calibration_split": {
            "fit_fraction_per_source": 1
            - PROBABILITY_CALIBRATION_FRACTION
            - CONFORMAL_CALIBRATION_FRACTION,
            "probability_calibration_fraction_per_source": PROBABILITY_CALIBRATION_FRACTION,
            "conformal_calibration_fraction_per_source": CONFORMAL_CALIBRATION_FRACTION,
            "split_indices_by_source": model["splits"],
            "source_fit_domain_counts": {
                str(k): int(v) for k, v in sorted(Counter(model["fit_domains"]).items())
            },
            "source_calibration_domain_counts": {
                str(k): int(v) for k, v in sorted(Counter(model["cal_domains"]).items())
            },
            "probability_calibration_domain_counts": {
                str(k): int(v) for k, v in sorted(Counter(model["platt_domains"]).items())
            },
        },
        "model": {
            "predictor": "domain-weighted logistic regression, C=1, liblinear",
            "calibrator": "source-only Platt logistic regression, C=1e6",
            "features": FEATURES,
            "source_cohorts": SOURCE_ORDER,
            "domain_weighting": "equal total sample weight per source cohort",
            "ood_primary": (
                "mean Euclidean distance to 10 nearest source-fit rows; max "
                "source-specific 95% conformal quantile"
            ),
            "conformal": (
                "binary nonconformity 1-p(y); max source-specific finite-sample 90% quantile"
            ),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
        },
        "source_audit": source_audit,
        "target_audit": target_audit,
        "input_hashes": {
            str(path.relative_to(ROOT)): sha256_file(path)
            for path in (
                SOURCE_ARCHIVE,
                DUKE_ARCHIVE,
                DUKE_WORKBOOK,
                SOURCE_MANIFEST,
                TARGET_MANIFEST,
                PROTOCOL,
            )
        },
        "code_hashes": {str(path.relative_to(ROOT)): sha256_file(path) for path in code_paths},
        "output_hashes": {
            str(path.relative_to(ROOT)): sha256_file(path) for path in generated_paths
        },
        "target_labels_used_for": (
            "Final evaluation metrics and row-level audit only; not training, calibration, "
            "feature selection, or thresholds."
        ),
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote CD-XD-005 metrics, predictions, and run manifest to {output_dir}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        run_experiment(args.output_dir)


if __name__ == "__main__":
    main()
