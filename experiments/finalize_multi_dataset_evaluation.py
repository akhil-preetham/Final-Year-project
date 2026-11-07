"""Create figures, compatibility tables, and a traceable evaluation report."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "multi_dataset_evaluation_20261108"
DOC_REPORT = ROOT / "docs" / "MULTI_DATASET_EXPERIMENTAL_EVALUATION_REPORT.md"
MODEL_ORDER = ["logistic", "knn", "svm", "random_forest", "ovec", "osec"]
MODEL_LABELS = {
    "logistic": "Logistic Regression",
    "knn": "K-Nearest Neighbors",
    "svm": "Support Vector Machine",
    "random_forest": "Random Forest",
    "ovec": "OVEC",
    "osec": "OSEC",
}
DATASET_LABELS = {
    "uci_cleveland": "UCI Cleveland",
    "uci_hungary": "UCI Hungary",
    "uci_switzerland": "UCI Switzerland",
    "uci_va_long_beach": "UCI VA Long Beach",
    "uci_heart_failure_519": "UCI Heart Failure",
    "uci_mi_complications_579": "UCI MI Complications",
    "uci_spectf_heart": "UCI SPECTF Heart",
}
METRIC_DISPLAY = [
    ("accuracy", "Accuracy"),
    ("precision", "Precision"),
    ("recall", "Recall / sensitivity"),
    ("specificity", "Specificity"),
    ("f1", "F1"),
    ("roc_auc", "ROC-AUC"),
    ("pr_auc", "PR-AUC"),
]


def write_figure(fig: plt.Figure, directory: Path, stem: str) -> list[str]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = [directory / f"{stem}.pdf", directory / f"{stem}.png"]
    for path in paths:
        fig.savefig(path, bbox_inches="tight", dpi=220 if path.suffix == ".png" else None)
    plt.close(fig)
    return [path.relative_to(ROOT).as_posix() for path in paths]


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    return float(roc_auc_score(y, score)) if np.unique(y).size == 2 else float("nan")


def make_ood_diagnostics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (dataset, model), frame in predictions.groupby(["dataset", "model"], sort=True):
        y = frame["y_true"].to_numpy(dtype=int)
        predicted = frame["predicted_label_at_0_5"].to_numpy(dtype=int)
        alert = frame["ood_alert"].to_numpy(dtype=int)
        error = predicted != y
        alerted = alert == 1
        unflagged = ~alerted
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "n": len(frame),
                "ood_alert_rate": float(alerted.mean()),
                "error_rate_all": float(error.mean()),
                "error_rate_alerted": float(error[alerted].mean()) if alerted.any() else None,
                "error_rate_unflagged": float(error[unflagged].mean()) if unflagged.any() else None,
                "error_alert_sensitivity": float((error & alerted).sum() / error.sum())
                if error.any()
                else None,
                "error_alert_precision": float((error & alerted).sum() / alerted.sum())
                if alerted.any()
                else None,
                "ood_error_discrimination_auc": safe_auc(
                    error.astype(int), frame["ood_score"].to_numpy()
                ),
                "note": (
                    "Fold-calibrated feature-support alerts are diagnostics, "
                    "not a clinical safety gate."
                ),
            }
        )
    return pd.DataFrame(rows)


def make_selective_diagnostics(
    predictions: pd.DataFrame, selective_curve: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    curve_summary = selective_curve[selective_curve.nominal_coverage.isna()]
    for (dataset, model), frame in predictions.groupby(["dataset", "model"], sort=True):
        accepted = frame.accepted_by_singleton_and_ood_diagnostics.to_numpy(dtype=bool)
        errors = frame.predicted_label_at_0_5.to_numpy(dtype=int) != frame.y_true.to_numpy(
            dtype=int
        )
        current = curve_summary[(curve_summary.dataset == dataset) & (curve_summary.model == model)]
        rows.append(
            {
                "dataset": dataset,
                "model": model,
                "n": len(frame),
                "confidence_aurc": float(current.iloc[0].aurc_trapezoid)
                if not current.empty
                else None,
                "confidence_risk_at_80pct_coverage": float(current.iloc[0].risk_at_80pct_coverage)
                if not current.empty
                else None,
                "singleton_plus_ood_accepted_n": int(accepted.sum()),
                "singleton_plus_ood_accepted_coverage": float(accepted.mean()),
                "singleton_plus_ood_error_rate": float(errors[accepted].mean())
                if accepted.any()
                else None,
                "singleton_plus_ood_errors": int(errors[accepted].sum()),
                "interpretation": (
                    "Retrospective diagnostic; accepted-set error rate may be undefined "
                    "or unstable at low coverage."
                ),
            }
        )
    return pd.DataFrame(rows)


def dataset_comparison(manifest: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dataset_id, item in manifest["datasets"].items():
        source = item["source"]
        counts = item.get("class_counts", {})
        rows.append(
            {
                "dataset_id": dataset_id,
                "dataset_name": source["name"],
                "dataset_id_uci": source.get("dataset_id"),
                "source_url": source.get("url"),
                "license": source.get("license"),
                "records": item.get("rows"),
                "predictors": item.get("predictor_count"),
                "target_definition": item.get("target_definition"),
                "class_counts": json.dumps(counts, sort_keys=True),
                "missing_predictor_cells": item.get("missing_predictor_cells"),
                "exact_duplicate_predictor_rows": item.get("exact_duplicate_predictor_rows"),
                "patient_independence": "Not established from public records",
                "lineage_and_compatibility": item.get("interpretation"),
                "decision": "Included as its own task; no cross-task pooling",
                "status": "included",
            }
        )
    excluded = [
        (
            "uci_statlog_heart",
            "UCI Statlog Heart",
            145,
            "https://archive.ics.uci.edu/dataset/145/statlog+heart",
            "CC BY 4.0",
            270,
            13,
            "CAD classification; Cleveland-compatible labels",
            "All 270 records match Cleveland after harmonization; duplicate cohort",
            "Excluded from added evaluation",
        ),
        (
            "mendeley_heart_disease_2026",
            "Mendeley Heart Disease 2026",
            None,
            "https://data.mendeley.com/datasets/nt4y898vyh/1",
            "CC BY 4.0",
            918,
            None,
            "Binary target; composite lineage",
            "Exact 918/918 labeled-row multiset match with Heart5; duplicate historical benchmark, not a new cohort",
            "Excluded; prior benchmark only",
        ),
        (
            "mendeley_cardiovascular_2021",
            "Mendeley Cardiovascular 2021",
            None,
            "https://data.mendeley.com/datasets/dzz48mvjht/1",
            "CC BY 4.0 per project source audit",
            1000,
            None,
            "Binary cardiovascular label",
            "No verified angiographic reference standard or predictor timing; previously examined",
            "Excluded from new experiment",
        ),
        (
            "z_alizadeh_sani",
            "Z-Alizadeh Sani",
            412,
            "https://archive.ics.uci.edu/dataset/412/z+alizadeh+sani",
            "CC BY 4.0",
            303,
            54,
            "CAD threshold >=50%",
            "Previously examined; endpoint differs from UCI >50% rule; no patient linkage",
            "Excluded from new run; historical transfer remains separate",
        ),
        (
            "angiocad",
            "AngioCAD",
            None,
            "https://zenodo.org/records/15826856",
            "CC BY 4.0; dataset and article attribution required",
            413,
            None,
            "Coronary segment stenosis bins; 377 feature matches",
            "Previously examined; incomplete ID-feature matching and uncertain age/FBS units; post-hoc analyses",
            "Excluded from new run; historical stress test remains separate",
        ),
        (
            "duke_acath",
            "Duke ACATH",
            None,
            "https://hbiostat.org/data/repo/acath",
            "Provider permits use with attribution; redistribution terms unspecified",
            3504,
            None,
            "Significant disease at >=75% stenosis",
            "Endpoint mismatch versus UCI; previously examined",
            "Excluded from new run; historical stress test remains separate",
        ),
        (
            "kaggle_cardio_70k",
            "Cardio Train (Kaggle 70K)",
            None,
            "https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset",
            "Dataset card reports license Unknown",
            70000,
            11,
            "Distinct binary risk label",
            "Target and clinical timing not equivalent to angiographic CAD; license unresolved",
            "Excluded",
        ),
        (
            "mimic_iv",
            "MIMIC-IV",
            None,
            "https://physionet.org/content/mimiciv/3.1/",
            "Credentialed access, training, and data-use agreement required",
            None,
            None,
            "Hospital EHR; derived task required",
            "Access credentials and data-use agreement were not available in this run",
            "Not acquired",
        ),
        (
            "multid4cad",
            "MultiD4CAD",
            None,
            "https://zenodo.org/records/15148653",
            "Controlled access; data-use agreement required",
            None,
            None,
            "Multi-center CAD records",
            "Controlled-access agreement was not acquired",
            "Not acquired",
        ),
    ]
    for dataset_id, name, uci_id, url, license_name, n, p, target, reason, decision in excluded:
        rows.append(
            {
                "dataset_id": dataset_id,
                "dataset_name": name,
                "dataset_id_uci": uci_id,
                "source_url": url,
                "license": license_name,
                "records": n,
                "predictors": p,
                "target_definition": target,
                "class_counts": None,
                "missing_predictor_cells": None,
                "exact_duplicate_predictor_rows": None,
                "patient_independence": "Not established",
                "lineage_and_compatibility": reason,
                "decision": decision,
                "status": "excluded_or_not_acquired",
            }
        )
    return pd.DataFrame(rows)


def plot_roc_pr(pred: pd.DataFrame, out: Path) -> list[str]:
    from sklearn.metrics import roc_curve

    dataset_ids = list(DATASET_LABELS)
    fig, axes = plt.subplots(4, 2, figsize=(12, 17))
    for axis, dataset in zip(axes.flat, dataset_ids, strict=False):
        frame = pred[pred.dataset == dataset]
        for model in MODEL_ORDER:
            group = frame[frame.model == model]
            if group.empty or group.y_true.nunique() < 2:
                continue
            y = group.y_true.to_numpy(dtype=int)
            p = group.probability_positive.to_numpy(dtype=float)
            fpr, tpr, _ = roc_curve(y, p)
            axis.plot(fpr, tpr, label=f"{MODEL_LABELS[model]} ({roc_auc_score(y, p):.2f})", lw=1.25)
        axis.plot([0, 1], [0, 1], color="0.65", ls="--", lw=0.8)
        axis.set(
            title=DATASET_LABELS[dataset],
            xlabel="False-positive rate",
            ylabel="True-positive rate",
            xlim=(0, 1),
            ylim=(0, 1),
        )
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.005),
        fontsize=8,
    )
    fig.suptitle(
        "ROC curves from outer-fold predictions or the official SPECTF test split", y=0.995
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.98))
    return write_figure(fig, out, "roc_curves")


def plot_precision_recall(pred: pd.DataFrame, out: Path) -> list[str]:
    from sklearn.metrics import precision_recall_curve

    fig, axes = plt.subplots(4, 2, figsize=(12, 17))
    for axis, dataset in zip(axes.flat, DATASET_LABELS, strict=False):
        frame = pred[pred.dataset == dataset]
        for model in MODEL_ORDER:
            group = frame[frame.model == model]
            if group.empty or group.y_true.nunique() < 2:
                continue
            y = group.y_true.to_numpy(dtype=int)
            p = group.probability_positive.to_numpy(dtype=float)
            precision, recall, _ = precision_recall_curve(y, p)
            axis.plot(
                recall,
                precision,
                label=f"{MODEL_LABELS[model]} ({average_precision_score(y, p):.2f})",
                lw=1.25,
            )
        if not frame.empty:
            axis.axhline(frame.y_true.mean(), color="0.65", ls="--", lw=0.8, label="Prevalence")
        axis.set(
            title=DATASET_LABELS[dataset],
            xlabel="Recall / sensitivity",
            ylabel="Precision",
            xlim=(0, 1),
            ylim=(0, 1),
        )
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.005),
        fontsize=8,
    )
    fig.suptitle(
        "Precision–recall curves from outer-fold predictions or the official SPECTF test split",
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.98))
    return write_figure(fig, out, "precision_recall_curves")


def plot_confusion(pred: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(7, 6, figsize=(16, 18))
    for i, dataset in enumerate(DATASET_LABELS):
        for j, model in enumerate(MODEL_ORDER):
            axis = axes[i, j]
            group = pred[(pred.dataset == dataset) & (pred.model == model)]
            if group.empty:
                axis.axis("off")
                continue
            matrix = confusion_matrix(group.y_true, group.predicted_label_at_0_5, labels=[0, 1])
            axis.imshow(matrix, cmap="Blues", vmin=0)
            for row in range(2):
                for col in range(2):
                    axis.text(col, row, str(matrix[row, col]), ha="center", va="center", fontsize=8)
            axis.set_xticks([0, 1], ["0", "1"])
            axis.set_yticks([0, 1], ["0", "1"])
            if i == 0:
                axis.set_title(MODEL_LABELS[model], fontsize=9)
            if j == 0:
                axis.set_ylabel(f"{DATASET_LABELS[dataset]}\nTrue label", fontsize=8)
            if i == 6:
                axis.set_xlabel("Predicted at 0.5", fontsize=8)
    fig.suptitle("Confusion matrices at a fixed 0.5 probability threshold", y=1.002)
    fig.tight_layout()
    return write_figure(fig, out, "confusion_matrices")


def plot_performance(metrics: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(2, 1, figsize=(14, 11), sharex=True)
    x = np.arange(len(DATASET_LABELS))
    width = 0.12
    for axis, metric, title in zip(axes, ["roc_auc", "pr_auc"], ["ROC-AUC", "PR-AUC"], strict=True):
        for index, model in enumerate(MODEL_ORDER):
            subset = metrics.set_index(["dataset", "model"])
            values = [
                subset.loc[(dataset, model), f"fold_mean_{metric}"]
                if (dataset, model) in subset.index
                else np.nan
                for dataset in DATASET_LABELS
            ]
            errors = [
                subset.loc[(dataset, model), f"{metric}_fold_sd"]
                if (dataset, model) in subset.index
                else 0
                for dataset in DATASET_LABELS
            ]
            axis.bar(
                x + (index - 2.5) * width,
                values,
                width,
                yerr=errors,
                capsize=2,
                label=MODEL_LABELS[model],
            )
        axis.set(title=title, ylabel=title, ylim=(0, 1.03))
        axis.grid(axis="y", alpha=0.25)
    axes[-1].set_xticks(x, [DATASET_LABELS[key] for key in DATASET_LABELS], rotation=20, ha="right")
    axes[0].legend(ncol=3, frameon=False, fontsize=9)
    fig.suptitle("Nested cross-validation and official test performance (fold mean ± SD)")
    fig.tight_layout()
    return write_figure(fig, out, "model_performance_comparison")


def plot_gaps(metrics: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(4, 2, figsize=(14, 15), sharey=True)
    for axis, dataset in zip(axes.flat, DATASET_LABELS, strict=False):
        frame = (
            metrics[metrics.dataset == dataset]
            .set_index("model")
            .reindex(MODEL_ORDER)
            .dropna(subset=["fold_mean_roc_auc"])
        )
        x = np.arange(len(frame))
        axis.plot(
            x, frame.train_roc_auc_resubstitution_mean, "o-", label="Development resubstitution"
        )
        axis.plot(
            x, frame.inner_validation_roc_auc_mean, "s-", label="Selected inner-CV validation"
        )
        axis.plot(x, frame.fold_mean_roc_auc, "^-", label="Outer test / official test")
        axis.set(
            title=DATASET_LABELS[dataset],
            xticks=x,
            xticklabels=[MODEL_LABELS[item] for item in frame.index],
            ylim=(0, 1.05),
        )
        axis.tick_params(axis="x", rotation=25, labelsize=8)
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    axes.flat[0].legend(fontsize=8, frameon=False)
    fig.suptitle("Training, inner-validation, and held-out performance")
    fig.tight_layout()
    return write_figure(fig, out, "training_validation_gaps")


def plot_learning_curves(learning: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(4, 2, figsize=(14, 15), sharey=True)
    for axis, dataset in zip(axes.flat, DATASET_LABELS, strict=False):
        frame = learning[learning.dataset == dataset]
        if frame.empty:
            axis.text(0.5, 0.5, "No learning-curve results", ha="center", va="center")
            axis.set_title(DATASET_LABELS[dataset])
            continue
        for model in MODEL_ORDER:
            group = frame[frame.model == model].sort_values("train_rows")
            if group.empty:
                continue
            axis.plot(
                group.train_rows,
                group.validation_roc_auc_mean,
                "o-",
                lw=1.2,
                label=f"{MODEL_LABELS[model]} validation",
            )
            axis.plot(group.train_rows, group.train_roc_auc_mean, "--", lw=0.9, alpha=0.7)
        axis.set(
            title=DATASET_LABELS[dataset],
            xlabel="Training rows per fold",
            ylabel="ROC-AUC",
            ylim=(0, 1.05),
        )
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=3,
        fontsize=7,
        frameon=False,
        bbox_to_anchor=(0.5, 0.005),
    )
    fig.suptitle(
        "Learning curves: validation is solid; corresponding training score is dashed", y=0.995
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.98))
    return write_figure(fig, out, "learning_curves")


def plot_calibration(bins: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(4, 2, figsize=(13, 14), sharex=True, sharey=True)
    for axis, dataset in zip(axes.flat, DATASET_LABELS, strict=False):
        frame = bins[bins.dataset == dataset]
        for model in MODEL_ORDER:
            group = frame[frame.model == model].sort_values("mean_predicted_probability")
            if not group.empty:
                axis.plot(
                    group.mean_predicted_probability,
                    group.observed_positive_fraction,
                    "o-",
                    ms=3,
                    lw=1.1,
                    label=MODEL_LABELS[model],
                )
        axis.plot([0, 1], [0, 1], color="0.5", ls="--", lw=0.8)
        axis.set(
            title=DATASET_LABELS[dataset],
            xlabel="Mean predicted probability",
            ylabel="Observed positive fraction",
            xlim=(0, 1),
            ylim=(0, 1),
        )
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    axes.flat[0].legend(fontsize=7, frameon=False)
    fig.suptitle("Calibration of pooled outer-fold / official-test predictions")
    fig.tight_layout()
    return write_figure(fig, out, "calibration_curves")


def plot_risk_coverage(selective: pd.DataFrame, out: Path) -> list[str]:
    fig, axes = plt.subplots(4, 2, figsize=(13, 14), sharex=True, sharey=True)
    for axis, dataset in zip(axes.flat, DATASET_LABELS, strict=False):
        frame = selective[(selective.dataset == dataset) & selective.nominal_coverage.notna()]
        for model in MODEL_ORDER:
            group = frame[frame.model == model].sort_values("achieved_coverage")
            if not group.empty:
                axis.plot(
                    group.achieved_coverage,
                    group.risk_error_rate,
                    "o-",
                    ms=3,
                    lw=1.1,
                    label=MODEL_LABELS[model],
                )
        axis.set(
            title=DATASET_LABELS[dataset],
            xlabel="Coverage",
            ylabel="Error rate among retained",
            xlim=(0, 1),
            ylim=(0, 1),
        )
        axis.grid(alpha=0.2)
    axes.flat[-1].axis("off")
    axes.flat[0].legend(fontsize=7, frameon=False)
    fig.suptitle("Confidence-ranked selective prediction (descriptive risk–coverage curves)")
    fig.tight_layout()
    return write_figure(fig, out, "risk_coverage_curves")


def plot_cross_heatmaps(cross: pd.DataFrame, out: Path) -> list[str]:
    cad = ["uci_cleveland", "uci_hungary", "uci_switzerland", "uci_va_long_beach"]
    fig, axes = plt.subplots(
        2, 3, figsize=(15, 9), sharex=True, sharey=True, constrained_layout=True
    )
    fields = [
        ("target_roc_auc", "Target ROC-AUC"),
        ("target_ood_detection_roc_auc", "Source vs target OOD AUROC"),
        ("target_ood_alert_rate", "Target OOD alert rate"),
    ]
    for index, model in enumerate(MODEL_ORDER):
        axis = axes.flat[index]
        matrix = np.full((len(cad), len(cad)), np.nan)
        subset = cross[cross.model == model]
        for row, source in enumerate(cad):
            for column, target in enumerate(cad):
                match = subset[
                    (subset.source_dataset == source) & (subset.target_dataset == target)
                ]
                if not match.empty:
                    matrix[row, column] = float(match.iloc[0].target_roc_auc)
        image = axis.imshow(matrix, cmap="viridis", vmin=0, vmax=1)
        for row in range(len(cad)):
            for column in range(len(cad)):
                axis.text(
                    column,
                    row,
                    "—" if np.isnan(matrix[row, column]) else f"{matrix[row, column]:.2f}",
                    ha="center",
                    va="center",
                    color="white" if matrix[row, column] < 0.55 else "black",
                    fontsize=8,
                )
        axis.set(
            title=MODEL_LABELS[model],
            xticks=range(4),
            xticklabels=["CLE", "HUN", "SWI", "VA"],
            yticks=range(4),
            yticklabels=["CLE", "HUN", "SWI", "VA"],
            xlabel="Target",
            ylabel="Source",
        )
    fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.8, label="Target ROC-AUC")
    fig.suptitle("Source-only cross-cohort CAD stress tests (diagonal omitted)")
    paths = write_figure(fig, out, "cross_dataset_roc_auc_heatmaps")

    fig, axes = plt.subplots(
        1, 2, figsize=(10, 4.8), sharex=True, sharey=True, constrained_layout=True
    )
    for axis, (field, title) in zip(axes, fields[1:], strict=True):
        matrix = np.full((len(cad), len(cad)), np.nan)
        for row, source in enumerate(cad):
            for column, target in enumerate(cad):
                match = cross[(cross.source_dataset == source) & (cross.target_dataset == target)]
                if not match.empty:
                    matrix[row, column] = float(match[field].mean())
        im = axis.imshow(matrix, cmap="magma" if "alert" in field else "cividis", vmin=0, vmax=1)
        for row in range(len(cad)):
            for column in range(len(cad)):
                axis.text(
                    column,
                    row,
                    "—" if np.isnan(matrix[row, column]) else f"{matrix[row, column]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8,
                )
        axis.set(
            title=title,
            xticks=range(4),
            xticklabels=["CLE", "HUN", "SWI", "VA"],
            yticks=range(4),
            yticklabels=["CLE", "HUN", "SWI", "VA"],
            xlabel="Target",
            ylabel="Source",
        )
        fig.colorbar(im, ax=axis, shrink=0.75)
    fig.suptitle(
        "Cross-cohort feature-support alert and domain discrimination diagnostics (model mean)"
    )
    paths.extend(write_figure(fig, out, "cross_dataset_ood_heatmaps"))
    return paths


def plot_cross_mean_auc_heatmap(cross: pd.DataFrame, out: Path) -> list[str]:
    cad = ["uci_cleveland", "uci_hungary", "uci_switzerland", "uci_va_long_beach"]
    labels = ["Cleveland", "Hungary", "Switzerland", "VA Long Beach"]
    matrix = np.full((len(cad), len(cad)), np.nan)
    for row, source in enumerate(cad):
        for column, target in enumerate(cad):
            subset = cross[(cross.source_dataset == source) & (cross.target_dataset == target)]
            if not subset.empty:
                matrix[row, column] = float(subset.target_roc_auc.mean())
    fig, axis = plt.subplots(figsize=(6.2, 5.2), constrained_layout=True)
    image = axis.imshow(matrix, cmap="viridis", vmin=0, vmax=1)
    for row in range(len(cad)):
        for column in range(len(cad)):
            value = matrix[row, column]
            axis.text(
                column,
                row,
                "—" if np.isnan(value) else f"{value:.2f}",
                ha="center",
                va="center",
                color="white" if value < 0.55 else "black",
                fontsize=9,
            )
    axis.set(
        title="Mean target ROC-AUC across six source-only models",
        xticks=range(4),
        xticklabels=labels,
        yticks=range(4),
        yticklabels=labels,
        xlabel="Target cohort",
        ylabel="Source cohort",
    )
    axis.tick_params(axis="x", labelrotation=25)
    fig.colorbar(image, ax=axis, shrink=0.82, label="Mean ROC-AUC")
    return write_figure(fig, out, "cross_dataset_mean_auc_heatmap")


def metric_check(predictions: pd.DataFrame, metrics: pd.DataFrame) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for (dataset, model), group in predictions.groupby(["dataset", "model"], sort=True):
        y = group.y_true.to_numpy(dtype=int)
        p = group.probability_positive.to_numpy(dtype=float)
        pred = (p >= 0.5).astype(int)
        expected = metrics[(metrics.dataset == dataset) & (metrics.model == model)]
        if len(expected) != 1:
            raise AssertionError(f"Expected exactly one summary row for {dataset}/{model}")
        row = expected.iloc[0]
        values = {
            "accuracy": accuracy_score(y, pred),
            "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0),
            "specificity": confusion_matrix(y, pred, labels=[0, 1])[0, 0]
            / max(1, confusion_matrix(y, pred, labels=[0, 1])[0].sum()),
            "f1": f1_score(y, pred, zero_division=0),
            "roc_auc": roc_auc_score(y, p),
            "pr_auc": average_precision_score(y, p),
            "brier": brier_score_loss(y, p),
        }
        for key, value in values.items():
            if not np.isclose(float(row[f"pooled_{key}"]), float(value), rtol=0, atol=1e-12):
                raise AssertionError(f"Prediction/metric mismatch {dataset}/{model}/{key}")
        checks.append({"dataset": dataset, "model": model, "n": len(group), "checks": list(values)})
    return {
        "prediction_group_count": len(checks),
        "all_pooled_metrics_recomputed": True,
        "groups": checks,
    }


def cross_metric_check(predictions: pd.DataFrame, cross_metrics: pd.DataFrame) -> dict[str, Any]:
    checked = 0
    for keys, group in predictions.groupby(
        ["source_dataset", "target_dataset", "model"], sort=True
    ):
        expected = cross_metrics[
            (cross_metrics.source_dataset == keys[0])
            & (cross_metrics.target_dataset == keys[1])
            & (cross_metrics.model == keys[2])
        ]
        if len(expected) != 1:
            raise AssertionError(f"Expected exactly one cross metric row for {keys}")
        y = group.y_true.to_numpy(dtype=int)
        probability = group.probability_positive.to_numpy(dtype=float)
        predicted = (probability >= 0.5).astype(int)
        matrix = confusion_matrix(y, predicted, labels=[0, 1])
        values = {
            "accuracy": accuracy_score(y, predicted),
            "precision": precision_score(y, predicted, zero_division=0),
            "recall": recall_score(y, predicted, zero_division=0),
            "specificity": matrix[0, 0] / max(1, matrix[0].sum()),
            "f1": f1_score(y, predicted, zero_division=0),
            "roc_auc": roc_auc_score(y, probability),
            "pr_auc": average_precision_score(y, probability),
            "brier": brier_score_loss(y, probability),
        }
        row = expected.iloc[0]
        for key, value in values.items():
            if not np.isclose(float(row[f"target_{key}"]), float(value), rtol=0, atol=1e-12):
                raise AssertionError(f"Cross prediction/metric mismatch {keys}/{key}")
        if len(group) != int(row.target_n):
            raise AssertionError(f"Cross prediction count mismatch {keys}")
        if group.row_index.duplicated().any():
            raise AssertionError(f"Duplicate cross prediction row in {keys}")
        checked += 1
    return {"prediction_group_count": checked, "all_cross_metrics_recomputed": True}


def prepared_target(dataset_id: str, manifest: dict[str, Any]) -> np.ndarray:
    record = manifest["datasets"][dataset_id]
    source = record["source"]
    if source.get("prepared_paths"):
        relative_path = source["prepared_paths"]["test"]
    else:
        relative_path = source["prepared_path"]
    frame = pd.read_csv(ROOT / relative_path)
    return pd.to_numeric(frame[record["target"]], errors="raise").to_numpy(dtype=int)


def check_saved_labels(
    predictions: pd.DataFrame, cross_predictions: pd.DataFrame, manifest: dict[str, Any]
) -> dict[str, int]:
    within_groups = 0
    for (dataset, model), group in predictions.groupby(["dataset", "model"], sort=True):
        expected = prepared_target(dataset, manifest)
        indices = group.row_index.to_numpy(dtype=int)
        labels = group.y_true.to_numpy(dtype=int)
        if not np.array_equal(labels, expected[indices]):
            raise AssertionError(f"Saved labels differ from prepared targets in {dataset}/{model}")
        within_groups += 1
    cross_groups = 0
    for keys, group in cross_predictions.groupby(
        ["source_dataset", "target_dataset", "model"], sort=True
    ):
        expected = prepared_target(keys[1], manifest)
        indices = group.row_index.to_numpy(dtype=int)
        labels = group.y_true.to_numpy(dtype=int)
        if not np.array_equal(labels, expected[indices]):
            raise AssertionError(f"Cross saved labels differ from target data in {keys}")
        cross_groups += 1
    return {"within_task_label_groups": within_groups, "cross_task_label_groups": cross_groups}


def fmt(value: Any, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "—"
    if isinstance(value, str):
        return value
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return str(int(value))
    return f"{float(value):.{digits}f}"


def md_table(frame: pd.DataFrame, columns: list[tuple[str, str]], limit: int | None = None) -> str:
    selected = frame if limit is None else frame.head(limit)
    header = "| " + " | ".join(label for _, label in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in selected.iterrows():
        rows.append("| " + " | ".join(fmt(row.get(key)) for key, _ in columns) + " |")
    return "\n".join([header, divider, *rows])


def verify_artifacts(
    manifest: dict[str, Any],
    predictions: pd.DataFrame,
    cross_predictions: pd.DataFrame,
    metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    cross_metrics: pd.DataFrame,
) -> dict[str, Any]:
    checksum_checks = []
    prepared_checks = []
    for dataset_id, record in manifest["datasets"].items():
        source = record["source"]
        raw_key = "archive_path" if source.get("archive_path") else "source_path"
        raw_path = ROOT / source[raw_key]
        actual = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        expected = source.get("archive_sha256") or source.get("source_sha256")
        if actual != expected:
            raise AssertionError(f"Source checksum mismatch for {dataset_id}")
        checksum_checks.append(dataset_id)
        if source.get("prepared_paths"):
            for split_name, relative_path in source["prepared_paths"].items():
                if split_name not in source["prepared_sha256"]:
                    continue
                path = ROOT / relative_path
                prepared_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if prepared_hash != source["prepared_sha256"][split_name]:
                    raise AssertionError(
                        f"Prepared {split_name} checksum mismatch for {dataset_id}"
                    )
                prepared_checks.append(f"{dataset_id}:{split_name}")
        elif source.get("prepared_path"):
            path = ROOT / source["prepared_path"]
            prepared_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if prepared_hash != source["prepared_sha256"]:
                raise AssertionError(f"Prepared checksum mismatch for {dataset_id}")
            prepared_checks.append(dataset_id)
    for (dataset, model), group in predictions.groupby(["dataset", "model"]):
        if group.row_index.duplicated().any():
            raise AssertionError(f"Duplicate scored row in {dataset}/{model}")
        expected_n = (
            187 if dataset == "uci_spectf_heart" else int(manifest["datasets"][dataset]["rows"])
        )
        if len(group) != expected_n:
            raise AssertionError(
                f"Prediction count mismatch {dataset}/{model}: {len(group)} != {expected_n}"
            )
    assignments_path = next((RESULTS / "predictions").glob("*/fold_assignments.csv"))
    assignments = pd.read_csv(assignments_path)
    assignment_checks = []
    assignment_keys = ["dataset", "fold"]
    if "model" in assignments.columns:
        assignment_keys.append("model")
    for keys, group in assignments.groupby(assignment_keys, dropna=False):
        dataset, fold = keys[:2]
        duplicate_rows = group.duplicated(["split_role", "row_index"])
        if duplicate_rows.any():
            raise AssertionError(f"Fold assignment overlap in {dataset} fold {fold}")
        roles = set(group.split_role)
        if dataset != "uci_spectf_heart" and group.row_index.duplicated().any():
            raise AssertionError(f"Cross-role fold overlap in {dataset} fold {fold}")
        if (
            not {"development", "conformal_calibration", "outer_test"}.issubset(roles)
            and dataset != "uci_spectf_heart"
        ):
            raise AssertionError(f"Missing nested roles in {dataset} fold {fold}")
        if dataset == "uci_spectf_heart":
            if not {"development", "conformal_calibration", "official_test"}.issubset(roles):
                raise AssertionError("SPECTF assignments do not preserve the official split")
            role_counts = group.split_role.value_counts().to_dict()
            if role_counts != {
                "official_test": 187,
                "development": 64,
                "conformal_calibration": 16,
            }:
                raise AssertionError(f"Unexpected SPECTF role sizes: {role_counts}")
        assignment_checks.append(
            {
                "dataset": dataset,
                "fold": fold,
                "model": keys[2] if len(keys) > 2 else None,
                "rows": len(group),
                "roles": sorted(roles),
            }
        )
    for dataset_id in set(assignments.dataset) - {"uci_spectf_heart"}:
        outer_test = assignments[
            (assignments.dataset == dataset_id) & (assignments.split_role == "outer_test")
        ]
        counts = outer_test.row_index.value_counts()
        expected_n = int(manifest["datasets"][dataset_id]["rows"])
        if len(counts) != expected_n or not (counts == 1).all():
            raise AssertionError(
                f"Each row must appear in exactly one outer test fold for {dataset_id}"
            )
    cross_assignments_path = next(
        (RESULTS / "predictions").glob("*/cross_dataset_split_assignments.csv")
    )
    cross_assignments = pd.read_csv(cross_assignments_path)
    cross_assignment_checks = []
    for keys, group in cross_assignments.groupby(
        ["source_dataset", "target_dataset", "model"], sort=True
    ):
        if group.duplicated(["split_role", "row_index"]).any():
            raise AssertionError(f"Duplicate cross split assignment in {keys}")
        roles = set(group.split_role)
        if not {"source_development", "source_calibration", "target_test"}.issubset(roles):
            raise AssertionError(f"Incomplete source-only assignment roles in {keys}")
        target_count = int((group.split_role == "target_test").sum())
        if target_count != int(manifest["datasets"][keys[1]]["rows"]):
            raise AssertionError(f"Unexpected target assignment count in {keys}")
        source_roles = group[group.split_role.isin(["source_development", "source_calibration"])]
        if source_roles.row_index.duplicated().any():
            raise AssertionError(f"Source development/calibration overlap in {keys}")
        if len(source_roles) != int(manifest["datasets"][keys[0]]["rows"]):
            raise AssertionError(f"Unexpected source row assignment count in {keys}")
        cross_assignment_checks.append(
            {"source": keys[0], "target": keys[1], "model": keys[2], "target_rows": target_count}
        )
    for keys, group in cross_predictions.groupby(
        ["source_dataset", "target_dataset", "model"], sort=True
    ):
        if group.row_index.duplicated().any():
            raise AssertionError(f"Duplicate target prediction row in {keys}")
        expected_n = int(manifest["datasets"][keys[1]]["rows"])
        if len(group) != expected_n:
            raise AssertionError(f"Cross-dataset prediction count mismatch in {keys}")
    check = metric_check(predictions, metrics)
    cross_check = cross_metric_check(cross_predictions, cross_metrics)
    label_check = check_saved_labels(predictions, cross_predictions, manifest)
    if fold_metrics.empty:
        raise AssertionError("Fold metric file is empty")
    return {
        "status": "passed",
        "source_checksum_count": len(checksum_checks),
        "source_checksums_verified": checksum_checks,
        "prepared_checksum_count": len(prepared_checks),
        "prepared_checksums_verified": prepared_checks,
        "saved_ground_truth_matches_prepared_data": label_check,
        "prediction_and_metric_consistency": check,
        "cross_prediction_and_metric_consistency": cross_check,
        "fold_assignment_groups_checked": len(assignment_checks),
        "fold_assignments": assignment_checks,
        "cross_dataset_assignment_groups_checked": len(cross_assignment_checks),
        "cross_dataset_assignments": cross_assignment_checks,
        "cross_dataset_prediction_groups_checked": int(
            cross_predictions.groupby(["source_dataset", "target_dataset", "model"]).ngroups
        ),
        "no_duplicate_scored_row_within_dataset_model": True,
        "cross_dataset_prediction_rows": int(len(cross_predictions)),
        "fold_metric_rows": int(len(fold_metrics)),
        "no_existing_artifact_paths_touched": "Outputs confined to new multi_dataset_evaluation_20261108 directory and new report paths.",
    }


def generate_latex_tables(
    dataset_manifest: dict[str, Any], metrics: pd.DataFrame, cross: pd.DataFrame, run_id: str
) -> list[str]:
    paper_dir = ROOT / "paper" / "multi_dataset_study_20261108"
    tables_dir = paper_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    def model_value(row: pd.Series, key: str) -> str:
        mean = row.get(f"fold_mean_{key}")
        sd = row.get(f"{key}_fold_sd")
        if pd.isna(sd):
            return fmt(mean)
        return f"{fmt(mean)} $\\pm$ {fmt(sd)}"

    characteristics = [
        r"\begin{tabular}{lrrrrl}",
        r"\toprule",
        r"Dataset & $n$ & Predictors & Negative/positive & Missing cells & Task \\",
        r"\midrule",
    ]
    for dataset_id, item in dataset_manifest["datasets"].items():
        negative = item["class_counts"].get("0", 0)
        positive = item["class_counts"].get("1", 0)
        task = item.get("interpretation", "")
        if len(task) > 50:
            task = task[:47] + "..."
        characteristics.append(
            f"{DATASET_LABELS[dataset_id]} & {item['rows']} & "
            f"{item['predictor_count']} & {negative}/{positive} & "
            f"{item['missing_predictor_cells']} & {task} \\\\"
        )
    characteristics.extend([r"\bottomrule", r"\end{tabular}"])
    (tables_dir / "dataset_characteristics.tex").write_text(
        "\n".join(characteristics) + "\n", encoding="utf-8"
    )

    auc_lines = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Dataset & LR & KNN & SVM & RF & OVEC & OSEC \\",
        r"\midrule",
    ]
    for dataset_id in DATASET_LABELS:
        group = metrics[metrics.dataset == dataset_id].set_index("model")
        values = [
            model_value(group.loc[model], "roc_auc") if model in group.index else "--"
            for model in MODEL_ORDER
        ]
        auc_lines.append(DATASET_LABELS[dataset_id] + " & " + " & ".join(values) + r" \\")
    auc_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (tables_dir / "model_auc_matrix.tex").write_text("\n".join(auc_lines) + "\n", encoding="utf-8")

    full_columns = [
        ("accuracy", "Acc."),
        ("precision", "Prec."),
        ("recall", "Sens."),
        ("specificity", "Spec."),
        ("f1", "F1"),
        ("roc_auc", "ROC-AUC"),
        ("pr_auc", "PR-AUC"),
    ]
    cad_ids = {"uci_cleveland", "uci_hungary", "uci_switzerland", "uci_va_long_beach"}
    for name, selected in (
        ("cad_model_metrics.tex", metrics[metrics.dataset.isin(cad_ids)]),
        ("other_task_model_metrics.tex", metrics[~metrics.dataset.isin(cad_ids)]),
    ):
        lines = [
            r"\begin{tabular}{llrrrrrrr}",
            r"\toprule",
            "Dataset & Model & " + " & ".join(label for _, label in full_columns) + r" \\",
            r"\midrule",
        ]
        for _, row in selected.sort_values(["dataset", "model"]).iterrows():
            model = row["model"]
            cells = [model_value(row, key) for key, _ in full_columns]
            lines.append(
                f"{DATASET_LABELS[row['dataset']]} & {MODEL_LABELS[model]} & "
                + " & ".join(cells)
                + r" \\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}"])
        (tables_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    cross_lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Source & Target & Mean AUC & Model range & Domain OOD AUROC & Target alert \\",
        r"\midrule",
    ]
    for (source, target), group in cross.groupby(["source_dataset", "target_dataset"], sort=True):
        aucs = group.target_roc_auc.to_numpy(dtype=float)
        cross_lines.append(
            f"{DATASET_LABELS[source]} & {DATASET_LABELS[target]} & "
            f"{np.mean(aucs):.3f} & {np.min(aucs):.3f}--{np.max(aucs):.3f} & "
            f"{group.target_ood_detection_roc_auc.mean():.3f} & "
            f"{group.target_ood_alert_rate.mean():.3f} \\\\"
        )
    cross_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (tables_dir / "cross_cohort_summary.tex").write_text(
        "\n".join(cross_lines) + "\n", encoding="utf-8"
    )

    meta_lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Dataset & Brier range & Weighted ECE range & Conformal coverage range & Set size range & Joint coverage range \\",
        r"\midrule",
    ]
    selective = pd.read_csv(RESULTS / "metrics" / "selective_prediction_diagnostics.csv")
    for dataset_id, group in metrics.groupby("dataset", sort=False):
        selected = selective[selective.dataset == dataset_id]

        def span(values: pd.Series) -> str:
            return f"{values.min():.3f}--{values.max():.3f}"

        meta_lines.append(
            f"{DATASET_LABELS[dataset_id]} & "
            f"{span(group.pooled_brier)} & {span(group.pooled_ece_weighted_uniform)} & "
            f"{span(group.conformal_coverage_mean)} & {span(group.conformal_set_size_mean)} & "
            f"{span(selected.singleton_plus_ood_accepted_coverage)} \\\\"
        )
    meta_lines.extend([r"\bottomrule", r"\end{tabular}"])
    (tables_dir / "uncertainty_ranges.tex").write_text(
        "\n".join(meta_lines) + "\n", encoding="utf-8"
    )
    (paper_dir / "run_metadata.tex").write_text(
        f"\\newcommand{{\\CARDIODIAGRunID}}{{{run_id}}}\n"
        "\\newcommand{\\CARDIODIAGFigureDir}{figures}\n",
        encoding="utf-8",
    )
    return [
        str((tables_dir / name).relative_to(ROOT)).replace("\\", "/")
        for name in (
            "dataset_characteristics.tex",
            "model_auc_matrix.tex",
            "cad_model_metrics.tex",
            "other_task_model_metrics.tex",
            "cross_cohort_summary.tex",
            "uncertainty_ranges.tex",
        )
    ]


def create_report(
    manifest: dict[str, Any],
    metrics: pd.DataFrame,
    folds: pd.DataFrame,
    cross: pd.DataFrame,
    conformal: pd.DataFrame,
    learning: pd.DataFrame,
    selective: pd.DataFrame,
    failures: pd.DataFrame,
    ood: pd.DataFrame,
    comparison: pd.DataFrame,
    verification: dict[str, Any],
    figure_paths: list[str],
) -> str:
    display = metrics.copy()
    display["dataset"] = display.dataset.map(DATASET_LABELS).fillna(display.dataset)
    display["model"] = display.model.map(MODEL_LABELS).fillna(display.model)
    display["accuracy_display"] = display.apply(
        lambda row: f"{fmt(row.fold_mean_accuracy)} ± {fmt(row.accuracy_fold_sd)}", axis=1
    )
    for key in ("precision", "recall", "specificity", "f1", "roc_auc", "pr_auc"):
        display[f"{key}_display"] = display.apply(
            lambda row,
            metric=key: f"{fmt(row[f'fold_mean_{metric}'])} ± {fmt(row[f'{metric}_fold_sd'])}",
            axis=1,
        )
    main_columns = [
        ("dataset", "Dataset"),
        ("model", "Model"),
        ("n_evaluated", "n"),
        ("accuracy_display", "Accuracy"),
        ("precision_display", "Precision"),
        ("recall_display", "Recall"),
        ("specificity_display", "Specificity"),
        ("f1_display", "F1"),
        ("roc_auc_display", "ROC-AUC"),
        ("pr_auc_display", "PR-AUC"),
    ]
    main_table = md_table(display.sort_values(["dataset", "model"]), main_columns)

    best_rows = []
    for dataset, group in metrics.groupby("dataset", sort=False):
        if group.empty:
            continue
        row = group.sort_values("fold_mean_roc_auc", ascending=False).iloc[0]
        best_rows.append(
            {
                "dataset": DATASET_LABELS.get(dataset, dataset),
                "model": row.model_label,
                "roc_auc": row.fold_mean_roc_auc,
                "roc_auc_sd": row.roc_auc_fold_sd,
                "pr_auc": row.fold_mean_pr_auc,
                "n": row.n_evaluated,
                "protocol": row.split_protocol,
            }
        )
    best_frame = pd.DataFrame(best_rows)
    best_table = md_table(
        best_frame,
        [
            ("dataset", "Dataset"),
            ("model", "Highest observed model"),
            ("n", "n"),
            ("roc_auc", "ROC-AUC mean"),
            ("roc_auc_sd", "Fold SD"),
            ("pr_auc", "PR-AUC mean"),
            ("protocol", "Protocol"),
        ],
    )

    ensemble = (
        metrics[metrics.model.isin(["ovec", "osec"])]
        .pivot(index="dataset", columns="model", values="fold_mean_roc_auc")
        .reset_index()
    )
    ensemble["dataset"] = ensemble.dataset.map(DATASET_LABELS)
    ensemble["delta_ovec_minus_osec"] = ensemble.get("ovec") - ensemble.get("osec")
    ensemble_table = md_table(
        ensemble,
        [
            ("dataset", "Dataset"),
            ("ovec", "OVEC ROC-AUC"),
            ("osec", "OSEC ROC-AUC"),
            ("delta_ovec_minus_osec", "OVEC − OSEC"),
        ],
    )

    trainval = metrics.copy()
    trainval["dataset"] = trainval.dataset.map(DATASET_LABELS)
    trainval["model"] = trainval.model_label
    trainval["train_test_gap"] = trainval.train_minus_outer_test_roc_auc_mean
    trainval["val_test_gap"] = trainval.inner_validation_minus_outer_test_roc_auc_mean
    trainval_table = md_table(
        trainval,
        [
            ("dataset", "Dataset"),
            ("model", "Model"),
            ("train_roc_auc_resubstitution_mean", "Train resub. AUC"),
            ("inner_validation_roc_auc_mean", "Inner CV AUC"),
            ("fold_mean_roc_auc", "Outer/official AUC"),
            ("train_test_gap", "Train − test"),
            ("val_test_gap", "Selected CV − test"),
        ],
    )

    cal = metrics.copy()
    cal["dataset"] = cal.dataset.map(DATASET_LABELS)
    cal["model"] = cal.model_label
    calibration_table = md_table(
        cal,
        [
            ("dataset", "Dataset"),
            ("model", "Model"),
            ("pooled_brier", "Pooled Brier"),
            ("pooled_ece_uniform", "ECE, uniform bins"),
            ("pooled_ece_weighted_uniform", "Weighted ECE"),
            ("conformal_coverage_mean", "Mean conformal coverage"),
            ("conformal_set_size_mean", "Mean set size"),
            ("conformal_singleton_rate_mean", "Singleton rate"),
            ("ood_alert_rate_mean", "OOD alert rate"),
        ],
    )

    transfers = cross.copy()
    transfers["source_dataset"] = transfers.source_dataset.map(DATASET_LABELS)
    transfers["target_dataset"] = transfers.target_dataset.map(DATASET_LABELS)
    transfer_table = md_table(
        transfers.sort_values(["source_dataset", "target_dataset", "model"]),
        [
            ("source_dataset", "Source"),
            ("target_dataset", "Target"),
            ("model_label", "Model"),
            ("target_rows", "Target n"),
            ("target_roc_auc", "ROC-AUC"),
            ("target_pr_auc", "PR-AUC"),
            ("target_roc_auc_ci_low", "ROC-AUC CI low"),
            ("target_roc_auc_ci_high", "ROC-AUC CI high"),
            ("target_ood_alert_rate", "OOD alert rate"),
            ("target_ood_detection_roc_auc", "Domain OOD AUROC"),
        ],
    )

    conformal_summary = conformal.groupby(["dataset", "model"], as_index=False).agg(
        coverage=("empirical_coverage", "mean"),
        set_size=("average_set_size", "mean"),
        singleton=("singleton_rate", "mean"),
    )
    conformal_summary["dataset"] = conformal_summary.dataset.map(DATASET_LABELS)
    conformal_summary["model"] = conformal_summary.model.map(MODEL_LABELS)
    conformal_table = md_table(
        conformal_summary,
        [
            ("dataset", "Dataset"),
            ("model", "Model"),
            ("coverage", "Empirical coverage"),
            ("set_size", "Average set size"),
            ("singleton", "Singleton fraction"),
        ],
    )

    ood_display = ood.copy()
    ood_display["dataset"] = ood_display.dataset.map(DATASET_LABELS)
    ood_display["model"] = ood_display.model.map(MODEL_LABELS)
    ood_table = md_table(
        ood_display,
        [
            ("dataset", "Dataset"),
            ("model", "Model"),
            ("ood_alert_rate", "Alert rate"),
            ("error_rate_all", "Overall error rate"),
            ("error_rate_alerted", "Error rate if alerted"),
            ("error_rate_unflagged", "Error rate if unflagged"),
            ("error_alert_sensitivity", "Error capture"),
            ("ood_error_discrimination_auc", "OOD score / error AUROC"),
        ],
    )

    selective_display = pd.read_csv(RESULTS / "metrics" / "selective_prediction_diagnostics.csv")
    selective_display["dataset"] = selective_display.dataset.map(DATASET_LABELS)
    selective_display["model"] = selective_display.model.map(MODEL_LABELS)
    selective_table = md_table(
        selective_display,
        [
            ("dataset", "Dataset"),
            ("model", "Model"),
            ("confidence_aurc", "Confidence AURC"),
            ("confidence_risk_at_80pct_coverage", "Risk at 80% coverage"),
            ("singleton_plus_ood_accepted_n", "Singleton + OOD accepted n"),
            ("singleton_plus_ood_accepted_coverage", "Accepted coverage"),
            ("singleton_plus_ood_error_rate", "Accepted error rate"),
        ],
    )

    compat = comparison[
        [
            "dataset_name",
            "records",
            "predictors",
            "target_definition",
            "class_counts",
            "missing_predictor_cells",
            "license",
            "lineage_and_compatibility",
            "decision",
            "status",
        ]
    ].copy()
    compat_table = md_table(
        compat,
        [
            ("dataset_name", "Dataset"),
            ("records", "Records"),
            ("predictors", "Predictors"),
            ("target_definition", "Target / task"),
            ("class_counts", "Class counts"),
            ("missing_predictor_cells", "Missing cells"),
            ("license", "License/access"),
            ("lineage_and_compatibility", "Lineage and compatibility"),
            ("decision", "Decision"),
            ("status", "Status"),
        ],
    )

    failure_table = (
        "No failed experiment rows were recorded."
        if failures.empty
        else md_table(
            failures.fillna("—"),
            [
                ("dataset", "Dataset / transfer"),
                ("model", "Model"),
                ("stage", "Stage"),
                ("error_type", "Failure"),
                ("reason", "Reason"),
            ],
        )
    )
    figures_md = "\n".join(f"- `{path}`" for path in figure_paths)
    run_id = manifest["run_id"]
    succeeded = len(metrics)
    failed = len(failures)
    n_transfer = len(cross)
    n_tasks = metrics.dataset.nunique()
    return f"""# CARDIODIAG Multi-Dataset Experimental Evaluation Report

