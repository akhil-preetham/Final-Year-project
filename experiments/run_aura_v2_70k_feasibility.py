"""Resource-bounded 3x3 AURA V2 evaluation on the 70K benchmark.

This is deliberately not presented as the failed full V2 confirmatory grid.
AURA performs its complete inner 3-fold candidate selection. Comparison models
are frozen, single-threaded estimators from the existing bounded model factory
and are evaluated on the same outer folds; their hyperparameters are not
reselected in this run. The distinction is recorded in the artifact.

The runner checkpoints after each outer fold so an interruption leaves a valid
partial artifact rather than silently losing completed work.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from run_aura_v2_confirmatory import aura_v2_config
from run_tuned_ensemble import _models, _pipeline
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold

from cardiodiag.aura import AURAClassifier
from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions

BASELINE_NAMES = ("logistic", "random_forest", "hist_gradient_boosting", "xgboost", "catboost")


def estimate_resources(dataset: Path) -> dict[str, Any]:
    reference = Path("results/generated/live_70k_nested_2x2.json")
    reference_runtime = None
    if reference.exists():
        reference_runtime = json.loads(reference.read_text(encoding="utf-8"))["execution"][
            "runtime_seconds"
        ]
    return {
        "dataset_bytes": dataset.stat().st_size,
        "rows": 70000,
        "reference_v1_2x2_seconds": reference_runtime,
        "protocol": (
            "3 outer x 3 inner for AURA; fixed baseline fits on identical "
            "3-fold outer splits"
        ),
        "thread_policy": "single process; n_jobs/thread_count=1",
        "oversampling": "none",
        "expected_runtime_seconds": [900, 1800],
        "memory_policy": "one estimator at a time; fold predictions only; atomic checkpoints",
    }


def _fold_record(
    fold: int,
    train: np.ndarray,
    test: np.ndarray,
    y: Any,
    probabilities: np.ndarray,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "fold": fold,
        "train_n": int(len(train)),
        "test_n": int(len(test)),
        "test_indices": test.astype(int).tolist(),
        "y_true": y.iloc[test].astype(int).tolist(),
        "predicted_probability": probabilities.astype(float).tolist(),
        "metrics": evaluate_predictions(y.iloc[test].to_numpy(), probabilities),
        **extra,
    }


def _section(folds: list[dict[str, Any]], rows: int) -> dict[str, Any]:
    y_true = np.concatenate([np.asarray(fold["y_true"], dtype=int) for fold in folds])
    probabilities = np.concatenate(
        [np.asarray(fold["predicted_probability"], dtype=float) for fold in folds]
    )
    metrics = [fold["metrics"] for fold in folds]
    return {
        "status": "completed",
        "folds": folds,
        "pooled_outer_metrics": evaluate_predictions(y_true, probabilities),
        "fold_mean": {
            key: float(np.mean([metric[key] for metric in metrics]))
            for key in (
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
        },
        "fold_std": {
            "roc_auc": float(np.std([metric["roc_auc"] for metric in metrics], ddof=1))
            if len(metrics) > 1
            else 0.0
        },
        "prediction_count": int(len(probabilities)),
        "prediction_partition": len(probabilities) == rows,
    }


def _paired_bootstrap_delta(
    y: np.ndarray,
    aura: np.ndarray,
    baseline: np.ndarray,
    seed: int = 42,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(1000):
        indices = rng.integers(0, len(y), size=len(y))
        sampled_y = y[indices]
        if np.unique(sampled_y).size < 2:
            continue
        aura_auc = evaluate_predictions(sampled_y, aura[indices])["roc_auc"]
        baseline_auc = evaluate_predictions(sampled_y, baseline[indices])["roc_auc"]
        values.append(aura_auc - baseline_auc)
    low, high = np.quantile(values, [0.025, 0.975])
    point = evaluate_predictions(y, aura)["roc_auc"] - evaluate_predictions(y, baseline)["roc_auc"]
    return {"point": float(point), "low": float(low), "high": float(high)}


def _write_checkpoint(output: Path, result: dict[str, Any]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2), encoding="utf-8")
    temporary.replace(output)


def run(
    dataset: Path,
    target: str,
    output: Path,
    outer_splits: int = 3,
    inner_splits: int = 3,
    seed: int = 42,
) -> dict[str, Any]:
    started = time.perf_counter()
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    outer = list(
        StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed).split(X, y)
    )
    models = _models(seed)
    missing = [name for name in BASELINE_NAMES if name not in models]
    if missing:
        raise RuntimeError(f"Required baseline estimators unavailable: {missing}")
    aura_folds: list[dict[str, Any]] = []
    baseline_folds: dict[str, list[dict[str, Any]]] = {name: [] for name in BASELINE_NAMES}
    aura_predictions = np.full(len(y), np.nan)
    baseline_predictions = {
        name: np.full(len(y), np.nan) for name in BASELINE_NAMES
    }
    completed_folds: list[int] = []
    partial_result: dict[str, Any] = {
        "status": "running",
        "method": "AURA-ML V2 70K resource-bounded feasibility run",
        "dataset": str(dataset),
        "target": target,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "dropped_identifier_columns": dropped,
        "configuration": {
            "outer_splits": outer_splits,
            "inner_splits": inner_splits,
            "seed": seed,
            "protocol_class": "resource_bounded_3x3_fixed_baselines",
            "aura_policy": aura_v2_config(seed, inner_splits).__dict__,
            "baseline_names": list(BASELINE_NAMES),
            "baseline_hyperparameters": "frozen model-factory defaults; no baseline inner retuning",
            "identical_outer_folds": True,
            "outer_test_isolation": True,
            "oversampling": "none",
        },
        "resource_estimate": estimate_resources(dataset),
        "completed_outer_folds": completed_folds,
        "aura_ml": {"status": "incomplete", "folds": aura_folds},
        "baselines": {
            name: {"status": "incomplete", "folds": folds}
            for name, folds in baseline_folds.items()
        },
        "execution": {"started_seconds": started},
    }
    _write_checkpoint(output, partial_result)

    for fold, (train, test) in enumerate(outer):
        fold_started = time.perf_counter()
        estimator = AURAClassifier(aura_v2_config(seed, inner_splits))
        estimator.fit(X.iloc[train], y.iloc[train])
        prediction_started = time.perf_counter()
        aura_probability = estimator.predict_proba(X.iloc[test])[:, 1]
        aura_predictions[test] = aura_probability
        aura_folds.append(
            _fold_record(
                fold,
                train,
                test,
                y,
                aura_probability,
                fit_seconds=float(prediction_started - fold_started),
                inference_seconds=float(time.perf_counter() - prediction_started),
                fit_summary=estimator.fit_summary_,
            )
        )
        for name in BASELINE_NAMES:
            model_started = time.perf_counter()
            model, _ = models[name]
            estimator = _pipeline(X.iloc[train], clone(model))
            estimator.fit(X.iloc[train], y.iloc[train])
            prediction_started = time.perf_counter()
            probabilities = estimator.predict_proba(X.iloc[test])[:, 1]
            baseline_predictions[name][test] = probabilities
            baseline_folds[name].append(
                _fold_record(
                    fold,
                    train,
                    test,
                    y,
                    probabilities,
                    fit_seconds=float(prediction_started - model_started),
                    inference_seconds=float(time.perf_counter() - prediction_started),
                    hyperparameters="frozen model-factory estimator",
                )
            )
        completed_folds.append(fold)
        partial_result["completed_outer_folds"] = completed_folds
        partial_result["aura_ml"] = {"status": "partial", "folds": aura_folds}
        partial_result["baselines"] = {
            name: {"status": "partial", "folds": folds}
            for name, folds in baseline_folds.items()
        }
        partial_result["execution"]["last_checkpoint_seconds"] = time.perf_counter() - started
        _write_checkpoint(output, partial_result)

    ensemble_names = ("xgboost", "hist_gradient_boosting", "logistic")
    ensemble_predictions = np.mean(
        [baseline_predictions[name] for name in ensemble_names], axis=0
    )
    ensemble_folds = [
        _fold_record(
            fold,
            train,
            test,
            y,
            ensemble_predictions[test],
            members=list(ensemble_names),
        )
        for fold, (train, test) in enumerate(outer)
    ]
    result = {
        **partial_result,
        "status": "completed",
        "aura_ml": _section(aura_folds, len(y)),
        "baselines": {
            name: _section(folds, len(y)) for name, folds in baseline_folds.items()
        },
        "existing_ensemble": {
            "members": list(ensemble_names),
            **_section(ensemble_folds, len(y)),
        },
        "paired_comparisons": {
            "versus_catboost": _paired_bootstrap_delta(
                y.to_numpy(dtype=int), aura_predictions, baseline_predictions["catboost"]
            ),
            "versus_existing_ensemble": _paired_bootstrap_delta(
                y.to_numpy(dtype=int), aura_predictions, ensemble_predictions
            ),
        },
        "execution": {
            "runtime_seconds": time.perf_counter() - started,
            "completed_outer_folds": completed_folds,
        },
    }
    _write_checkpoint(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--estimate-only", action="store_true")
    args = parser.parse_args()
    if args.estimate_only:
        print(json.dumps(estimate_resources(args.dataset), indent=2))
        return
    result = run(
        args.dataset,
        args.target,
        args.output,
        args.outer_splits,
        args.inner_splits,
        args.seed,
    )
    print(
        f"Wrote {result['status']} AURA V2 70K feasibility artifact to {args.output}; "
        f"runtime={result['execution'].get('runtime_seconds', 0):.1f}s"
    )


if __name__ == "__main__":
    main()
