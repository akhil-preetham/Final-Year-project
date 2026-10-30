"""Nested validation and ablation orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold

from .data import drop_identifier_columns, load_dataset, summarize_dataset
from .evaluation import bootstrap_metric_ci, evaluate_predictions
from .experiments import build_corrected_pipeline


@dataclass(frozen=True)
class NestedConfig:
    dataset: str
    target: str
    outer_splits: int = 3
    outer_repeats: int = 1
    inner_splits: int = 3
    seed: int = 42
    scoring: str = "roc_auc"


def candidate_grid(variant: str, stable_selector: bool) -> dict[str, list[Any]]:
    """Return intentionally small, prespecified inner-search grids."""

    grid: dict[str, list[Any]] = {}
    if variant == "logistic":
        grid["model__C"] = [0.1, 1.0, 10.0]
    elif variant == "ovec":
        grid["model__weights"] = [None]
    elif variant == "osec":
        grid["model__final_estimator__C"] = [0.1, 1.0, 10.0]
    else:
        raise ValueError(f"Unknown candidate variant: {variant}")
    if stable_selector:
        grid["stable_xaih_drc__stability_threshold"] = [0.5, 0.75, 1.0]
    return grid


def default_candidates() -> list[tuple[str, bool, str]]:
    return [
        ("logistic", False, "corrected_logistic"),
        ("ovec", False, "corrected_ovec"),
        ("osec", False, "corrected_osec"),
        ("logistic", True, "stable_logistic"),
        ("osec", True, "stable_osec"),
    ]


def run_nested_validation(
    dataset_path: str | Path,
    target: str,
    candidates: list[tuple[str, bool, str]] | None = None,
    outer_splits: int = 3,
    outer_repeats: int = 1,
    inner_splits: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    """Run an outer evaluation with all model selection inside inner folds."""

    X, y = load_dataset(dataset_path, target)
    X, dropped_identifiers = drop_identifier_columns(X)
    config = NestedConfig(
        dataset=str(dataset_path),
        target=target,
        outer_splits=outer_splits,
        outer_repeats=outer_repeats,
        inner_splits=inner_splits,
        seed=seed,
    )
    candidates = candidates or default_candidates()
    outer_cv = RepeatedStratifiedKFold(
        n_splits=outer_splits,
        n_repeats=outer_repeats,
        random_state=seed,
    )
    candidate_results: dict[str, Any] = {}
    for variant, stable_selector, name in candidates:
        fold_results: list[dict[str, Any]] = []
        pooled_y: list[int] = []
        pooled_p: list[float] = []
        for fold_id, (train_index, test_index) in enumerate(outer_cv.split(X, y)):
            X_train = X.iloc[train_index]
            X_test = X.iloc[test_index]
            y_train = y.iloc[train_index]
            y_test = y.iloc[test_index]
            pipeline = build_corrected_pipeline(
                X_train,
                variant=variant,
                seed=seed + fold_id,
                use_stable_selector=stable_selector,
            )
            search = GridSearchCV(
                estimator=pipeline,
                param_grid=candidate_grid(variant, stable_selector),
                scoring="roc_auc",
                cv=inner_splits,
                refit=True,
                n_jobs=1,
                return_train_score=True,
            )
            search.fit(X_train, y_train)
            probabilities = search.best_estimator_.predict_proba(X_test)[:, 1]
            metrics = evaluate_predictions(y_test.to_numpy(), probabilities)
            fold_results.append(
                {
                    "fold": fold_id,
                    "train_n": int(len(train_index)),
                    "test_n": int(len(test_index)),
                    "best_params": search.best_params_,
                    "inner_best_score": float(search.best_score_),
                    "metrics": metrics,
                }
            )
            pooled_y.extend(y_test.astype(int).tolist())
            pooled_p.extend(probabilities.astype(float).tolist())
        y_array = np.asarray(pooled_y, dtype=int)
        p_array = np.asarray(pooled_p, dtype=float)
        pooled_metrics = evaluate_predictions(y_array, p_array)
        roc_ci = bootstrap_metric_ci(y_array, p_array, roc_auc_score, random_state=seed)
        pr_ci = bootstrap_metric_ci(y_array, p_array, average_precision_score, random_state=seed)
        candidate_results[name] = {
            "variant": variant,
            "stable_selector": stable_selector,
            "folds": fold_results,
            "pooled_outer_metrics": pooled_metrics,
            "bootstrap_ci": {
                "roc_auc": {"point": roc_ci[0], "low": roc_ci[1], "high": roc_ci[2]},
                "pr_auc": {"point": pr_ci[0], "low": pr_ci[1], "high": pr_ci[2]},
            },
            "fold_mean": _mean_metrics(fold_results),
            "fold_std": _std_metrics(fold_results),
        }
    return {
        "config": asdict(config),
        "dataset_summary": summarize_dataset(dataset_path, target).to_dict(),
        "dropped_identifier_columns": dropped_identifiers,
        "candidates": candidate_results,
        "selection_rule": (
            "report all candidates; do not select a final model from the pooled outer "
            "test metrics alone"
        ),
    }


def _mean_metrics(folds: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["accuracy", "balanced_accuracy", "roc_auc", "pr_auc", "brier", "ece_uniform"]
    return {key: float(np.mean([fold["metrics"][key] for fold in folds])) for key in keys}


def _std_metrics(folds: list[dict[str, Any]]) -> dict[str, float]:
    keys = ["accuracy", "balanced_accuracy", "roc_auc", "pr_auc", "brier", "ece_uniform"]
    return {key: float(np.std([fold["metrics"][key] for fold in folds], ddof=1)) for key in keys}