- **Run:** `{manifest["experiment_id"]}` / `{run_id}`
- **Status:** `{manifest["status"]}`
- **Generated:** `{manifest["generated_at_utc"]}`
- **Branch:** `{manifest["git"]["branch"]}`
**Evaluation scope:** {n_tasks} task datasets, {succeeded} successful dataset–model summaries, {n_transfer} directed CAD cohort transfer results, {failed} recorded failure rows.

## Executive summary

This report presents new, isolated experiments using the existing CARDIODIAG training-only preprocessing and unchanged OVEC/OSEC definitions. Four UCI angiographic cohorts were evaluated separately; each was already represented in the project’s Heart5 lineage, so these are retrospective cohort stress tests rather than independent validation. Heart-failure death, myocardial-infarction lethal outcome, and SPECT imaging normal/abnormal were kept as separate tasks and were not pooled or described as CAD validation.

Nested 3-fold outer / 3-fold inner evaluation was used where supported. SPECTF retained its official 80-record training and 187-record test split. Reported “best observed” models are descriptive maxima from this comparison; no superiority or clinical-use claim follows from those rankings. The uncertainty analysis is exploratory because cohorts are small, outcome definitions differ, and the class-stratified bootstrap conditions on observed class counts.

## Research objectives

1. Compare Logistic Regression, K-Nearest Neighbors, Support Vector Machine, Random Forest, OVEC, and OSEC under training-only preprocessing.
2. Measure discrimination, thresholded classification, calibration, conformal coverage, selective risk, learning behavior, and feature-support OOD diagnostics.
3. Test source-only transfer among the four feature-compatible angiographic cohorts without tuning on target labels.
4. Record provenance, cohort overlap screening, failed runs, and reproducibility metadata.

