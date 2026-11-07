"""Recompute and summarize the Mendeley and AngioCAD validity sensitivities."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

from cardiodiag.evaluation import evaluate_predictions

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "validity_audit_20261105"
MENDLEY_BASELINE = (
    ROOT / "results" / "master_directive_20261105_serial" / "mendeley_nested_validation.json"
)
MENDELEY_ABLATION = RESULTS / "mendeley_without_major_vessels.json"
ANGIO_BASELINE = ROOT / "results" / "transfer_20261105_angiocad_external"
ANGIO_NO_FBS = RESULTS / "angiocad_without_fbs"
TABLE_DIR = ROOT / "paper" / "tables"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual: float, expected: float, name: str, atol: float = 1e-10) -> None:
    if not np.isclose(actual, expected, rtol=0, atol=atol):
        raise AssertionError(f"{name} mismatch: recomputed={actual}, saved={expected}")


def audit_nested_pair(
    ablation_path: Path = MENDELEY_ABLATION,
) -> tuple[dict[str, Any], dict[str, Any]]:
    ablation_path = ablation_path.resolve()
    baseline = json.loads(MENDLEY_BASELINE.read_text(encoding="utf-8"))
    ablation = json.loads(ablation_path.read_text(encoding="utf-8"))
    if baseline["dataset_summary"]["sha256"] != ablation["dataset_summary"]["sha256"]:
        raise AssertionError("Mendeley baseline and ablation do not use the same input file")
    if baseline["dataset_summary"]["rows"] != ablation["dataset_summary"]["rows"]:
        raise AssertionError("Mendeley baseline and ablation row counts differ")
    if ablation.get("excluded_features") != ["noofmajorvessels"]:
        raise AssertionError("Expected only noofmajorvessels to be excluded")
    if set(baseline["candidates"]) != set(ablation["candidates"]):
        raise AssertionError("Candidate sets differ between Mendeley runs")

    candidate_summary: dict[str, Any] = {}
    row_count = int(baseline["dataset_summary"]["rows"])
    for name, full in baseline["candidates"].items():
        reduced = ablation["candidates"][name]
        full_folds = full["folds"]
        reduced_folds = reduced["folds"]
        if len(full_folds) != len(reduced_folds):
            raise AssertionError(f"Fold count differs for {name}")
        full_y: list[int] = []
        full_p: list[float] = []
        reduced_y: list[int] = []
        reduced_p: list[float] = []
        seen = np.zeros(row_count, dtype=int)
        for full_fold, reduced_fold in zip(full_folds, reduced_folds, strict=True):
            for key in ("outer_train_indices", "outer_test_indices", "outer_test_y_true"):
                if full_fold[key] != reduced_fold[key]:
                    raise AssertionError(f"Mendeley split or target differs for {name}: {key}")
            test_indices = np.asarray(full_fold["outer_test_indices"], dtype=int)
            seen[test_indices] += 1
            full_y.extend(full_fold["outer_test_y_true"])
            full_p.extend(full_fold["outer_test_probability"])
            reduced_y.extend(reduced_fold["outer_test_y_true"])
            reduced_p.extend(reduced_fold["outer_test_probability"])
        if not np.all(seen == 1):
            raise AssertionError(f"Outer folds do not score every Mendeley row once for {name}")
        full_recomputed = evaluate_predictions(np.asarray(full_y), np.asarray(full_p))
        reduced_recomputed = evaluate_predictions(np.asarray(reduced_y), np.asarray(reduced_p))
        close(
            full_recomputed["roc_auc"],
            full["pooled_outer_metrics"]["roc_auc"],
            f"Mendeley {name} full-feature AUC",
        )
        close(
            reduced_recomputed["roc_auc"],
            reduced["pooled_outer_metrics"]["roc_auc"],
            f"Mendeley {name} reduced-feature AUC",
        )
        fold_aucs = [fold["metrics"]["roc_auc"] for fold in reduced_folds]
        reduced_mean = float(np.mean(fold_aucs))
        reduced_sd = float(np.std(fold_aucs, ddof=1))
        close(reduced_mean, reduced["fold_mean"]["roc_auc"], f"Mendeley {name} fold mean")
        close(reduced_sd, reduced["fold_std"]["roc_auc"], f"Mendeley {name} fold SD")
        full_mean = float(full["fold_mean"]["roc_auc"])
        full_sd = float(full["fold_std"]["roc_auc"])
        candidate_summary[name] = {
            "all_feature_auc_mean": full_mean,
            "all_feature_auc_fold_sd": full_sd,
            "without_major_vessels_auc_mean": reduced_mean,
            "without_major_vessels_auc_fold_sd": reduced_sd,
            "auc_difference": reduced_mean - full_mean,
            "all_feature_brier_mean": float(full["fold_mean"]["brier"]),
            "without_major_vessels_brier_mean": float(reduced["fold_mean"]["brier"]),
        }
    return candidate_summary, {
        "baseline_sha256": sha256_file(MENDLEY_BASELINE),
        "ablation_sha256": sha256_file(ablation_path),
        "dataset_sha256": ablation["dataset_summary"]["sha256"],
        "row_count": row_count,
        "all_outer_rows_scored_once": True,
        "same_splits_and_targets": True,
        "candidates": candidate_summary,
    }


def _recompute_external_predictions(path: Path) -> dict[str, Any]:
    frame = pd.read_csv(path)
    y = frame["y_binary"].to_numpy(dtype=int)
    raw = frame["raw_probability"].to_numpy(dtype=float)
    platt = frame["platt_probability"].to_numpy(dtype=float)
    return {
        "raw": _independent_metrics(y, raw),
        "platt": _independent_metrics(y, platt),
        "prediction_sha256": sha256_file(path),
        "rows": int(len(frame)),
        "positive_count": int(y.sum()),
    }


def _independent_metrics(y: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    probability = np.clip(np.asarray(probability, dtype=float), 1e-7, 1 - 1e-7)
    edges = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    for index in range(10):
        if index == 9:
            selected = (probability >= edges[index]) & (probability <= edges[index + 1])
        else:
            selected = (probability >= edges[index]) & (probability < edges[index + 1])
        if selected.any():
            ece += float(selected.mean()) * abs(
                float(probability[selected].mean()) - float(y[selected].mean())
            )
    return {
        "roc_auc": float(roc_auc_score(y, probability)),
        "average_precision": float(average_precision_score(y, probability)),
        "brier_score": float(brier_score_loss(y, probability)),
        "log_loss": float(log_loss(y, probability, labels=[0, 1])),
        "ece_10_bins": ece,
    }


def _audit_saved_external_metrics(
    recomputed: dict[str, Any], manifest: dict[str, Any], feature_condition: str
) -> None:
    if feature_condition == "with_fbs":
        raw_key, platt_key = "raw_predictor_metrics", "platt_calibrated_metrics"
        auc_ci = manifest["predictor_bootstrap_95_ci"]["raw"]["roc_auc"]
    else:
        raw_key, platt_key = "target_raw_metrics", "target_calibrated_metrics"
        auc_ci = manifest["predictive_bootstrap_95_ci"]["raw"]["roc_auc"]
    for kind, manifest_key in (("raw", raw_key), ("platt", platt_key)):
        actual = recomputed[kind]
        expected = manifest[manifest_key]
        for field in ("roc_auc", "average_precision", "brier_score", "log_loss", "ece_10_bins"):
            close(actual[field], expected[field], f"AngioCAD {feature_condition} {kind} {field}")
    if auc_ci["lower_95"] is None or auc_ci["upper_95"] is None:
        raise AssertionError("AngioCAD bootstrap AUC interval is missing")


def audit_angiocad_pair(
    no_fbs_dir: Path = ANGIO_NO_FBS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    no_fbs_dir = no_fbs_dir.resolve()
    full_manifest = json.loads((ANGIO_BASELINE / "run_manifest.json").read_text(encoding="utf-8"))
    reduced_manifest = json.loads((no_fbs_dir / "run_manifest.json").read_text(encoding="utf-8"))
    full_target = pd.read_csv(ANGIO_BASELINE / "external_predictions.csv")
    reduced_target = pd.read_csv(no_fbs_dir / "target_predictions.csv")
    for key in ("record_id", "y_binary"):
        if not np.array_equal(full_target[key].to_numpy(), reduced_target[key].to_numpy()):
            raise AssertionError(f"AngioCAD rows or target differ by feature condition: {key}")
    if full_manifest["source_splits"] != reduced_manifest["source_splits"]:
        raise AssertionError("Source fitting/calibration partitions differ")

    full_metrics = _recompute_external_predictions(ANGIO_BASELINE / "external_predictions.csv")
    reduced_metrics = _recompute_external_predictions(no_fbs_dir / "target_predictions.csv")
    _audit_saved_external_metrics(full_metrics, full_manifest, "with_fbs")
    _audit_saved_external_metrics(reduced_metrics, reduced_manifest, "without_fbs")

    source_full = pd.read_csv(ANGIO_BASELINE / "source_calibration_predictions.csv")
    source_reduced = pd.read_csv(no_fbs_dir / "source_calibration_predictions.csv")
    if not np.array_equal(
        source_full["source_cohort"].to_numpy(),
        source_reduced["source_cohort"].to_numpy(),
    ):
        raise AssertionError("AngioCAD source calibration row order differs")
    full_ood_y = np.r_[np.zeros(len(source_full)), np.ones(len(full_target))]
    reduced_ood_y = np.r_[np.zeros(len(source_reduced)), np.ones(len(reduced_target))]
    full_ood_score = np.r_[source_full["ood_anomaly_score"], full_target["ood_anomaly_score"]]
    reduced_ood_score = np.r_[
        source_reduced["ood_anomaly_score"], reduced_target["ood_anomaly_score"]
    ]
    full_ood_auc = float(roc_auc_score(full_ood_y, full_ood_score))
    reduced_ood_auc = float(roc_auc_score(reduced_ood_y, reduced_ood_score))
    close(
        full_ood_auc,
        full_manifest["ood"]["source_vs_target_ood_auroc"],
        "AngioCAD full-feature OOD AUROC",
    )
    close(
        reduced_ood_auc,
        reduced_manifest["ood"]["source_vs_target_auroc"],
        "AngioCAD age/sex OOD AUROC",
    )

    def interval(value: dict[str, float]) -> str:
        return f"{value['lower_95']:.3f}--{value['upper_95']:.3f}"

    full_auc_ci = full_manifest["predictor_bootstrap_95_ci"]["raw"]["roc_auc"]
    reduced_auc_ci = reduced_manifest["predictive_bootstrap_95_ci"]["raw"]["roc_auc"]
    full_ood_ci = full_manifest["ood"]["source_vs_target_ood_auroc_bootstrap_95_ci"]
    reduced_ood_ci = reduced_manifest["ood"]["source_vs_target_auroc_bootstrap_95_ci"]
    table = {
        "with_fbs": {
            "raw_auc": float(full_metrics["raw"]["roc_auc"]),
            "raw_auc_ci": interval(full_auc_ci),
            "calibrated_brier": float(full_metrics["platt"]["brier_score"]),
            "calibrated_ece": float(full_metrics["platt"]["ece_10_bins"]),
            "ood_auc": full_ood_auc,
            "ood_auc_ci": interval(full_ood_ci),
        },
        "age_sex_only": {
            "raw_auc": float(reduced_metrics["raw"]["roc_auc"]),
            "raw_auc_ci": interval(reduced_auc_ci),
            "calibrated_brier": float(reduced_metrics["platt"]["brier_score"]),
            "calibrated_ece": float(reduced_metrics["platt"]["ece_10_bins"]),
            "ood_auc": reduced_ood_auc,
            "ood_auc_ci": interval(reduced_ood_ci),
        },
        "auc_difference_age_sex_minus_full": float(
            reduced_metrics["raw"]["roc_auc"] - full_metrics["raw"]["roc_auc"]
        ),
    }
    audit = {
        "baseline_manifest_sha256": sha256_file(ANGIO_BASELINE / "run_manifest.json"),
        "sensitivity_manifest_sha256": sha256_file(no_fbs_dir / "run_manifest.json"),
        "sensitivity_result_dir": str(no_fbs_dir.relative_to(ROOT)),
        "same_target_records_and_labels": True,
        "same_source_fit_and_calibration_partitions": True,
        "target_rows": int(len(full_target)),
        "negative_count": int((full_target["y_binary"] == 0).sum()),
        "positive_count": int((full_target["y_binary"] == 1).sum()),
        "metrics_recomputed_from_prediction_files": True,
        "ood_auc_recomputed_from_source_and_target_scores": True,
        "summary": table,
    }
    return table, audit


def write_tables(mendeley: dict[str, Any], angiocad: dict[str, Any]) -> tuple[Path, Path]:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    mend_rows = []
    for name, result in mendeley.items():
        label = name.replace("_", r"\_")
        full = (
            f"{result['all_feature_auc_mean']:.4f} $\\pm$ {result['all_feature_auc_fold_sd']:.4f}"
        )
        reduced = (
            f"{result['without_major_vessels_auc_mean']:.4f} $\\pm$ "
            f"{result['without_major_vessels_auc_fold_sd']:.4f}"
        )
        delta = f"{result['auc_difference']:+.4f}"
        mend_rows.append(f"{label} & {full} & {reduced} & {delta} \\\\")
    mend_text = "\n".join(
        [
            r"\begin{tabular}{lrrr}",
            r"\toprule",
            r"Candidate & All predictors & Excluding major vessels & Difference \\",
            r"\midrule",
            *mend_rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    mend_path = TABLE_DIR / "validity_sensitivity_mendeley.tex"
    mend_path.write_text(mend_text + "\n", encoding="utf-8")

    ang_rows = []
    for label, result in (
        ("Age, sex, FBS", angiocad["with_fbs"]),
        ("Age, sex only", angiocad["age_sex_only"]),
    ):
        auc = f"{result['raw_auc']:.3f} ({result['raw_auc_ci']})"
        ood = f"{result['ood_auc']:.3f} ({result['ood_auc_ci']})"
        ang_rows.append(
            f"{label} & {auc} & {result['calibrated_brier']:.3f} & "
            f"{result['calibrated_ece']:.3f} & {ood} \\\\"
        )
    ang_text = "\n".join(
        [
            r"\begin{tabular}{lrrrr}",
            r"\toprule",
            r"Features & Raw AUC (95\% CI) & Calibrated Brier & "
            + r"Calibrated ECE & OOD AUC (95\% CI) "
            + r"\\",
            r"\midrule",
            *ang_rows,
            r"\bottomrule",
            r"\end{tabular}",
        ]
    )
    ang_path = TABLE_DIR / "validity_sensitivity_angiocad.tex"
    ang_path.write_text(ang_text + "\n", encoding="utf-8")
    return mend_path, ang_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mendeley-ablation", type=Path, default=MENDELEY_ABLATION)
    parser.add_argument("--angiocad-dir", type=Path, default=ANGIO_NO_FBS)
    parser.add_argument("--output", type=Path, default=RESULTS / "validity_sensitivity_audit.json")
    arguments = parser.parse_args()
    mendley_summary, mendley_audit = audit_nested_pair(arguments.mendeley_ablation)
    angiocad_summary, angiocad_audit = audit_angiocad_pair(arguments.angiocad_dir)
    table_paths = write_tables(mendley_summary, angiocad_summary)
    result = {
        "status": "passed",
        "mendeley": mendley_audit,
        "angiocad": angiocad_audit,
        "generated_tables": {
            str(path.relative_to(ROOT)): sha256_file(path) for path in table_paths
        },
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    output = arguments.output
    output.parent.mkdir(parents=True, exist_ok=True)
    result["audit_script_sha256"] = sha256_file(Path(__file__).resolve())
    output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Validity sensitivity audit passed; wrote {output}")


if __name__ == "__main__":
    main()
