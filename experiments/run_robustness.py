"""Evaluate fitted candidates under prespecified evaluation-only perturbations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline


def make_evaluation_perturbations(
    X_fit: pd.DataFrame,
    X_eval: pd.DataFrame,
    seed: int,
    missing_rate: float = 0.10,
    noise_fraction_of_sd: float = 0.05,
) -> dict[str, pd.DataFrame]:
    """Create unlabeled perturbations without changing the fitted data."""

    if not 0 <= missing_rate <= 1:
        raise ValueError("missing_rate must be in [0, 1]")
    if noise_fraction_of_sd < 0:
        raise ValueError("noise_fraction_of_sd must be non-negative")
    rng = np.random.default_rng(seed)
    missing = X_eval.copy()
    for column in missing.columns:
        mask = rng.random(len(missing)) < missing_rate
        missing.loc[mask, column] = np.nan

    noisy = X_eval.copy()
    for column in X_fit.select_dtypes(include=[np.number]).columns:
        scale = float(pd.to_numeric(X_fit[column], errors="coerce").std())
        if np.isfinite(scale) and scale > 0:
            noise = rng.normal(0.0, noise_fraction_of_sd * scale, size=len(noisy))
            noisy[column] = pd.to_numeric(noisy[column], errors="coerce") + noise
    return {"clean": X_eval, "missing_10pct": missing, "numeric_noise_5pct_sd": noisy}


def run_dataset(
    dataset: Path,
    target: str,
    seed: int = 42,
    test_size: float = 0.25,
) -> dict[str, Any]:
    """Fit on one development split and perturb evaluation rows only."""

    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    X_fit, X_eval, y_fit, y_eval = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=seed
    )
    perturbations = make_evaluation_perturbations(X_fit, X_eval, seed)
    candidates: dict[str, Any] = {}
    for variant, stable in [("osec", False), ("osec", True)]:
        name = "stable_osec" if stable else "corrected_osec"
        pipeline = build_corrected_pipeline(
            X_fit, variant=variant, seed=seed, use_stable_selector=stable
        )
        pipeline.fit(X_fit, y_fit)
        candidate_results = {}
        for condition, features in perturbations.items():
            probabilities = pipeline.predict_proba(features)[:, 1]
            candidate_results[condition] = evaluate_predictions(
                y_eval.to_numpy(), probabilities
            )
        candidates[name] = candidate_results
    return {
        "dataset": str(dataset),
        "target": target,
        "seed": seed,
        "dropped_identifier_columns": dropped,
        "dataset_summary": summarize_dataset(dataset, target).to_dict(),
        "protocol": {
            "fit_fraction": float(1 - test_size),
            "evaluation_fraction": float(test_size),
            "missing_rate": 0.10,
            "numeric_noise_fraction_of_training_sd": 0.05,
            "labels_used_to_create_perturbations": False,
            "external_validation": False,
            "interpretation": "evaluation-only stress test, not external validation",
        },
        "candidates": candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_dataset(args.dataset, args.target, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote robustness evidence to {args.output}")


if __name__ == "__main__":
    main()
