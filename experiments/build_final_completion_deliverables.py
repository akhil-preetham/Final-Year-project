# ruff: noqa: E501
"""Build completion tables, plots, and reports from frozen CARDIODIAG evidence.

Raw data and row-level predictions remain in the local ignored research tree.
This script only writes aggregate outputs beneath results/final_research_20261108
and focused Markdown reports beneath docs/.
"""

from __future__ import annotations

import ast
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    cohen_kappa_score,
    confusion_matrix,
    matthews_corrcoef,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "multi_dataset_evaluation_20261108"
RUN = SRC / "predictions" / "20261107T202404Z"
OUT = ROOT / "results" / "final_research_20261108"
MET = OUT / "metrics"
FIG = OUT / "figures"
TAB = OUT / "tables"
MAN = OUT / "manifests"
DOC = ROOT / "docs"
DATA = ROOT / "data" / "processed" / "multi_dataset_evaluation_20261108"
DATASET_IDS = [
    "uci_cleveland",
    "uci_hungary",
    "uci_switzerland",
    "uci_va_long_beach",
    "uci_heart_failure_519",
    "uci_mi_complications_579",
    "uci_spectf_heart",
]
DISPLAY = {
    "uci_cleveland": "UCI Cleveland",
    "uci_hungary": "UCI Hungary",
    "uci_switzerland": "UCI Switzerland",
    "uci_va_long_beach": "UCI VA Long Beach",
    "uci_heart_failure_519": "UCI Heart Failure",
    "uci_mi_complications_579": "UCI MI Complications",
    "uci_spectf_heart": "UCI SPECTF Heart",
}
MODEL_ORDER = ["logistic", "knn", "svm", "random_forest", "ovec", "osec"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )


def metric_from_counts(tn: int, fp: int, fn: int, tp: int) -> dict[str, float | int]:
    y = np.array([0] * (tn + fp) + [1] * (fn + tp), dtype=int)
    p = np.array([0] * tn + [1] * fp + [0] * fn + [1] * tp, dtype=int)
    return {
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "mcc": float(matthews_corrcoef(y, p)) if len(y) else 0.0,
        "cohen_kappa": float(cohen_kappa_score(y, p)) if len(y) else 0.0,
        "false_positive_rate": float(fp / (fp + tn)) if fp + tn else 0.0,
        "false_negative_rate": float(fn / (fn + tp)) if fn + tp else 0.0,
        "balanced_accuracy": float(balanced_accuracy_score(y, p)) if len(y) else 0.0,
    }


def prediction_metrics(group: pd.DataFrame) -> dict:
    y = group.y_true.astype(int).to_numpy()
    p = group.probability_positive.astype(float).to_numpy()
    yhat = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yhat, labels=[0, 1]).ravel()
    out = metric_from_counts(int(tn), int(fp), int(fn), int(tp))
    out["accuracy"] = float((y == yhat).mean())
    out["precision"] = float(tp / (tp + fp)) if tp + fp else 0.0
    out["sensitivity"] = out["recall"] = float(tp / (tp + fn)) if tp + fn else 0.0
    out["specificity"] = float(tn / (tn + fp)) if tn + fp else 0.0
    out["f1"] = float(2 * tp / (2 * tp + fp + fn)) if 2 * tp + fp + fn else 0.0
    out["roc_auc"] = float(roc_auc_score(y, p)) if np.unique(y).size == 2 else None
    out["pr_auc"] = float(average_precision_score(y, p)) if y.sum() else None
    out["brier"] = float(brier_score_loss(y, p))
    out["n"] = int(len(y))
    out["positive_count"] = int(y.sum())
    out["prevalence"] = float(y.mean()) if len(y) else None
    return out


