"""Plot fold-level performance for the separate new UCI clinical tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "results" / "new_datasets_20261107"
DATASETS = [
    ("uci_heart_failure_519", "Heart failure\ndeath by follow-up"),
    ("uci_mi_complications_579", "Post-MI\nany lethal outcome"),
]
MODELS = [
    ("corrected_logistic", "Logistic regression"),
    ("corrected_ovec", "OVEC"),
    ("corrected_osec", "OSEC"),
]


def read_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def plot_metric(results_dir: Path, metric: str, ylabel: str, output_stem: str) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), constrained_layout=True)
    palette = ["#1f5a94", "#dd8b35", "#4a8d68"]
    for axis, (dataset_id, title) in zip(axes, DATASETS, strict=True):
        result = read_result(results_dir / f"{dataset_id}_nested_metrics.json")
        means = []
        stds = []
        labels = []
        for model_name, label in MODELS:
            model = result["candidates"][model_name]
            means.append(model["fold_mean"][metric])
            stds.append(model["fold_std"][metric])
            labels.append(label)
        x = np.arange(len(labels))
        axis.bar(
            x,
            means,
            yerr=stds,
            capsize=4,
            color=palette,
            edgecolor="white",
            linewidth=0.8,
            error_kw={"elinewidth": 1.3, "ecolor": "#333333"},
        )
        axis.set_xticks(x, labels, rotation=18, ha="right")
        axis.set_ylim(0.0, 1.05)
        axis.set_ylabel(ylabel)
        axis.set_title(title, fontsize=11, weight="bold")
        axis.grid(axis="y", alpha=0.22, linewidth=0.7)
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)
        for position, value in enumerate(means):
            axis.text(position, min(value + 0.04, 1.01), f"{value:.2f}", ha="center", fontsize=9)

    figure.suptitle(
        f"Exploratory nested CV: {ylabel}\n"
        "Different outcomes; performance is not directly comparable",
        fontsize=12,
        weight="bold",
    )
    figure.text(
        0.5,
        -0.025,
        "Bars show the mean across five outer folds; whiskers show fold SD "
        "(not a confidence interval).",
        ha="center",
        fontsize=8.5,
        color="#444444",
    )
    for extension, dpi in (("pdf", None), ("png", 220)):
        path = results_dir / "figures" / f"{output_stem}.{extension}"
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    results_dir = args.results_dir.resolve()
    plot_metric(results_dir, "roc_auc", "ROC-AUC", "new_dataset_roc_auc")
    plot_metric(results_dir, "pr_auc", "Average precision", "new_dataset_average_precision")
    print(f"Wrote two-panel plots under {results_dir / 'figures'}")


if __name__ == "__main__":
    main()