## Repository and methodology inspection

The repository’s established architecture includes `build_corrected_pipeline`, the fold-fitted `TrainingOnlyCleaner`, numeric median imputation/scaling, categorical most-frequent imputation/one-hot encoding, and pre-existing `build_ovec` / `build_osec` implementations. This experiment adds individual baseline builders while reusing the ensemble definitions. No feature-selection stage was added to this experiment because the established corrected pipeline used here does not require a selector. No SMOTE or pre-split balancing was applied. Existing historical result files and manuscript tables were left in place; all new outputs are under `results/multi_dataset_evaluation_20261108/` and this new report path.

OVEC uses the project’s existing soft-voting estimator with KNN, Random Forest, balanced Logistic Regression, and balanced SVC constituents. OSEC uses the existing stacking architecture and meta-classifier. The implementation and exact estimator definitions remain in `src/cardiodiag/models.py` and `src/cardiodiag/experiments.py`.

## Dataset descriptions, provenance, and compatibility

The four CAD tasks share the UCI Heart Disease 13-predictor schema and binary endpoint (`num=0` versus `num=1..4`, described by UCI as disease presence at greater than 50% diameter narrowing). Question marks were treated as missing; zero resting blood pressure and cholesterol were also treated as missing under the repository’s earlier protocol. Exact feature-row comparisons found no pairwise duplicates among the four prepared cohorts. This is only a record-matching screen: no participant identifiers establish person-level independence. The source cohorts are known components of the previously evaluated Heart5 composite.

