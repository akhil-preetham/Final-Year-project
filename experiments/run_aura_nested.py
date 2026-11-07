"""Leakage-controlled nested evaluation for the AURA-ML research prototype."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from run_tuned_ensemble import _models, _pipeline
from sklearn.base import clone
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from cardiodiag.aura import AURAClassifier, AURAConfig
from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import bootstrap_metric_ci, evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.nested_validation import candidate_grid

METRIC_KEYS = (
    "accuracy",
    "balanced_accuracy",
    "precision",
    "recall",
    "specificity",
    "f1",
    "roc_auc",
    "pr_auc",
    "brier",
    "ece_uniform",
)


def _fit_existing_baseline(
    X: Any,
    y: Any,
    train: np.ndarray,
    test: np.ndarray,
    target: str,
    inner_splits: int,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Fit the strongest already-identified baseline without outer leakage."""

    started = time.perf_counter()
    X_train, X_test = X.iloc[train], X.iloc[test]
    y_train, y_test = y.iloc[train], y.iloc[test]
    if target == "cardio":
        models = _models(seed)
        model, grid = models["catboost"]
        estimator = _pipeline(X_train, clone(model))
    else:
        estimator = build_corrected_pipeline(
            X_train, variant="ovec", seed=seed, use_stable_selector=False
        )
        grid = candidate_grid("ovec", False)
    search = GridSearchCV(
        estimator,
        grid,
        scoring="roc_auc",
        cv=inner_splits,
        n_jobs=1,
        refit=True,
        error_score="raise",
    )
    search.fit(X_train, y_train)
    prediction_started = time.perf_counter()
    probabilities = search.predict_proba(X_test)[:, 1]
    return probabilities, {
        "model": "catboost" if target == "cardio" else "corrected_ovec",
        "best_params": search.best_params_,
        "inner_best_score": float(search.best_score_),
        "fit_seconds": float(prediction_started - started),
        "inference_seconds": float(time.perf_counter() - prediction_started),
        "metrics": evaluate_predictions(y_test.to_numpy(), probabilities),
    }


def _summary(folds: list[dict[str, Any]], y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    return {
        "pooled_outer_metrics": evaluate_predictions(y, p),
        "fold_mean": {
            key: float(np.mean([fold["metrics"][key] for fold in folds]))
            for key in METRIC_KEYS
        },
        "fold_std": {
            key: float(np.std([fold["metrics"][key] for fold in folds], ddof=1))
            if len(folds) > 1
            else 0.0
            for key in METRIC_KEYS
        },
        "bootstrap_ci": {
            key: {
                "point": bootstrap_metric_ci(
                    y,
                    p,
                    _metric_function(key),
                    n_bootstrap=300,
                    random_state=42,
                )[0],
                "low": bootstrap_metric_ci(
                    y,
                    p,
                    _metric_function(key),
                    n_bootstrap=300,
                    random_state=42,
                )[1],
                "high": bootstrap_metric_ci(
                    y,
                    p,
                    _metric_function(key),
                    n_bootstrap=300,
                    random_state=42,
                )[2],
            }
            for key in ("roc_auc", "pr_auc")
        },
    }


def _metric_function(name: str):
    if name == "roc_auc":
        return roc_auc_score
    if name == "pr_auc":
        from sklearn.metrics import average_precision_score

        return average_precision_score
    raise ValueError(f"Unsupported bootstrap metric {name}")


def _paired_auc_bootstrap(
    y: np.ndarray,
    aura: np.ndarray,
    baseline: np.ndarray,
    n_bootstrap: int = 500,
    seed: int = 42,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(n_bootstrap):
        indices = rng.integers(0, len(y), size=len(y))
        sampled_y = y[indices]
        if np.unique(sampled_y).size < 2:
            continue
        values.append(
            float(
                roc_auc_score(sampled_y, aura[indices])
                - roc_auc_score(sampled_y, baseline[indices])
            )
        )
    low, high = np.quantile(values, [0.025, 0.975])
    return {
        "point": float(roc_auc_score(y, aura) - roc_auc_score(y, baseline)),
        "low": float(low),
        "high": float(high),
    }


def run(
    dataset: Path,
    target: str,
    output: Path,
    outer_splits: int = 2,
    inner_splits: int = 2,
    seed: int = 42,
    config: AURAConfig | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    y_array = y.to_numpy(dtype=int)
    outer = StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed)
    aura_config = config or AURAConfig(inner_splits=inner_splits, seed=seed)
    aura_folds: list[dict[str, Any]] = []
    baseline_folds: list[dict[str, Any]] = []
    aura_predictions = np.full(len(y), np.nan)
    baseline_predictions = np.full(len(y), np.nan)
    for fold, (train, test) in enumerate(outer.split(X, y)):
        aura_started = time.perf_counter()
        estimator = AURAClassifier(aura_config)
        estimator.fit(X.iloc[train], y.iloc[train])
        prediction_started = time.perf_counter()
        aura_probability = estimator.predict_proba(X.iloc[test])[:, 1]
        aura_predictions[test] = aura_probability
        aura_folds.append(
            {
                "fold": fold,
                "train_n": int(len(train)),
                "test_n": int(len(test)),
                "test_indices": test.astype(int).tolist(),
                "y_true": y.iloc[test].astype(int).tolist(),
                "predicted_probability": aura_probability.astype(float).tolist(),
                "metrics": evaluate_predictions(y.iloc[test].to_numpy(), aura_probability),
                "fit_seconds": float(prediction_started - aura_started),
                "inference_seconds": float(time.perf_counter() - prediction_started),
                "fit_summary": estimator.fit_summary_,
            }
        )
        baseline_probability, baseline_record = _fit_existing_baseline(
            X, y, train, test, target, inner_splits, seed + fold
        )
        baseline_predictions[test] = baseline_probability
        baseline_folds.append(
            {
                "fold": fold,
                "train_n": int(len(train)),
                "test_n": int(len(test)),
                "test_indices": test.astype(int).tolist(),
                "y_true": y.iloc[test].astype(int).tolist(),
                "predicted_probability": baseline_probability.astype(float).tolist(),
                **baseline_record,
            }
        )
    aura_summary = _summary(aura_folds, y_array, aura_predictions)
    baseline_summary = _summary(baseline_folds, y_array, baseline_predictions)
    result = {
        "status": "completed",
        "method": "AURA-ML research prototype",
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "configuration": {
            "outer_splits": outer_splits,
            "inner_splits": inner_splits,
            "seed": seed,
            "selection_metric": "inner reliability objective with ROC-AUC primary component",
            "aura_config": aura_config.__dict__,
            "outer_test_isolation": True,
            "oversampling": "none",
        },
        "aura_ml": {"folds": aura_folds, **aura_summary},
        "existing_baseline": {"folds": baseline_folds, **baseline_summary},
        "paired_comparison": {
            "roc_auc_delta_aura_minus_baseline": _paired_auc_bootstrap(
                y_array, aura_predictions, baseline_predictions
            ),
            "interpretation": (
                "paired bootstrap over outer-test predictions; "
                "not an independent-patient CI"
            ),
        },
        "execution": {"runtime_seconds": float(time.perf_counter() - started)},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary.replace(output)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-splits", type=int, default=2)
    parser.add_argument("--inner-splits", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run(
        args.dataset,
        args.target,
        args.output,
        args.outer_splits,
        args.inner_splits,
        args.seed,
    )
    print(
        f"Wrote AURA-ML nested artifact to {args.output}; "
        f"runtime={result['execution']['runtime_seconds']:.1f}s"
    )


if __name__ == "__main__":
    main()
