# ruff: noqa: E501
"""Publish the duplicate-safe sensitivity through tables, reports, and a paper copy.

The frozen experiment remains unchanged. This script adds exact-row deduplication
results, explicit boundary-leakage evidence, descriptive EDA tables, and a versioned
manuscript source bundle. It never writes row-level outputs to tracked locations.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_research_20261108"
MET = OUT / "metrics"
TAB = OUT / "tables"
FIG = OUT / "figures"
DOC = ROOT / "docs"
BASE_PAPER = ROOT / "paper" / "multi_dataset_study_20261108"
PAPER = ROOT / "paper" / "multi_dataset_study_20261108_dedup_safe"
DATA = ROOT / "data" / "processed" / "multi_dataset_evaluation_20261108"
DISPLAY = {
    "uci_cleveland": "UCI Cleveland",
    "uci_hungary": "UCI Hungary",
    "uci_switzerland": "UCI Switzerland",
    "uci_va_long_beach": "UCI VA Long Beach",
    "uci_heart_failure_519": "UCI Heart Failure",
    "uci_mi_complications_579": "UCI MI Complications",
    "uci_spectf_heart": "UCI SPECTF Heart",
}
MODEL_LABELS = {
    "logistic": "Logistic Regression",
    "knn": "K-Nearest Neighbors",
    "svm": "Support Vector Machine",
    "random_forest": "Random Forest",
    "ovec": "OVEC",
    "osec": "OSEC",
}
MODEL_ORDER = list(MODEL_LABELS)
MODEL_SHORT = {
    "logistic": "LR",
    "knn": "KNN",
    "svm": "SVM",
    "random_forest": "RF",
    "ovec": "OVEC",
    "osec": "OSEC",
}
CAD = ["uci_cleveland", "uci_hungary", "uci_switzerland", "uci_va_long_beach"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def fmt(value: float, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def pooled_metrics(group: pd.DataFrame) -> dict[str, float | int | None]:
    y = group.y_true.astype(int).to_numpy()
    prob = group.probability_positive.astype(float).to_numpy()
    predicted = (prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    edges = np.linspace(0.0, 1.0, 11)
    bin_ids = np.minimum(np.digitize(prob, edges[1:-1], right=False), 9)
    calibration_errors = []
    for bin_id in range(10):
        selected = bin_ids == bin_id
        if selected.any():
            calibration_errors.append(
                (
                    int(selected.sum()),
                    abs(float(y[selected].mean()) - float(prob[selected].mean())),
                )
            )
    ece_macro = (
        float(np.mean([error for _, error in calibration_errors])) if calibration_errors else 0.0
    )
    ece_weighted = (
        float(sum(count * error for count, error in calibration_errors) / len(y)) if len(y) else 0.0
    )
    return {
        "n_evaluated": int(len(y)),
        "positive_count": int(y.sum()),
        "prevalence": float(y.mean()) if len(y) else None,
        "pooled_accuracy": float(accuracy_score(y, predicted)),
        "pooled_balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "pooled_precision": float(precision_score(y, predicted, zero_division=0)),
        "pooled_recall": float(recall_score(y, predicted, zero_division=0)),
        "pooled_specificity": float(tn / (tn + fp)) if tn + fp else None,
        "pooled_f1": float(f1_score(y, predicted, zero_division=0)),
        "pooled_roc_auc": float(roc_auc_score(y, prob)) if np.unique(y).size == 2 else None,
        "pooled_pr_auc": float(average_precision_score(y, prob)) if y.sum() else None,
        "pooled_brier": float(brier_score_loss(y, prob)),
        "pooled_ece_uniform": ece_macro,
        "pooled_ece_weighted_uniform": ece_weighted,
        "pooled_mcc": float(matthews_corrcoef(y, predicted))
        if np.unique(predicted).size > 1
        else 0.0,
        "pooled_cohen_kappa": float(cohen_kappa_score(y, predicted)),
        "pooled_false_positive_rate": float(fp / (fp + tn)) if fp + tn else None,
        "pooled_false_negative_rate": float(fn / (fn + tp)) if fn + tp else None,
        "pooled_tn": int(tn),
        "pooled_fp": int(fp),
        "pooled_fn": int(fn),
        "pooled_tp": int(tp),
    }


def replace_section(path: Path, heading: str, body: str) -> None:
    start = "<!-- " + heading + " START -->"
    end = "<!-- " + heading + " END -->"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = f"{start}\n{body.strip()}\n{end}\n"
    if start in old and end in old:
        before, remainder = old.split(start, 1)
        _, after = remainder.split(end, 1)
        new = before.rstrip() + "\n\n" + block + after.lstrip("\n")
    else:
        new = old.rstrip() + "\n\n" + block
    path.write_text(new, encoding="utf-8")


def insert_after_title(path: Path, heading: str, body: str) -> None:
    start = "<!-- " + heading + " START -->"
    end = "<!-- " + heading + " END -->"
    old = path.read_text(encoding="utf-8")
    block = f"{start}\n{body.strip()}\n{end}\n"
    if start in old and end in old:
        before, remainder = old.split(start, 1)
        _, after = remainder.split(end, 1)
        old = before.rstrip() + "\n" + after.lstrip("\n")
    lines = old.splitlines()
    new = lines[0] + "\n\n" + block + "\n" + "\n".join(lines[1:]).lstrip("\n")
    path.write_text(new.rstrip() + "\n", encoding="utf-8")


def build_descriptive_data_tables() -> dict[str, pd.DataFrame]:
    manifest_path = (
        ROOT
        / "results"
        / "multi_dataset_evaluation_20261108"
        / "datasets"
        / "dataset_manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    numeric_rows, categorical_rows, corr_rows, leakage_rows = [], [], [], []
    dedup_class_rows = []
    for dataset, entry in manifest["datasets"].items():
        spec = entry
        prepared = spec.get("prepared_path") or spec.get("source", {}).get("prepared_path")
        if not prepared:
            prepared = spec.get(
                "prepared_paths", spec.get("source", {}).get("prepared_paths", {})
            ).get("all")
        data_path = ROOT / prepared if prepared else DATA / f"{dataset}.csv"
        if dataset == "uci_spectf_heart":
            data_path = DATA / "uci_spectf_all.csv"
        frame = pd.read_csv(data_path)
        target = spec.get("target", "OVERALL_DIAGNOSIS")
        categorical = set(spec.get("categorical_features", []))
        predictors = frame.drop(columns=[target], errors="ignore")
        if target in predictors.columns:
            raise AssertionError(f"Target is present among predictors for {dataset}")
        if dataset in CAD:
            keep = ~predictors.duplicated(keep="first")
            clean_y = frame.loc[keep, target].astype(int)
            for label in (0, 1):
                count = int(clean_y.eq(label).sum())
                dedup_class_rows.append(
                    {
                        "dataset_id": dataset,
                        "dataset": DISPLAY[dataset],
                        "partition": "deduplicated_sensitivity",
                        "class_label": label,
                        "count": count,
                        "prevalence": float(count / len(clean_y)) if len(clean_y) else None,
                        "n": len(clean_y),
                    }
                )
        for feature in predictors.columns:
            series = predictors[feature]
            observed = series.dropna()
            if feature in categorical or not pd.api.types.is_numeric_dtype(series):
                counts = series.value_counts(dropna=False)
                for value, count in counts.items():
                    categorical_rows.append(
                        {
                            "dataset_id": dataset,
                            "feature": feature,
                            "value": "<missing>" if pd.isna(value) else str(value),
                            "count": int(count),
                            "fraction": float(count / len(series)) if len(series) else None,
                        }
                    )
                continue
            numeric = pd.to_numeric(observed, errors="coerce").dropna()
            if numeric.empty:
                continue
            numeric_rows.append(
                {
                    "dataset_id": dataset,
                    "feature": feature,
                    "n_observed": int(numeric.size),
                    "missing_count": int(series.isna().sum()),
                    "mean": float(numeric.mean()),
                    "std": float(numeric.std(ddof=1)) if len(numeric) > 1 else 0.0,
                    "min": float(numeric.min()),
                    "q25": float(numeric.quantile(0.25)),
                    "median": float(numeric.median()),
                    "q75": float(numeric.quantile(0.75)),
                    "max": float(numeric.max()),
                    "skew": float(numeric.skew()) if len(numeric) > 2 else None,
                }
            )
        numeric_features = [
            col
            for col in predictors.select_dtypes(include=np.number).columns
            if col not in categorical
        ]
        if len(numeric_features) > 1:
            corr = predictors[numeric_features].corr(method="spearman")
            for i, a in enumerate(numeric_features):
                for b in numeric_features[i + 1 :]:
                    rho = corr.loc[a, b]
                    if pd.notna(rho) and abs(float(rho)) >= 0.8:
                        corr_rows.append(
                            {
                                "dataset_id": dataset,
                                "feature_a": a,
                                "feature_b": b,
                                "spearman_rho": float(rho),
                                "absolute_rho": abs(float(rho)),
                                "threshold": 0.8,
                                "interpretation": "descriptive pairwise rank correlation; not a VIF or causal analysis",
                            }
                        )
        leakage_rows.append(
            {
                "dataset_id": dataset,
                "audit_type": "target_as_predictor",
                "finding": "target excluded from predictor matrix in the recorded loader manifest",
                "evidence": f"{manifest_path.relative_to(ROOT).as_posix()} and fold-local model pipeline",
                "limitation": "cannot verify undocumented source measurement timing or hidden identifiers from public tables",
            }
        )
    numeric_df = pd.DataFrame(numeric_rows)
    categorical_df = pd.DataFrame(categorical_rows)
    corr_df = (
        pd.DataFrame(corr_rows).sort_values(["dataset_id", "absolute_rho"], ascending=[True, False])
        if corr_rows
        else pd.DataFrame(
            columns=[
                "dataset_id",
                "feature_a",
                "feature_b",
                "spearman_rho",
                "absolute_rho",
                "threshold",
                "interpretation",
            ]
        )
    )
    duplicate = pd.read_csv(OUT / "duplicate_audit.csv")
    partitions = pd.read_csv(OUT / "duplicate_partition_audit.csv")
    for _, group in duplicate.iterrows():
        if group["dataset"] not in CAD:
            continue
        part = partitions[
            partitions.duplicate_group_id.eq(group.group_id) & partitions.dataset.eq(group.dataset)
        ]
        crosses_test = (
            bool(part.crossed_development_and_outer_test.astype(bool).any())
            if not part.empty
            else False
        )
        crosses_calibration_test = (
            bool(part.crossed_calibration_and_outer_test.astype(bool).any())
            if not part.empty
            else False
        )
        leakage_rows.append(
            {
                "dataset_id": group["dataset"],
                "audit_type": "exact_predictor_duplicate_partition_boundary",
                "finding": f"rows {group.original_row_indices} have identical predictors and label {int(group.label)}; {int(group.duplicate_rows_removed)} duplicate row removed before sensitivity splits",
                "evidence": "results/final_research_20261108/duplicate_audit.csv; boundary rows in duplicate_partition_audit.csv",
                "limitation": f"development/outer-test crossing={crosses_test}; calibration/outer-test crossing={crosses_calibration_test}; no patient ID exists to audit non-identical same-person records",
            }
        )
    leakage_rows.extend(
        [
            {
                "dataset_id": "four UCI CAD cohorts",
                "audit_type": "cross_cohort_person_overlap",
                "finding": "no exact predictor-row matches in the recorded pairwise screen",
                "evidence": "results/final_research_20261108/dataset_duplicate_report.csv",
                "limitation": "cohorts appear in Heart5 lineage; exact matching cannot detect transformed/near duplicates and no person-level key is available",
            },
            {
                "dataset_id": "heart failure and MI tasks",
                "audit_type": "outcome_timing",
                "finding": "target columns were excluded from predictor matrices; endpoint definitions are death event and lethal complication",
                "evidence": "dataset manifest target and predictor schemas",
                "limitation": "public records do not establish a prospective index time or all predictor timestamps; post-outcome feature leakage cannot be ruled out from files alone",
            },
        ]
    )
    class_path = OUT / "dataset_class_distribution.csv"
    class_frame = pd.read_csv(class_path)
    class_frame = class_frame[~class_frame.partition.eq("deduplicated_sensitivity")]
    class_frame = pd.concat([class_frame, pd.DataFrame(dedup_class_rows)], ignore_index=True)
    write_csv(class_frame, class_path)
    inventory_path = OUT / "dataset_inventory.csv"
    inventory = pd.read_csv(inventory_path)
    sizes = {row["dataset_id"]: row["n"] for row in dedup_class_rows if row["class_label"] == 0}
    inventory["deduplicated_sensitivity_n"] = inventory.dataset_id.map(sizes)
    inventory.to_csv(inventory_path, index=False)
    write_csv(numeric_df, OUT / "feature_distribution_summary.csv")
    write_csv(categorical_df, OUT / "categorical_value_distribution.csv")
    write_csv(corr_df, OUT / "feature_correlation_pairs.csv")
    write_csv(pd.DataFrame(leakage_rows), OUT / "leakage_audit.csv")
    return {
        "numeric": numeric_df,
        "categorical": categorical_df,
        "correlations": corr_df,
        "leakage": pd.DataFrame(leakage_rows),
    }


def build_metrics_and_figures() -> dict[str, pd.DataFrame]:
    mapping = {
        "duplicate_safe_within_model_metrics.csv": "duplicate_safe_within_model_metrics.csv",
        "duplicate_safe_within_fold_metrics.csv": "duplicate_safe_within_fold_metrics.csv",
        "duplicate_safe_conformal_metrics.csv": "duplicate_safe_conformal_metrics.csv",
        "duplicate_safe_cross_dataset_metrics.csv": "duplicate_safe_cross_dataset_metrics.csv",
    }
    for source, destination in mapping.items():
        shutil.copy2(OUT / source, MET / destination)
    within = pd.read_csv(MET / mapping["duplicate_safe_within_model_metrics.csv"])
    folds = pd.read_csv(MET / mapping["duplicate_safe_within_fold_metrics.csv"])
    cross = pd.read_csv(MET / mapping["duplicate_safe_cross_dataset_metrics.csv"])
    conf = pd.read_csv(MET / mapping["duplicate_safe_conformal_metrics.csv"])
    conf["nominal_coverage"] = 1.0 - conf.alpha
    conf.to_csv(MET / "duplicate_safe_conformal_metrics.csv", index=False)
    direction = cross.groupby(["source_dataset", "target_dataset"], as_index=False).agg(
        mean_target_roc_auc=("target_roc_auc", "mean"),
        min_model_target_roc_auc=("target_roc_auc", "min"),
        max_model_target_roc_auc=("target_roc_auc", "max"),
        mean_domain_ood_roc_auc=("target_ood_detection_roc_auc", "mean"),
        mean_target_alert_rate=("target_ood_alert_rate", "mean"),
        models=("model", "size"),
    )
    direction.to_csv(MET / "duplicate_safe_transfer_summary.csv", index=False)
    direction.to_csv(TAB / "duplicate_safe_transfer_summary.csv", index=False)
    # Rebuild the CAD comparison tables from frozen untouched tasks plus deduplicated Hungary/VA.
    primary = pd.read_csv(MET / "model_metrics.csv")
    overrides = within.set_index(["dataset", "model"])
    paper_rows, auc_rows = [], []
    for ds in CAD:
        for model in MODEL_ORDER:
            p = primary[(primary.dataset == ds) & (primary.model == model)].iloc[0]
            if ds in ("uci_hungary", "uci_va_long_beach"):
                d = overrides.loc[(ds, model)]
                auc_mean = d.duplicate_safe_fold_mean_roc_auc
                auc_sd = d.duplicate_safe_fold_sd_roc_auc
                stats = folds[(folds.dataset == ds) & (folds.model == model)]
                values = {
                    "accuracy": stats.accuracy.mean(),
                    "precision": stats.precision.mean(),
                    "sensitivity": stats.recall.mean(),
                    "specificity": stats.specificity.mean(),
                    "f1": stats.f1.mean(),
                    "roc_auc": stats.roc_auc.mean(),
                    "pr_auc": stats.pr_auc.mean(),
                }
                sd = {
                    "accuracy": stats.accuracy.std(ddof=1),
                    "precision": stats.precision.std(ddof=1),
                    "sensitivity": stats.recall.std(ddof=1),
                    "specificity": stats.specificity.std(ddof=1),
                    "f1": stats.f1.std(ddof=1),
                    "roc_auc": auc_sd,
                    "pr_auc": stats.pr_auc.std(ddof=1),
                }
            else:
                auc_mean, auc_sd = p.fold_mean_roc_auc, p.roc_auc_fold_sd
                f = pd.read_csv(MET / "fold_metrics.csv")
                stats = f[(f.dataset == ds) & (f.model == model)]
                values = {
                    "accuracy": stats.accuracy.mean(),
                    "precision": stats.precision.mean(),
                    "sensitivity": stats.recall.mean(),
                    "specificity": stats.specificity.mean(),
                    "f1": stats.f1.mean(),
                    "roc_auc": stats.roc_auc.mean(),
                    "pr_auc": stats.pr_auc.mean(),
                }
                sd = {key: stats[key].std(ddof=1) for key in values}
            auc_rows.append((DISPLAY[ds], model, float(auc_mean), float(auc_sd)))
            paper_rows.append((DISPLAY[ds], MODEL_LABELS[model], values, sd))
    auc_tex = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Dataset & LR & KNN & SVM & RF & OVEC & OSEC \\",
        r"\midrule",
    ]
    for ds in CAD:
        row = [DISPLAY[ds]]
        for model in MODEL_ORDER:
            item = next(x for x in auc_rows if x[0] == DISPLAY[ds] and x[1] == model)
            row.append(f"{fmt(item[2])} $\\pm$ {fmt(item[3])}")
        auc_tex.append(" & ".join(row) + r" \\")
    auc_tex.extend([r"\bottomrule", r"\end{tabular}"])
    (PAPER / "tables").mkdir(parents=True, exist_ok=True)
    (PAPER / "tables" / "model_auc_matrix.tex").write_text(
        "\n".join(auc_tex) + "\n", encoding="utf-8"
    )
    full_tex = [
        r"\begin{tabular}{llrrrrrrr}",
        r"\toprule",
        r"Dataset & Model & Acc. & Prec. & Sens. & Spec. & F1 & ROC-AUC & PR-AUC \\",
        r"\midrule",
    ]
    for ds, model, values, sd in paper_rows:
        vals = [
            f"{fmt(values[k])} $\\pm$ {fmt(sd[k])}"
            for k in (
                "accuracy",
                "precision",
                "sensitivity",
                "specificity",
                "f1",
                "roc_auc",
                "pr_auc",
            )
        ]
        full_tex.append(" & ".join([ds, model, *vals]) + r" \\")
    full_tex.extend([r"\bottomrule", r"\end{tabular}"])
    (PAPER / "tables" / "cad_model_metrics.tex").write_text(
        "\n".join(full_tex) + "\n", encoding="utf-8"
    )
    # Explicit model-by-model sensitivity table for the two affected datasets.
    compare_tex = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Dataset & Model & Frozen AUC & Dedup-safe AUC & Frozen $-$ dedup \\",
        r"\midrule",
    ]
    for _, row in within.iterrows():
        compare_tex.append(
            " & ".join(
                [
                    DISPLAY[row.dataset],
                    MODEL_SHORT[row.model],
                    fmt(row.fold_mean_roc_auc),
                    fmt(row.duplicate_safe_fold_mean_roc_auc),
                    f"{row.frozen_minus_duplicate_safe_auc:+.3f}",
                ]
            )
            + r" \\"
        )
    compare_tex.extend([r"\bottomrule", r"\end{tabular}"])
    (PAPER / "tables" / "duplicate_sensitivity.tex").write_text(
        "\n".join(compare_tex) + "\n", encoding="utf-8"
    )
    uncertainty = (BASE_PAPER / "tables" / "uncertainty_ranges.tex").read_text(encoding="utf-8")
    nominal_90 = conf[conf.alpha.eq(0.1)]
    for dataset in ("uci_hungary", "uci_va_long_beach"):
        subset = nominal_90[nominal_90.dataset.eq(dataset)]
        coverage = f"{subset.empirical_coverage.min():.3f}--{subset.empirical_coverage.max():.3f}"
        set_size = f"{subset.average_set_size.min():.3f}--{subset.average_set_size.max():.3f}"
        old_line = next(
            line for line in uncertainty.splitlines() if line.startswith(DISPLAY[dataset] + " &")
        )
        parts = old_line.split(" & ")
        parts[3] = coverage
        parts[4] = set_size
        uncertainty = uncertainty.replace(old_line, " & ".join(parts))
    (PAPER / "tables" / "uncertainty_ranges.tex").write_text(uncertainty, encoding="utf-8")
    # Counts table shows both untouched primary inputs and the dedup-safe sensitivity size.
    chars = (BASE_PAPER / "tables" / "dataset_characteristics.tex").read_text(encoding="utf-8")
    chars = chars.replace("UCI Hungary & 294 & 13 & 188/106", "UCI Hungary & 293 & 13 & 187/106")
    chars = chars.replace(
        "UCI VA Long Beach & 200 & 13 & 51/149", "UCI VA Long Beach & 199 & 13 & 51/148"
    )
    (PAPER / "tables" / "dataset_characteristics.tex").write_text(chars, encoding="utf-8")
    # Updated transfer table and heatmap are built from all 72 dedup-safe transfers.
    display_direction = direction.copy()
    transfer_tex = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Source & Target & Mean AUC & Model range & Domain OOD AUROC & Target alert \\",
        r"\midrule",
    ]
    for _, row in display_direction.sort_values(["source_dataset", "target_dataset"]).iterrows():
        transfer_tex.append(
            " & ".join(
                [
                    DISPLAY[row.source_dataset],
                    DISPLAY[row.target_dataset],
                    fmt(row.mean_target_roc_auc),
                    f"{fmt(row.min_model_target_roc_auc)}--{fmt(row.max_model_target_roc_auc)}",
                    fmt(row.mean_domain_ood_roc_auc),
                    fmt(row.mean_target_alert_rate),
                ]
            )
            + r" \\"
        )
    transfer_tex.extend([r"\bottomrule", r"\end{tabular}"])
    (PAPER / "tables" / "cross_cohort_summary.tex").write_text(
        "\n".join(transfer_tex) + "\n", encoding="utf-8"
    )
    # Update heatmap at publication resolution from actual target AUCs.
    matrix = direction.pivot(
        index="source_dataset", columns="target_dataset", values="mean_target_roc_auc"
    ).reindex(index=CAD, columns=CAD)
    np.fill_diagonal(matrix.values, np.nan)
    fig, ax = plt.subplots(figsize=(6.3, 5.0))
    masked = np.ma.masked_invalid(matrix.to_numpy(dtype=float))
    image = ax.imshow(masked, cmap="viridis", vmin=0.45, vmax=0.95)
    ax.set_xticks(
        range(len(CAD)), [DISPLAY[x].replace("UCI ", "") for x in CAD], rotation=30, ha="right"
    )
    ax.set_yticks(range(len(CAD)), [DISPLAY[x].replace("UCI ", "") for x in CAD])
    ax.set_xlabel("Target cohort")
    ax.set_ylabel("Source cohort")
    ax.set_title("Deduplicated source-only transfer mean ROC-AUC")
    for i in range(len(CAD)):
        for j in range(len(CAD)):
            if not np.isnan(matrix.iloc[i, j]):
                ax.text(
                    j,
                    i,
                    f"{matrix.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                    color="white" if matrix.iloc[i, j] < 0.72 else "black",
                    fontsize=8,
                )
    fig.colorbar(image, ax=ax, label="Mean target ROC-AUC across six models")
    fig.tight_layout()
    fig.savefig(PAPER / "figures" / "cross_dataset_mean_auc_heatmap.pdf")
    plt.close(fig)
    primary_predictions_path = (
        ROOT
        / "results"
        / "multi_dataset_evaluation_20261108"
        / "predictions"
        / "20261107T202404Z"
        / "out_of_fold_and_official_predictions.csv"
    )
    primary_predictions = pd.read_csv(primary_predictions_path)
    local_predictions = pd.read_csv(OUT / "duplicate_safe_local" / "within_predictions.csv")
    primary_predictions = primary_predictions[
        ~primary_predictions.dataset.isin(["uci_hungary", "uci_va_long_beach"])
    ]
    predictions = pd.concat([primary_predictions, local_predictions], ignore_index=True, sort=False)
    primary_folds = pd.read_csv(MET / "fold_metrics.csv")
    primary_folds = primary_folds[
        ~primary_folds.dataset.isin(["uci_hungary", "uci_va_long_beach"])
    ].copy()
    primary_folds["evaluation_basis"] = "frozen_primary"
    duplicate_folds = folds.copy()
    duplicate_folds["evaluation_basis"] = "duplicate_safe_rerun"
    combined_folds = pd.concat([primary_folds, duplicate_folds], ignore_index=True, sort=False)
    combined_folds["fold"] = combined_folds.fold.astype(str)
    combined_folds.to_csv(MET / "final_analysis_fold_metrics.csv", index=False)
    metadata = pd.read_csv(MET / "model_metrics.csv")
    analysis_rows = []
    fold_metric_names = [
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
        "ece_weighted_uniform",
        "mcc",
        "cohen_kappa",
        "false_positive_rate",
        "false_negative_rate",
        "train_roc_auc_resubstitution",
        "train_accuracy_resubstitution",
        "train_minus_outer_test_roc_auc",
        "inner_validation_minus_outer_test_roc_auc",
    ]
    for (dataset, model), group in predictions.groupby(["dataset", "model"], sort=False):
        fold_group = combined_folds[
            combined_folds.dataset.eq(dataset) & combined_folds.model.eq(model)
        ]
        if len(fold_group) == 0:
            raise AssertionError(f"Missing final-analysis folds for {dataset}/{model}")
        basis = sorted(fold_group.evaluation_basis.dropna().unique())
        if len(basis) != 1:
            raise AssertionError(f"Mixed evaluation basis for {dataset}/{model}: {basis}")
        row = {
            "dataset": dataset,
            "model": model,
            "model_label": MODEL_LABELS[model],
            "task_family": metadata[metadata.dataset.eq(dataset) & metadata.model.eq(model)]
            .iloc[0]
            .task_family,
            "evaluation_basis": basis[0],
            "fold_count": int(len(fold_group)),
        }
        for metric in fold_metric_names:
            if metric in fold_group:
                row[f"fold_mean_{metric}"] = float(fold_group[metric].mean())
                row[f"fold_sd_{metric}"] = (
                    float(fold_group[metric].std(ddof=1)) if len(fold_group) > 1 else None
                )
        row.update(pooled_metrics(group))
        analysis_rows.append(row)
    final_analysis = pd.DataFrame(analysis_rows)
    if len(final_analysis) != 42:
        raise AssertionError(f"Expected 42 final-analysis model rows, found {len(final_analysis)}")
    final_analysis.to_csv(MET / "final_analysis_model_metrics.csv", index=False)
    fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.6), sharex=True, sharey=True)
    axes_flat = axes.ravel()
    for ax, dataset in zip(axes_flat, DISPLAY):
        subset = predictions[predictions.dataset.eq(dataset)]
        for model in MODEL_ORDER:
            group = subset[subset.model.eq(model)]
            if group.empty or group.y_true.nunique() < 2:
                continue
            observed, predicted = calibration_curve(
                group.y_true.astype(int),
                group.probability_positive.astype(float),
                n_bins=10,
                strategy="uniform",
            )
            ax.plot(
                predicted,
                observed,
                marker=".",
                linewidth=0.8,
                markersize=3,
                label=MODEL_SHORT[model],
            )
        ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=0.7)
        ax.set_title(DISPLAY[dataset].replace("UCI ", ""))
        ax.grid(alpha=0.2)
    axes_flat[-1].axis("off")
    for ax in axes[1, :]:
        ax.set_xlabel("Mean predicted probability")
    axes[0, 0].set_ylabel("Observed positive fraction")
    axes[1, 0].set_ylabel("Observed positive fraction")
    axes_flat[0].legend(loc="lower right", fontsize=6, ncol=2)
    fig.tight_layout()
    fig.savefig(PAPER / "figures" / "calibration_curves.pdf")
    plt.close(fig)
    performance = pd.read_csv(MET / "model_metrics.csv")
    performance = performance[~performance.dataset.isin(["uci_hungary", "uci_va_long_beach"])]
    dedup_folds = folds
    for dataset in ("uci_hungary", "uci_va_long_beach"):
        for model in MODEL_ORDER:
            sample = dedup_folds[dedup_folds.dataset.eq(dataset) & dedup_folds.model.eq(model)]
            performance = pd.concat(
                [
                    performance,
                    pd.DataFrame(
                        [
                            {
                                "dataset": dataset,
                                "model": model,
                                "fold_mean_roc_auc": sample.roc_auc.mean(),
                                "fold_mean_pr_auc": sample.pr_auc.mean(),
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
    fig, axes = plt.subplots(2, 4, figsize=(12.5, 6.2))
    for ax, dataset in zip(axes.ravel(), DISPLAY):
        group = performance[performance.dataset.eq(dataset)].set_index("model")
        values_auc = [group.loc[m, "fold_mean_roc_auc"] for m in MODEL_ORDER]
        values_pr = [group.loc[m, "fold_mean_pr_auc"] for m in MODEL_ORDER]
        bars = np.arange(len(MODEL_ORDER))
        ax.bar(bars - 0.18, values_auc, width=0.36, label="ROC-AUC")
        ax.bar(bars + 0.18, values_pr, width=0.36, label="PR-AUC")
        ax.set_xticks(bars, [MODEL_SHORT[m] for m in MODEL_ORDER], rotation=35)
        ax.set_ylim(0, 1.04)
        ax.set_title(DISPLAY[dataset].replace("UCI ", ""))
        ax.grid(axis="y", alpha=0.2)
    axes.ravel()[-1].axis("off")
    axes[0, 0].legend(fontsize=6)
    axes[0, 0].set_ylabel("Mean held-out score")
    axes[1, 0].set_ylabel("Mean held-out score")
    fig.tight_layout()
    fig.savefig(PAPER / "figures" / "model_performance_comparison.pdf")
    plt.close(fig)
    # Compare the frozen and deduplicated AUCs without implying paired resampling.
    fig, ax = plt.subplots(figsize=(8, 4.8))
    positions = np.arange(len(within))
    ax.scatter(within.fold_mean_roc_auc, positions, label="Frozen split", marker="o")
    ax.scatter(
        within.duplicate_safe_fold_mean_roc_auc, positions, label="Deduplicated rerun", marker="s"
    )
    for y, (_, row) in zip(positions, within.iterrows()):
        ax.plot(
            [row.fold_mean_roc_auc, row.duplicate_safe_fold_mean_roc_auc],
            [y, y],
            color="#999999",
            lw=0.8,
        )
    ax.set_yticks(
        positions,
        [
            f"{DISPLAY[r.dataset].replace('UCI ', '')} · {MODEL_SHORT[r.model]}"
            for _, r in within.iterrows()
        ],
    )
    ax.set_xlabel("Fold-mean ROC-AUC")
    ax.set_title("Exact-duplicate sensitivity (rerun folds; descriptive comparison)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "duplicate_safe_auc_sensitivity.png")
    plt.close(fig)
    # Write aggregate sensitivity metrics and updated source tables.
    write_csv(within, MET / "duplicate_safe_within_model_metrics.csv")
    write_csv(folds, MET / "duplicate_safe_within_fold_metrics.csv")
    write_csv(conf, MET / "duplicate_safe_conformal_metrics.csv")
    return {
        "within": within,
        "folds": folds,
        "cross": cross,
        "direction": direction,
        "conformal": conf,
    }


def revise_manuscript(tables: dict[str, pd.DataFrame]) -> None:
    if PAPER.exists():
        shutil.rmtree(PAPER)
    shutil.copytree(
        BASE_PAPER,
        PAPER,
        ignore=shutil.ignore_patterns("paper", "build", "*.log", "*.aux", "*.out"),
    )
    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    tex = tex.replace(
        "(920 records total)", "(920 source rows; 918 after exact-row deduplication sensitivity)"
    )
    tex = tex.replace(
        "The four component cohorts total 920 records.",
        "The four source cohorts contain 920 rows; the duplicate-safe sensitivity removes one repeated predictor row in Hungary and one in VA Long Beach (918 records remain).",
    )
    tex = tex.replace(
        "The highest observed within-task ROC-AUC ranged from 0.679 to 0.911 across CAD cohorts and was 0.805 on the SPECTF held-out test set.",
        "Using the deduplicated reruns for Hungary and VA Long Beach, the best observed CAD fold-mean ROC-AUC ranged from 0.694 to 0.911; SPECTF remained 0.805 on its official held-out test set.",
    )
    tex = tex.replace(
        "Cross-cohort ROC-AUC ranged from 0.238 to 0.903 across model-transfer pairs.",
        "After deduplicating both source and target cohorts before all transfer partitions, cross-cohort ROC-AUC ranged from 0.236 to 0.903 across model-transfer pairs.",
    )
    tex = tex.replace(
        "source-versus-target feature-score AUROC varied from 0.357 to 0.934.",
        "source-versus-target feature-score AUROC varied from 0.357 to 0.951 after the duplicate-safe transfer rerun.",
    )
    tex = tex.replace(
        "Across cross-cohort transfers, source-versus-target feature-score AUROC ranged from 0.357 to 0.934, showing that feature-support separation depended strongly on source, target, and model.",
        "Across duplicate-safe cross-cohort transfers, source-versus-target feature-score AUROC ranged from 0.357 to 0.951, showing that feature-support separation depended strongly on source, target, and model.",
    )
    tex = tex.replace(
        "no patient identifier permits an independentness guarantee.",
        "no patient identifier permits an independence guarantee.",
    )
    tex = tex.replace(
        "Outer-fold mean ROC-AUC and PR-AUC with fold standard deviations. The SPECTF point is from its official test set and has no fold-based interval.",
        "Outer-fold mean ROC-AUC and PR-AUC. The SPECTF point is from its official test set and has no fold-based interval.",
    )
    tex = tex.replace(
        "Empirical coverage for nominal 90\\% split-conformal sets varied from 0.791 to 1.000 across dataset--model groups; therefore the target was not uniformly met on these held-out samples.",
        "Empirical coverage for nominal 90\\% split-conformal sets varied from 0.791 to 1.000 across dataset--model groups; Hungary and VA Long Beach use duplicate-safe reruns, and coverage remained below nominal for some held-out samples.",
    )
    tex = tex.replace(
        "Exact predictor-row matching found no cross-cohort exact duplicates, but no persistent participant identifiers were available to rule out transformed or near-duplicate records.",
        "The pairwise screen found no exact cross-cohort predictor-row matches. A subsequent within-cohort audit found one exact duplicate row in Hungary (rows 101/102) and one in VA Long Beach (139/187); no persistent participant identifiers were available to rule out transformed or near-duplicate records.",
    )
    tex = tex.replace(
        "The highest observed model by fold-mean ROC-AUC varied across tasks: random forest on Cleveland (0.911), OVEC on Hungary (0.890), logistic regression on Switzerland (0.772), random forest on VA Long Beach (0.679), OVEC on heart failure (0.752), random forest on MI complications (0.869), and OVEC on SPECTF (0.805).",
        "The highest observed model by fold-mean ROC-AUC varied across tasks: random forest on Cleveland (0.911), logistic regression on deduplicated Hungary (0.897), logistic regression on Switzerland (0.772), random forest on deduplicated VA Long Beach (0.694), OVEC on heart failure (0.752), random forest on MI complications (0.869), and OVEC on SPECTF (0.805).",
    )
    tex = tex.replace(
        "OVEC exceeded OSEC ROC-AUC on Cleveland, Hungary, heart failure, SPECTF, and VA Long Beach, while OSEC was higher on Switzerland and MI.",
        "On the deduplicated Hungary and VA sensitivity, OVEC did not exceed OSEC in Hungary and exceeded it in VA Long Beach; the original frozen split had different fold allocations and is retained in the sensitivity table for comparison.",
    )
    old_transfer = "Across model--direction pairs, target ROC-AUC ranged from 0.238 to 0.903. The average ROC-AUC across models varied by direction from 0.538 (Switzerland to VA Long Beach) to 0.886 (Cleveland to Hungary)."
    new_transfer = "Across the deduplicated model--direction pairs, target ROC-AUC ranged from 0.236 to 0.903. The average ROC-AUC across models varied by direction from 0.539 (Switzerland to VA Long Beach) to 0.885 (Cleveland to Hungary)."
    tex = tex.replace(old_transfer, new_transfer)
    tex = tex.replace(
        "All nested model evaluations and all cross-cohort transfers completed.",
        "All nested model evaluations and all cross-cohort transfers completed. A duplicate-safe rerun removed exact predictor duplicates before partitioning and re-evaluated all 12 Hungary/VA model configurations plus all 72 directed transfers.",
    )
    tex = tex.replace(
        "The datasets are small, historical, and in some cases severely imbalanced or incomplete. Exact-row matching cannot detect near duplicates or transformations, while persistent participant identifiers are unavailable.",
        "The datasets are small, historical, and in some cases severely imbalanced or incomplete. The frozen Hungary evaluation placed one exact duplicate across development and outer test in fold 3, and across calibration and test in fold 2. The frozen VA split did not place the duplicate pair across development and outer test, but the rows were repeated within partitions. We therefore report a fresh duplicate-safe rerun for both cohorts; its folds differ from the frozen folds, so score deltas conflate duplicate removal and fold reshuffling and are not paired causal effects. Exact-row matching cannot detect near duplicates or transformations, while persistent participant identifiers are unavailable.",
    )
    tex = tex.replace(
        "In the compatible CAD cohorts, internal scores were strongest on Cleveland and Hungary and substantially weaker on VA Long Beach; Switzerland had only eight negative cases and yielded unstable fold estimates.",
        "In the compatible CAD cohorts, internal scores were strongest on Cleveland and deduplicated Hungary and weaker on deduplicated VA Long Beach; Switzerland had only eight negative cases and yielded unstable fold estimates. The Hungary frozen estimate is qualified by exact duplicate leakage across development and test; the deduplicated rerun is the more defensible within-cohort sensitivity result.",
    )
    insert = r"""
