"""Render the primary leave-one-source-out transfer results figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "transfer_20261105_lodo_final"
MANIFEST = RESULTS / "run_manifest.json"
OUTPUT = RESULTS / "transfer_summary.png"
DISPLAY_NAMES = {
    "cleveland": "Cleveland",
    "hungary": "Hungary",
    "switzerland": "Switzerland",
    "va_long_beach": "VA Long Beach",
}


def ci_errors(fold: dict, metric: str, source: str = "platt") -> np.ndarray:
    interval = fold["predictor_bootstrap_95_ci"][source][metric]
    value = (
        fold["raw_predictor_metrics"][metric]
        if source == "raw"
        else fold["platt_calibrated_metrics"][metric]
    )
    return np.array([[value - interval["lower_95"]], [interval["upper_95"] - value]])


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    folds = manifest["runs"]["impossible_zeros_as_missing"]["folds"]
    labels = [DISPLAY_NAMES[fold["target_cohort"]] for fold in folds]
    positions = np.arange(len(folds))
    figure, axes = plt.subplots(2, 2, figsize=(12.5, 8.2), constrained_layout=True)
    figure.suptitle("Leave-one-source-out transfer: four UCI heart-disease cohorts", fontsize=15)

    ax = axes[0, 0]
    auc_values = [fold["platt_calibrated_metrics"]["roc_auc"] for fold in folds]
    auc_errors = np.array(
        [
            [
                value - fold["predictor_bootstrap_95_ci"]["platt"]["roc_auc"]["lower_95"],
                fold["predictor_bootstrap_95_ci"]["platt"]["roc_auc"]["upper_95"] - value,
            ]
            for fold, value in zip(folds, auc_values, strict=True)
        ]
    ).T
    ax.errorbar(positions, auc_values, yerr=auc_errors, fmt="o", capsize=4, color="#2B6F9C")
    ax.axhline(0.5, color="#777777", linestyle="--", linewidth=1)
    ax.set_xticks(positions, labels)
    ax.set_ylim(0.42, 1.02)
    ax.set_ylabel("ROC-AUC (class-stratified bootstrap 95% CI)")
    ax.set_title("Predictive discrimination")

    ax = axes[0, 1]
    for offset, source, label, color in (
        (-0.11, "raw", "Raw logistic", "#557A95"),
        (0.11, "platt", "Source-calibrated", "#D17A38"),
    ):
        values = [
            fold["raw_predictor_metrics"]["brier_score"]
            if source == "raw"
            else fold["platt_calibrated_metrics"]["brier_score"]
            for fold in folds
        ]
        errors = np.array(
            [ci_errors(fold, "brier_score", source=source).ravel() for fold in folds]
        ).T
        ax.errorbar(
            positions + offset, values, yerr=errors, fmt="o", capsize=3, label=label, color=color
        )
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 0.34)
    ax.set_ylabel("Brier score (lower is better)")
    ax.set_title("Probability accuracy")
    ax.legend(frameon=False)

    ax = axes[1, 0]
    ood_values = [fold["ood"]["source_vs_target_ood_auroc"] for fold in folds]
    ood_errors = np.array(
        [
            [
                value - fold["ood"]["source_vs_target_ood_auroc_bootstrap_95_ci"]["lower_95"],
                fold["ood"]["source_vs_target_ood_auroc_bootstrap_95_ci"]["upper_95"] - value,
            ]
            for fold, value in zip(folds, ood_values, strict=True)
        ]
    ).T
    ax.errorbar(positions, ood_values, yerr=ood_errors, fmt="o", capsize=4, color="#7355A3")
    ax.axhline(0.5, color="#777777", linestyle="--", linewidth=1)
    ax.set_xticks(positions, labels)
    ax.set_ylim(0.42, 1.02)
    ax.set_ylabel("OOD-score AUROC (bootstrap 95% CI)")
    ax.set_title("Held-out-site detection from predictors")

    ax = axes[1, 1]
    flagged = np.array([fold["ood"]["target_alert_rate"] for fold in folds])
    accepted = np.array([fold["ood"]["target_coverage"] for fold in folds])
    ax.bar(positions, flagged, label="Flagged", color="#C86B57")
    ax.bar(positions, accepted, bottom=flagged, label="Accepted", color="#6FA68A")
    for index, (flag_rate, coverage) in enumerate(zip(flagged, accepted, strict=True)):
        ax.text(index, 1.025, f"flagged {flag_rate:.0%}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(positions, labels)
    ax.set_ylim(0, 1.16)
    ax.set_ylabel("Share of target cohort")
    ax.set_title(
        "Selective coverage at source-calibrated 5% alert rate\n"
        "(orange = flagged; green = accepted)"
    )

    figure.savefig(OUTPUT, dpi=180, bbox_inches="tight")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
