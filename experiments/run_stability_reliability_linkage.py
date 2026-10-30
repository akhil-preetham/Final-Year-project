"""Test whether feature-selection stability predicts selective reliability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr
from sklearn.model_selection import train_test_split

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.provenance import collect_provenance
from cardiodiag.reliability import (
    bootstrap_mean_ci,
    calibration_summary,
    nogueira_stability,
    uncertainty_evidence,
)
from cardiodiag.uncertainty import SplitConformalClassifier

RELIABILITY_METRICS = [
    "roc_auc",
    "confidence_error_auc",
    "aurc",
    "full_coverage_risk",
    "conformal_coverage",
    "ece_uniform",
]


def _as_float(value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected a numeric value, got {type(value).__name__}")
    return float(value)


def _fit_candidate(
    X_fit: Any,
    y_fit: Any,
    X_cal: Any,
    y_cal: Any,
    X_eval: Any,
    y_eval: Any,
    stable_selector: bool,
    seed: int,
) -> tuple[dict[str, float | int], set[str] | None]:
    pipeline = build_corrected_pipeline(
        X_fit,
        variant="osec",
        seed=seed,
        use_stable_selector=stable_selector,
    )
    conformal = SplitConformalClassifier(pipeline, alpha=0.1)
    conformal.fit(X_fit, y_fit, X_cal, y_cal)
    probabilities = conformal.predict_proba(X_eval)[:, 1]
    labels = y_eval.to_numpy()
    calibration = calibration_summary(labels, probabilities)
    uncertainty = uncertainty_evidence(labels, probabilities)
    curve = uncertainty["selective_risk"]
    if not isinstance(curve, list):
        raise TypeError("uncertainty_evidence selective_risk must be a list")
    metrics: dict[str, float | int] = {
        "roc_auc": _as_float(evaluate_predictions(labels, probabilities)["roc_auc"]),
        "confidence_error_auc": _as_float(uncertainty["confidence_error_auc"]),
        "aurc": _as_float(uncertainty["aurc"]),
        "full_coverage_risk": _as_float(curve[-1]["risk"]),
        "conformal_coverage": _as_float(conformal.summarize(X_eval, labels)["coverage"]),
        "ece_uniform": _as_float(calibration["ece_uniform"]),
    }
    selected_names: set[str] | None = None
    if stable_selector:
        fitted = conformal.estimator_
        selector = fitted.named_steps["stable_xaih_drc"]
        feature_names = fitted.named_steps["preprocessor"].get_feature_names_out()
        selected_names = {
            str(feature_names[index]) for index in selector.get_support(indices=True)
        }
        metrics["selector_internal_nogueira_stability"] = float(
            nogueira_stability(selector.selection_matrix_)
        )
        metrics["selected_feature_count"] = int(selector.get_support().sum())
    return metrics, selected_names


def _selection_matrix(selection_sets: list[set[str]], universe: list[str]) -> np.ndarray:
    positions = {name: index for index, name in enumerate(universe)}
    matrix = np.zeros((len(selection_sets), len(universe)), dtype=float)
    for row, selected in enumerate(selection_sets):
        for name in selected:
            matrix[row, positions[name]] = 1.0
    return matrix


def _summarize_difference(values: list[float]) -> dict[str, Any]:
    mean, low, high = bootstrap_mean_ci(values, random_state=42)
    return {
        "mean": mean,
        "bootstrap_ci": {"low": low, "high": high},
    }


def _rank_correlation(x: list[float], y: list[float]) -> dict[str, float | None]:
    if len(set(x)) < 2 or len(set(y)) < 2:
        return {"spearman_rho": None, "p_value": None}
    result = spearmanr(x, y)
    return {
        "spearman_rho": float(result.statistic),
        "p_value": float(result.pvalue),
    }


def run_dataset(dataset: Path, target: str, seeds: list[int]) -> dict[str, Any]:
    """Run paired reliability and stability measurements on repeated splits."""

    if len(seeds) < 3:
        raise ValueError("At least three seeds are required for linkage analysis")
    X, y = load_dataset(dataset, target)
    X, dropped_identifiers = drop_identifier_columns(X)
    per_seed: list[dict[str, Any]] = []
    stable_sets: list[set[str]] = []

    for seed in seeds:
        X_dev, X_eval, y_dev, y_eval = train_test_split(
            X,
            y,
            test_size=0.25,
            stratify=y,
            random_state=seed,
        )
        X_fit, X_cal, y_fit, y_cal = train_test_split(
            X_dev,
            y_dev,
            test_size=0.25,
            stratify=y_dev,
            random_state=seed,
        )
        corrected, _ = _fit_candidate(
            X_fit, y_fit, X_cal, y_cal, X_eval, y_eval, False, seed
        )
        stable, selected_names = _fit_candidate(
            X_fit, y_fit, X_cal, y_cal, X_eval, y_eval, True, seed
        )
        if selected_names is None:
            raise RuntimeError("Stable candidate did not return selected feature names")
        stable_sets.append(selected_names)
        per_seed.append(
            {
                "seed": seed,
                "corrected_osec": corrected,
                "stable_osec": stable,
                "paired_difference_stable_minus_corrected": {
                    metric: float(stable[metric] - corrected[metric])
                    for metric in RELIABILITY_METRICS
                },
            }
        )

    stable_metrics = [record["stable_osec"] for record in per_seed]
    differences = {
        metric: _summarize_difference(
            [
                float(record["paired_difference_stable_minus_corrected"][metric])
                for record in per_seed
            ]
        )
        for metric in RELIABILITY_METRICS
    }
    stability_values = [
        float(record["stable_osec"]["selector_internal_nogueira_stability"])
        for record in per_seed
    ]
    correlations = {
        metric: _rank_correlation(
            stability_values,
            [float(candidate[metric]) for candidate in stable_metrics],
        )
        for metric in RELIABILITY_METRICS
    }
    universe = sorted(set().union(*stable_sets))
    cross_seed_stability = nogueira_stability(_selection_matrix(stable_sets, universe))
    mean_internal_stability, low_internal_stability, high_internal_stability = (
        bootstrap_mean_ci(stability_values, random_state=42)
    )

    return {
        "dataset": str(dataset),
        "target": target,
        "dropped_identifier_columns": dropped_identifiers,
        "protocol": {
            "seeds": seeds,
            "fit_fraction": 0.5625,
            "calibration_fraction": 0.1875,
            "evaluation_fraction": 0.25,
            "external_labels_used": False,
            "candidate_pair": "corrected_osec versus stable_osec",
            "linkage_question": (
                "does training-only selector stability predict selective reliability "
                "on the same held-out split?"
            ),
        },
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "stability": {
            "mean_internal_nogueira": mean_internal_stability,
            "mean_internal_nogueira_bootstrap_ci": {
                "low": low_internal_stability,
                "high": high_internal_stability,
            },
            "cross_seed_selected_set_nogueira": cross_seed_stability,
            "mean_selected_feature_count": float(
                np.mean([record["stable_osec"]["selected_feature_count"] for record in per_seed])
            ),
            "feature_universe": universe,
        },
        "paired_reliability_differences": differences,
        "stability_reliability_rank_correlations": correlations,
        "per_seed": per_seed,
        "interpretation": (
            "Positive evidence that stability improves reliability would require "
            "repeated paired differences favoring the stable candidate. A weak or "
            "absent rank correlation indicates that feature-set stability and "
            "predictive reliability are distinct empirical properties. Neither "
            "result establishes external validity."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(42, 52)))
    args = parser.parse_args()
    result = run_dataset(args.dataset, args.target, args.seeds)
    result["provenance"] = collect_provenance(
        dataset=args.dataset,
        target=args.target,
        experiment_type="stability_reliability_linkage",
        configuration={
            "seeds": args.seeds,
            "fit_fraction": 0.5625,
            "calibration_fraction": 0.1875,
            "evaluation_fraction": 0.25,
            "candidate_pair": "corrected_osec versus stable_osec",
            "external_labels_used": False,
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote stability-reliability linkage evidence to {args.output}")


if __name__ == "__main__":
    main()