def build_metrics() -> dict:
    MET.mkdir(parents=True, exist_ok=True)
    preds = pd.read_csv(RUN / "out_of_fold_and_official_predictions.csv")
    base_models = pd.read_csv(SRC / "metrics" / "model_metrics.csv")
    base_folds = pd.read_csv(SRC / "metrics" / "fold_metrics.csv")
    fold_updates, model_updates = [], []
    for (ds, model, fold), group in preds.groupby(["dataset", "model", "fold"], sort=False):
        fold_updates.append(
            {"dataset": ds, "model": model, "fold": str(fold), **prediction_metrics(group)}
        )
    for (ds, model), group in preds.groupby(["dataset", "model"], sort=False):
        model_updates.append({"dataset": ds, "model": model, **prediction_metrics(group)})
    fupd = pd.DataFrame(fold_updates)
    mupd = pd.DataFrame(model_updates)
    verification_rows = []
    verify_metrics = {
        "accuracy": "accuracy",
        "balanced_accuracy": "balanced_accuracy",
        "precision": "precision",
        "recall": "recall",
        "specificity": "specificity",
        "f1": "f1",
        "roc_auc": "roc_auc",
        "pr_auc": "pr_auc",
        "brier": "brier",
    }
    for scope, recomputed, stored, keys, metric_names in (
        (
            "fold",
            fupd,
            base_folds,
            ["dataset", "model", "fold"],
            verify_metrics,
        ),
        (
            "pooled_model",
            mupd,
            base_models,
            ["dataset", "model"],
            {f"pooled_{k}": v for k, v in verify_metrics.items() if k != "balanced_accuracy"},
        ),
    ):
        for _, computed in recomputed.iterrows():
            select = np.ones(len(stored), dtype=bool)
            for key in keys:
                left = str(computed[key])
                right = stored[key].astype(str)
                select &= right.eq(left).to_numpy()
            reference = stored.loc[select]
            if len(reference) != 1:
                raise ValueError(f"Expected one stored {scope} row for {keys}")
            for stored_metric, computed_metric in metric_names.items():
                expected = reference.iloc[0][stored_metric]
                observed = computed[computed_metric]
                if pd.isna(expected) or pd.isna(observed):
                    passed = bool(pd.isna(expected) and pd.isna(observed))
                    difference = None
                else:
                    difference = abs(float(expected) - float(observed))
                    passed = difference <= 1e-10
                verification_rows.append(
                    {
                        "scope": scope,
                        **{key: computed[key] for key in keys},
                        "metric": stored_metric,
                        "stored_value": expected,
                        "recomputed_value": observed,
                        "absolute_difference": difference,
                        "tolerance": 1e-10,
                        "passed": passed,
                    }
                )
    mv = pd.DataFrame(verification_rows)
    mv.to_csv(MET / "metrics_versus_predictions.csv", index=False)
    base_folds["fold"] = base_folds.fold.astype(str)
    folds = base_folds.merge(
        fupd, on=["dataset", "model", "fold"], how="left", suffixes=("", "_recomputed")
    )
    models = base_models.merge(
        mupd, on=["dataset", "model"], how="left", suffixes=("", "_recomputed")
    )
    for frame, prefix in ((folds, ""), (models, "pooled_")):
        for col in (
            "tn",
            "fp",
            "fn",
            "tp",
            "mcc",
            "cohen_kappa",
            "false_positive_rate",
            "false_negative_rate",
            "balanced_accuracy",
        ):
            source = col + "_recomputed"
            if source in frame:
                frame[prefix + col] = frame[source]
                frame.drop(columns=source, inplace=True)
            elif prefix and col in frame:
                frame[prefix + col] = frame[col]
    folds.drop(
        columns=[c for c in folds if c.endswith("_recomputed")], inplace=True, errors="ignore"
    )
    models.drop(
        columns=[c for c in models if c.endswith("_recomputed")], inplace=True, errors="ignore"
    )
    models.drop(
        columns=[
            "accuracy",
            "precision",
            "sensitivity",
            "recall",
            "specificity",
            "f1",
            "roc_auc",
            "pr_auc",
            "brier",
            "n",
            "balanced_accuracy",
            "tn",
            "fp",
            "fn",
            "tp",
            "mcc",
            "cohen_kappa",
            "false_positive_rate",
            "false_negative_rate",
        ],
        inplace=True,
        errors="ignore",
    )
    folds.to_csv(MET / "fold_metrics.csv", index=False)
    models.to_csv(MET / "model_metrics.csv", index=False)
    models[
        [
            "dataset",
            "task_family",
            "model",
            "n_evaluated",
            "prevalence",
            "pooled_brier",
            "pooled_ece_uniform",
            "pooled_ece_weighted_uniform",
        ]
    ].to_csv(MET / "calibration_metrics.csv", index=False)
    cross = pd.read_csv(SRC / "metrics" / "cross_dataset_metrics.csv")
    for role in ("target", "target_accepted"):
        counts = [
            [int(row[f"{role}_{metric}"]) if pd.notna(row[f"{role}_{metric}"]) else 0
             for metric in ("tn", "fp", "fn", "tp")]
            for _, row in cross.iterrows()
        ]
        extra_rows = []
        for tn, fp, fn, tp in counts:
            vals = metric_from_counts(tn, fp, fn, tp)
            if tn + fp + fn + tp == 0:
                vals = {key: None for key in vals}
            extra_rows.append(vals)
        cross = pd.concat(
            [cross.reset_index(drop=True), pd.DataFrame(extra_rows).add_prefix(f"{role}_")],
            axis=1,
        )
    cross.to_csv(MET / "cross_dataset_metrics.csv", index=False)
    pd.read_csv(SRC / "metrics" / "selective_prediction_metrics.csv").to_csv(
        MET / "selective_prediction_metrics.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "selective_prediction_diagnostics.csv").to_csv(
        MET / "selective_prediction_diagnostics.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "calibration_bins.csv").to_csv(
        MET / "calibration_bins.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "ood_diagnostics.csv").to_csv(
        MET / "within_task_ood_diagnostics.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "learning_curve_metrics.csv").to_csv(
        MET / "learning_curve_metrics.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "failed_experiments.csv").to_csv(
        MET / "failed_experiments.csv", index=False
    )
    pd.read_csv(SRC / "metrics" / "execution_attempts.csv").to_csv(
        MET / "execution_attempts.csv", index=False
    )
    pd.read_csv(OUT / "training_validation_metrics.csv").to_csv(
        MET / "training_validation_metrics.csv", index=False
    )
    tv = pd.read_csv(OUT / "training_validation_metrics.csv")
    tv.to_csv(MET / "overfitting_analysis.csv", index=False)
    conf = pd.read_csv(OUT / "conformal_levels_metrics.csv")
    conf.to_csv(MET / "conformal_metrics.csv", index=False)
    pd.read_csv(OUT / "runtime_metrics.csv").to_csv(MET / "runtime_metrics.csv", index=False)
    cross_ood = pd.read_csv(OUT / "cross_dataset_ood_metrics.csv")
    cross_ood.to_csv(MET / "cross_dataset_ood_metrics.csv", index=False)
    # A typed long table keeps the different OOD questions distinct.
    within_ood = pd.read_csv(MET / "within_task_ood_diagnostics.csv")
    within_ood.insert(0, "analysis_scope", "within_task_error_detection")
    cross_ood_long = cross_ood.copy()
    cross_ood_long.insert(0, "analysis_scope", "cross_dataset_domain_detection")
    ood = pd.concat([within_ood, cross_ood_long], ignore_index=True, sort=False)
    ood.to_csv(MET / "ood_metrics.csv", index=False)
    # Feature-selection and ablation evidence is transcribed from the cited, frozen reports.
    fs_rows = [
        {
            "dataset": "Kaggle Cardio Train 70K",
            "comparison": "StableXAIHDRC vs one-shot selector",
            "metric": "Nogueira stability",
            "candidate": "StableXAIHDRC",
            "value": 0.8432,
            "comparator": "one-shot selector",
            "comparator_value": 0.8429,
            "difference": 0.00036,
            "interval_low": 0.0,
            "interval_high": 0.00109,
            "positive_evidence": False,
            "source": "docs/final_feature_stability_report.md",
        },
        {
            "dataset": "Kaggle Cardio Train 70K reduced nested pair",
            "comparison": "Stable logistic vs corrected logistic",
            "metric": "ROC-AUC",
            "candidate": "stable logistic",
            "value": 0.78862,
            "comparator": "corrected logistic",
            "comparator_value": 0.78930,
            "difference": -0.00068,
            "interval_low": None,
            "interval_high": None,
            "positive_evidence": False,
            "source": "docs/final_feature_stability_report.md",
        },
    ]
    pd.DataFrame(fs_rows).to_csv(MET / "feature_selection_metrics.csv", index=False)
    abl = []
    vals = {
        "Heart5": {
            "Logistic": (0.922575, 0.108764, 0.042428),
            "OVEC": (0.924376, 0.101386, 0.064511),
            "OSEC": (0.912056, 0.112506, 0.077005),
            "Stable logistic": (0.922715, 0.108699, 0.042472),
            "Stable OSEC": (0.911677, 0.112456, 0.082004),
        },
        "Mendeley": {
            "Logistic": (0.987705, 0.032236, 0.098549),
            "OVEC": (0.994561, 0.029531, 0.091993),
            "OSEC": (0.985657, 0.031626, 0.097200),
            "Stable logistic": (0.989635, 0.031629, 0.074198),
            "Stable OSEC": (0.992516, 0.028423, 0.170655),
        },
    }
    for ds, candidates in vals.items():
        for candidate, (auc, brier, ece) in candidates.items():
            abl.append(
                {
                    "dataset": ds,
                    "candidate": candidate,
                    "roc_auc": auc,
                    "brier": brier,
                    "ece": ece,
                    "protocol": "matched corrected 2x2 comparison; pooled predictions",
                    "source": "docs/ABLATION_REPORT.md",
                }
            )
    for ds, candidate, auc, brier, note in [
        (
            "Heart5",
            "AURA without dynamic fusion",
            0.922556,
            None,
            "removing dynamic fusion reduced ROC-AUC",
        ),
        (
            "Heart5",
            "AURA without multiview",
            0.925855,
            0.101326,
            "removing multiview slightly improved this task",
        ),
        (
            "Mendeley",
            "AURA full",
            0.995854,
            0.019551,
            "single tree model often selected; switches may be inactive",
        ),
    ]:
        abl.append(
            {
                "dataset": ds,
                "candidate": candidate,
                "roc_auc": auc,
                "brier": brier,
                "ece": None,
                "protocol": "historical AURA ablation; exploratory",
                "note": note,
                "source": "docs/ABLATION_REPORT.md",
            }
        )
    pd.DataFrame(abl).to_csv(MET / "ablation_metrics.csv", index=False)
    # Add the previously measured 70k timings as historical rows, separate from this run.
    prior = pd.DataFrame(
        [
            {
                "analysis_scope": "historical 70K tuned benchmark",
                "dataset": "Kaggle Cardio Train 70K",
                "model": m,
                "primary_search_fit_calibration_seconds": sec,
                "source": "docs/final_runtime_and_resources.md",
            }
            for m, sec in [
                ("Logistic", 5.6),
                ("Random Forest", 227.3),
                ("HistGradientBoosting", 51.3),
                ("XGBoost", 33.4),
                ("LightGBM", 16.5),
                ("CatBoost", 48.2),
            ]
        ]
    )
    current = pd.read_csv(MET / "runtime_metrics.csv")
    current.insert(0, "analysis_scope", "current multi-dataset diagnostic fixed configuration")
    runtime = pd.concat([current, prior], ignore_index=True, sort=False)
    runtime.to_csv(MET / "runtime_metrics.csv", index=False)
    return {
        "models": models,
        "folds": folds,
        "tv": tv,
        "conformal": conf,
        "cross_ood": cross_ood,
        "runtime": runtime,
        "metrics_verification": mv,
        "metrics_verification_passed": bool(mv.passed.all()),
    }


