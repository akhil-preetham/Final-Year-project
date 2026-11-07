"""Plot saved CD-XD-003 external-cohort predictions and OOD scores."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "transfer_20261105_zas_external"
MANIFEST = RESULTS / "run_manifest.json"
TARGET_PREDICTIONS = RESULTS / "external_predictions.csv"
SOURCE_PREDICTIONS = RESULTS / "source_calibration_predictions.csv"
OUTPUT = RESULTS / "external_transfer_summary.png"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = pd.read_csv(TARGET_PREDICTIONS)
    source = pd.read_csv(SOURCE_PREDICTIONS)
    y = target["y_binary"].to_numpy(dtype=int)
    raw = target["raw_probability"].to_numpy(dtype=float)
    calibrated = target["platt_probability"].to_numpy(dtype=float)

    figure, axes = plt.subplots(1, 3, figsize=(15.2, 4.7), constrained_layout=True)
    figure.suptitle(
        "Source-only transfer to the Z-Alizadeh Sani cohort (n=303)\n"
        "Endpoint boundary differs: source >50%; target ≥50%",
        fontsize=14,
    )

    ax = axes[0]
    for probabilities, label, color in (
        (raw, "Raw", "#4778A8"),
        (calibrated, "Source Platt", "#D47C36"),
    ):
        fpr, tpr, _ = roc_curve(y, probabilities)
        auc = manifest["raw_predictor_metrics" if label == "Raw" else "platt_calibrated_metrics"][
            "roc_auc"
        ]
        ax.plot(fpr, tpr, label=f"{label} (AUC {auc:.3f})", color=color, linewidth=2)
    ax.plot([0, 1], [0, 1], "--", color="#777777", linewidth=1)
    ax.set(xlabel="False-positive rate", ylabel="True-positive rate", title="Discrimination")
    ax.legend(frameon=False, loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)

    ax = axes[1]
    for probabilities, label, color in (
        (raw, "Raw", "#4778A8"),
        (calibrated, "Source Platt", "#D47C36"),
    ):
        observed, predicted = calibration_curve(y, probabilities, n_bins=6, strategy="quantile")
        ax.plot(predicted, observed, marker="o", label=label, color=color, linewidth=1.8)
    ax.plot([0, 1], [0, 1], "--", color="#777777", linewidth=1, label="Ideal")
    ax.set(
        xlabel="Mean predicted probability",
        ylabel="Observed positive fraction",
        title="Target calibration",
    )
    ax.legend(frameon=False, loc="upper left")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax = axes[2]
    source_scores = source["ood_anomaly_score"].to_numpy(dtype=float)
    target_scores = target["ood_anomaly_score"].to_numpy(dtype=float)
    threshold = float(manifest["ood"]["threshold_source_calibration_weighted_q95"])
    bins = np.histogram_bin_edges(np.concatenate([source_scores, target_scores]), bins=18)
    ax.hist(
        source_scores,
        bins=bins,
        density=True,
        alpha=0.58,
        color="#4778A8",
        label="Source calibration",
    )
    ax.hist(
        target_scores, bins=bins, density=True, alpha=0.55, color="#C96B58", label="External target"
    )
    ax.axvline(
        threshold, color="#333333", linestyle="--", linewidth=1.5, label="Source 95th percentile"
    )
    alert_rate = manifest["ood"]["target_alert_rate"]
    ood_auc = manifest["ood"]["source_vs_target_ood_auroc"]
    ax.set(
        xlabel="Isolation Forest anomaly score",
        ylabel="Density",
        title=f"OOD warning (AUROC {ood_auc:.3f}; flagged {alert_rate:.1%})",
    )
    ax.legend(frameon=False, fontsize=8)

    figure.savefig(OUTPUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
