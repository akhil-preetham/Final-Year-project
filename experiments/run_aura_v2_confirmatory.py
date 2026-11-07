"""Run separate AURA-ML V2 confirmatory nested validation artifacts.

V2 is intentionally simpler than V1: feature selection is disabled because its
ablations did not show a consistent benefit, while representation choice,
inner-only model selection, reliability-gated fusion, calibration comparison,
and training-side threshold selection remain active.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from run_tuned_ensemble import _models, _pipeline
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold

from cardiodiag.aura import AURAClassifier, AURAConfig
from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.nested_validation import candidate_grid
from cardiodiag.reliability import calibration_summary

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


def aura_v2_config(seed: int, inner_splits: int) -> AURAConfig:
    """Return the frozen V2 policy selected before confirmatory execution."""

    return AURAConfig(
        inner_splits=inner_splits,
        seed=seed,
        use_intelligence=True,
        use_multiview=True,
        use_feature_selection=False,
        use_fusion=True,
        use_reliability=True,
        use_calibration=True,
        calibration_methods=("sigmoid", "isotonic"),
        calibration_min_brier_improvement=1e-4,
        threshold_mode="validation_balanced_accuracy",
    )


def _baseline_specs(target: str) -> list[str]:
    generic = ["logistic", "random_forest", "hist_gradient_boosting", "xgboost", "catboost"]
    if target == "cardio":
        return generic
    return ["corrected_ovec", "corrected_osec", *generic]


def _fit_baseline(
    name: str,
    X: Any,
    y: Any,
    train: np.ndarray,
    test: np.ndarray,
    target: str,
    inner_splits: int,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    X_train, X_test = X.iloc[train], X.iloc[test]
    y_train, y_test = y.iloc[train], y.iloc[test]
    started = time.perf_counter()
    if name in {"corrected_ovec", "corrected_osec"}:
        variant = name.removeprefix("corrected_")
        estimator = build_corrected_pipeline(X_train, variant=variant, seed=seed)
        grid = candidate_grid(variant, False)
    else:
        models = _models(seed)
        if name not in models:
            raise RuntimeError(f"Baseline {name} is unavailable in this environment")
        model, grid = models[name]
        estimator = _pipeline(X_train, clone(model))
    search = GridSearchCV(
        estimator,
        grid,
        scoring="roc_auc",
        cv=inner_splits,
        n_jobs=1,
        refit=True,
        error_score="raise",
        return_train_score=False,
    )
    search.fit(X_train, y_train)
    prediction_started = time.perf_counter()
    probabilities = search.predict_proba(X_test)[:, 1]
    return probabilities, {
        "name": name,
        "best_params": search.best_params_,
        "inner_best_score": float(search.best_score_),
        "fit_seconds": float(prediction_started - started),
        "inference_seconds": float(time.perf_counter() - prediction_started),
        "metrics": evaluate_predictions(y_test.to_numpy(), probabilities),
    }


def _section_summary(
    folds: list[dict[str, Any]], rows: int, predictions: np.ndarray
) -> dict[str, Any]:
    y_true = np.concatenate([np.asarray(fold["y_true"], dtype=int) for fold in folds])
    probabilities = np.concatenate(
        [np.asarray(fold["predicted_probability"], dtype=float) for fold in folds]
    )
    fold_metrics = [fold["metrics"] for fold in folds]
    return {
        "pooled_outer_metrics": evaluate_predictions(y_true, probabilities),
        "fold_mean": {
            key: float(np.mean([metrics[key] for metrics in fold_metrics]))
            for key in METRIC_KEYS
        },
        "fold_std": {
            key: float(np.std([metrics[key] for metrics in fold_metrics], ddof=1))
            if len(fold_metrics) > 1
            else 0.0
            for key in METRIC_KEYS
        },
        "prediction_partition": bool(
            len(predictions) == rows
            and np.isfinite(predictions).all()
        ),
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
        aura_metrics = evaluate_predictions(sampled_y, aura[indices])
        baseline_metrics = evaluate_predictions(sampled_y, baseline[indices])
        values.append(aura_metrics["roc_auc"] - baseline_metrics["roc_auc"])
    low, high = np.quantile(values, [0.025, 0.975])
    point = evaluate_predictions(y, aura)["roc_auc"] - evaluate_predictions(y, baseline)["roc_auc"]
    return {"point": float(point), "low": float(low), "high": float(high)}


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
    y_array = y.to_numpy(dtype=int)
    outer = list(
        StratifiedKFold(n_splits=outer_splits, shuffle=True, random_state=seed).split(X, y)
    )
    config = aura_v2_config(seed, inner_splits)
    aura_folds: list[dict[str, Any]] = []
    aura_predictions = np.full(len(y), np.nan)
    for fold, (train, test) in enumerate(outer):
        fit_started = time.perf_counter()
        estimator = AURAClassifier(config).fit(X.iloc[train], y.iloc[train])
        prediction_started = time.perf_counter()
        probabilities = estimator.predict_proba(X.iloc[test])[:, 1]
        aura_predictions[test] = probabilities
        default_metrics = evaluate_predictions(
            y.iloc[test].to_numpy(), probabilities, threshold=0.5
        )
        optimized_metrics = evaluate_predictions(
            y.iloc[test].to_numpy(), probabilities, threshold=estimator.decision_threshold_
        )
        calibration = calibration_summary(y.iloc[test].to_numpy(), probabilities)
        aura_folds.append(
            {
                "fold": fold,
                "train_n": int(len(train)),
                "test_n": int(len(test)),
                "test_indices": test.astype(int).tolist(),
                "y_true": y.iloc[test].astype(int).tolist(),
                "predicted_probability": probabilities.astype(float).tolist(),
                "metrics": default_metrics,
                "default_threshold_metrics": default_metrics,
                "optimized_threshold": float(estimator.decision_threshold_),
                "optimized_threshold_metrics": optimized_metrics,
                "calibration_summary": calibration,
                "fit_seconds": float(prediction_started - fit_started),
                "inference_seconds": float(time.perf_counter() - prediction_started),
                "fit_summary": estimator.fit_summary_,
            }
        )

    baseline_names = _baseline_specs(target)
    baseline_folds: dict[str, list[dict[str, Any]]] = {name: [] for name in baseline_names}
    baseline_predictions: dict[str, np.ndarray] = {
        name: np.full(len(y), np.nan) for name in baseline_names
    }
    for fold, (train, test) in enumerate(outer):
        for name in baseline_names:
            probabilities, record = _fit_baseline(
                name, X, y, train, test, target, inner_splits, seed + fold
            )
            baseline_predictions[name][test] = probabilities
            baseline_folds[name].append(
                {
                    "fold": fold,
                    "train_n": int(len(train)),
                    "test_n": int(len(test)),
                    "test_indices": test.astype(int).tolist(),
                    "y_true": y.iloc[test].astype(int).tolist(),
                    "predicted_probability": probabilities.astype(float).tolist(),
                    **record,
                }
            )

    baseline_sections = {
        name: {
            "folds": baseline_folds[name],
            **_section_summary(baseline_folds[name], len(y), baseline_predictions[name]),
        }
        for name in baseline_names
    }
    if target == "cardio":
        ensemble_members = [
            name
            for name in ("xgboost", "hist_gradient_boosting", "logistic")
            if name in baseline_predictions
        ]
    else:
        ensemble_members = ["corrected_ovec", "corrected_osec"]
    ensemble_predictions = np.mean(
        [baseline_predictions[name] for name in ensemble_members], axis=0
    )
    ensemble_folds = []
    for fold, (_, test) in enumerate(outer):
        probabilities = ensemble_predictions[test]
        ensemble_folds.append(
            {
                "fold": fold,
                "train_n": int(len(y) - len(test)),
                "test_n": int(len(test)),
                "test_indices": test.astype(int).tolist(),
                "y_true": y.iloc[test].astype(int).tolist(),
                "predicted_probability": probabilities.astype(float).tolist(),
                "metrics": evaluate_predictions(y.iloc[test].to_numpy(), probabilities),
                "members": ensemble_members,
            }
        )
    baseline_sections["existing_ensemble"] = {
        "members": ensemble_members,
        "folds": ensemble_folds,
        **_section_summary(ensemble_folds, len(y), ensemble_predictions),
    }
    primary_baseline = "catboost" if target == "cardio" else "corrected_ovec"
    result = {
        "status": "completed",
        "method": "AURA-ML V2 evidence-gated adaptive policy",
        "dataset": str(dataset),
        "target": target,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "dropped_identifier_columns": dropped,
        "configuration": {
            "outer_splits": outer_splits,
            "inner_splits": inner_splits,
            "seed": seed,
            "protocol_class": (
                "confirmatory_v2_single_seed"
                if outer_splits >= 3 and inner_splits >= 3
                else "exploratory"
            ),
            "primary_baseline": primary_baseline,
            "aura_config": config.__dict__,
            "threshold_selection": (
                "inner-training OOF balanced accuracy grid; default 0.5 also reported"
            ),
            "calibration_selection": (
                "inner-training cross-fitted Brier then ECE; sigmoid/isotonic/none"
            ),
            "outer_test_isolation": True,
            "oversampling": "none",
        },
        "aura_ml": {
            "folds": aura_folds,
            **_section_summary(aura_folds, len(y), aura_predictions),
            "default_threshold_pooled_metrics": evaluate_predictions(
                y_array, aura_predictions, threshold=0.5
            ),
            "optimized_threshold_pooled_metrics": evaluate_predictions(
                y_array,
                aura_predictions,
                threshold=float(np.mean([fold["optimized_threshold"] for fold in aura_folds])),
            ),
            "outer_calibration_summary": calibration_summary(y_array, aura_predictions),
        },
        "baselines": baseline_sections,
        "primary_paired_comparison": {
            "baseline": primary_baseline,
            "roc_auc_delta_aura_minus_baseline": _paired_bootstrap_delta(
                y_array, aura_predictions, baseline_predictions[primary_baseline]
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
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=3)
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
        f"Wrote AURA V2 confirmatory artifact to {args.output}; "
        f"runtime={result['execution']['runtime_seconds']:.1f}s"
    )


if __name__ == "__main__":
    main()
