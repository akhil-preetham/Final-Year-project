"""Calculate paired post-run calibration deltas for CD-XD-004 predictions."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import run_lodo_transfer as shared
from sklearn.metrics import brier_score_loss, log_loss

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "transfer_20261105_angiocad_external"
PREDICTIONS = RESULTS / "external_predictions.csv"
OUTPUT = RESULTS / "paired_calibration_differences.json"
BOOTSTRAP_REPLICATES = 1000
SEED = 20264105


def main() -> None:
    frame = pd.read_csv(PREDICTIONS)
    y = frame["y_binary"].to_numpy(dtype=int)
    raw = frame["raw_probability"].to_numpy(dtype=float)
    calibrated = frame["platt_probability"].to_numpy(dtype=float)
    by_class = [np.flatnonzero(y == label) for label in (0, 1)]
    if any(len(indices) < 2 for indices in by_class):
        raise ValueError("Paired class-stratified bootstrap requires both target classes")

    metrics = {
        "brier_score": brier_score_loss,
        "log_loss": lambda truth, probability: log_loss(truth, probability, labels=[0, 1]),
        "ece_10_bins": lambda truth, probability: shared.expected_calibration_error(
            truth, probability
        ),
    }
    rng = np.random.default_rng(SEED)
    results: dict[str, object] = {
        "analysis_type": "post_run_descriptive_paired_class_stratified_bootstrap",
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "seed": SEED,
        "difference_definition": (
            "Platt-calibrated metric minus raw-probability metric; "
            "negative favors calibrated probabilities"
        ),
        "used_for_model_or_threshold_selection": False,
        "metrics": {},
    }
    for name, metric in metrics.items():
        point = float(metric(y, calibrated) - metric(y, raw))
        samples = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
        for replicate in range(BOOTSTRAP_REPLICATES):
            indices = np.concatenate(
                [rng.choice(group, size=len(group), replace=True) for group in by_class]
            )
            samples[replicate] = metric(y[indices], calibrated[indices]) - metric(
                y[indices], raw[indices]
            )
        results["metrics"][name] = {
            "point_difference": point,
            "paired_bootstrap_95_ci": [
                float(np.quantile(samples, 0.025)),
                float(np.quantile(samples, 0.975)),
            ],
            "bootstrap_fraction_with_lower_calibrated_metric": float(np.mean(samples < 0)),
        }

    OUTPUT.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Wrote paired descriptive deltas to {OUTPUT}")


if __name__ == "__main__":
    main()
