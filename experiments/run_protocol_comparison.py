"""Compare native historical and corrected/proposed protocols."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from cardiodiag.experiments import run_single_experiment
from cardiodiag.historical import run_historical_native


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("heart5.csv"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    frame = pd.read_csv(args.dataset)
    historical = {
        model: run_historical_native(frame, model_name=model, seed=42)
        for model in ["ovec", "osec"]
    }
    corrected = {
        "logistic": run_single_experiment(
            args.dataset, "HeartDisease", "logistic", seed=42, use_stable_selector=False
        ),
        "ovec": run_single_experiment(
            args.dataset, "HeartDisease", "ovec", seed=42, use_stable_selector=False
        ),
        "osec": run_single_experiment(
            args.dataset, "HeartDisease", "osec", seed=42, use_stable_selector=False
        ),
        "logistic_stable_xaih_drc": run_single_experiment(
            args.dataset, "HeartDisease", "logistic", seed=42, use_stable_selector=True
        ),
        "osec_stable_xaih_drc": run_single_experiment(
            args.dataset, "HeartDisease", "osec", seed=42, use_stable_selector=True
        ),
    }
    result = {
        "dataset": str(args.dataset),
        "historical_native": historical,
        "corrected_common_split": corrected,
        "interpretation": [
            (
                "Historical and corrected metrics use different native protocols and are "
                "not directly comparable as a leaderboard."
            ),
            (
                "The corrected comparison uses training-only transformations and a common "
                "75/25 stratified split."
            ),
            "No external-validation claim is made by this report.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote protocol comparison to {args.output}")


if __name__ == "__main__":
    main()