SPECTF has 44 SPECT-derived predictors and a separate normal/abnormal imaging endpoint. It is not feature-compatible with the clinical CAD cohorts. Its source-defined training/test split was preserved; the test partition has 172 positive-coded and 15 negative-coded records, which makes operating characteristics and uncertainty estimates especially sensitive to a small minority count.

Heart Failure Clinical Records includes follow-up time in the source table; time was excluded from predictors and the event of death was used as the outcome. The cohort has varying follow-up horizons. MI Complications uses admission-available variables only; identifiers, post-admission features, and outcome proxies were excluded under the source timing audit. Its endpoint is any lethal complication. Neither is a CAD endpoint.

UCI sources: [Heart Disease (ID 45)](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease), [SPECTF Heart (ID 96)](https://archive.ics.uci.edu/dataset/96/spectf%2Bheart), [Heart Failure Clinical Records (ID 519)](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords), and [Myocardial Infarction Complications (ID 579)](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications). Their UCI dataset pages state CC BY 4.0; attribution is retained in the manifest. Dataset screening decisions are summarized below and fully represented in `dataset_comparison.csv`.

{compat_table}

Statlog Heart was excluded because the project’s exact matching audit found all 270 harmonized records match Cleveland. Previously evaluated Mendeley, Z-Alizadeh Sani, AngioCAD, and Duke ACATH data were excluded from this new run to prevent post-hoc reuse from being presented as fresh evidence; their endpoint, provenance, measurement, or rights limits remain in prior project audits. The Kaggle 70K task has a distinct target and unresolved license. MIMIC-IV and MultiD4CAD require access steps or agreements not acquired for this run.

## Experimental design and preprocessing

For each supported task, the outer split is stratified 3-fold cross-validation (seed `{manifest["protocol"]["seed"]}`). Within each outer training partition, 20% was held out for conformal and OOD threshold calibration. Hyperparameter selection used stratified 3-fold CV only on the remaining development rows. The untouched outer fold was scored once. The candidate grids and selected settings by fold are in `metrics/fold_metrics.csv` and `model_metrics.csv`.

Imputation, scaling, category encoding, and the established 1st/99th percentile training-only median replacement were fitted inside each pipeline. The held-out fold did not inform preprocessing, tuning, calibration, or thresholds. Cross-cohort experiments used source-only training, source-only inner CV, and source calibration; target features and labels were not used for selection. All 12 ordered source-to-target directions among the four compatible CAD cohorts were attempted for each model. These cohorts have matching feature schema and endpoint coding, but their known Heart5 lineage means the transfers are not independent external validations.

The individual baseline grids were Logistic Regression C ∈ {{0.1, 1, 10}}, KNN k ∈ {{3, 5, 7}} with uniform/distance weighting, SVM C ∈ {{0.1, 1, 10}} with linear/RBF kernels, and Random Forest with square-root/all-feature subsampling and leaf size 1/3. OVEC’s project configuration was fixed; OSEC’s existing final-estimator regularization parameter was selected from C ∈ {{0.1, 1, 10}}. See the experiment manifest for software versions and hashes.

## Main model comparison

The table reports the mean across outer folds and fold standard deviation. For SPECTF, the value comes from one official held-out test partition; no fold SD exists. Full fold-level results and confusion-matrix counts are in the machine-readable files.

{main_table}

### Highest observed ROC-AUC by task

{best_table}

These are descriptive rankings on the evaluated partitions. They do not establish that an ensemble is better than an individual model, and they are not evidence of clinical utility.

## OVEC versus OSEC

{ensemble_table}

The sign of `OVEC − OSEC` varies by task where both estimates exist. Differences are small-sample, descriptive comparisons, not significance tests. If an entry is missing, the corresponding model did not complete and appears in the failure table.

## Overfitting and learning behavior

Training resubstitution scores are measured on the development subset used to fit the selected pipeline; selected inner-CV scores are tuning-stage validation estimates; outer-test scores are the held-out estimates. The differences are diagnostic and not independent comparisons. A positive train–test gap alone does not prove overfitting. The 3-fold learning curves use fixed default estimators and are descriptive, not part of hyperparameter selection.

{trainval_table}

Learning curves are saved as vector PDF and PNG and as the per-size CSV in `metrics/learning_curve_metrics.csv`. They can reveal high training / lower validation performance or data-limited behavior, but the small cohorts do not support strong asymptotic learning claims.

## Calibration and uncertainty

Brier score and two ten-bin ECE variants are computed from pooled held-out predictions. “Uniform” ECE denotes equal-width probability bins; weighted ECE weights occupied bins by their sample share. Calibration bins are included in `metrics/calibration_bins.csv`.

Split-conformal prediction uses nonconformity `1 − p(true class)` and a finite-sample 90% threshold from the held-out calibration partition in each outer fold. Coverage and set size are reported as empirical values. Exchangeability between calibration and evaluation data is an assumption; it is not assured across sites or time.

{calibration_table}

{conformal_table}

## Selective prediction and OOD diagnostics

Confidence-ranked risk–coverage curves retain the most confident predictions at each coverage level. The OOD score is mean distance to the five nearest development observations after the fitted feature transformation; its alert cutoff is the 95th percentile of source calibration scores. This is a simple feature-support diagnostic. It is not a validated shift detector or safety gate. Within-task alert/error associations and source-to-target domain discrimination are summarized below and in `metrics/ood_diagnostics.csv` / `cross_dataset_metrics.csv`.

{ood_table}

Combined singleton-conformal and in-support accepted predictions are also reported:

{selective_table}

The alert rate is determined without target labels, while error capture and error rates use labels only for retrospective scoring. Small or zero accepted groups should not be interpreted as a safe operating point. All risk–coverage coordinates are in `metrics/selective_prediction_metrics.csv`.

## Cross-dataset evaluation

The following table shows each directed transfer. Selection, preprocessing, and calibration were source-only; target labels were used only to calculate final metrics. The class-stratified percentile intervals use 1,000 bootstrap replicates over target predictions and condition on observed class counts. Because observations come from small, historical source files and patient linkage cannot be checked, intervals are descriptive rather than population-level uncertainty estimates. No p-values or fold-level significance claims are made.

{transfer_table}

The heatmaps display target ROC-AUC by source, target, and model. OOD heatmaps display mean model results for the source-versus-target feature-score discrimination AUROC and target alert rate. A high domain-detection AUROC indicates score separation in these samples; a low AUROC does not prove absence of clinically relevant shift.

## Figures

{figures_md}

Every figure is created from the saved metric, fold, or prediction tables in this run. The prediction files contain row-level labels and outputs and are intentionally local / gitignored; aggregate tables and figures are release artifacts. The experiment manifest links predictions, assignments, checksums, model configurations, software versions, and logs.

## Failed experiments and exclusions

{failure_table}

Any failure caused by class counts or a fixed ensemble internal-CV requirement is reported as a failure rather than silently omitted. Switzerland contains only 8 negative examples; therefore three-fold validation is technically possible but estimates are highly unstable, and stack fitting may fail for an inner split. Dataset incompatibilities and access exclusions are recorded in the compatibility table.

An initial execution attempt (`20261107T202151Z`) was stopped after the learning-curve score array was indexed along the wrong axis. Its partial checkpoints and execution log remain under the ignored experiment directory for audit; they were excluded from all reported metrics. The corrected complete run is `{run_id}`. The six failures above are from the completed run and are the Switzerland learning-curve configurations.

## Main findings and conclusions

- The four UCI CAD cohorts can be evaluated separately with the same feature schema and coded endpoint, but this run cannot establish independent external validation because they overlap historically with Heart5 and do not contain participant linkage keys.
- No model should be declared generally superior from the observed rankings. OVEC and OSEC performance varies by task and the sample sizes limit precision.
- SPECTF, heart-failure mortality, and MI lethal outcomes provide additional model-behavior experiments but answer different prediction questions and must remain separate from CAD claims.
- Training–validation gaps, calibration, conformal sets, selective risk, and OOD alerts provide complementary diagnostics. None establishes deployment safety, prospective benefit, or clinical readiness.
- The strongest next scientific step is a pre-registered evaluation on a genuinely independent, endpoint-aligned clinical cohort with documented prediction time, participant-level identifiers or overlap controls, and a fixed operating protocol. Secure-access data require approved access and governance.

## Limitations

1. Small and historical public cohorts, substantial missingness in some sites, and severe class imbalance in Switzerland and SPECTF.
2. Patient-level independence cannot be verified. Exact-row scans find no cross-cohort duplicates among the four UCI prepared tables, but they cannot detect transformed or near-duplicate participants.
3. The UCI datasets have historical clinical workflows and do not establish the intended prospective prediction time. UCI endpoint documentation is not enough to infer deployment suitability.
4. Heart-failure follow-up is not a uniform horizon; MI mortality labels concern a separate clinical stage; SPECTF is an imaging endpoint.
5. Bootstrap intervals condition on the observed target case mix and do not model site sampling or between-site variation.
6. OOD alert thresholds and selective diagnostics are experimental, not safety-certified. Conformal guarantees rely on exchangeability.
7. No external clinical deployment, prospective study, fairness analysis, or clinician-reviewed utility evaluation was performed.

## Reproducibility and verification

Run from the repository root in the project Python environment:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path 'src')
python experiments/prepare_multi_dataset_evaluation.py
python experiments/run_multi_dataset_evaluation.py
python experiments/finalize_multi_dataset_evaluation.py
```

The raw datasets are not included in the public repository; they must be acquired from the cited UCI pages and their archive hashes must match `datasets/dataset_manifest.json`. Row-level predictions and fold assignments are local ignored files because they contain record-level output. Aggregate results, code, and figures are versionable. Python, NumPy, pandas, scikit-learn, and SciPy versions are stored in `manifests/experiment_manifest.json`.

Verification status: **{verification["status"]}**. Source archive entries verified: {verification["source_checksum_count"]}; prepared-file checksums verified: {verification["prepared_checksum_count"]}. Ground-truth labels match the prepared files for {verification["saved_ground_truth_matches_prepared_data"]["within_task_label_groups"]} within-task and {verification["saved_ground_truth_matches_prepared_data"]["cross_task_label_groups"]} transfer groups. Pooled metrics were recomputed for {verification["prediction_and_metric_consistency"]["prediction_group_count"]} within-task groups and {verification["cross_prediction_and_metric_consistency"]["prediction_group_count"]} transfer groups. Fold-assignment groups checked: {verification["fold_assignment_groups_checked"]}. No previously existing experiment paths were written.

## Exact deliverables

- Dataset compatibility table: `results/multi_dataset_evaluation_20261108/dataset_comparison.csv`.
- Dataset provenance and checksum manifest: `results/multi_dataset_evaluation_20261108/datasets/dataset_manifest.json`.
- Model, fold, transfer, calibration, conformal, learning-curve, selective-risk, OOD, and failure tables: `results/multi_dataset_evaluation_20261108/metrics/`.
- Fold-level predictions and assignments: `results/multi_dataset_evaluation_20261108/predictions/{run_id}/` (local, gitignored).
- Per-experiment checkpoints: `results/multi_dataset_evaluation_20261108/experiments/{run_id}/` (local, gitignored).
- Experiment logs and manifest: `results/multi_dataset_evaluation_20261108/logs/` and `results/multi_dataset_evaluation_20261108/manifests/`.
- Figure pack: `results/multi_dataset_evaluation_20261108/figures/{run_id}/`.
- This report: `docs/MULTI_DATASET_EXPERIMENTAL_EVALUATION_REPORT.md` and `results/multi_dataset_evaluation_20261108/reports/`.
"""


def main() -> None:
    manifest = json.loads(
        (RESULTS / "manifests" / "experiment_manifest.json").read_text(encoding="utf-8")
    )
    run_id = manifest["run_id"]
    prediction_path = RESULTS / "predictions" / run_id / "out_of_fold_and_official_predictions.csv"
    cross_prediction_path = RESULTS / "predictions" / run_id / "cross_dataset_predictions.csv"
    predictions = pd.read_csv(prediction_path)
    cross_predictions = pd.read_csv(cross_prediction_path)
    metrics = pd.read_csv(RESULTS / "metrics" / "model_metrics.csv")
    folds = pd.read_csv(RESULTS / "metrics" / "fold_metrics.csv")
    cross = pd.read_csv(RESULTS / "metrics" / "cross_dataset_metrics.csv")
    conformal = pd.read_csv(RESULTS / "metrics" / "conformal_metrics.csv")
    learning = pd.read_csv(RESULTS / "metrics" / "learning_curve_metrics.csv")
    selective = pd.read_csv(RESULTS / "metrics" / "selective_prediction_metrics.csv")
    failures_path = RESULTS / "metrics" / "failed_experiments.csv"
    failures = pd.read_csv(failures_path) if failures_path.stat().st_size else pd.DataFrame()
    pd.DataFrame(
        [
            {
                "run_id": "20261107T202151Z",
                "status": "aborted_incomplete",
                "included_in_final_metrics": False,
                "reason": (
                    "Stopped after detecting incorrect learning-curve score-array indexing; "
                    "partial results excluded."
                ),
                "log": "results/multi_dataset_evaluation_20261108/logs/run_20261107T202151Z.log",
            },
            {
                "run_id": run_id,
                "status": manifest["status"],
                "included_in_final_metrics": True,
                "reason": (
                    "Complete corrected evaluation; six Switzerland learning curves failed "
                    "because the smallest training subset contained one class."
                ),
                "log": manifest["artifacts"]["log"],
            },
        ]
    ).to_csv(RESULTS / "metrics" / "execution_attempts.csv", index=False)
    dataset_manifest = json.loads(
        (RESULTS / "datasets" / "dataset_manifest.json").read_text(encoding="utf-8")
    )
    comparison = dataset_comparison(dataset_manifest)
    comparison_path = RESULTS / "dataset_comparison.csv"
    comparison.to_csv(comparison_path, index=False)
    ood = make_ood_diagnostics(predictions)
    ood.to_csv(RESULTS / "metrics" / "ood_diagnostics.csv", index=False)
    selective_diagnostics = make_selective_diagnostics(predictions, selective)
    selective_diagnostics.to_csv(
        RESULTS / "metrics" / "selective_prediction_diagnostics.csv", index=False
    )
    manuscript_tables = generate_latex_tables(dataset_manifest, metrics, cross, run_id)
    verification = verify_artifacts(
        dataset_manifest, predictions, cross_predictions, metrics, folds, cross
    )
    (RESULTS / "manifests" / "verification_manifest.json").write_text(
        json.dumps(verification, indent=2) + "\n", encoding="utf-8"
    )
    figure_dir = RESULTS / "figures" / run_id
    figure_paths = []
    figure_paths.extend(plot_roc_pr(predictions, figure_dir))
    figure_paths.extend(plot_precision_recall(predictions, figure_dir))
    figure_paths.extend(plot_confusion(predictions, figure_dir))
    figure_paths.extend(plot_performance(metrics, figure_dir))
    figure_paths.extend(plot_gaps(metrics, figure_dir))
    figure_paths.extend(plot_learning_curves(learning, figure_dir))
    figure_paths.extend(
        plot_calibration(pd.read_csv(RESULTS / "metrics" / "calibration_bins.csv"), figure_dir)
    )
    figure_paths.extend(plot_risk_coverage(selective, figure_dir))
    figure_paths.extend(plot_cross_heatmaps(cross, figure_dir))
    figure_paths.extend(plot_cross_mean_auc_heatmap(cross, figure_dir))
    paper_figure_dir = ROOT / "paper" / "multi_dataset_study_20261108" / "figures"
    paper_figure_dir.mkdir(parents=True, exist_ok=True)
    for figure_name in (
        "model_performance_comparison.pdf",
        "calibration_curves.pdf",
        "cross_dataset_mean_auc_heatmap.pdf",
    ):
        shutil.copy2(figure_dir / figure_name, paper_figure_dir / figure_name)
    (figure_dir / "figure_manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "figures": figure_paths,
                "manuscript_tables": manuscript_tables,
                "source_metrics": sorted(
                    str(path.relative_to(ROOT)) for path in (RESULTS / "metrics").glob("*.csv")
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report = create_report(
        manifest,
        metrics,
        folds,
        cross,
        conformal,
        learning,
        selective,
        failures,
        ood,
        comparison,
        verification,
        figure_paths,
    )
    DOC_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DOC_REPORT.write_text(report, encoding="utf-8")
    report_copy = RESULTS / "reports" / "MULTI_DATASET_EXPERIMENTAL_EVALUATION_REPORT.md"
    report_copy.write_text(report, encoding="utf-8")
    print(f"Wrote report: {DOC_REPORT}")
    print(f"Wrote report copy: {report_copy}")
    print(f"Wrote {len(figure_paths)} figure files under: {figure_dir}")
    print(
        f"Verified {verification['prediction_and_metric_consistency']['prediction_group_count']} metric groups."
    )


if __name__ == "__main__":
    main()
