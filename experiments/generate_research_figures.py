"""Generate publication figures from checked-in CARDIODIAG result artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

ROOT = Path(__file__).resolve().parents[1]
DATASET_FILES = {
    "heart5": "heart5_nested_validation.json",
    "mendeley": "mendeley_nested_validation.json",
}
MODEL_NAMES = {
    "corrected_logistic": "Corrected logistic",
    "corrected_ovec": "Corrected OVEC",
    "corrected_osec": "Corrected OSEC",
    "stable_logistic": "Stable logistic",
    "stable_osec": "Stable OSEC",
}
CURVE_COLORS = {
    "corrected_logistic": "#4C78A8",
    "corrected_ovec": "#F58518",
    "corrected_osec": "#54A24B",
    "stable_logistic": "#B279A2",
    "stable_osec": "#E45756",
}
PRIMARY_MODELS = ("corrected_ovec", "stable_osec")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pooled_predictions(candidate: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    y_true = np.asarray(
        [value for fold in candidate["folds"] for value in fold["outer_test_y_true"]],
        dtype=int,
    )
    probabilities = np.asarray(
        [
            value
            for fold in candidate["folds"]
            for value in fold["outer_test_probability"]
        ],
        dtype=float,
    )
    if y_true.shape != probabilities.shape or not y_true.size:
        raise ValueError("Nested artifact has missing or inconsistent outer predictions")
    return y_true, probabilities


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _save_figure(figure: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"
    if png_path.exists() or pdf_path.exists():
        raise FileExistsError(f"Refusing to overwrite generated figure {stem!r}")
    figure.savefig(png_path, dpi=300, bbox_inches="tight")
    figure.savefig(pdf_path, bbox_inches="tight")
    plt.close(figure)
    return [png_path.name, pdf_path.name]


def _performance_curves(
    nested: dict[str, dict[str, Any]], output_dir: Path
) -> list[str]:
    figure, axes = plt.subplots(2, 2, figsize=(12, 9))
    for row, dataset in enumerate(("heart5", "mendeley")):
        candidates = nested[dataset]["candidates"]
        for candidate_name, label in MODEL_NAMES.items():
            y_true, probability = _pooled_predictions(candidates[candidate_name])
            color = CURVE_COLORS[candidate_name]
            fpr, tpr, _ = roc_curve(y_true, probability)
            auc = roc_auc_score(y_true, probability)
            axes[row, 0].plot(fpr, tpr, label=f"{label} ({auc:.3f})", color=color, lw=1.8)
            precision, recall, _ = precision_recall_curve(y_true, probability)
            ap = average_precision_score(y_true, probability)
            axes[row, 1].plot(recall, precision, label=f"{label} ({ap:.3f})", color=color, lw=1.8)
        axes[row, 0].plot([0, 1], [0, 1], linestyle="--", color="#777777", lw=1)
        axes[row, 0].set_title(f"{dataset.title()} - ROC")
        axes[row, 0].set_xlabel("False positive rate")
        axes[row, 0].set_ylabel("True positive rate")
        axes[row, 0].set_xlim(0, 1)
        axes[row, 0].set_ylim(0, 1.02)
        axes[row, 1].set_title(f"{dataset.title()} - precision-recall")
        axes[row, 1].set_xlabel("Recall")
        axes[row, 1].set_ylabel("Precision")
        axes[row, 1].set_xlim(0, 1)
        axes[row, 1].set_ylim(0, 1.02)
        for axis in axes[row]:
            axis.grid(alpha=0.2)
            axis.legend(loc="lower left", fontsize=8, frameon=False)
    figure.suptitle(
        "Pooled outer-fold predictions (3 outer x 3 inner folds, seed 42)"
    )
    figure.tight_layout()
    return _save_figure(figure, output_dir, "nested_roc_pr_curves")


def _calibration_figure(
    nested: dict[str, dict[str, Any]], output_dir: Path
) -> list[str]:
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True)
    for axis, dataset in zip(axes, ("heart5", "mendeley"), strict=True):
        axis.plot([0, 1], [0, 1], linestyle="--", color="#777777", label="Ideal")
        for candidate_name in PRIMARY_MODELS:
            y_true, probability = _pooled_predictions(
                nested[dataset]["candidates"][candidate_name]
            )
            observed, predicted = calibration_curve(
                y_true, probability, n_bins=10, strategy="uniform"
            )
            metrics = nested[dataset]["candidates"][candidate_name]["pooled_outer_metrics"]
            label = (
                f"{MODEL_NAMES[candidate_name]} "
                f"(Brier {metrics['brier']:.3f}, macro-bin ECE {metrics['ece_uniform']:.3f})"
            )
            axis.plot(
                predicted,
                observed,
                marker="o",
                lw=1.8,
                color=CURVE_COLORS[candidate_name],
                label=label,
            )
        axis.set_title(dataset.title())
        axis.set_xlabel("Mean predicted probability")
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        axis.grid(alpha=0.2)
        axis.legend(fontsize=8, frameon=False, loc="upper left")
    axes[0].set_ylabel("Observed event frequency")
    figure.suptitle("Calibration on pooled outer-fold predictions (10 equal-width bins)")
    figure.tight_layout()
    return _save_figure(figure, output_dir, "nested_calibration")


def _confusion_matrix_figure(
    nested: dict[str, dict[str, Any]], output_dir: Path
) -> list[str]:
    figure, axes = plt.subplots(2, 2, figsize=(10, 7))
    for row, dataset in enumerate(("heart5", "mendeley")):
        for column, candidate_name in enumerate(PRIMARY_MODELS):
            y_true, probability = _pooled_predictions(
                nested[dataset]["candidates"][candidate_name]
            )
            matrix = confusion_matrix(y_true, probability >= 0.5, labels=[0, 1])
            axes[row, column].imshow(matrix, cmap="Blues", vmin=0)
            for (i, j), value in np.ndenumerate(matrix):
                axes[row, column].text(
                    j,
                    i,
                    f"{value:,}",
                    ha="center",
                    va="center",
                    color="white" if value > matrix.max() * 0.55 else "black",
                )
            axes[row, column].set_title(f"{dataset.title()} - {MODEL_NAMES[candidate_name]}")
            axes[row, column].set_xlabel("Predicted class")
            axes[row, column].set_ylabel("Observed class")
            axes[row, column].set_xticks([0, 1], labels=["0", "1"])
            axes[row, column].set_yticks([0, 1], labels=["0", "1"])
    figure.suptitle("Outer-fold confusion matrices at threshold 0.5")
    figure.tight_layout()
    return _save_figure(figure, output_dir, "nested_confusion_matrices")


def _risk_coverage_figure(
    nested: dict[str, dict[str, Any]], output_dir: Path
) -> list[str]:
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharex=True, sharey=True)
    for axis, dataset in zip(axes, ("heart5", "mendeley"), strict=True):
        for candidate_name in PRIMARY_MODELS:
            y_true, probability = _pooled_predictions(
                nested[dataset]["candidates"][candidate_name]
            )
            confidence = np.maximum(probability, 1.0 - probability)
            error = ((probability >= 0.5).astype(int) != y_true).astype(float)
            order = np.argsort(-confidence, kind="stable")
            risk = np.cumsum(error[order]) / np.arange(1, len(y_true) + 1)
            coverage = np.arange(1, len(y_true) + 1) / len(y_true)
            axis.plot(
                coverage,
                risk,
                color=CURVE_COLORS[candidate_name],
                lw=1.8,
                label=MODEL_NAMES[candidate_name],
            )
        axis.set_title(dataset.title())
        axis.set_xlabel("Coverage")
        axis.set_xlim(0, 1)
        axis.set_ylim(bottom=0)
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    axes[0].set_ylabel("Selective classification risk")
    figure.suptitle("Risk-coverage from confidence-ranked abstention")
    figure.tight_layout()
    return _save_figure(figure, output_dir, "nested_risk_coverage")


def _feature_stability_figure(output_dir: Path) -> tuple[list[str], list[str]]:
    figure, axes = plt.subplots(2, 1, figsize=(12, 9))
    inputs = []
    for axis, dataset in zip(axes, ("heart5", "mendeley"), strict=True):
        path = ROOT / "results" / "generated" / f"{dataset}_stability_evidence.json"
        inputs.append(str(path.relative_to(ROOT)))
        methods = _load_json(path)["methods"]
        stable = {
            row["feature"]: row["frequency"]
            for row in methods["stable_xaih_drc"]["selection_frequency"]
        }
        one_shot = {
            row["feature"]: row["frequency"]
            for row in methods["one_shot_xaih_drc"]["selection_frequency"]
        }
        names = sorted(
            set(stable) | set(one_shot),
            key=lambda feature: max(stable.get(feature, 0.0), one_shot.get(feature, 0.0)),
            reverse=True,
        )[:14]
        positions = np.arange(len(names))
        axis.barh(
            positions + 0.18,
            [stable.get(name, 0.0) for name in names],
            height=0.34,
            label="Stability-aware selector",
            color="#4C78A8",
        )
        axis.barh(
            positions - 0.18,
            [one_shot.get(name, 0.0) for name in names],
            height=0.34,
            label="One-shot selector",
            color="#F58518",
        )
        axis.set_yticks(positions, labels=names)
        axis.invert_yaxis()
        axis.set_xlim(0, 1)
        axis.set_xlabel("Selection frequency")
        axis.set_title(dataset.title())
        axis.grid(axis="x", alpha=0.2)
    figure.legend(
        ["Stability-aware selector", "One-shot selector"],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.97),
        ncol=2,
        frameon=False,
    )
    figure.suptitle(
        "Training-only feature selection frequency across perturbations", y=1.0
    )
    figure.tight_layout(rect=[0, 0, 1, 0.94])
    return _save_figure(figure, output_dir, "feature_selection_stability"), inputs


def _distribution_shift_figure(output_dir: Path) -> tuple[list[str], str]:
    path = ROOT / "results" / "generated" / "dataset_shift.json"
    data = _load_json(path)
    pairs = data["pairs"]
    pair_names = list(pairs)
    auc_values = [pairs[name]["domain_classifier_auc"] for name in pair_names]
    labels = [name.replace("_to_", " -> ").replace("_", " ") for name in pair_names]
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    positions = np.arange(len(pair_names))
    axes[0].barh(positions, auc_values, color="#4C78A8")
    axes[0].set_yticks(positions, labels=labels)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 1)
    axes[0].set_xlabel("Cross-validated domain-classifier ROC-AUC")
    axes[0].set_title("Can a classifier distinguish dataset source?")
    axes[0].grid(axis="x", alpha=0.2)

    numeric_rows = []
    for pair_name in pair_names:
        for feature, summary in pairs[pair_name]["feature_summaries"].items():
            if isinstance(summary, dict) and "standardized_mean_difference" in summary:
                numeric_rows.append(
                    (pair_name, feature, summary["standardized_mean_difference"])
                )
    y_positions = np.arange(len(numeric_rows))
    colors = ["#E45756" if value < 0 else "#54A24B" for _, _, value in numeric_rows]
    axes[1].barh(y_positions, [value for _, _, value in numeric_rows], color=colors)
    axes[1].axvline(0, color="#444444", lw=0.8)
    axes[1].set_yticks(
        y_positions,
        labels=[f"{pair.replace('_to_', ' -> ')}: {feature}" for pair, feature, _ in numeric_rows],
        fontsize=8,
    )
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Standardized mean difference (target - source)")
    axes[1].set_title("Numeric-feature distribution differences")
    axes[1].grid(axis="x", alpha=0.2)
    figure.suptitle("Unlabelled covariate-shift diagnostics; not predictive transfer")
    figure.tight_layout()
    return (
        _save_figure(figure, output_dir, "distribution_shift_diagnostics"),
        str(path.relative_to(ROOT)),
    )


def _aura_ablation_figure(output_dir: Path) -> tuple[list[str], list[str]]:
    figure, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)
    inputs = []
    display_names = {
        "full": "Full",
        "without_intelligence": "Without intelligence",
        "without_adaptive_preprocessing": "Without adaptive preprocessing",
        "without_multiview": "Without multiview",
        "without_feature_selection": "Without feature selection",
        "without_dynamic_fusion": "Without dynamic fusion",
        "without_reliability_weighting": "Without reliability weighting",
        "without_calibration": "Without calibration",
    }
    for axis, dataset in zip(axes, ("heart5", "mendeley"), strict=True):
        path = ROOT / "results" / "aura_ml" / "ablations" / dataset / "summary.json"
        inputs.append(str(path.relative_to(ROOT)))
        ablations = _load_json(path)["ablations"]
        labels = [display_names.get(row["ablation"], row["ablation"]) for row in ablations]
        values = [row["roc_auc"] for row in ablations]
        y = np.arange(len(labels))
        axis.barh(y, values, color=["#F58518" if i == 0 else "#9ECAE9" for i in range(len(labels))])
        axis.set_yticks(y, labels=labels)
        axis.invert_yaxis()
        axis.set_xlim(min(values) - 0.01, 1.0)
        axis.set_xlabel("ROC-AUC")
        axis.set_title(dataset.title())
        axis.grid(axis="x", alpha=0.2)
    figure.suptitle("AURA-ML V1 component ablations (2x2 exploratory protocol)")
    figure.tight_layout()
    return _save_figure(figure, output_dir, "aura_v1_ablation_roc_auc"), inputs


def _robustness_figure(output_dir: Path) -> tuple[list[str], list[str]]:
    figure, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    inputs = []
    conditions = ("clean", "missing_10pct", "numeric_noise_5pct_sd")
    labels = ("Clean", "10% missingness", "5% numeric noise")
    colors = {"corrected_osec": "#4C78A8", "stable_osec": "#E45756"}
    for axis, dataset in zip(axes, ("heart5", "mendeley"), strict=True):
        path = ROOT / "results" / "generated" / f"schema_corrected_{dataset}_robustness.json"
        inputs.append(str(path.relative_to(ROOT)))
        candidates = _load_json(path)["candidates"]
        x = np.arange(len(conditions))
        for candidate in ("corrected_osec", "stable_osec"):
            values = [candidates[candidate][condition]["roc_auc"] for condition in conditions]
            axis.plot(x, values, marker="o", color=colors[candidate], label=MODEL_NAMES[candidate])
        axis.set_xticks(x, labels=labels, rotation=15, ha="right")
        axis.set_ylim(0.5, 1.02)
        axis.set_title(dataset.title())
        axis.set_ylabel("ROC-AUC")
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    figure.suptitle("Evaluation-only perturbation stress tests (not external validation)")
    figure.tight_layout()
    return _save_figure(figure, output_dir, "robustness_stress_tests"), inputs


def _workflow_figure(output_dir: Path) -> list[str]:
    figure, axis = plt.subplots(figsize=(12, 3.4))
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    boxes = [
        (0.02, "Dataset +\nmanifest"),
        (0.20, "Outer split"),
        (0.39, "Train-only\npreprocessing"),
        (0.59, "Inner search +\nOOF stacking"),
        (0.79, "Untouched outer\nscore"),
    ]
    for x, text in boxes:
        axis.text(
            x + 0.075,
            0.54,
            text,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.7", "fc": "#EAF2F8", "ec": "#4C78A8", "lw": 1.4},
            fontsize=9,
        )
    for left, right in zip(boxes[:-1], boxes[1:], strict=True):
        axis.annotate(
            "",
            xy=(right[0] + 0.005, 0.54),
            xytext=(left[0] + 0.15, 0.54),
            arrowprops={"arrowstyle": "->", "lw": 1.4, "color": "#555555"},
        )
    axis.text(
        0.49,
        0.12,
        "Separate reliability runs reserve calibration rows before evaluation;\n"
        "outer test labels are not used for fitting, selection, or calibration.",
        ha="center",
        va="center",
        fontsize=9,
        color="#333333",
    )
    axis.set_title("Leakage-controlled nested evaluation workflow", pad=12)
    return _save_figure(figure, output_dir, "research_workflow")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results/master_directive_20261105_serial"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("paper/figures/master_directive_20261105"),
    )
    args = parser.parse_args()
    nested = {
        dataset: _load_json(args.results_dir / filename)
        for dataset, filename in DATASET_FILES.items()
    }
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    generated.extend(_performance_curves(nested, output_dir))
    generated.extend(_calibration_figure(nested, output_dir))
    generated.extend(_confusion_matrix_figure(nested, output_dir))
    generated.extend(_risk_coverage_figure(nested, output_dir))
    stability_files, stability_inputs = _feature_stability_figure(output_dir)
    generated.extend(stability_files)
    shift_files, shift_input = _distribution_shift_figure(output_dir)
    generated.extend(shift_files)
    ablation_files, ablation_inputs = _aura_ablation_figure(output_dir)
    generated.extend(ablation_files)
    robustness_files, robustness_inputs = _robustness_figure(output_dir)
    generated.extend(robustness_files)
    generated.extend(_workflow_figure(output_dir))

    input_paths = [
        args.results_dir / filename for filename in DATASET_FILES.values()
    ] + [
        ROOT / path
        for path in stability_inputs + [shift_input] + ablation_inputs + robustness_inputs
    ]
    manifest = {
        "status": "complete",
        "external_validation": False,
        "protocol": {
            "internal_predictions": "3 outer x 3 inner folds, seed 42; no external data",
            "calibration_bins": 10,
            "selective_threshold": 0.5,
            "figures_are_derived_from": "saved machine-readable artifacts only",
        },
        "input_artifacts": [
            {"path": str(path), "sha256": _sha256(path)} for path in input_paths
        ],
        "figure_generator_sha256": _sha256(Path(__file__)),
        "outputs": [
            {"path": name, "sha256": _sha256(output_dir / name)}
            for name in generated
        ],
        "not_generated": {
            "lime_explanation_stability": (
                "No validated fold-local LIME explanation artifact is available; "
                "feature-selection stability is not a substitute."
            ),
            "cross_dataset_performance": (
                "No predictive transfer run is authorized because endpoint and "
                "feature compatibility gates are blocked."
            ),
        },
    }
    manifest_path = output_dir / "figure_manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"Refusing to overwrite figure manifest: {manifest_path}")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(generated)} figure files in {output_dir}")


if __name__ == "__main__":
    main()