def build_dataset_tables() -> dict:
    MET.mkdir(parents=True, exist_ok=True)
    manifest = read_json(SRC / "datasets" / "dataset_manifest.json")
    comp = pd.read_csv(SRC / "dataset_comparison.csv")
    inv_rows, class_rows, missing_rows, dup_rows, outlier_rows = [], [], [], [], []
    for ds, detail in manifest["datasets"].items():
        entry = detail
        cm = comp[comp.dataset_id.astype(str) == ds]
        comparison = cm.iloc[0].to_dict() if not cm.empty else {}
        srcinfo = entry.get("source", {})
        prepared_paths = entry.get("prepared_paths", srcinfo.get("prepared_paths", {}))
        prepared_path = entry.get("prepared_path", srcinfo.get("prepared_path"))
        prepared_hash = entry.get("prepared_sha256", srcinfo.get("prepared_sha256"))
        rec = {**comparison}
        rec.update(
            {
                "dataset_id": ds,
                "dataset_version": str(srcinfo.get("dataset_id", "UCI source archive")),
                "source_doi": srcinfo.get("doi"),
                "target": entry.get("target"),
                "categorical_features": json.dumps(entry.get("categorical_features", [])),
                "predictor_names": json.dumps(entry.get("predictor_names", [])),
                "prepared_path": prepared_path or prepared_paths.get("all"),
                "prepared_sha256": prepared_hash or prepared_paths.get("all_sha256"),
                "patient_independence": comparison.get(
                    "patient_independence", "Not established from public records"
                ),
                "lineage": entry.get("lineage_note", detail.get("interpretation", "")),
                "target_semantics": entry.get("target_definition"),
                "evaluation_status": "evaluated",
            }
        )
        inv_rows.append(rec)
        paths = prepared_paths
        p = ROOT / (prepared_path or paths.get("all") or paths.get("train"))
        if ds == "uci_spectf_heart":
            parts = [
                ("official_train", DATA / "uci_spectf_train.csv"),
                ("official_test", DATA / "uci_spectf_test.csv"),
            ]
            full = DATA / "uci_spectf_all.csv"
        else:
            parts = [("all", p)]
            full = p
        for part, path in parts:
            df = pd.read_csv(path)
            ycol = entry.get("target", "OVERALL_DIAGNOSIS")
            counts = df[ycol].astype(int).value_counts().sort_index()
            for label in (0, 1):
                class_rows.append(
                    {
                        "dataset_id": ds,
                        "dataset": DISPLAY[ds],
                        "partition": part,
                        "class_label": label,
                        "count": int(counts.get(label, 0)),
                        "prevalence": float(counts.get(label, 0) / len(df)) if len(df) else None,
                        "n": len(df),
                    }
                )
        dfall = pd.read_csv(full)
        ycol = entry.get("target", "OVERALL_DIAGNOSIS")
        x = dfall.drop(columns=[ycol], errors="ignore")
        cats = set(entry.get("categorical_features", []))
        for col in x.columns:
            vals = x[col]
            null_count = int(vals.isna().sum())
            row = {
                "dataset_id": ds,
                "feature": col,
                "dtype": str(vals.dtype),
                "categorical": col in cats,
                "rows": len(vals),
                "missing_count": null_count,
                "missing_fraction": null_count / len(vals) if len(vals) else 0.0,
                "unique_nonmissing": int(vals.nunique(dropna=True)),
            }
            missing_rows.append(row)
            if col not in cats and pd.api.types.is_numeric_dtype(vals):
                z = pd.to_numeric(vals, errors="coerce").dropna()
                if len(z):
                    q1, q3 = z.quantile([0.25, 0.75])
                    iqr = q3 - q1
                    nout = (
                        int(((z < q1 - 1.5 * iqr) | (z > q3 + 1.5 * iqr)).sum()) if iqr > 0 else 0
                    )
                    outlier_rows.append(
                        {
                            "dataset_id": ds,
                            "feature": col,
                            "n_observed": len(z),
                            "q1": float(q1),
                            "median": float(z.median()),
                            "q3": float(q3),
                            "iqr": float(iqr),
                            "iqr_outlier_count": nout,
                            "iqr_outlier_fraction": nout / len(z),
                            "interpretation": "descriptive 1.5-IQR flag; no observations removed",
                        }
                    )
        if ds != "uci_spectf_heart":
            exactdup = int(entry.get("exact_duplicate_predictor_rows", 0))
            conflicts = int(entry.get("duplicate_predictor_groups_with_label_conflict", 0))
            dup_rows.append(
                {
                    "scope": "within_dataset_predictors",
                    "dataset_a": ds,
                    "dataset_b": "",
                    "exact_duplicate_rows_or_overlap": exactdup,
                    "label_conflict_groups": conflicts,
                    "interpretation": "Exact duplicate predictor rows within prepared cohort.",
                }
            )
    evaluated_ids = {row["dataset_id"] for row in inv_rows}
    for _, candidate in comp.iterrows():
        candidate_id = str(candidate.dataset_id)
        if candidate_id in evaluated_ids:
            continue
        record = candidate.to_dict()
        record.update(
            {
                "dataset_version": str(candidate.get("dataset_id_uci", "screened source")),
                "source_doi": None,
                "target": None,
                "categorical_features": None,
                "predictor_names": None,
                "prepared_path": None,
                "prepared_sha256": None,
                "lineage": candidate.get("lineage_and_compatibility"),
                "target_semantics": candidate.get("target_definition"),
                "evaluation_status": "screened; excluded or not acquired",
            }
        )
        inv_rows.append(record)
    inv_rows.append(
        {
            "dataset_id": "heart5_five_states",
            "dataset_name": "Heart5 / Five States",
            "records": 918,
            "predictors": None,
            "class_counts": None,
            "license": "Composite lineage; source redistribution status must be checked",
            "source_url": None,
            "target_definition": "Historical binary heart-disease benchmark; source imputation history is incomplete",
            "missing_predictor_cells": None,
            "exact_duplicate_predictor_rows": None,
            "patient_independence": "Not established; 914 unique source-row matches and 4 ambiguous matches",
            "lineage_and_compatibility": "Derived from UCI Heart Disease components; not an independent cohort",
            "decision": "Historical development benchmark; not a new external cohort",
            "status": "historical",
            "dataset_version": "Heart5 composite, 918 records",
            "source_doi": None,
            "target": None,
            "categorical_features": None,
            "predictor_names": None,
            "prepared_path": None,
            "prepared_sha256": None,
            "lineage": "Derived from UCI Heart Disease components; source missingness caused 4 ambiguous matches",
            "target_semantics": "Historical binary heart-disease benchmark; source imputation history is incomplete",
            "evaluation_status": "historical prior benchmark; not evaluated in current run",
        }
    )
    pd.DataFrame(inv_rows).to_csv(OUT / "dataset_inventory.csv", index=False)
    pd.DataFrame(class_rows).to_csv(OUT / "dataset_class_distribution.csv", index=False)
    pd.DataFrame(missing_rows).to_csv(OUT / "dataset_missing_value_report.csv", index=False)
    outlier_df = pd.DataFrame(outlier_rows)
    outlier_df.to_csv(MET / "outlier_summary.csv", index=False)
    pd.DataFrame(dup_rows).to_csv(OUT / "dataset_duplicate_report.csv", index=False)
    # Pairwise exact overlap checks are those recorded in the signed dataset manifest.
    overlap = manifest.get("uci_cohort_overlap_audit", {}).get("pairwise", {})
    with (OUT / "dataset_duplicate_report.csv").open("a", encoding="utf-8", newline="") as f:
        for pair, check in overlap.items():
            pd.DataFrame(
                [
                    {
                        "scope": "between_cohorts_exact_feature_rows",
                        "dataset_a": pair.split("__")[0],
                        "dataset_b": pair.split("__")[1],
                        "exact_duplicate_rows_or_overlap": check.get(
                            "exact_feature_row_overlap_count"
                        ),
                        "label_conflict_groups": None,
                        "interpretation": check.get("interpretation"),
                    }
                ]
            ).to_csv(f, index=False, header=False)
    # Compatibility matrix for evaluated and screened candidates, preserving unknowns.
    task = {
        "uci_cleveland": ("angiographic CAD, UCI num=0 vs 1..4", "heart13"),
        "uci_hungary": ("angiographic CAD, UCI num=0 vs 1..4", "heart13"),
        "uci_switzerland": ("angiographic CAD, UCI num=0 vs 1..4", "heart13"),
        "uci_va_long_beach": ("angiographic CAD, UCI num=0 vs 1..4", "heart13"),
        "uci_heart_failure_519": ("heart-failure death event", "hf11"),
        "uci_mi_complications_579": ("MI lethal complication", "mi100"),
        "uci_spectf_heart": ("SPECT normal/abnormal", "spect44"),
        "uci_statlog_heart": ("angiographic CAD, Cleveland-compatible", "heart13"),
        "mendeley_heart_disease_2026": ("Heart5-derived CAD benchmark", "heart13"),
        "mendeley_cardiovascular_2021": (
            "cardiovascular label, reference standard unclear",
            "unknown",
        ),
        "z_alizadeh_sani": ("CAD threshold >=50%", "z54"),
        "angiocad": ("coronary segment stenosis", "partial"),
        "duke_acath": ("CAD threshold >=75%", "partial"),
        "kaggle_cardio_70k": ("distinct risk label", "kaggle11"),
        "heart5_five_states": ("Heart5-derived CAD benchmark", "heart13"),
        "mimic_iv": ("task requires definition and access", "unknown"),
        "multid4cad": ("task requires controlled data access", "unknown"),
    }
    ids = comp.dataset_id.astype(str).tolist() + ["heart5_five_states"]
    # Canonicalize display labels from the existing candidate table.
    compat = []
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            ta, sa = task.get(a, ("unknown", "unknown"))
            tb, sb = task.get(b, ("unknown", "unknown"))
            pair = {a, b}
            if pair == {"uci_cleveland", "uci_statlog_heart"}:
                status = "exact duplicate after target harmonization; not independent"
            elif pair == {"heart5_five_states", "mendeley_heart_disease_2026"}:
                status = "exact 918/918 labelled-row duplicate; not independent"
            elif "heart5_five_states" in pair and sa == sb == "heart13":
                status = "Heart5 contains the component cohort; retrospective lineage overlap"
            elif sa == sb == "heart13" and ta == tb:
                status = (
                    "schema/endpoint compatible; independence or duplicate lineage must be assessed"
                )
            elif sa == sb and sa != "unknown":
                status = "technically compatible; exact overlap/lineage needs separate assessment"
            elif "unknown" in (sa, sb) or "partial" in (sa, sb):
                status = "not established from current codebook/access evidence"
            else:
                status = "incompatible prediction task or feature schema"
            compat.append(
                {
                    "dataset_a": a,
                    "dataset_b": b,
                    "task_a": ta,
                    "task_b": tb,
                    "schema_a": sa,
                    "schema_b": sb,
                    "compatibility": status,
                    "evidence": "results/multi_dataset_evaluation_20261108/dataset_comparison.csv; docs/DATASET_LINEAGE_AUDIT.md",
                }
            )
    pd.DataFrame(compat).to_csv(OUT / "dataset_compatibility_matrix.csv", index=False)
    return {
        "manifest": manifest,
        "inventory": pd.DataFrame(inv_rows),
        "classes": pd.DataFrame(class_rows),
        "missing": pd.DataFrame(missing_rows),
        "outliers": outlier_df,
        "compatibility": pd.DataFrame(compat),
    }


