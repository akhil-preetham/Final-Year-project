"""Run the requested resource-aware 2x2 nested validation on the 70K task.

This runner deliberately writes a new artifact and reuses the model definitions
and preprocessing pipeline from ``run_tuned_ensemble.py``.  It does not use
oversampling, fits all transformations inside each outer training fold, tunes
only inside the inner folds, and stores fold-level labels, probabilities, and
metrics for every fitted model and the prespecified ensemble.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np
from run_tuned_ensemble import _models, _pipeline
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.provenance import collect_provenance

PRIMARY_MODELS = ("logistic", "random_forest", "xgboost", "catboost")
ENSEMBLE_COMPONENTS = ("xgboost", "hist_gradient_boosting", "logistic")


class _MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total", ctypes.c_ulonglong),
        ("available", ctypes.c_ulonglong),
        ("page_total", ctypes.c_ulonglong),
        ("page_available", ctypes.c_ulonglong),
        ("virtual_total", ctypes.c_ulonglong),
        ("virtual_available", ctypes.c_ulonglong),
        ("extended_available", ctypes.c_ulonglong),
    ]


def _memory_gib() -> dict[str, float | int | None]:
    """Return portable-enough Windows memory information without psutil."""

    status = _MemoryStatus()
    status.length = ctypes.sizeof(_MemoryStatus)
    try:
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    except AttributeError:
        return {"total_gib": None, "available_gib": None, "logical_cpus": os.cpu_count()}
    return {
        "total_gib": round(status.total / 2**30, 2),
        "available_gib": round(status.available / 2**30, 2),
        "logical_cpus": os.cpu_count(),
    }


def estimate_resources(dataset: Path) -> dict[str, Any]:
    """Estimate runtime from the existing measured 3-fold tuned artifact."""

    reference = Path("results/generated/kaggle70k_tuned_priority_oof_ensemble.json")
    reference_seconds: dict[str, float] = {}
    if reference.exists():
        payload = json.loads(reference.read_text(encoding="utf-8"))
        reference_seconds = {
            name: float(payload["models"][name]["total_seconds"])
            for name in (*PRIMARY_MODELS, "hist_gradient_boosting")
            if name in payload.get("models", {})
        }
    projected_seconds = sum(reference_seconds.values()) * (2 / 3)
    return {
        "hardware_before_execution": _memory_gib(),
        "dataset_csv_bytes": dataset.stat().st_size,
        "dataset_rows": 70000,
        "reference_artifact": str(reference).replace("\\", "/"),
        "reference_three_outer_fold_seconds": reference_seconds,
        "projection_for_two_outer_folds_seconds": round(projected_seconds, 1),
        "expected_runtime_range_seconds": [
            round(projected_seconds * 0.75, 1),
            round(projected_seconds * 1.75, 1),
        ],
        "memory_policy": (
            "single-process execution; estimator and GridSearchCV n_jobs/thread counts "
            "are fixed to 1; no oversampling or prediction-time all-pairs method"
        ),
        "feasibility_assessment": (
            "Expected to fit within the observed available memory; runtime is bounded "
            "by the existing measured random-forest configuration."
        ),
    }


def _fit_model(
    X: Any,
    y: Any,
    train: np.ndarray,
    test: np.ndarray,
    name: str,
    models: dict[str, tuple[Any, dict[str, list[Any]]]],
    inner_splits: int,
    seed: int,
) -> tuple[dict[str, Any], np.ndarray]:
    model, grid = models[name]
    estimator = _pipeline(X.iloc[train], clone(model))
    search = GridSearchCV(
        estimator,
        grid,
        scoring="roc_auc",
        cv=inner_splits,
        n_jobs=1,
        refit=True,
        error_score="raise",
    )
    started = time.perf_counter()
    search.fit(X.iloc[train], y.iloc[train])
    probabilities = search.predict_proba(X.iloc[test])[:, 1]
    metrics = evaluate_predictions(y.iloc[test].to_numpy(), probabilities)
    return (
        {
            "fold": None,
            "train_n": int(len(train)),
            "test_n": int(len(test)),
            "best_params": search.best_params_,
            "inner_best_score": float(search.best_score_),
            "fit_seconds": time.perf_counter() - started,
            "metrics": metrics,
            "test_indices": test.astype(int).tolist(),
            "y_true": y.iloc[test].astype(int).tolist(),
            "predicted_probability": probabilities.astype(float).tolist(),
        },
        probabilities,
    )


def run(dataset: Path, target: str, output: Path, seed: int = 42) -> dict[str, Any]:
    started = time.perf_counter()
    resource_estimate = estimate_resources(dataset)
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    outer = StratifiedKFold(n_splits=2, shuffle=True, random_state=seed)
    splits = list(outer.split(X, y))
    models = _models(seed)
    requested = (*PRIMARY_MODELS, "hist_gradient_boosting")
    missing = [name for name in requested if name not in models]
    if missing:
        raise RuntimeError(f"Required models are unavailable: {missing}")

    records: dict[str, dict[str, Any]] = {
        name: {"status": "completed", "folds": []} for name in requested
    }
    outer_predictions: dict[str, np.ndarray] = {}
    failures: dict[str, str] = {}
    for name in requested:
        predictions = np.full(len(y), np.nan)
        for fold, (train, test) in enumerate(splits):
            try:
                fold_record, probabilities = _fit_model(
                    X, y, train, test, name, models, inner_splits=2, seed=seed
                )
            except Exception as error:  # pragma: no cover - retained in artifact on failure
                records[name]["status"] = "failed"
                failures[name] = f"{type(error).__name__}: {error}"
                break
            fold_record["fold"] = fold
            records[name]["folds"].append(fold_record)
            predictions[test] = probabilities
        if records[name]["status"] == "completed":
            records[name]["pooled_outer_metrics"] = evaluate_predictions(
                y.to_numpy(), predictions
            )
            records[name]["mean_metrics"] = {
                key: float(np.mean([fold["metrics"][key] for fold in records[name]["folds"]]))
                for key in (
                    "roc_auc",
                    "pr_auc",
                    "accuracy",
                    "balanced_accuracy",
                    "recall",
                    "specificity",
                    "brier",
                    "ece_uniform",
                )
            }
            outer_predictions[name] = predictions

    ensemble_members = [
        name for name in ENSEMBLE_COMPONENTS if name in outer_predictions
    ]
    ensemble: dict[str, Any]
    if len(ensemble_members) == len(ENSEMBLE_COMPONENTS):
        ensemble_predictions = np.mean(
            [outer_predictions[name] for name in ensemble_members], axis=0
        )
        ensemble_folds = []
        for fold, (_, test) in enumerate(splits):
            fold_probabilities = ensemble_predictions[test]
            fold_metrics = evaluate_predictions(y.iloc[test].to_numpy(), fold_probabilities)
            ensemble_folds.append(
                {
                    "fold": fold,
                    "train_n": int(len(y) - len(test)),
                    "test_n": int(len(test)),
                    "metrics": fold_metrics,
                    "test_indices": test.astype(int).tolist(),
                    "y_true": y.iloc[test].astype(int).tolist(),
                    "predicted_probability": fold_probabilities.astype(float).tolist(),
                }
            )
        ensemble = {
            "status": "completed",
            "members": ensemble_members,
            "weights": [1.0 / len(ensemble_members)] * len(ensemble_members),
            "folds": ensemble_folds,
            "pooled_outer_metrics": evaluate_predictions(y.to_numpy(), ensemble_predictions),
            "mean_metrics": {
                key: float(np.mean([fold["metrics"][key] for fold in ensemble_folds]))
                for key in (
                    "roc_auc",
                    "pr_auc",
                    "accuracy",
                    "balanced_accuracy",
                    "recall",
                    "specificity",
                    "brier",
                    "ece_uniform",
                )
            },
        }
    else:
        ensemble = {
            "status": "failed",
            "members": ensemble_members,
            "required_members": list(ENSEMBLE_COMPONENTS),
            "reason": "One or more ensemble components failed.",
        }
        failures["existing_justified_ensemble"] = ensemble["reason"]

    configuration = {
        "stage": "live_70k_nested_2x2",
        "outer_splits": 2,
        "inner_splits": 2,
        "seed": seed,
        "scoring": "roc_auc",
        "primary_models": list(PRIMARY_MODELS),
        "supporting_ensemble_component": "hist_gradient_boosting",
        "ensemble_members": list(ENSEMBLE_COMPONENTS),
        "ensemble_weights": [1.0 / len(ENSEMBLE_COMPONENTS)] * len(ENSEMBLE_COMPONENTS),
        "oversampling": "none",
        "outer_test_isolation": True,
        "prediction_storage": "fold-level y_true, test_indices, and predicted_probability",
    }
    result = {
        "status": "completed" if not failures else "completed_with_failures",
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "configuration": configuration,
        "resource_estimate": resource_estimate,
        "execution": {
            "runtime_seconds": time.perf_counter() - started,
            "hardware_after_execution": _memory_gib(),
            "completed_outer_folds": 2,
            "failed_models": failures,
        },
        "models": {name: records[name] for name in PRIMARY_MODELS},
        "supporting_components": {"hist_gradient_boosting": records["hist_gradient_boosting"]},
        "ensemble": ensemble,
        "provenance": collect_provenance(
            dataset, target, "live_70k_nested_2x2", configuration
        ),
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
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--estimate-only", action="store_true")
    args = parser.parse_args()
    if args.estimate_only:
        print(json.dumps(estimate_resources(args.dataset), indent=2))
        return
    result = run(args.dataset, args.target, args.output, args.seed)
    print(
        f"Wrote {result['status']} 70K nested artifact to {args.output}; "
        f"runtime={result['execution']['runtime_seconds']:.1f}s"
    )
    if result["status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