\subsection{Exact-duplicate sensitivity}
The frozen partition audit identified two within-cohort groups with identical predictor values and labels. In Hungary, rows 101 and 102 were split between calibration and outer test in fold 2 and between development and outer test in fold 3, creating a direct test-boundary leak in one of three folds. In VA Long Beach, rows 139 and 187 remained together within each fold role; they did not cross development and outer test, but duplicated observations violate a unique-record assumption. We removed one row from each group before forming new partitions, retained all four cohorts in transfer analyses after deduplicating source and target, and preserved the frozen run. The new folds were re-created from the same protocol and seed, so the frozen-versus-rerun differences also reflect changed fold membership. The sensitivity is descriptive and cannot isolate the duplicate's causal contribution.

\begin{table*}[t]
\centering
\caption{Hungary and VA Long Beach fold-mean ROC-AUC before and after exact-row deduplication. The partitions were re-created, so changes combine row removal and fold reshuffling.}
\label{tab:duplicate-sensitivity}
\scriptsize
\input{tables/duplicate_sensitivity.tex}
\end{table*}
"""
    anchor = r"\subsection{Failed analyses}"
    if insert.strip() not in tex:
        tex = tex.replace(anchor, insert + "\n" + anchor)
    tex = tex.replace(
        "Source-only transfer summary over the six models per direction.",
        "Duplicate-safe source-only transfer summary over the six models per direction.",
    )
    tex = tex.replace(
        "Mean target ROC-AUC over six source-only models for each CAD cohort direction.",
        "Mean target ROC-AUC over six source-only models after exact-row deduplication for each CAD cohort direction.",
    )
    (PAPER / "main.tex").write_text(tex, encoding="utf-8")
    readme = (BASE_PAPER / "README.md").read_text(encoding="utf-8")
    readme += "\n\nThis versioned bundle incorporates the exact-duplicate sensitivity replay. It updates the Hungary and VA CAD tables and reruns all 72 directed transfers after removing exact predictor duplicates before partitioning. See `BUILD_MANIFEST.json`; the original source bundle remains unchanged.\n"
    (PAPER / "README.md").write_text(readme, encoding="utf-8")


def update_reports(tables: dict[str, pd.DataFrame], metrics: dict[str, pd.DataFrame]) -> None:
    within = metrics["within"]
    cross = metrics["cross"]
    direction = metrics["direction"]
    conf = metrics["conformal"]
    conf_summary = conf.groupby("nominal_coverage").empirical_coverage.agg(["mean", "min", "max"])
    auc_min, auc_max = cross.target_roc_auc.min(), cross.target_roc_auc.max()
    ood_min, ood_max = (
        cross.target_ood_detection_roc_auc.min(),
        cross.target_ood_detection_roc_auc.max(),
    )
    alert_min, alert_max = cross.target_ood_alert_rate.min(), cross.target_ood_alert_rate.max()
    direction_min = direction.loc[direction.mean_target_roc_auc.idxmin()]
    direction_max = direction.loc[direction.mean_target_roc_auc.idxmax()]
    winners = within.loc[within.groupby("dataset").duplicate_safe_fold_mean_roc_auc.idxmax()]
    final_analysis = pd.read_csv(MET / "final_analysis_model_metrics.csv")
    ranked = final_analysis.loc[final_analysis.groupby("dataset").fold_mean_roc_auc.idxmax()].copy()
    ranked["dataset_label"] = ranked.dataset.map(DISPLAY)
    winner_table = [
        "| task | fold-mean AUC winner | fold-mean ROC-AUC | pooled ROC-AUC | basis |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for _, row in ranked.sort_values("dataset_label").iterrows():
        winner_table.append(
            f"| {row.dataset_label} | {row.model_label} | "
            f"{row.fold_mean_roc_auc:.3f} | {row.pooled_roc_auc:.3f} | "
            f"{row.evaluation_basis} |"
        )
    ensemble = final_analysis[final_analysis.model.isin(["ovec", "osec"])].pivot(
        index="dataset", columns="model", values="fold_mean_roc_auc"
    )
    ensemble_table = [
        "| task | OVEC fold-mean AUC | OSEC fold-mean AUC | OVEC − OSEC |",
        "| --- | ---: | ---: | ---: |",
    ]
    for dataset in DISPLAY:
        if dataset not in ensemble.index:
            continue
        ensemble_table.append(
            f"| {DISPLAY[dataset]} | {ensemble.loc[dataset, 'ovec']:.3f} | "
            f"{ensemble.loc[dataset, 'osec']:.3f} | "
            f"{ensemble.loc[dataset, 'ovec'] - ensemble.loc[dataset, 'osec']:+.3f} |"
        )
    ranking_body = (
        "## Leakage-qualified fold-mean comparison\n\n"
        "The table uses fold means for nested tasks and the single official held-out "
        "SPECTF score. Hungary and VA Long Beach use the duplicate-safe reruns; the "
        "other five tasks retain the frozen evaluation. All 42 model rows and 114 "
        "fold/test rows are included in final_analysis_model_metrics.csv and "
        "final_analysis_fold_metrics.csv with an evaluation_basis column. Model "
        "selection maxima are descriptive.\n\n"
        + "\n".join(winner_table)
        + "\n\n### OVEC versus OSEC on the same fold-mean scale\n\n"
        + "\n".join(ensemble_table)
        + "\n\nNo consistent ensemble advantage is supported."
    )
    summary = (
        "## Exact-duplicate audit and sensitivity\n\n"
        "The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.\n\n"
        "The duplicate-safe within-task winners are "
        + "; ".join(
            f"{DISPLAY[r.dataset]}: {r.model} ({r.duplicate_safe_fold_mean_roc_auc:.3f})"
            for _, r in winners.iterrows()
        )
        + ". Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges "
        + f"{auc_min:.3f}–{auc_max:.3f}; direction-level six-model means range {direction.mean_target_roc_auc.min():.3f}–{direction.mean_target_roc_auc.max():.3f} (minimum {DISPLAY[direction_min.source_dataset]}→{DISPLAY[direction_min.target_dataset]}, maximum {DISPLAY[direction_max.source_dataset]}→{DISPLAY[direction_max.target_dataset]}). "
        + f"Feature-support domain OOD AUROC ranges {ood_min:.3f}–{ood_max:.3f}, while target alert rate ranges {alert_min:.3f}–{alert_max:.3f}. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.\n\n"
        "Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.\n\n"
        "No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies."
    )
    section_docs = [
        "COMPLETE_PROJECT_TECHNICAL_AUDIT.md",
        "DATASET_PROVENANCE_AND_COMPATIBILITY.md",
        "COMPLETE_MODEL_COMPARISON_REPORT.md",
        "OVERFITTING_AND_GENERALIZATION_REPORT.md",
        "CROSS_DATASET_EVALUATION_REPORT.md",
        "OOD_AND_SELECTIVE_PREDICTION_REPORT.md",
        "CARDIODIAG_COMPLETE_TECHNICAL_RESEARCH_REPORT.md",
    ]
    for filename in section_docs:
        replace_section(DOC / filename, "DUPLICATE_SAFE_AUDIT", summary)
    model_report = DOC / "COMPLETE_MODEL_COMPARISON_REPORT.md"
    model_text = model_report.read_text(encoding="utf-8")
    model_text = model_text.replace(
        "## Best observed pooled AUC per task",
        "## Frozen primary pooled AUC per task (Hungary and VA qualified)",
        1,
    )
    model_text = model_text.replace(
        "These are descriptive maxima from the evaluated model set, not confirmatory winners.",
        "These descriptive pooled maxima preserve the frozen primary run. Hungary is directly affected by an exact duplicate crossing development/test; Hungary and VA values are superseded for the final fold-mean comparison below. Do not use the frozen Hungary/VA estimates as unqualified performance claims.",
        1,
    )
    model_text = model_text.replace(
        "## OVEC and OSEC comparison",
        "## Frozen primary OVEC and OSEC comparison (Hungary/VA qualified)",
        1,
    )
    model_text = model_text.replace(
        "The sign of the paired fold-mean ROC-AUC difference changes by task. This run does not show consistent ensemble superiority.",
        "This frozen primary table is superseded for the Hungary and VA fold means by the duplicate-safe comparison below. Across all tasks, results do not show consistent ensemble superiority.",
        1,
    )
    model_report.write_text(model_text, encoding="utf-8")
    replace_section(model_report, "FINAL_FOLD_MEAN_COMPARISON", ranking_body)
    insert_after_title(
        model_report,
        "MODEL_DATA_INTEGRITY_NOTICE",
        "> **Data-integrity qualification.** The frozen Hungary estimate includes an "
        "exact duplicate crossing development and outer test in one fold. Use the "
        "duplicate-safe values for Hungary and VA Long Beach. The complete 42-row "
        "mixed-basis comparison is in results/final_research_20261108/metrics/"
        "final_analysis_model_metrics.csv.",
    )
    analysis_folds = pd.read_csv(MET / "final_analysis_fold_metrics.csv")
    gap_rows = []
    for (dataset, model), group in analysis_folds.groupby(["dataset", "model"]):
        gap_rows.append(
            {
                "dataset": DISPLAY[dataset],
                "model": model,
                "train_auc": group.train_roc_auc_resubstitution.mean(),
                "test_auc": group.roc_auc.mean(),
                "auc_gap": group.train_minus_outer_test_roc_auc.mean(),
                "accuracy_gap": (
                    group.train_accuracy_resubstitution.mean() - group.accuracy.mean()
                ),
                "evaluation_basis": group.evaluation_basis.iloc[0],
            }
        )
    gaps = pd.DataFrame(gap_rows).sort_values("auc_gap", ascending=False)
    gap_table = [
        "| dataset | model | train AUC | test AUC | train − test AUC | train − test accuracy | basis |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for _, row in gaps.head(20).iterrows():
        gap_table.append(
            f"| {row.dataset} | {row.model} | {row.train_auc:.3f} | "
            f"{row.test_auc:.3f} | {row.auc_gap:+.3f} | "
            f"{row.accuracy_gap:+.3f} | {row.evaluation_basis} |"
        )
    overfit_report = DOC / "OVERFITTING_AND_GENERALIZATION_REPORT.md"
    overfit_text = overfit_report.read_text(encoding="utf-8")
    table_start = overfit_text.find("| dataset | model | train_auc |")
    if table_start >= 0:
        table_end = overfit_text.find("\n\n", table_start)
        if table_end >= 0:
            overfit_text = (
                overfit_text[:table_start] + "\n".join(gap_table) + overfit_text[table_end:]
            )
    overfit_report.write_text(overfit_text, encoding="utf-8")
    insert_after_title(
        overfit_report,
        "OVERFITTING_DATA_INTEGRITY_NOTICE",
        "> **Data-integrity qualification.** This report uses leakage-qualified folds "
        "for Hungary and VA Long Beach. Detailed inputs are in "
        "results/final_research_20261108/metrics/final_analysis_fold_metrics.csv. "
        "Duplicate-safe refits record training AUC and accuracy; resubstitution "
        "precision, recall, and F1 for those 12 sensitivity configurations were not "
        "generated, so these quantities remain partially completed.",
    )
    replace_section(
        overfit_report,
        "FINAL_DUPLICATE_SAFE_GAPS",
        "## Final leakage-qualified training/test gaps\n\n"
        "The table aggregates train resubstitution and outer-test fold AUC and "
        "accuracy gaps from the mixed-basis fold table. These are diagnostics and "
        "do not identify a single cause. Training precision, recall, and F1 were not "
        "regenerated for the 12 duplicate-safe sensitivity configurations.\n\n"
        + "\n".join(gap_table),
    )
    technical_report = DOC / "CARDIODIAG_COMPLETE_TECHNICAL_RESEARCH_REPORT.md"
    insert_after_title(
        technical_report,
        "TECHNICAL_REPORT_DATA_INTEGRITY_NOTICE",
        "> **Data-integrity qualification.** The frozen Hungary evaluation placed an "
        "exact duplicate across development and outer test in one fold. The fold-mean "
        "comparison below uses a duplicate-safe rerun for Hungary and VA Long Beach; "
        "the original frozen metrics remain available and are not overwritten.",
    )
    replace_section(
        technical_report,
        "FINAL_FOLD_MEAN_COMPARISON",
        ranking_body,
    )
    leakage = (
        "## Additional leakage and data-quality checks\n\n"
        "The target field is excluded from each recorded predictor matrix, and preprocessing/model selection remain partition-local. However, files alone cannot verify predictor timing for the death-event or MI-complication tasks. Numerical feature distribution summaries, categorical value counts, and pairwise Spearman correlations with |rho| >= 0.8 are machine-readable. Pairwise correlations are descriptive and are not variance-inflation factors or evidence of causal redundancy. `leakage_audit.csv` records these limits and the exact duplicate boundary evidence."
    )
    replace_section(DOC / "DATASET_PROVENANCE_AND_COMPATIBILITY.md", "DATA_QUALITY_DETAIL", leakage)
    replace_section(
        DOC / "FEATURE_SELECTION_AND_ABLATION_REPORT.md", "DATA_REPRESENTATION_AUDIT", leakage
    )
    conformal_body = (
        "## Duplicate-safe conformal sensitivity\n\n"
        "For Hungary and VA Long Beach, the exact duplicates were removed before folds and calibration sets were formed. At nominal levels, the mean empirical coverage across the two datasets, six models and three folds is:\n\n"
        + "\n".join(
            f"- {1 - alpha:.0%}: mean {row['mean']:.3f}, range {row['min']:.3f}–{row['max']:.3f}"
            for alpha, row in conf_summary.sort_index(ascending=False).iterrows()
        )
        + "\n\nThese finite-sample estimates remain conditional on exchangeability; the re-created splits are not the original calibration/test partitions."
    )
    replace_section(
        DOC / "CALIBRATION_AND_UNCERTAINTY_REPORT.md", "DUPLICATE_SAFE_CONFORMAL", conformal_body
    )
    manuscript = (
        "## Versioned duplicate-safe manuscript\n\n"
        "A revised source bundle is available at `paper/multi_dataset_study_20261108_dedup_safe/`. It uses duplicate-safe Hungary and VA within-task results, recalculates all 72 source-to-target transfers after removing exact repeated predictor rows before partitioning, and discloses the fold reshuffling. It is a versioned copy; the original six-page bundle and PDF are preserved. Compiler, citation, reference, page-count and visual checks are recorded in its `BUILD_MANIFEST.json` after compilation. Author order, affiliation, institutional determinations, funding, conflicts, contribution statements and venue remain for the project team to confirm."
    )
    replace_section(DOC / "MANUSCRIPT_FINALIZATION_REPORT.md", "DEDUP_SAFE_MANUSCRIPT", manuscript)
    changelog = DOC / "PROJECT_COMPLETION_CHANGELOG_20261108.md"
    replace_section(
        changelog,
        "DEDUP_SAFE_IMPLEMENTATION",
        "The exact-duplicate sensitivity found two groups in Hungary and VA Long Beach. The Hungary frozen split placed one duplicate across development/test and calibration/test boundaries. A fresh deduplicated evaluation completed 12 within-task model runs and all 72 directed transfers. Aggregate comparisons, data-quality tables, updated manuscript tables/figure, and a versioned LaTeX source bundle were added. The primary frozen outputs were retained.",
    )
    insert_after_title(
        ROOT / "README.md",
        "CURRENT_COMPLETION_STATUS_20261108",
        "## Completion update (2026-11-08)\n\n"
        "The frozen multi-dataset run remains preserved. A subsequent exact-row "
        "audit found Hungary rows 101/102 crossing development and outer-test in "
        "one frozen fold, plus one duplicate group in VA Long Beach. A duplicate-safe "
        "rerun completed 12 within-task model configurations and all 72 directed "
        "CAD transfers after removing exact duplicates before partitioning. The "
        "revised seven-page manuscript and its compiled PDF are under "
        "paper/multi_dataset_study_20261108_dedup_safe/ and "
        "output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe.pdf. "
        "The corrected Hungary and VA results supersede those two frozen within-task "
        "estimates; their rerun fold differences also include fold reshuffling. "
        "This is retrospective benchmark work and does not establish independent "
        "external validation or clinical use.",
    )
    readme = ROOT / "README.md"
    readme_text = readme.read_text(encoding="utf-8")
    readme_text = readme_text.replace(
        "its build manifest and PDF hash verify, but a fresh LaTeX compiler is not\ninstalled in the current environment.",
        "its original build manifest and PDF hash verify. A revised seven-page "
        "duplicate-safe manuscript was freshly compiled with Tectonic 0.17.0 and "
        "visually checked under paper/multi_dataset_study_20261108_dedup_safe/; "
        "its PDF is output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe.pdf.",
    )
    readme.write_text(readme_text, encoding="utf-8")


def main() -> None:
    for folder in (MET, TAB, FIG, PAPER / "tables", PAPER / "figures"):
        folder.mkdir(parents=True, exist_ok=True)
    data_tables = build_descriptive_data_tables()
    revise_manuscript(data_tables)
    metrics = build_metrics_and_figures()
    update_reports(data_tables, metrics)
    manifest = json.loads((OUT / "duplicate_safe_manifest.json").read_text(encoding="utf-8"))
    dataset_manifest_path = OUT / "manifests" / "dataset_manifest.json"
    dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
    dataset_manifest.setdefault("completion_outputs", {}).update(
        {
            "exact_duplicate_audit": "results/final_research_20261108/duplicate_audit.csv",
            "duplicate_partition_audit": "results/final_research_20261108/duplicate_partition_audit.csv",
            "numeric_feature_distributions": "results/final_research_20261108/feature_distribution_summary.csv",
            "categorical_value_distributions": "results/final_research_20261108/categorical_value_distribution.csv",
            "high_spearman_pairs_abs_0_8": "results/final_research_20261108/feature_correlation_pairs.csv",
            "leakage_audit": "results/final_research_20261108/leakage_audit.csv",
            "deduplicated_sensitivity_class_counts": "results/final_research_20261108/dataset_class_distribution.csv",
            "row_level_data_in_git": False,
        }
    )
    dataset_manifest_path.write_text(
        json.dumps(dataset_manifest, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    final = {
        "study": "CARDIODIAG duplicate-safe completion deliverables",
        "source_run_id": manifest["source_run_id"],
        "duplicate_safe_run": "results/final_research_20261108/duplicate_safe_manifest.json",
        "counts": manifest["counts"],
        "descriptive_data_rows": {name: len(frame) for name, frame in data_tables.items()},
        "duplicate_safe_transfer_direction_rows": len(metrics["direction"]),
        "duplicate_safe_within_model_rows": len(metrics["within"]),
        "manuscript_source": "paper/multi_dataset_study_20261108_dedup_safe/main.tex",
        "row_level_outputs_are_local": True,
        "sha256": {},
    }
    hash_paths = [
        OUT / "duplicate_safe_manifest.json",
        OUT / "duplicate_audit.csv",
        OUT / "duplicate_partition_audit.csv",
        OUT / "leakage_audit.csv",
        OUT / "feature_distribution_summary.csv",
        OUT / "categorical_value_distribution.csv",
        OUT / "feature_correlation_pairs.csv",
        MET / "duplicate_safe_within_model_metrics.csv",
        MET / "duplicate_safe_within_fold_metrics.csv",
        MET / "duplicate_safe_conformal_metrics.csv",
        MET / "duplicate_safe_cross_dataset_metrics.csv",
        MET / "duplicate_safe_transfer_summary.csv",
        MET / "final_analysis_fold_metrics.csv",
        MET / "final_analysis_model_metrics.csv",
        PAPER / "main.tex",
        PAPER / "tables" / "model_auc_matrix.tex",
        PAPER / "tables" / "cad_model_metrics.tex",
        PAPER / "tables" / "duplicate_sensitivity.tex",
        PAPER / "tables" / "cross_cohort_summary.tex",
        PAPER / "tables" / "uncertainty_ranges.tex",
        PAPER / "figures" / "cross_dataset_mean_auc_heatmap.pdf",
        PAPER / "figures" / "calibration_curves.pdf",
        PAPER / "figures" / "model_performance_comparison.pdf",
    ]
    for path in hash_paths:
        final["sha256"][path.relative_to(ROOT).as_posix()] = sha256(path)
    final["finalizer_script_sha256"] = sha256(Path(__file__).resolve())
    (OUT / "manifests" / "duplicate_safe_completion_manifest.json").write_text(
        json.dumps(final, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "within_rows": len(metrics["within"]),
                "fold_rows": len(metrics["folds"]),
                "transfer_rows": len(metrics["cross"]),
                "direction_rows": len(metrics["direction"]),
                "leakage_rows": len(data_tables["leakage"]),
                "numeric_distribution_rows": len(data_tables["numeric"]),
                "categorical_value_rows": len(data_tables["categorical"]),
                "high_correlation_pairs": len(data_tables["correlations"]),
                "paper_source": str(PAPER / "main.tex"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