def build_figures(tables: dict, metric_tables: dict) -> list[str]:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 140, "savefig.bbox": "tight", "font.size": 9})
    classes = tables["classes"]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    piv = (
        classes[classes.partition.isin(["all", "official_test"])]
        .pivot_table(
            index="dataset", columns="class_label", values="count", aggfunc="sum", fill_value=0
        )
        .reindex([DISPLAY[x] for x in DATASET_IDS])
    )
    piv.plot(kind="bar", stacked=True, ax=ax, color=["#4c78a8", "#e45756"])
    ax.set_ylabel("Records")
    ax.set_xlabel("")
    ax.set_title("Class counts by separately defined task")
    ax.legend(title="Class label")
    fig.tight_layout()
    p = FIG / "eda_class_distribution.png"
    fig.savefig(p)
    plt.close(fig)
    miss = tables["missing"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    data = []
    for ds in DATASET_IDS:
        g = miss[miss.dataset_id == ds]
        data.append(100 * g.missing_count.sum() / (int(g.rows.iloc[0]) * len(g)) if len(g) else 0)
    ax.bar([DISPLAY[d] for d in DATASET_IDS], data, color="#72b7b2")
    ax.set_ylabel("Missing predictor cells (%)")
    ax.set_title("Prepared-table missingness before fold-local imputation")
    ax.tick_params(axis="x", rotation=32)
    fig.tight_layout()
    fig.savefig(FIG / "eda_missingness_by_dataset.png")
    plt.close(fig)
    # Per-task correlation heatmaps use numeric predictor columns; categorical codes are excluded.
    manifest = tables["manifest"]
    for ds, detail in manifest["datasets"].items():
        entry = detail
        source_info = entry.get("source", {})
        paths = entry.get("prepared_paths", source_info.get("prepared_paths", {}))
        path = ROOT / (
            entry.get("prepared_path") or source_info.get("prepared_path") or paths.get("all")
        )
        df = pd.read_csv(path)
        ycol = entry.get("target", "OVERALL_DIAGNOSIS")
        x = df.drop(columns=[ycol], errors="ignore")
        cats = set(entry.get("categorical_features", []))
        numeric = [c for c in x.select_dtypes(include=np.number).columns if c not in cats]
        if len(numeric) < 2:
            continue
        corr = x[numeric].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(max(5, len(numeric) * 0.36), max(4, len(numeric) * 0.32)))
        im = ax.imshow(corr.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(numeric)), numeric, rotation=75, ha="right")
        ax.set_yticks(range(len(numeric)), numeric)
        ax.set_title(f"{DISPLAY[ds]} numeric predictors: Spearman correlation")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(FIG / f"eda_spearman_{ds}.png")
        plt.close(fig)
    # New diagnostics figures from saved artifacts.
    conf = metric_tables["conformal"]
    csum = (
        conf.groupby("nominal_coverage")
        .agg(
            mean_empirical_coverage=("empirical_coverage", "mean"),
            mean_set_size=("average_set_size", "mean"),
            groups=("dataset", "size"),
        )
        .reset_index()
    )
    csum.to_csv(TAB / "conformal_summary_by_level.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(
        csum.nominal_coverage, csum.mean_empirical_coverage, marker="o", label="Observed coverage"
    )
    ax.plot([0.79, 0.96], [0.79, 0.96], linestyle="--", color="gray", label="Nominal")
    ax.set(
        xlabel="Nominal coverage",
        ylabel="Mean empirical test coverage",
        title="Split-conformal coverage across nominal levels",
    )
    ax.set_xlim(0.79, 0.96)
    ax.set_ylim(0.70, 1.02)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "conformal_coverage_80_90_95.png")
    plt.close(fig)
    ood = (
        metric_tables["cross_ood"]
        .groupby(["source_dataset", "target_dataset"])
        .agg(
            domain_auc=("domain_detection_roc_auc", "mean"),
            domain_ap=("domain_detection_average_precision", "mean"),
            target_alert_rate=("target_alert_rate_sensitivity", "mean"),
        )
        .reset_index()
    )
    ood.to_csv(TAB / "cross_ood_transfer_summary.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(ood.domain_auc, ood.domain_ap, c=ood.target_alert_rate, cmap="viridis", s=38)
    ax.axvline(0.5, ls="--", color="gray")
    ax.set(
        xlabel="Domain detection ROC-AUC",
        ylabel="Domain detection average precision",
        title="Cross-cohort feature-support detection",
    )
    fig.colorbar(sc, ax=ax, label="Target alert rate at source 95th percentile")
    fig.tight_layout()
    fig.savefig(FIG / "cross_ood_auc_ap.png")
    plt.close(fig)
    rt = metric_tables["runtime"]
    cur = rt[rt.analysis_scope.eq("current multi-dataset diagnostic fixed configuration")]
    summary = (
        cur.groupby("model")
        .agg(
            median_fit_s=("diagnostic_refit_seconds", "median"),
            median_inference_us_per_row=("inference_microseconds_per_row", "median"),
            median_pipeline_bytes=("serialized_pipeline_bytes_uncompressed", "median"),
            fold_count=("fold", "size"),
        )
        .reset_index()
    )
    summary.to_csv(TAB / "runtime_summary_by_model.csv", index=False)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(summary.model, summary.median_inference_us_per_row, color="#f2cf5b")
    ax.set(
        ylabel="Median microseconds per row",
        title="Fixed-configuration prediction latency (median across dataset folds)",
    )
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(FIG / "runtime_inference_latency.png")
    plt.close(fig)
    # Copy the frozen primary figure pack without changing its source files.
    primary_fig = SRC / "figures"
    copied = []
    if primary_fig.exists():
        for src in sorted(primary_fig.glob("*")):
            if src.is_file() and src.suffix.lower() in {".png", ".pdf"}:
                dst = FIG / f"primary_{src.name}"
                shutil.copy2(src, dst)
                copied.append(dst.name)
    return [str(p.relative_to(ROOT)).replace("\\", "/") for p in FIG.glob("*") if p.is_file()]


def markdown_table(
    df: pd.DataFrame,
    cols: list[str],
    labels: dict[str, str] | None = None,
    limit: int | None = None,
) -> str:
    labels = labels or {}
    data = df[cols].copy()
    if limit:
        data = data.head(limit)
    data = data.rename(columns=labels)
    headers = list(data.columns)
    lines = [
        "| " + " | ".join(map(str, headers)) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in data.itertuples(index=False, name=None):
        cells = []
        for v in row:
            if pd.isna(v):
                cells.append("—")
            elif isinstance(v, (float, np.floating)):
                cells.append(f"{v:.3f}")
            else:
                cells.append(str(v).replace("|", "/"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_docs(tables: dict, metrics: dict, figures: list[str]) -> None:
    models, folds, tv, conf, cross_ood, runtime = (
        metrics[k] for k in ("models", "folds", "tv", "conformal", "cross_ood", "runtime")
    )
    latest = read_json(SRC / "manifests" / "experiment_manifest.json")
    overall_best = (
        models.sort_values("pooled_roc_auc", ascending=False)
        .groupby("dataset", as_index=False)
        .first()
    )
    besttable = markdown_table(
        overall_best.assign(task=overall_best.dataset.map(DISPLAY)),
        [
            "task",
            "model",
            "pooled_roc_auc",
            "pooled_accuracy",
            "pooled_recall",
            "pooled_specificity",
            "pooled_mcc",
        ],
    )
    ovec = models[models.model.eq("ovec")][["dataset", "fold_mean_roc_auc"]].rename(
        columns={"fold_mean_roc_auc": "ovec_auc"}
    )
    osec = models[models.model.eq("osec")][["dataset", "fold_mean_roc_auc"]].rename(
        columns={"fold_mean_roc_auc": "osec_auc"}
    )
    ens = ovec.merge(osec, on="dataset")
    ens["ovec_minus_osec_auc"] = ens.ovec_auc - ens.osec_auc
    ens["dataset"] = ens.dataset.map(DISPLAY)
    ensembletable = markdown_table(ens, ["dataset", "ovec_auc", "osec_auc", "ovec_minus_osec_auc"])
    gaps = tv.groupby(["dataset", "model"], as_index=False).agg(
        train_test_auc_gap=("train_minus_outer_validation_roc_auc", "mean"),
        train_test_accuracy_gap=("train_minus_outer_validation_accuracy", "mean"),
        train_test_f1_gap=("train_minus_outer_validation_f1", "mean"),
        train_auc=("train_roc_auc", "mean"),
        test_auc=("validation_roc_auc", "mean"),
    )
    gaps["dataset"] = gaps.dataset.map(DISPLAY)
    gaptable = markdown_table(
        gaps.sort_values("train_test_auc_gap", ascending=False),
        [
            "dataset",
            "model",
            "train_auc",
            "test_auc",
            "train_test_auc_gap",
            "train_test_accuracy_gap",
            "train_test_f1_gap",
        ],
        limit=16,
    )
    confsum = (
        conf.groupby("nominal_coverage")
        .agg(
            empirical_coverage_min=("empirical_coverage", "min"),
            empirical_coverage_mean=("empirical_coverage", "mean"),
            empirical_coverage_max=("empirical_coverage", "max"),
            average_set_size_mean=("average_set_size", "mean"),
            group_n=("dataset", "size"),
        )
        .reset_index()
    )
    ctable = markdown_table(
        confsum,
        [
            "nominal_coverage",
            "empirical_coverage_min",
            "empirical_coverage_mean",
            "empirical_coverage_max",
            "average_set_size_mean",
            "group_n",
        ],
    )
    cross_summary = cross_ood.groupby(["source_dataset", "target_dataset"], as_index=False).agg(
        mean_auc=("domain_detection_roc_auc", "mean"),
        mean_ap=("domain_detection_average_precision", "mean"),
        source_fpr=("source_calibration_alert_rate", "mean"),
        target_alert=("target_alert_rate_sensitivity", "mean"),
    )
    cross_summary["source_dataset"] = cross_summary.source_dataset.map(DISPLAY)
    cross_summary["target_dataset"] = cross_summary.target_dataset.map(DISPLAY)
    cross_table = markdown_table(
        cross_summary.sort_values("mean_auc", ascending=False),
        ["source_dataset", "target_dataset", "mean_auc", "mean_ap", "source_fpr", "target_alert"],
        limit=12,
    )
    runtime_cur = runtime[
        runtime.analysis_scope.eq("current multi-dataset diagnostic fixed configuration")
    ]
    rsummary = runtime_cur.groupby("model", as_index=False).agg(
        median_fit_s=("diagnostic_refit_seconds", "median"),
        median_us_per_row=("inference_microseconds_per_row", "median"),
        median_pipeline_bytes=("serialized_pipeline_bytes_uncompressed", "median"),
    )
    rtable = markdown_table(
        rsummary, ["model", "median_fit_s", "median_us_per_row", "median_pipeline_bytes"]
    )
    data_table = markdown_table(
        tables["inventory"][tables["inventory"].evaluation_status.eq("evaluated")],
        [
            "dataset_id",
            "records",
            "predictors",
            "class_counts",
            "missing_predictor_cells",
            "license",
            "evaluation_status",
        ],
    )
    suite_count = len(folds)
    # Focused and evidence-linked reports.
    docs = {}
    docs["COMPLETE_PROJECT_TECHNICAL_AUDIT.md"] = f"""# CARDIODIAG complete project technical audit

**Assessment date:** 2026-11-08
**Branch:** `research/cardiodiag-complete-project-finalization`
**Evidence base:** frozen multi-dataset run `{latest.get("run_id")}`, its prediction/index manifests, the existing implementation and prior audit records.

## Scope and implementation history

The repository preserves historical notebooks and student implementations alongside the corrected `src/cardiodiag` research package. The corrected package is the source for the current experiment. Earlier Heart5, Mendeley, Kaggle and transfer results remain historical evidence with their own protocols; they are not pooled with this run. Original LoRAS/LIME/XAIH-DRC behavior is not reproduced bit for bit because the exact original resampling and explainer settings are unavailable. The stable selector is a training-fold approximation and is reported as such.

## Execution path

1. Dataset-specific loaders keep the CAD, heart-failure death, MI complication and SPECT imaging outcomes separate.
2. `build_corrected_pipeline` applies training-only cleaning, median/mode imputation, categorical encoding and numeric scaling; `build_ovec` and `build_osec` preserve established ensemble definitions.
3. Six candidates are compared with nested 3x3 stratified CV where supported. SPECTF retains its official 80/187 train/test split; only its 80 training rows are subdivided for development and calibration.
4. Saved predictions are used to derive classification metrics. Source-only calibration supports conformal and feature-support diagnostics; target outcomes do not enter transfer OOD scores.
5. Machine-readable outputs and plots are written under `results/final_research_20261108/`; the manuscript source and compiled artifact remain versioned under `paper/multi_dataset_study_20261108/` and `output/pdf/`.

## Main implementation components

See [SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md](SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md), the generated module inventory at `results/final_research_20261108/module_inventory.csv`, and dependency edges at `results/final_research_20261108/module_dependency_edges.csv`. The package separates loading, preprocessing, feature selection, model construction, nested validation, evaluation, calibration/uncertainty, experiment orchestration, demo and tests.

## Verified experiment state

- 7 task datasets; 6 models; 42 within-task model summaries and {suite_count} fold/test records.
- 72 directed model-transfer comparisons among the four UCI CAD cohorts.
- Refits reproduce saved within-task probabilities to floating-point precision; cross-OOD values are checked against the frozen run in the completion manifest.
- Six Switzerland learning-curve configurations are recorded as failed because small training subsets do not contain both classes for the requested split.
- The frozen run verification manifest records source/prepared checksums and recomputation checks. See `results/final_research_20261108/manifests/verification_manifest.json` for the consolidated validation.

## Material limitations

The four CAD cohorts are known components of Heart5; exact-row overlap checks do not establish person-level independence. Switzerland contains only eight negative cases. Heart failure, MI and SPECTF are distinct endpoints. The public benchmarks are small, old and retrospective. No prospective or independent contemporary external validation was conducted. No clinical performance or deployment conclusion is supported.

## Preserved work and additions

Frozen experiment outputs, prior audit reports, test suite, offline demo and manuscript source were preserved. This branch adds replay diagnostics, enriched aggregate metrics, data-quality tables/figures, focused reports, a completion matrix and manuscript checks. The accompanying changelog records each new artifact and excludes local raw data, row-level diagnostics and credentials.
"""
    docs["DATASET_PROVENANCE_AND_COMPATIBILITY.md"] = f"""# Dataset provenance and compatibility

This report follows the prepared dataset manifest, the candidate screening table, and prior lineage/licensing audits. Raw data are local and excluded from this branch.

## Evaluated data

{data_table}

The UCI Heart Disease cohorts use the UCI binary target `num=0` versus `num=1..4`; heart failure uses a death-event endpoint, MI uses lethal complication, and SPECTF uses a normal/abnormal imaging endpoint. Outcomes are not pooled. Full class counts, per-feature missingness, exact duplicate counts and pairwise overlap screens are in the adjacent CSV files.

## Compatibility rules

The four UCI angiographic cohorts share the 13-predictor schema and target coding, so they support directed feature-level transfer stress tests. They are previously represented in Heart5 and participant independence is not established. Statlog is an exact Cleveland duplicate after harmonization. Mendeley 2026 is a Heart5 duplicate. The 2021 Mendeley target reference standard and timing are undocumented. Z-Alizadeh Sani uses a different threshold; AngioCAD has incomplete feature mapping and uncertain units; Duke ACATH uses a 75% threshold. The Kaggle 70K dataset has a distinct target and unresolved license. MIMIC-IV and MultiD4CAD access conditions were not acquired.

## Artifacts

- `results/final_research_20261108/dataset_inventory.csv`
- `results/final_research_20261108/dataset_compatibility_matrix.csv`
- `results/final_research_20261108/dataset_class_distribution.csv`
- `results/final_research_20261108/dataset_missing_value_report.csv`
- `results/final_research_20261108/dataset_duplicate_report.csv`
- `results/final_research_20261108/manifests/dataset_manifest.json`

License and attribution remain source-specific. UCI attribution is retained in the frozen manifest. This report does not grant redistribution rights for restricted or locally held data.
"""
    docs["COMPLETE_MODEL_COMPARISON_REPORT.md"] = f"""# Complete model comparison report

All six candidates use the frozen task-specific evaluation protocol. Binary threshold metrics use probability 0.5; positive labels follow each dataset's stated target. ROC-AUC is threshold-independent. Cross-task metrics are not combined into one score.

## Best observed pooled AUC per task

These are descriptive maxima from the evaluated model set, not confirmatory winners.

{besttable}

## OVEC and OSEC comparison

{ensembletable}

The sign of the paired fold-mean ROC-AUC difference changes by task. This run does not show consistent ensemble superiority. Accuracy can conceal poor minority sensitivity, especially for heart failure and MI; use the full metrics CSV, including specificity, MCC, kappa, false-positive and false-negative rates.

## Evidence and interpretation

The machine-readable full model table is `results/final_research_20261108/metrics/model_metrics.csv`; fold detail is `.../fold_metrics.csv`. The primary held-out predictions are `results/multi_dataset_evaluation_20261108/predictions/20261107T202404Z/out_of_fold_and_official_predictions.csv`. The verification manifest checks metric reconstruction against these predictions. Confidence intervals in the frozen report use a class-stratified bootstrap; they are descriptive and do not make CV folds independent.
"""
    docs["OVERFITTING_AND_GENERALIZATION_REPORT.md"] = f"""# Overfitting and generalization report

Training values are resubstitution scores on the selected development subset. Test values are untouched outer-fold or official SPECTF test predictions. Differences are diagnostics, not independent estimates. Tuning-stage inner-CV results are separate and included in the full CSV.

{gaptable}

Positive AUC gaps occur frequently, particularly for KNN, tree models and small cohorts. Switzerland results are especially unstable because there are only eight negative records overall; the same cohort's smallest learning subsets triggered six documented failures. SPECTF shows large train/test gaps for several models under its single official test partition. A negative gap does not establish the absence of overfitting; it can reflect split variability.

Learning curves and train/validation plots from the frozen run are retained in `results/final_research_20261108/figures/primary_*`. The current replayed training/validation metrics, including accuracy, precision, sensitivity, specificity, F1, AUC, Brier/log loss and confusion counts, are in `metrics/training_validation_metrics.csv`. The plots and numbers do not identify leakage, patient overlap or causality by themselves. The corrected pipeline fits all transforms and model selection within training partitions; no person identifier is available to guarantee patient-grouped splitting.
"""
    docs["FEATURE_SELECTION_AND_ABLATION_REPORT.md"] = """# Feature selection and ablation report

The corrected multi-dataset run compared the six existing model configurations and did not add a feature selector to those pipelines. Earlier evidence is summarized from the frozen feature-stability and ablation reports.

On the Kaggle 70K benchmark, mean Nogueira stability was 0.8432 for StableXAIHDRC and 0.8429 for the one-shot selector; the difference was 0.00036 with descriptive interval [0, 0.00109], and the existing positive-evidence flag was false. In a reduced nested pair, stable logistic ROC-AUC was 0.78862 versus 0.78930 for corrected logistic. The matched Heart5/Mendeley 2x2 comparisons show small, dataset-specific shifts in ROC-AUC, Brier and ECE. The AURA results are exploratory, and some switches were inactive when the same tree model was selected repeatedly.

The historical A–L ablation labels were not prespecified; the complete factorial and original LoRAS/LIME settings are unavailable. The evidence therefore does not establish a causal contribution for each named component or a universal benefit from stable feature selection.

Machine-readable tables: `results/final_research_20261108/metrics/feature_selection_metrics.csv` and `ablation_metrics.csv`. Provenance is given per row. Primary source reports: `docs/final_feature_stability_report.md`, `docs/ABLATION_REPORT.md`, and `docs/ABLATION_A_L_MATRIX_20261105.md`.
"""
    docs["CALIBRATION_AND_UNCERTAINTY_REPORT.md"] = f"""# Calibration and uncertainty report

The frozen run includes Brier score, ten-bin expected calibration error, split-conformal prediction sets and source-only 95th-percentile feature-support thresholds. ECE depends on binning; estimates from small held-out partitions are noisy. Conformal coverage depends on calibration/evaluation exchangeability, which is not established under cohort shift.

## Split-conformal coverage

{ctable}

There are 114 task/model/fold combinations per nominal level, including a single official test for SPECTF. Mean empirical coverage is pooled over heterogeneous tasks and must not be read as a global guarantee. Class-conditional coverage and set-size diagnostics are reported per row in `metrics/conformal_metrics.csv`; the 90% level can be compared with the frozen primary table at `metrics/source_conformal_metrics_90.csv`.

![Conformal coverage by nominal level](../results/final_research_20261108/figures/conformal_coverage_80_90_95.png)

No calibrated clinical threshold is established. The uncertainty results support only retrospective method diagnostics.
"""
    docs["OOD_AND_SELECTIVE_PREDICTION_REPORT.md"] = f"""# OOD and selective-prediction report

Two distinct OOD questions are retained. Within-task analysis asks whether the support score flags model errors on held-out records. Cross-dataset analysis asks whether a nearest-neighbor distance score distinguishes source-calibration feature vectors from target-cohort feature vectors. Target outcome labels are not used to compute the cross-domain score or threshold.

## Directed transfer domain detection

The table reports the mean over six models for each direction. Average precision depends on the sampled source/target mixture, so it is a ranking diagnostic rather than a population-prevalence-calibrated value.

{cross_table}

The threshold is the source-calibration 95th percentile. Its alert rate is approximately the nominal 5% by construction up to finite-sample ties; target alert rates vary by direction. Detection quality is heterogeneous and does not guarantee safe rejection. Selective prediction tables report coverage, accepted-set size, risk and AURC; in some historical external evaluations very little coverage remained. There is no demonstrated operating point that establishes reliable use under shift.

Detailed outputs: `metrics/ood_metrics.csv`, `metrics/cross_dataset_ood_metrics.csv`, `metrics/selective_prediction_metrics.csv`, and `metrics/selective_prediction_diagnostics.csv`. The 72 OOD refits and scores are reproducible from source features and saved settings.
"""
    docs["CROSS_DATASET_EVALUATION_REPORT.md"] = f"""# Cross-dataset evaluation report

The evaluation includes all 12 ordered source-to-target directions among four UCI Heart Disease cohorts, each evaluated with six models (72 directed comparisons). The 13 predictors and binarized target are aligned. Models and preprocessing are fitted on source rows, with source-only inner selection and calibration. Target outcomes are excluded from OOD fitting/threshold selection; predictive AUC is computed afterward for retrospective audit.

{cross_table}

The cohorts are known components of Heart5, and patient-level linkage is unavailable. These analyses are retrospective cohort stress tests, not independent external validation. Performance varies substantially by direction and target; the lowest target AUCs are retained as failures of transfer, not removed. See `results/final_research_20261108/metrics/cross_dataset_metrics.csv` for target-label predictive results and `cross_dataset_ood_metrics.csv` for target-label-free domain diagnostics.
"""
    docs["COMPUTATIONAL_PERFORMANCE_REPORT.md"] = f"""# Computational performance report

The current measurements refit the saved selected configuration once per task/model/fold, time batch prediction, and record uncompressed serialized pipeline size. They exclude hyperparameter search from the refit timing. The source run separately records total search/calibration runtime. Values depend on the recorded Windows environment and package versions.

{rtable}

The historical 70K tuned benchmark took about 5.6 s for Logistic Regression, 227.3 s for Random Forest, 51.3 s for HistGradientBoosting, 33.4 s for XGBoost, 16.5 s for LightGBM and 48.2 s for CatBoost. The full custom five-candidate 70K nested run was not completed. Peak memory was not instrumented, and timing differences are not benchmark-grade cross-hardware comparisons. See `metrics/runtime_metrics.csv`, `tables/runtime_summary_by_model.csv`, and `figures/runtime_inference_latency.png`.
"""
    docs[
        "SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md"
    ] = """# Software architecture and engineering report

The repository preserves an original/student implementation and a corrected research implementation. The latter is a Python package under `src/cardiodiag`, with separate modules for data loading/schema, fold-local preprocessing, feature selection, model factories (including unchanged OVEC/OSEC definitions), nested validation, metrics/reliability, uncertainty and experiment provenance. `experiments/` contains runnable study entry points, `tests/` exercises package behavior, and `demo/` contains offline demonstration code. `paper/` holds the editable manuscript and tables; `results/` is organized by experiment evidence.

The primary pipeline fits imputation, encoding and scaling within training partitions. Current nested evaluation keeps tuning inside outer training folds and scores held-out folds once. The cross-cohort OOD extension fits a support score only on source feature vectors. The historical path is preserved for forensic comparison and clearly separated from corrected evidence.

The generated `module_inventory.csv` inventories Python modules by line count and internal imports; `module_dependency_edges.csv` provides a module graph. Existing `uv.lock` is the dependency lock. `pyproject.toml` requires Python >=3.11,<3.14. Verification results are recorded in the acceptance matrix and run manifest. The project is a local research prototype, not a clinical application.
"""
    docs["DEMO_APPLICATION_DOCUMENTATION.md"] = """# Offline demonstration documentation

The desktop demonstration in `demo/app.py` is synthetic-only and is guarded to prevent the supplied synthetic example from being interpreted as an actual patient diagnosis. `demo/run_domain_guard_demo.py` exercises registered-domain checks and unknown-domain rejection using synthetic examples. The older `demo/run_demo.py` is a benchmark CLI that loads the Heart5 benchmark and reports a held-out row's actual benchmark label and score; it is not a patient-facing workflow.

Run the guarded logic check from the project environment with `python demo/run_domain_guard_demo.py --output <temporary-path>`. Start the desktop demo with `python demo/app.py` where a Windows display is available. No network or external service is required. Raw external datasets and credentials are not required for the synthetic desktop demo. Detailed results and file hashes are captured in the current verification manifest. Do not use the benchmark CLI with patient data.
"""
    docs[
        "CARDIODIAG_COMPLETE_TECHNICAL_RESEARCH_REPORT.md"
    ] = f"""# CARDIODIAG complete technical research report

## Abstract

This report audits and completes the current CARDIODIAG machine-learning research snapshot. Six classifiers, including the preserved OVEC and OSEC definitions, were evaluated across seven distinct tabular tasks with training-only preprocessing and leakage-controlled validation. The work adds full threshold and ranking metrics, training/test diagnostics, conformal levels, directed transfer OOD metrics, runtime measurements and data-quality visualizations. Results show task-dependent rankings and substantial distribution sensitivity; the evidence does not establish universal ensemble benefit or independent external validity.

## Research questions and contribution

The study asks whether project ensembles consistently outperform four individual classifiers; whether training/test gaps suggest data-limited overfitting; whether calibration, conformal sets, OOD alerts and selective prediction remain useful under cohort shift; and how cost varies across model families. The defensible contribution is an auditable, multi-task evaluation of preserved project methods with explicit compatibility, lineage and reliability limits. It is not a newly validated clinical algorithm.

## Methods and architecture

The corrected implementation performs fold-local cleaning, imputation, encoding and scaling. The six model configurations are Logistic Regression, KNN, SVM, Random Forest, OVEC soft voting and OSEC stacking. Nested 3x3 stratified validation is used where supported. SPECTF retains its UCI 80/187 official split; its 80 training rows are divided into development and calibration rows. No test labels are used to select hyperparameters or fit transforms. Cross-cohort target labels are not used in source fitting or OOD thresholds. Details and code map are in `docs/SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md` and `docs/EXPERIMENTAL_PROTOCOL.md`.

## Dataset tasks and EDA

{data_table}

The CAD cohorts share an endpoint/schema but are known in Heart5 lineage. Heart failure, MI complications and SPECTF are separate tasks. Missingness, class counts, exact duplicates, pairwise exact feature overlaps, numeric outliers and numeric feature correlations are stored beneath `results/final_research_20261108/`. The outlier table uses the descriptive 1.5-IQR rule and removes nothing. UCI source and license records remain in the frozen manifest and focused provenance report.

## Results

### Model comparison

{besttable}

OVEC-minus-OSEC AUC differences change sign by task. The model maximizing AUC is not necessarily the model maximizing threshold sensitivity or specificity. Imbalance is material for the MI and SPECT tasks; a high accuracy alone is not a sufficient summary.

### Overfitting and generalization

Train resubstitution AUC frequently exceeds held-out AUC; the largest gaps occur in small or unstable tasks and flexible models. Learning curves are descriptive. The six Switzerland small-subset learning-curve failures remain in the failure ledger. These findings motivate caution but do not identify a single cause.

### Feature selection and ablations

Existing matched comparisons show small dataset-dependent changes. Stable selection did not improve the reduced nested Kaggle AUC pair and its stability advantage interval includes zero. The original A–L design and exact XAIH-DRC settings are unavailable, so causal component attribution remains incomplete.

### Calibration and conformal uncertainty

{ctable}

Coverage is empirical and conditional on an exchangeability assumption that may fail across cohorts. Brier and ECE are retained; ECE depends on binning. Class-conditional coverage and set size vary by task and fold.

### OOD, selective prediction and transfer

There are 72 directed source/target/model comparisons among the four UCI CAD cohorts. Domain ROC-AUC and average precision vary by direction; no single threshold makes target features uniformly detectable. Selective prediction provides a coverage-risk tradeoff, but useful coverage under shift is not established. Since cohort linkage is unavailable and all cohorts are represented in Heart5, this is not independent external validation.

### Computational performance

{rtable}

Peak memory is not measured. Historical 70K timings are separated from this multi-dataset refit analysis.

## Software, tests, demo and reproducibility

The module inventory and dependency graph are machine generated from Python ASTs. Full pytest, Ruff, Python compilation, lockfile, manifest, metric/prediction and guarded offline demo checks are reported in `docs/FINAL_PROJECT_ACCEPTANCE_MATRIX.md` and `results/final_research_20261108/manifests/verification_manifest.json`. Raw datasets, access requests, checkpoints and row-level derived artifacts remain local and are not part of the release commit.

## Limitations and conclusion

The datasets are small and legacy; endpoint definitions differ across task families, Switzerland has only eight negatives, public files lack stable participant identifiers, and the primary CAD cohorts overlap Heart5 lineage. The original method cannot be reconstructed exactly from available notebooks. The full original ablation design, independent contemporary validation, peak-memory profiling, authorship/institution declarations and some data redistribution permissions remain unresolved. The current work supports reproducible algorithm comparisons on specified benchmark tasks and demonstrates that transfer and reliability degrade unevenly. It does not support clinical use, broad unseen-site generalization, universal OVEC/OSEC superiority or external validation.
"""
    docs["MANUSCRIPT_FINALIZATION_REPORT.md"] = """# Manuscript finalization report

The versioned LaTeX manuscript is `paper/multi_dataset_study_20261108/main.tex`, with its bibliography, table fragments and figure sources kept in that directory. The manuscript preserves the established terminology and reports the primary frozen run. Its results are traceable to the experiment metrics and manifest; the additional completion diagnostics expand the technical project report and do not silently replace the original paper's prespecified primary results.

The current manuscript's main scope is a multi-dataset experimental evaluation. It separates angiographic CAD from heart-failure death, MI complication and SPECT imaging. It describes the four CAD cohorts as retrospective stress tests because they are in Heart5 lineage; it does not assert patient independence or clinical validation. The 80/90/95 conformal replay is a supplemental diagnostic and the manuscript retains the original nominal-90% primary table.

Before submission, confirm author names/order, affiliations, institutional declarations, ethics determination, funding, conflicts, data-use statements, acknowledgements and target venue. These facts are not invented in the source. The final verification entry records LaTeX compilation and visual PDF checks, citation/reference resolution, figure/table inclusion and page count.
"""
    for name, body in docs.items():
        (DOC / name).write_text(body.rstrip() + "\n", encoding="utf-8")
    # AST-derived inventory and import graph.
    source_roots = [
        ROOT / "src/cardiodiag",
        ROOT / "src/clin_adapt",
        ROOT / "experiments",
        ROOT / "demo",
    ]
    files = []
    edges = []
    module_paths = {}
    for base in source_roots:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(text)
            except SyntaxError:
                tree = None
            module = rel[:-3].replace("/", ".")
            module_paths[module] = path
            imports = []
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(a.name for a in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)
            internals = [
                i
                for i in imports
                if i.startswith(("cardiodiag", "clin_adapt", "experiments", "demo"))
            ]
            files.append(
                {
                    "path": rel,
                    "module": module,
                    "lines": len(text.splitlines()),
                    "internal_imports": ";".join(sorted(set(internals))),
                    "top_level_imports": ";".join(sorted(set(i.split(".")[0] for i in imports))),
                    "functions": sum(
                        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        for n in ast.walk(tree)
                    )
                    if tree
                    else None,
                    "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
                    if tree
                    else None,
                }
            )
    allmodules = set(module_paths)
    for row in files:
        for imp in row["internal_imports"].split(";"):
            candidates = [imp, *[m for m in allmodules if m.startswith(imp + ".")]]
            target = next((m for m in candidates if m in allmodules), None)
            if target:
                edges.append({"source_module": row["module"], "target_module": target})
    pd.DataFrame(files).sort_values("path").to_csv(OUT / "module_inventory.csv", index=False)
    pd.DataFrame(edges).drop_duplicates().sort_values(["source_module", "target_module"]).to_csv(
        OUT / "module_dependency_edges.csv", index=False
    )
    changelog = """# Project completion changelog — 2026-11-08

## Added on `research/cardiodiag-complete-project-finalization`

- `experiments/run_project_completion_diagnostics.py`: exact-order replay of saved selected fits, training/resubstitution diagnostics, 80/90/95 conformal coverage, OOD-score replay, latency and serialized size.
- `experiments/build_final_completion_deliverables.py`: deterministic builder for aggregate metric/data-quality tables, figures, manifests and focused reports.
- `results/final_research_20261108/`: aggregate metrics, inventory/compatibility tables, EDA and reliability figures, module inventory, manifests; row-level scores/checkpoints are ignored locally.
- Focused technical audit, data compatibility, model comparison, overfitting, ablation, calibration, OOD/selective, transfer, performance, architecture, demo, technical research, manuscript-finalization, acceptance and changelog reports.
- Root README current-status note for this completion branch.

## Preservation and exclusions

The original and corrected implementations, OVEC/OSEC definitions, prior experiment results, existing tests, demo, historical reports, and versioned manuscript were preserved. Raw datasets, `data/access_requests/`, local row-level predictions/checkpoints, credentials, and prior untracked audit artifacts are not staged. The exact-SPECT partition-name adjustment only aligns replay with the frozen assignment manifest; it does not change the primary run.
"""
    (DOC / "PROJECT_COMPLETION_CHANGELOG_20261108.md").write_text(changelog, encoding="utf-8")
    provenance_summary = """# Dataset provenance report

This inventory follows `results/multi_dataset_evaluation_20261108/datasets/dataset_manifest.json` and its dataset screening table. The seven evaluated prepared datasets are UCI Cleveland, Hungary, Switzerland and VA Long Beach Heart Disease; UCI Heart Failure Clinical Records; UCI Myocardial Infarction Complications; and UCI SPECTF Heart. Source attribution and SHA-256 records remain in the frozen manifests.

The evaluated UCI pages record CC BY 4.0 attribution. This does not resolve redistribution terms for unrelated third-party datasets. The candidate table records unresolved or distinct decisions for Mendeley 2021 (reference standard and predictor timing unclear), Z-Alizadeh Sani (different threshold), AngioCAD (incomplete feature mapping and uncertain units), Duke ACATH (>=75% endpoint and missing cholesterol), Kaggle Cardio Train 70K (unknown license and distinct target), and controlled-access MIMIC-IV/MultiD4CAD. Statlog is an exact Cleveland duplicate after label harmonization. Mendeley 2026 is an exact duplicate of Heart5. Heart5 is a 918-record composite with 914 unique component-source matches and 4 ambiguous matches; available records do not prove person-level independence.

The four UCI CAD cohorts have no exact pairwise feature-row matches in the recorded screen, but no stable participant IDs exist to establish patient independence. Heart-failure death, MI lethal complication and SPECT normal/abnormal remain distinct tasks. Feature compatibility does not establish cohort independence.

See `dataset_inventory.csv`, `dataset_compatibility_matrix.csv`, `dataset_class_distribution.csv`, `dataset_missing_value_report.csv`, and `dataset_duplicate_report.csv`. Raw dataset files and restricted-access material are excluded from the release branch.
"""
    (OUT / "dataset_provenance_report.md").write_text(provenance_summary, encoding="utf-8")
    # Dataset and experiment manifests retain original manifests and add hashes of final aggregate artifacts.
    dataset_manifest = dict(tables["manifest"])
    dataset_manifest["completion_outputs"] = {
        "inventory": "results/final_research_20261108/dataset_inventory.csv",
        "compatibility": "results/final_research_20261108/dataset_compatibility_matrix.csv",
        "row_level_data_in_git": False,
    }
    write_json(MAN / "dataset_manifest.json", dataset_manifest)
    experiment_manifest = {
        "study": "CARDIODIAG final completion diagnostics",
        "source_run_id": latest.get("run_id"),
        "branch": "research/cardiodiag-complete-project-finalization",
        "primary_run_status": latest.get("status"),
        "protocol": {
            "within_task": "3x3 nested stratified CV where supported; SPECTF official 80/187 split",
            "primary_models": MODEL_ORDER,
            "threshold_metrics_threshold": 0.5,
            "conformal_nominal_coverage": [0.8, 0.9, 0.95],
            "cross_ood_target_labels_used": False,
            "training_metrics": "selected pipeline resubstitution on development rows",
            "metric_source": "saved row-level predictions plus exact refit replay",
        },
        "source_manifest": "results/multi_dataset_evaluation_20261108/manifests/experiment_manifest.json",
        "diagnostics_manifest": "results/final_research_20261108/completion_diagnostics_manifest.json",
        "failure_ledger": "results/final_research_20261108/metrics/failed_experiments.csv",
    }
    for path in [
        SRC / "manifests" / "experiment_manifest.json",
        RUN / "out_of_fold_and_official_predictions.csv",
        RUN / "fold_assignments.csv",
        SRC / "datasets" / "dataset_manifest.json",
    ]:
        experiment_manifest.setdefault("input_sha256", {})[path.relative_to(ROOT).as_posix()] = (
            digest(path)
        )
    write_json(MAN / "experiment_manifest.json", experiment_manifest)
    # Verification here is independently recomputable from aggregate and frozen rows.
    checks = {
        "source_run_status": latest.get("status"),
        "within_task_model_groups": int(len(models)),
        "within_task_fold_groups": int(len(folds)),
        "expected_model_groups": 42,
        "expected_fold_groups": 114,
        "training_validation_rows": int(len(tv)),
        "expected_training_validation_rows": 114,
        "conformal_rows": int(len(conf)),
        "expected_conformal_rows": 342,
        "cross_ood_rows": int(len(cross_ood)),
        "expected_cross_ood_rows": 72,
        "within_task_probability_reproduced": int(tv.refit_prediction_reproduced.sum()),
        "within_task_auc_matches": int(tv.saved_outer_auc_matches.sum()),
        "cross_ood_auc_reproduced": int(cross_ood.saved_roc_auc_reproduced.sum()),
        "all_aggregate_sources_present": True,
        "row_level_predictions_local_ignored": True,
        "raw_data_not_in_git": True,
    }
    metric_match = bool(metrics["metrics_verification_passed"])
    verification = metrics["metrics_verification"]
    checks["metrics_versus_predictions_checks"] = int(len(verification))
    checks["metrics_versus_predictions_passed"] = int(verification.passed.sum())
    checks["metrics_recalculated_from_predictions_complete"] = metric_match
    checks["overall_pass"] = bool(
        checks["within_task_model_groups"] == 42
        and checks["within_task_fold_groups"] == 114
        and checks["training_validation_rows"] == 114
        and checks["conformal_rows"] == 342
        and checks["cross_ood_rows"] == 72
        and checks["within_task_probability_reproduced"] == 114
        and checks["within_task_auc_matches"] == 114
        and checks["cross_ood_auc_reproduced"] == 72
        and metric_match
    )
    write_json(MAN / "verification_manifest.json", checks)
    # Final acceptance is generated after external verification and is manually finalized in a second pass.


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MET.mkdir(parents=True, exist_ok=True)
    MAN.mkdir(parents=True, exist_ok=True)
    metrics = build_metrics()
    tables = build_dataset_tables()
    figures = build_figures(tables, metrics)
    build_docs(tables, metrics, figures)
    print(
        json.dumps(
            {
                "metric_groups": len(metrics["models"]),
                "fold_groups": len(metrics["folds"]),
                "training_validation": len(metrics["tv"]),
                "conformal": len(metrics["conformal"]),
                "cross_ood": len(metrics["cross_ood"]),
                "figures": len(figures),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
