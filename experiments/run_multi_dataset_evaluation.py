"""Run nested within-task and source-only cross-cohort CARDIODIAG comparisons.

This experiment is deliberately separate from the frozen historical results.
The existing OVEC/OSEC definitions and corrected training-only preprocessing
are reused without changing their ensemble structure.
"""

from __future__ import annotations

import hashlib
import json
import logging
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.metrics import (
    auc,
    average_precision_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, learning_curve, train_test_split
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "multi_dataset_evaluation_20261108"
PROCESSED = ROOT / "data" / "processed" / "multi_dataset_evaluation_20261108"
DATASET_MANIFEST_PATH = RESULTS / "datasets" / "dataset_manifest.json"
SEED = 20261108
OUTER_FOLDS = 3
INNER_FOLDS = 3
CALIBRATION_FRACTION = 0.20
CONFORMAL_ALPHA = 0.10
OOD_QUANTILE = 0.95
CALIBRATION_BINS = 10
BOOTSTRAP_REPLICATES = 1000
MODEL_VARIANTS = ("logistic", "knn", "svm", "random_forest", "ovec", "osec")
MODEL_LABELS = {
    "logistic": "Logistic Regression",
    "knn": "K-Nearest Neighbors",
    "svm": "Support Vector Machine",
    "random_forest": "Random Forest",
    "ovec": "OVEC",
    "osec": "OSEC",
}
GRID_BY_MODEL: dict[str, list[dict[str, list[Any]]]] = {
    "logistic": [{"model__C": [0.1, 1.0, 10.0]}],
    "knn": [
        {
            "model__n_neighbors": [3, 5, 7],
            "model__weights": ["uniform", "distance"],
        }
    ],
    "svm": [
        {
            "model__C": [0.1, 1.0, 10.0],
            "model__kernel": ["linear", "rbf"],
        }
    ],
    "random_forest": [
        {
            "model__max_features": ["sqrt", None],
            "model__min_samples_leaf": [1, 3],
        }
    ],
    "ovec": [{}],
    "osec": [{"model__final_estimator__C": [0.1, 1.0, 10.0]}],
}
DATASET_SPECS = {
    "uci_cleveland": {
        "path": PROCESSED / "uci_cleveland.csv",
        "target": "cad_positive",
        "categorical": ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"],
        "task_family": "angiographic CAD",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
    "uci_hungary": {
        "path": PROCESSED / "uci_hungary.csv",
        "target": "cad_positive",
        "categorical": ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"],
        "task_family": "angiographic CAD",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
    "uci_switzerland": {
        "path": PROCESSED / "uci_switzerland.csv",
        "target": "cad_positive",
        "categorical": ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"],
        "task_family": "angiographic CAD",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
    "uci_va_long_beach": {
        "path": PROCESSED / "uci_va_long_beach.csv",
        "target": "cad_positive",
        "categorical": ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"],
        "task_family": "angiographic CAD",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
    "uci_heart_failure_519": {
        "path": PROCESSED / "uci_heart_failure_519_binary_event.csv",
        "target": "death_event",
        "categorical": ["anaemia", "diabetes", "high_blood_pressure", "sex", "smoking"],
        "task_family": "HF death event",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
    "uci_mi_complications_579": {
        "path": PROCESSED / "uci_mi_complications_579_admission_binary.csv",
        "target": "any_lethal_outcome",
        "categorical": [],
        "task_family": "MI lethal outcome",
        "protocol": "3x3 nested stratified CV with source-only conformal calibration holdout",
    },
}
UCI_CAD_DATASETS = (
    "uci_cleveland",
    "uci_hungary",
    "uci_switzerland",
    "uci_va_long_beach",
)
METRIC_KEYS = (
    "accuracy",
    "precision",
    "recall",
    "specificity",
    "f1",
    "roc_auc",
    "pr_auc",
    "brier",
    "ece_uniform",
    "ece_weighted_uniform",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_value(value), indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def mark_categorical(frame: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    result = frame.copy()
    result.attrs["categorical_columns"] = list(names)
    return result


def load_task(dataset_id: str) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    spec = DATASET_SPECS[dataset_id]
    frame = pd.read_csv(spec["path"])
    target = str(spec["target"])
    if target not in frame.columns:
        raise ValueError(f"Target {target!r} is missing from {spec['path']}")
    y = pd.to_numeric(frame.pop(target), errors="raise").astype(int)
    if not set(y.unique()).issubset({0, 1}) or y.nunique() != 2:
        raise ValueError(
            f"{dataset_id} requires a two-class target; found {y.value_counts().to_dict()}"
        )
    X = mark_categorical(frame, list(spec["categorical"]))
    return X, y, spec


def conformal_threshold(y_cal: np.ndarray, probability_cal: np.ndarray) -> float:
    true_probability = np.where(y_cal == 1, probability_cal, 1.0 - probability_cal)
    nonconformity = 1.0 - true_probability
    count = len(nonconformity)
    rank = int(np.ceil((count + 1) * (1.0 - CONFORMAL_ALPHA)))
    if rank > count:
        return 1.0
    return float(np.sort(nonconformity)[rank - 1])


def make_conformal_sets(probability: np.ndarray, threshold: float) -> list[list[int]]:
    result: list[list[int]] = []
    for p in np.asarray(probability, dtype=float):
        labels = []
        if p <= threshold:
            labels.append(0)
        if 1.0 - p <= threshold:
            labels.append(1)
        result.append(labels)
    return result


def conformal_summary(y: np.ndarray, sets: list[list[int]]) -> dict[str, float]:
    sizes = np.asarray([len(item) for item in sets], dtype=float)
    covered = np.asarray([int(label) in values for label, values in zip(y, sets, strict=True)])
    return {
        "empirical_coverage": float(covered.mean()),
        "average_set_size": float(sizes.mean()),
        "singleton_rate": float(np.mean(sizes == 1)),
        "empty_set_rate": float(np.mean(sizes == 0)),
    }


def ood_scores(
    estimator: Any,
    X_reference: pd.DataFrame,
    X_calibration: pd.DataFrame,
    X_evaluation: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    feature_pipeline = estimator[:-1]
    reference = feature_pipeline.transform(X_reference)
    calibration = feature_pipeline.transform(X_calibration)
    evaluation = feature_pipeline.transform(X_evaluation)
    neighbors = NearestNeighbors(n_neighbors=min(5, len(reference)), n_jobs=1)
    neighbors.fit(reference)
    calibration_scores = neighbors.kneighbors(calibration, return_distance=True)[0].mean(axis=1)
    evaluation_scores = neighbors.kneighbors(evaluation, return_distance=True)[0].mean(axis=1)
    threshold = float(np.quantile(calibration_scores, OOD_QUANTILE, method="higher"))
    return calibration_scores, evaluation_scores, evaluation_scores > threshold, threshold


def fit_search(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variant: str,
    seed: int,
    folds: int = INNER_FOLDS,
) -> GridSearchCV:
    pipeline = build_corrected_pipeline(X_train, variant=variant, seed=seed)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    search = GridSearchCV(
        pipeline,
        GRID_BY_MODEL[variant],
        scoring="roc_auc",
        cv=cv,
        n_jobs=1,
        refit=True,
        return_train_score=True,
        error_score="raise",
    )
    search.fit(X_train, y_train)
    return search


def metric_row(
    y: np.ndarray,
    probability: np.ndarray,
    dataset_id: str,
    variant: str,
    fold: str | int,
    split: str,
) -> dict[str, Any]:
    return {
        "dataset": dataset_id,
        "model": variant,
        "model_label": MODEL_LABELS[variant],
        "fold": fold,
        "split": split,
        **evaluate_predictions(y, probability),
    }


def stratified_bootstrap_intervals(
    y: np.ndarray, probability: np.ndarray, seed: int
) -> dict[str, float | None]:
    rng = np.random.default_rng(seed)
    by_class = [np.flatnonzero(y == value) for value in (0, 1)]
    metrics: dict[str, list[float]] = {"roc_auc": [], "pr_auc": [], "brier": []}
    for _ in range(BOOTSTRAP_REPLICATES):
        indices = np.concatenate(
            [
                rng.choice(class_indices, len(class_indices), replace=True)
                for class_indices in by_class
            ]
        )
        sample_y = y[indices]
        sample_p = probability[indices]
        metrics["roc_auc"].append(float(roc_auc_score(sample_y, sample_p)))
        metrics["pr_auc"].append(float(average_precision_score(sample_y, sample_p)))
        metrics["brier"].append(float(np.mean((sample_y - sample_p) ** 2)))
    return {
        f"{metric}_ci_low": float(np.quantile(values, 0.025)) for metric, values in metrics.items()
    } | {
        f"{metric}_ci_high": float(np.quantile(values, 0.975)) for metric, values in metrics.items()
    }


def get_inner_train_auc(search: GridSearchCV) -> float | None:
    values = search.cv_results_.get("mean_train_score")
    if values is None:
        return None
    result = float(values[search.best_index_])
    return result if np.isfinite(result) else None


def run_nested_model(
    dataset_id: str,
    X: pd.DataFrame,
    y: pd.Series,
    variant: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    conformal_rows: list[dict[str, Any]] = []
    outer = StratifiedKFold(n_splits=OUTER_FOLDS, shuffle=True, random_state=SEED)
    for fold, (train_indices, test_indices) in enumerate(outer.split(X, y), start=1):
        fold_seed = SEED + fold
        X_outer_train = mark_categorical(
            X.iloc[train_indices], list(X.attrs.get("categorical_columns", []))
        )
        X_test = X.iloc[test_indices].copy()
        y_outer_train = y.iloc[train_indices]
        y_test = y.iloc[test_indices].to_numpy(dtype=int)
        dev_indices, calibration_indices = train_test_split(
            np.arange(len(X_outer_train)),
            test_size=CALIBRATION_FRACTION,
            random_state=fold_seed,
            stratify=y_outer_train,
        )
        X_dev = mark_categorical(
            X_outer_train.iloc[dev_indices], list(X.attrs.get("categorical_columns", []))
        )
        X_calibration = X_outer_train.iloc[calibration_indices].copy()
        y_dev = y_outer_train.iloc[dev_indices]
        y_calibration = y_outer_train.iloc[calibration_indices].to_numpy(dtype=int)
        start = time.perf_counter()
        search = fit_search(X_dev, y_dev, variant, fold_seed)
        estimator = search.best_estimator_
        probability_test = estimator.predict_proba(X_test)[:, 1]
        probability_calibration = estimator.predict_proba(X_calibration)[:, 1]
        probability_train = estimator.predict_proba(X_dev)[:, 1]
        test_metrics = evaluate_predictions(y_test, probability_test)
        train_metrics = evaluate_predictions(y_dev.to_numpy(dtype=int), probability_train)
        conformal_q = conformal_threshold(y_calibration, probability_calibration)
        sets = make_conformal_sets(probability_test, conformal_q)
        conf_stats = conformal_summary(y_test, sets)
        cal_ood, test_ood, alerts, ood_threshold = ood_scores(
            estimator, X_dev, X_calibration, X_test
        )
        fold_rows.append(
            {
                **metric_row(y_test, probability_test, dataset_id, variant, fold, "outer_test"),
                "train_roc_auc_resubstitution": train_metrics["roc_auc"],
                "train_accuracy_resubstitution": train_metrics["accuracy"],
                "inner_validation_roc_auc_best": float(search.best_score_),
                "inner_training_roc_auc_at_best": get_inner_train_auc(search),
                "train_minus_outer_test_roc_auc": float(
                    train_metrics["roc_auc"] - test_metrics["roc_auc"]
                ),
                "inner_validation_minus_outer_test_roc_auc": float(
                    search.best_score_ - test_metrics["roc_auc"]
                ),
                "conformal_threshold": conformal_q,
                "conformal_alpha": CONFORMAL_ALPHA,
                **{f"conformal_{key}": value for key, value in conf_stats.items()},
                "ood_threshold_calibration_q95": ood_threshold,
                "ood_test_alert_rate": float(alerts.mean()),
                "ood_test_accepted_coverage": float((~alerts).mean()),
                "calibration_rows": len(calibration_indices),
                "development_rows": len(dev_indices),
                "outer_test_rows": len(test_indices),
                "best_params": json.dumps(json_value(search.best_params_), sort_keys=True),
                "inner_cv_candidate_count": len(search.cv_results_["params"]),
                "split_seed": fold_seed,
                "runtime_seconds": float(time.perf_counter() - start),
                "ood_calibration_score_mean": float(np.mean(cal_ood)),
                "ood_test_score_mean": float(np.mean(test_ood)),
            }
        )
        conformal_rows.append(
            {
                "dataset": dataset_id,
                "model": variant,
                "fold": fold,
                "alpha": CONFORMAL_ALPHA,
                "threshold": conformal_q,
                **conf_stats,
            }
        )
        for local_index, row_index in enumerate(test_indices):
            prediction_rows.append(
                {
                    "dataset": dataset_id,
                    "model": variant,
                    "fold": fold,
                    "row_index": int(row_index),
                    "y_true": int(y_test[local_index]),
                    "probability_positive": float(probability_test[local_index]),
                    "predicted_label_at_0_5": int(probability_test[local_index] >= 0.5),
                    "confidence": float(
                        max(probability_test[local_index], 1 - probability_test[local_index])
                    ),
                    "conformal_set": ";".join(str(item) for item in sets[local_index]),
                    "conformal_set_size": len(sets[local_index]),
                    "conformal_covered": int(y_test[local_index] in sets[local_index]),
                    "ood_score": float(test_ood[local_index]),
                    "ood_alert": int(alerts[local_index]),
                    "accepted_by_singleton_and_ood_diagnostics": int(
                        len(sets[local_index]) == 1 and not alerts[local_index]
                    ),
                }
            )
    return fold_rows, prediction_rows, conformal_rows


def build_nested_assignments(
    dataset_id: str, X: pd.DataFrame, y: pd.Series
) -> list[dict[str, Any]]:
    assignments: list[dict[str, Any]] = []
    outer = StratifiedKFold(n_splits=OUTER_FOLDS, shuffle=True, random_state=SEED)
    for fold, (train_indices, test_indices) in enumerate(outer.split(X, y), start=1):
        dev_indices, calibration_indices = train_test_split(
            np.arange(len(train_indices)),
            test_size=CALIBRATION_FRACTION,
            random_state=SEED + fold,
            stratify=y.iloc[train_indices],
        )
        outer_train_rows = np.asarray(train_indices, dtype=int)
        dev_rows = set(outer_train_rows[dev_indices].tolist())
        for row_index in train_indices:
            role = "development" if int(row_index) in dev_rows else "conformal_calibration"
            assignments.append(
                {
                    "dataset": dataset_id,
                    "fold": fold,
                    "row_index": int(row_index),
                    "split_role": role,
                    "split_seed": SEED + fold,
                }
            )
        assignments.extend(
            {
                "dataset": dataset_id,
                "fold": fold,
                "row_index": int(row_index),
                "split_role": "outer_test",
                "split_seed": SEED,
            }
            for row_index in test_indices
        )
    return assignments


def run_spectf_official_split(
    prediction_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    train_path = PROCESSED / "uci_spectf_train.csv"
    test_path = PROCESSED / "uci_spectf_test.csv"
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    target = "OVERALL_DIAGNOSIS"
    y_train = train.pop(target).astype(int)
    y_test = test.pop(target).astype(int).to_numpy()
    train.attrs["categorical_columns"] = []
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    conformal_rows: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    for model_index, variant in enumerate(MODEL_VARIANTS):
        seed = SEED + 200 + model_index
        stratified_dev, calibration_indices = train_test_split(
            np.arange(len(train)),
            test_size=CALIBRATION_FRACTION,
            random_state=seed,
            stratify=y_train,
        )
        X_dev = train.iloc[stratified_dev].copy()
        X_dev.attrs["categorical_columns"] = []
        X_cal = train.iloc[calibration_indices].copy()
        y_dev = y_train.iloc[stratified_dev]
        y_cal = y_train.iloc[calibration_indices].to_numpy(dtype=int)
        development_rows = set(stratified_dev.tolist())
        for row_index in range(len(train)):
            assignments.append(
                {
                    "dataset": "uci_spectf_heart",
                    "model": variant,
                    "fold": "official_split",
                    "row_index": row_index,
                    "split_role": (
                        "development" if row_index in development_rows else "conformal_calibration"
                    ),
                    "split_seed": seed,
                }
            )
        assignments.extend(
            {
                "dataset": "uci_spectf_heart",
                "model": variant,
                "fold": "official_split",
                "row_index": row_index,
                "split_role": "official_test",
                "split_seed": seed,
            }
            for row_index in range(len(test))
        )
        start = time.perf_counter()
        search = fit_search(X_dev, y_dev, variant, seed)
        estimator = search.best_estimator_
        p_test = estimator.predict_proba(test)[:, 1]
        p_cal = estimator.predict_proba(X_cal)[:, 1]
        p_train = estimator.predict_proba(X_dev)[:, 1]
        test_metrics = evaluate_predictions(y_test, p_test)
        train_metrics = evaluate_predictions(y_dev.to_numpy(dtype=int), p_train)
        q = conformal_threshold(y_cal, p_cal)
        sets = make_conformal_sets(p_test, q)
        conf_stats = conformal_summary(y_test, sets)
        _, test_ood, alerts, ood_threshold = ood_scores(estimator, X_dev, X_cal, test)
        fold_rows.append(
            {
                **metric_row(
                    y_test, p_test, "uci_spectf_heart", variant, "official_test", "official_test"
                ),
                "train_roc_auc_resubstitution": train_metrics["roc_auc"],
                "train_accuracy_resubstitution": train_metrics["accuracy"],
                "inner_validation_roc_auc_best": float(search.best_score_),
                "inner_training_roc_auc_at_best": get_inner_train_auc(search),
                "train_minus_outer_test_roc_auc": float(
                    train_metrics["roc_auc"] - test_metrics["roc_auc"]
                ),
                "inner_validation_minus_outer_test_roc_auc": float(
                    search.best_score_ - test_metrics["roc_auc"]
                ),
                "conformal_threshold": q,
                "conformal_alpha": CONFORMAL_ALPHA,
                **{f"conformal_{key}": value for key, value in conf_stats.items()},
                "ood_threshold_calibration_q95": ood_threshold,
                "ood_test_alert_rate": float(alerts.mean()),
                "ood_test_accepted_coverage": float((~alerts).mean()),
                "calibration_rows": len(calibration_indices),
                "development_rows": len(stratified_dev),
                "outer_test_rows": len(test),
                "best_params": json.dumps(json_value(search.best_params_), sort_keys=True),
                "inner_cv_candidate_count": len(search.cv_results_["params"]),
                "split_seed": seed,
                "runtime_seconds": float(time.perf_counter() - start),
                "official_split_train_rows": len(train),
                "official_split_test_rows": len(test),
            }
        )
        conformal_rows.append(
            {
                "dataset": "uci_spectf_heart",
                "model": variant,
                "fold": "official_test",
                "alpha": CONFORMAL_ALPHA,
                "threshold": q,
                **conf_stats,
            }
        )
        for index, row_index in enumerate(range(len(test))):
            prediction_rows.append(
                {
                    "dataset": "uci_spectf_heart",
                    "model": variant,
                    "fold": "official_test",
                    "row_index": row_index,
                    "y_true": int(y_test[index]),
                    "probability_positive": float(p_test[index]),
                    "predicted_label_at_0_5": int(p_test[index] >= 0.5),
                    "confidence": float(max(p_test[index], 1 - p_test[index])),
                    "conformal_set": ";".join(str(item) for item in sets[index]),
                    "conformal_set_size": len(sets[index]),
                    "conformal_covered": int(y_test[index] in sets[index]),
                    "ood_score": float(test_ood[index]),
                    "ood_alert": int(alerts[index]),
                    "accepted_by_singleton_and_ood_diagnostics": int(
                        len(sets[index]) == 1 and not alerts[index]
                    ),
                }
            )
    return fold_rows, prediction_rows, conformal_rows, assignments


def run_cross_pair(
    source_id: str,
    target_id: str,
    source: tuple[pd.DataFrame, pd.Series, dict[str, Any]],
    target: tuple[pd.DataFrame, pd.Series, dict[str, Any]],
    variant: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    started = time.perf_counter()
    X_source, y_source, source_spec = source
    X_target, y_target, _ = target
    seed = SEED + sum(ord(char) for char in source_id + target_id + variant)
    dev_indices, calibration_indices = train_test_split(
        np.arange(len(X_source)),
        test_size=CALIBRATION_FRACTION,
        random_state=seed,
        stratify=y_source,
    )
    assignments = [
        {
            "source_dataset": source_id,
            "target_dataset": target_id,
            "model": variant,
            "row_index": int(row_index),
            "split_role": (
                "source_development"
                if int(row_index) in set(dev_indices.tolist())
                else "source_calibration"
            ),
            "split_seed": seed,
        }
        for row_index in range(len(X_source))
    ]
    assignments.extend(
        {
            "source_dataset": source_id,
            "target_dataset": target_id,
            "model": variant,
            "row_index": int(row_index),
            "split_role": "target_test",
            "split_seed": seed,
        }
        for row_index in range(len(X_target))
    )
    X_dev = mark_categorical(X_source.iloc[dev_indices], list(source_spec["categorical"]))
    X_cal = X_source.iloc[calibration_indices].copy()
    y_dev = y_source.iloc[dev_indices]
    y_cal = y_source.iloc[calibration_indices].to_numpy(dtype=int)
    search = fit_search(X_dev, y_dev, variant, seed)
    estimator = search.best_estimator_
    p_target = estimator.predict_proba(X_target)[:, 1]
    p_cal = estimator.predict_proba(X_cal)[:, 1]
    q = conformal_threshold(y_cal, p_cal)
    sets = make_conformal_sets(p_target, q)
    _, target_ood, alerts, ood_threshold = ood_scores(estimator, X_dev, X_cal, X_target)
    cal_ood, _, _, _ = ood_scores(estimator, X_dev, X_cal, X_cal)
    domain_y = np.r_[np.zeros(len(cal_ood), dtype=int), np.ones(len(target_ood), dtype=int)]
    domain_scores = np.r_[cal_ood, target_ood]
    metrics = evaluate_predictions(y_target.to_numpy(dtype=int), p_target)
    source_train_metrics = evaluate_predictions(
        y_dev.to_numpy(dtype=int), estimator.predict_proba(X_dev)[:, 1]
    )
    intervals = stratified_bootstrap_intervals(y_target.to_numpy(dtype=int), p_target, seed)
    accepted = ~alerts
    accepted_metrics: dict[str, Any] = {}
    if accepted.any() and np.unique(y_target.to_numpy()[accepted]).size == 2:
        accepted_metrics = evaluate_predictions(
            y_target.to_numpy(dtype=int)[accepted], p_target[accepted]
        )
    row = {
        "source_dataset": source_id,
        "target_dataset": target_id,
        "model": variant,
        "model_label": MODEL_LABELS[variant],
        "split_seed": seed,
        "source_train_rows": int(len(dev_indices)),
        "source_calibration_rows": int(len(calibration_indices)),
        "target_rows": int(len(y_target)),
        "inner_validation_roc_auc": float(search.best_score_),
        "source_train_roc_auc_resubstitution": source_train_metrics["roc_auc"],
        "source_train_minus_target_roc_auc": float(
            source_train_metrics["roc_auc"] - metrics["roc_auc"]
        ),
        "best_params": json.dumps(json_value(search.best_params_), sort_keys=True),
        "source_only_conformal_threshold": q,
        "target_conformal_coverage": conformal_summary(y_target.to_numpy(), sets)[
            "empirical_coverage"
        ],
        "target_conformal_average_set_size": conformal_summary(y_target.to_numpy(), sets)[
            "average_set_size"
        ],
        "ood_q95_source_calibration_threshold": ood_threshold,
        "target_ood_alert_rate": float(alerts.mean()),
        "target_accepted_coverage": float(accepted.mean()),
        "target_ood_detection_roc_auc": float(roc_auc_score(domain_y, domain_scores)),
        "runtime_seconds": float(time.perf_counter() - started),
        **{f"target_{key}": value for key, value in intervals.items()},
        **{f"target_{key}": value for key, value in metrics.items()},
    }
    if accepted_metrics:
        row.update({f"target_accepted_{key}": value for key, value in accepted_metrics.items()})
    else:
        row.update(
            {
                "target_accepted_roc_auc": None,
                "target_accepted_pr_auc": None,
                "target_accepted_brier": None,
            }
        )
    predictions = [
        {
            "source_dataset": source_id,
            "target_dataset": target_id,
            "model": variant,
            "row_index": int(index),
            "y_true": int(y_target.iloc[index]),
            "probability_positive": float(p_target[index]),
            "predicted_label_at_0_5": int(p_target[index] >= 0.5),
            "confidence": float(max(p_target[index], 1 - p_target[index])),
            "conformal_set": ";".join(str(item) for item in sets[index]),
            "conformal_set_size": len(sets[index]),
            "conformal_covered": int(int(y_target.iloc[index]) in sets[index]),
            "ood_score": float(target_ood[index]),
            "ood_alert": int(alerts[index]),
            "accepted_by_ood": int(not alerts[index]),
        }
        for index in range(len(y_target))
    ]
    return row, predictions, assignments


def run_learning_curves(
    dataset_id: str, X: pd.DataFrame, y: pd.Series
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    min_class = int(y.value_counts().min())
    folds = min(3, min_class)
    if folds < 2:
        return rows, [
            {
                "dataset": dataset_id,
                "model": "all",
                "stage": "learning_curve",
                "error_type": "InsufficientClassCount",
                "reason": "At least two examples per class are required.",
            }
        ]
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=SEED)
    for variant in MODEL_VARIANTS:
        try:
            pipeline = build_corrected_pipeline(X, variant=variant, seed=SEED)
            sizes, train_scores, validation_scores = learning_curve(
                pipeline,
                X,
                y,
                train_sizes=np.asarray([0.35, 0.55, 0.75, 1.0]),
                cv=cv,
                scoring="roc_auc",
                n_jobs=1,
                shuffle=True,
                random_state=SEED,
                error_score="raise",
            )
            for size_index, size in enumerate(sizes):
                rows.append(
                    {
                        "dataset": dataset_id,
                        "model": variant,
                        "train_rows": int(size),
                        "train_roc_auc_mean": float(np.mean(train_scores[size_index, :])),
                        "train_roc_auc_sd": float(np.std(train_scores[size_index, :], ddof=1)),
                        "validation_roc_auc_mean": float(np.mean(validation_scores[size_index, :])),
                        "validation_roc_auc_sd": float(
                            np.std(validation_scores[size_index, :], ddof=1)
                        ),
                        "cv_folds": folds,
                        "fit_scope": "descriptive learning-curve CV; not used for selection",
                    }
                )
        except Exception as exc:  # Keep every unsupported curve in the audit trail.
            failures.append(
                {
                    "dataset": dataset_id,
                    "model": variant,
                    "stage": "learning_curve",
                    "error_type": type(exc).__name__,
                    "reason": str(exc).splitlines()[0][:500],
                }
            )
            logging.exception("Learning curve failed: %s / %s", dataset_id, variant)
    return rows, failures


def build_model_summary(
    fold_frame: pd.DataFrame,
    predictions_frame: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (dataset_id, variant), group in fold_frame.groupby(["dataset", "model"], sort=True):
        pred = predictions_frame.loc[
            (predictions_frame["dataset"] == dataset_id) & (predictions_frame["model"] == variant)
        ].sort_values("row_index")
        y = pred["y_true"].to_numpy(dtype=int)
        probability = pred["probability_positive"].to_numpy(dtype=float)
        pooled = evaluate_predictions(y, probability)
        means = {key: float(group[key].mean()) for key in METRIC_KEYS}
        sds = {
            f"{key}_fold_sd": float(group[key].std(ddof=1)) if len(group) > 1 else None
            for key in METRIC_KEYS
        }
        ci = stratified_bootstrap_intervals(y, probability, SEED + len(rows))
        official_split = set(group["fold"].astype(str)) == {"official_test"}
        rows.append(
            {
                "dataset": dataset_id,
                "task_family": DATASET_SPECS.get(dataset_id, {}).get(
                    "task_family", "SPECTF binary diagnosis"
                ),
                "model": variant,
                "model_label": MODEL_LABELS[variant],
                "split_protocol": "official 80/187 source split"
                if official_split
                else "3x3 nested stratified CV",
                "n_evaluated": int(pooled["n"]),
                "positive_count": int(pooled["positive_count"]),
                "prevalence": float(pooled["prevalence"]),
                **{f"fold_mean_{key}": value for key, value in means.items()},
                **sds,
                **{f"pooled_{key}": pooled[key] for key in METRIC_KEYS},
                **ci,
                "train_roc_auc_resubstitution_mean": float(
                    group["train_roc_auc_resubstitution"].mean()
                ),
                "inner_validation_roc_auc_mean": float(
                    group["inner_validation_roc_auc_best"].mean()
                ),
                "train_minus_outer_test_roc_auc_mean": float(
                    group["train_minus_outer_test_roc_auc"].mean()
                ),
                "inner_validation_minus_outer_test_roc_auc_mean": float(
                    group["inner_validation_minus_outer_test_roc_auc"].mean()
                ),
                "conformal_coverage_mean": float(group["conformal_empirical_coverage"].mean()),
                "conformal_set_size_mean": float(group["conformal_average_set_size"].mean()),
                "conformal_singleton_rate_mean": float(group["conformal_singleton_rate"].mean()),
                "ood_alert_rate_mean": float(group["ood_test_alert_rate"].mean()),
                "ood_accepted_coverage_mean": float(group["ood_test_accepted_coverage"].mean()),
                "best_params_by_fold": ";".join(group["best_params"].astype(str)),
                "runtime_seconds_total": float(group["runtime_seconds"].sum()),
            }
        )
    return pd.DataFrame(rows)


def build_selective_and_calibration(
    predictions_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selective_rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    for (dataset, model), group in predictions_frame.groupby(["dataset", "model"], sort=True):
        y = group["y_true"].to_numpy(dtype=int)
        p = group["probability_positive"].to_numpy(dtype=float)
        confidence = np.maximum(p, 1 - p)
        order = np.argsort(-confidence, kind="stable")
        risks: list[float] = []
        coverages: list[float] = []
        for fraction in np.linspace(0.1, 1.0, 10):
            count = max(1, int(np.ceil(fraction * len(y))))
            selected = order[:count]
            risk = float(np.mean((p[selected] >= 0.5).astype(int) != y[selected]))
            coverage = float(count / len(y))
            risks.append(risk)
            coverages.append(coverage)
            selective_rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    "nominal_coverage": float(fraction),
                    "achieved_coverage": coverage,
                    "risk_error_rate": risk,
                    "accepted_n": count,
                }
            )
        selective_rows.append(
            {
                "dataset": dataset,
                "model": model,
                "nominal_coverage": None,
                "achieved_coverage": 1.0,
                "risk_error_rate": float(np.mean((p >= 0.5).astype(int) != y)),
                "accepted_n": int(len(y)),
                "aurc_trapezoid": float(auc(coverages, risks)),
                "risk_at_80pct_coverage": float(risks[7]),
            }
        )
        edges = np.linspace(0, 1, CALIBRATION_BINS + 1)
        bin_index = np.minimum(np.searchsorted(edges[1:-1], p, side="right"), CALIBRATION_BINS - 1)
        for index in range(CALIBRATION_BINS):
            selected = bin_index == index
            if selected.any():
                calibration_rows.append(
                    {
                        "dataset": dataset,
                        "model": model,
                        "bin_lower": float(edges[index]),
                        "bin_upper": float(edges[index + 1]),
                        "count": int(selected.sum()),
                        "mean_predicted_probability": float(p[selected].mean()),
                        "observed_positive_fraction": float(y[selected].mean()),
                    }
                )
    return pd.DataFrame(selective_rows), pd.DataFrame(calibration_rows)


def main() -> None:
    if not DATASET_MANIFEST_PATH.is_file():
        raise FileNotFoundError("Run experiments/prepare_multi_dataset_evaluation.py first")
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    for dirname in (
        "experiments",
        "metrics",
        "predictions",
        "figures",
        "logs",
        "manifests",
        "reports",
    ):
        (RESULTS / dirname).mkdir(parents=True, exist_ok=True)
    prediction_dir = RESULTS / "predictions" / run_id
    prediction_dir.mkdir(parents=True, exist_ok=True)
    attempt_dir = RESULTS / "experiments" / run_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    log_path = RESULTS / "logs" / f"run_{run_id}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    if any(not spec["path"].is_file() for spec in DATASET_SPECS.values()):
        missing = [
            str(spec["path"]) for spec in DATASET_SPECS.values() if not spec["path"].is_file()
        ]
        raise FileNotFoundError(f"Prepared evaluation inputs are missing: {missing}")

    manifest = json.loads(DATASET_MANIFEST_PATH.read_text(encoding="utf-8"))
    git_head_at_start = (
        __import__("subprocess")
        .check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True)
        .strip()
    )
    tasks = {dataset_id: load_task(dataset_id) for dataset_id in DATASET_SPECS}
    fold_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    conformal_rows: list[dict[str, Any]] = []
    learning_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    dataset_protocols: dict[str, Any] = {}

    for dataset_id, (X, y, spec) in tasks.items():
        logging.info("START dataset=%s n=%s p=%s", dataset_id, len(y), X.shape[1])
        dataset_protocols[dataset_id] = {
            "task_family": spec["task_family"],
            "protocol": spec["protocol"],
            "source_previously_examined": dataset_id != "uci_spectf_heart",
        }
        if dataset_id == "uci_switzerland" and y.value_counts().min() < 10:
            logging.warning(
                "Switzerland has only %s negative cases; metrics will be unstable",
                y.value_counts().min(),
            )
        assignments.extend(build_nested_assignments(dataset_id, X, y))
        for variant in MODEL_VARIANTS:
            logging.info("RUN nested dataset=%s model=%s", dataset_id, variant)
            try:
                rows, preds, conf = run_nested_model(dataset_id, X, y, variant)
                fold_rows.extend(rows)
                prediction_rows.extend(preds)
                conformal_rows.extend(conf)
                save_json(
                    attempt_dir / "nested" / f"{dataset_id}_{variant}.json",
                    {"fold_metrics": rows, "predictions": preds, "conformal": conf},
                )
                logging.info(
                    "PASS nested dataset=%s model=%s outer_roc_auc=%.4f",
                    dataset_id,
                    variant,
                    float(np.mean([row["roc_auc"] for row in rows])),
                )
            except Exception as exc:
                failure_rows.append(
                    {
                        "dataset": dataset_id,
                        "model": variant,
                        "stage": "nested_internal_evaluation",
                        "error_type": type(exc).__name__,
                        "reason": str(exc).splitlines()[0][:500],
                    }
                )
                logging.exception("FAILED nested dataset=%s model=%s", dataset_id, variant)
        learning, learning_failures = run_learning_curves(dataset_id, X, y)
        learning_rows.extend(learning)
        failure_rows.extend(learning_failures)
        save_json(
            attempt_dir / "learning_curves" / f"{dataset_id}.json",
            {"metrics": learning, "failures": learning_failures},
        )

    logging.info("RUN official SPECTF split")
    try:
        spectf_folds, spectf_preds, spectf_conf, spectf_assignments = run_spectf_official_split(
            prediction_dir
        )
        fold_rows.extend(spectf_folds)
        prediction_rows.extend(spectf_preds)
        conformal_rows.extend(spectf_conf)
        assignments.extend(spectf_assignments)
        spectf_train = pd.read_csv(PROCESSED / "uci_spectf_train.csv")
        spectf_y_train = spectf_train.pop("OVERALL_DIAGNOSIS").astype(int)
        spectf_train.attrs["categorical_columns"] = []
        learning, learning_failures = run_learning_curves(
            "uci_spectf_heart", spectf_train, spectf_y_train
        )
        learning_rows.extend(learning)
        failure_rows.extend(learning_failures)
        save_json(
            attempt_dir / "spectf_official_split.json",
            {
                "fold_metrics": spectf_folds,
                "predictions": spectf_preds,
                "conformal": spectf_conf,
                "fold_assignments": spectf_assignments,
            },
        )
        dataset_protocols["uci_spectf_heart"] = {
            "task_family": "SPECT imaging normal/abnormal",
            "protocol": "official 80-row development / 187-row held-out test split",
            "source_previously_examined": False,
            "exception_reason": (
                "Official source split retained; nested outer CV would disregard it."
            ),
        }
        logging.info("PASS official SPECTF split")
    except Exception as exc:
        failure_rows.append(
            {
                "dataset": "uci_spectf_heart",
                "model": "all",
                "stage": "official_split_evaluation",
                "error_type": type(exc).__name__,
                "reason": str(exc).splitlines()[0][:500],
            }
        )
        logging.exception("FAILED official SPECTF split")

    cross_rows: list[dict[str, Any]] = []
    cross_prediction_rows: list[dict[str, Any]] = []
    cross_assignment_rows: list[dict[str, Any]] = []
    for source_id in UCI_CAD_DATASETS:
        for target_id in UCI_CAD_DATASETS:
            if source_id == target_id:
                continue
            logging.info("RUN transfer source=%s target=%s", source_id, target_id)
            for variant in MODEL_VARIANTS:
                try:
                    row, preds, split_assignments = run_cross_pair(
                        source_id,
                        target_id,
                        tasks[source_id],
                        tasks[target_id],
                        variant,
                    )
                    cross_rows.append(row)
                    cross_prediction_rows.extend(preds)
                    cross_assignment_rows.extend(split_assignments)
                    save_json(
                        attempt_dir
                        / "cross_dataset"
                        / f"{source_id}__to__{target_id}__{variant}.json",
                        {"metrics": row, "predictions": preds, "assignments": split_assignments},
                    )
                    logging.info(
                        "PASS transfer %s -> %s model=%s auc=%.4f",
                        source_id,
                        target_id,
                        variant,
                        row["target_roc_auc"],
                    )
                except Exception as exc:
                    failure_rows.append(
                        {
                            "dataset": f"{source_id}->{target_id}",
                            "model": variant,
                            "stage": "source_only_cross_dataset_transfer",
                            "error_type": type(exc).__name__,
                            "reason": str(exc).splitlines()[0][:500],
                        }
                    )
                    logging.exception(
                        "FAILED transfer source=%s target=%s model=%s",
                        source_id,
                        target_id,
                        variant,
                    )

    fold_frame = pd.DataFrame(fold_rows)
    prediction_frame = pd.DataFrame(prediction_rows)
    if fold_frame.empty or prediction_frame.empty:
        raise RuntimeError("No model evaluation completed; inspect the execution log")
    if not prediction_frame.empty:
        prediction_frame.to_csv(
            prediction_dir / "out_of_fold_and_official_predictions.csv", index=False
        )
    pd.DataFrame(cross_prediction_rows).to_csv(
        prediction_dir / "cross_dataset_predictions.csv", index=False
    )
    pd.DataFrame(assignments).drop_duplicates().to_csv(
        prediction_dir / "fold_assignments.csv", index=False
    )
    pd.DataFrame(cross_assignment_rows).to_csv(
        prediction_dir / "cross_dataset_split_assignments.csv", index=False
    )
    fold_frame.to_csv(RESULTS / "metrics" / "fold_metrics.csv", index=False)
    model_summary = build_model_summary(fold_frame, prediction_frame)
    model_summary.to_csv(RESULTS / "metrics" / "model_metrics.csv", index=False)
    cross_frame = pd.DataFrame(cross_rows)
    cross_frame.to_csv(RESULTS / "metrics" / "cross_dataset_metrics.csv", index=False)
    pd.DataFrame(conformal_rows).to_csv(RESULTS / "metrics" / "conformal_metrics.csv", index=False)
    learning_frame = pd.DataFrame(learning_rows)
    learning_frame.to_csv(RESULTS / "metrics" / "learning_curve_metrics.csv", index=False)
    selective_frame, calibration_frame = build_selective_and_calibration(prediction_frame)
    selective_frame.to_csv(RESULTS / "metrics" / "selective_prediction_metrics.csv", index=False)
    calibration_frame.to_csv(RESULTS / "metrics" / "calibration_bins.csv", index=False)
    failures_frame = pd.DataFrame(failure_rows)
    failures_frame.to_csv(RESULTS / "metrics" / "failed_experiments.csv", index=False)

    overfit_columns = [
        "dataset",
        "model",
        "fold",
        "train_roc_auc_resubstitution",
        "inner_validation_roc_auc_best",
        "roc_auc",
        "train_minus_outer_test_roc_auc",
        "inner_validation_minus_outer_test_roc_auc",
        "runtime_seconds",
        "best_params",
    ]
    fold_frame[overfit_columns].to_csv(
        RESULTS / "metrics" / "overfitting_analysis.csv", index=False
    )
    manifest_output = {
        "experiment_id": "CARDIODIAG-MULTI-DATASET-20261108",
        "run_id": run_id,
        "status": "completed_with_failures" if failure_rows else "completed",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git": {
            "branch": "codex/multi-dataset-evaluation-2026-11-08",
            "head_at_run_start": git_head_at_start,
            "experiment_code_sha256": {
                path: sha256_file(ROOT / path)
                for path in (
                    "src/cardiodiag/models.py",
                    "src/cardiodiag/experiments.py",
                    "experiments/prepare_multi_dataset_evaluation.py",
                    "experiments/run_multi_dataset_evaluation.py",
                )
            },
        },
        "datasets": {
            key: {
                **value,
                "source_file": str(DATASET_SPECS[key]["path"].relative_to(ROOT))
                if key in DATASET_SPECS
                else "official UCI SPECTF split files",
                "prepared_sha256": sha256_file(DATASET_SPECS[key]["path"])
                if key in DATASET_SPECS
                else {
                    "train": sha256_file(PROCESSED / "uci_spectf_train.csv"),
                    "test": sha256_file(PROCESSED / "uci_spectf_test.csv"),
                },
                "data_manifest_entry": manifest["datasets"][key],
            }
            for key, value in dataset_protocols.items()
        },
        "models": {
            variant: {
                "display_name": MODEL_LABELS[variant],
                "baseline_grid": GRID_BY_MODEL[variant],
                "base_configuration": "src/cardiodiag/models.py and build_corrected_pipeline",
                "selection_score": "ROC-AUC in source/outer-training folds only",
            }
            for variant in MODEL_VARIANTS
        },
        "protocol": {
            "within_dataset_outer_folds": OUTER_FOLDS,
            "within_dataset_inner_folds": INNER_FOLDS,
            "seed": SEED,
            "conformal_alpha": CONFORMAL_ALPHA,
            "conformal_calibration_fraction_within_outer_training": CALIBRATION_FRACTION,
            "ood_calibration_quantile": OOD_QUANTILE,
            "preprocessing": (
                "TrainingOnlyCleaner 1st/99th percentile median replacement, training-only median "
                "numeric imputation and scaling, training-only most-frequent "
                "categorical imputation "
                "and one-hot encoding. All steps remain inside the candidate pipeline."
            ),
            "cross_dataset": (
                "All 12 ordered transfers among four compatible UCI source cohorts; source-only "
                "stratified inner CV, source calibration subset, target cohort "
                "untouched until scoring."
            ),
            "statistical": (
                "Fold means/SDs plus 1,000-replicate class-stratified percentile "
                "bootstrap intervals over pooled out-of-fold/official predictions; "
                "intervals are descriptive and do not "
                "treat CV folds as independent populations."
            ),
            "release": "Row-level prediction files remain local and are gitignored.",
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "scipy": scipy.__version__,
        },
        "artifacts": {
            "log": str(log_path.relative_to(ROOT)),
            "checkpoint_dir": str(attempt_dir.relative_to(ROOT)),
            "predictions": str(
                (prediction_dir / "out_of_fold_and_official_predictions.csv").relative_to(ROOT)
            ),
            "cross_predictions": str(
                (prediction_dir / "cross_dataset_predictions.csv").relative_to(ROOT)
            ),
            "fold_assignments": str((prediction_dir / "fold_assignments.csv").relative_to(ROOT)),
            "cross_split_assignments": str(
                (prediction_dir / "cross_dataset_split_assignments.csv").relative_to(ROOT)
            ),
            "model_metrics": "results/multi_dataset_evaluation_20261108/metrics/model_metrics.csv",
            "fold_metrics": "results/multi_dataset_evaluation_20261108/metrics/fold_metrics.csv",
            "cross_dataset_metrics": (
                "results/multi_dataset_evaluation_20261108/metrics/cross_dataset_metrics.csv"
            ),
            "failed_experiments": (
                "results/multi_dataset_evaluation_20261108/metrics/failed_experiments.csv"
            ),
        },
        "counts": {
            "successful_model_results": int(len(model_summary)),
            "failed_experiments": int(len(failures_frame)),
            "cross_dataset_results": int(len(cross_frame)),
            "learning_curve_points": int(len(learning_frame)),
        },
    }
    save_json(RESULTS / "manifests" / "experiment_manifest.json", manifest_output)
    logging.info(
        "COMPLETE model_rows=%s cross_rows=%s failures=%s",
        len(model_summary),
        len(cross_frame),
        len(failures_frame),
    )
    print(f"Experiment outputs: {RESULTS}")
    print(f"Run log: {log_path}")


if __name__ == "__main__":
    with threadpool_limits(limits=1):
        main()
