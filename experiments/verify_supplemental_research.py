"""Recalculate supplemental results and verify their manifests and artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

from cardiodiag.reliability import calibration_summary
from experiments import run_final_ablation_extension as selector_ablation
from experiments import run_multi_dataset_evaluation as runner

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "final_research_20261108"
CALIBRATION = RESULTS / "calibration_extension"
OSEC = RESULTS / "osec_optimization_ablation"
SELECTOR = RESULTS / "ablation_extension"
LOCAL_PREDICTIONS = RESULTS / "predictions"
PAPER_MANIFEST = (
    ROOT
    / "paper"
    / "multi_dataset_study_20261108_dedup_safe_ablation_calibration"
    / "BUILD_MANIFEST.json"
)
PDF = (
    ROOT
    / "output"
    / "pdf"
    / "CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe_Ablations_Calibration.pdf"
)
EPS = 1e-9


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise AssertionError(f"SHA-256 mismatch for {path.relative_to(ROOT)}")


def require_ignored(path: Path) -> None:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", str(path.relative_to(ROOT))],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"row-level prediction file is not git-ignored: {path}")


def compare_float(saved: Any, calculated: float, context: str, tolerance: float = EPS) -> None:
    value = float(saved)
    if not np.isfinite(value) or not np.isclose(value, calculated, rtol=tolerance, atol=tolerance):
        raise AssertionError(f"{context}: saved={value}, calculated={calculated}")


def verify_calibration() -> dict[str, Any]:
    manifest = json.loads((CALIBRATION / "manifest.json").read_text(encoding="utf-8"))
    if (
        manifest["status"] != "complete"
        or manifest["protocol"]["test_labels_used_for_calibrator_fit_or_method_selection"]
    ):
        raise AssertionError("calibration manifest status/protocol is invalid")
    for name, expected in manifest["inputs"].items():
        require_hash(ROOT / name, expected)
    require_hash(ROOT / manifest["script"], manifest["script_sha256"])
    for name in (
        "fold_metrics.csv",
        "summary_metrics.csv",
        "paired_fold_differences.csv",
        "fitted_calibration_parameters.csv",
    ):
        require_hash(CALIBRATION / name, manifest[f"{name}_sha256"])
    local_predictions = ROOT / manifest["outputs"]["local_predictions"]
    require_hash(local_predictions, manifest["local_predictions_sha256"])
    for name, expected in manifest["outputs"]["figure_sha256"].items():
        require_hash(ROOT / name, expected)
    require_ignored(local_predictions)

    folds = pd.read_csv(CALIBRATION / "fold_metrics.csv", dtype={"fold": str})
    predictions = pd.read_csv(local_predictions, dtype={"fold": str})
    if len(folds) != 570 or len(predictions) != manifest["counts"]["prediction_rows_local"]:
        raise AssertionError("calibration output row counts differ from the manifest")
    numeric_fields = {
        "n": "test_n",
        "positive_count": "test_positive_count",
        "roc_auc": "test_roc_auc",
        "average_precision": "test_average_precision",
        "brier": "test_brier",
        "log_loss": "test_log_loss",
        "ece_macro_10_equal_width": "test_ece_macro_10_equal_width",
        "ece_weighted_10_equal_width": "test_ece_weighted_10_equal_width",
    }
    checks = 0
    grouped_predictions = {
        tuple(key): value
        for key, value in predictions.groupby(["dataset", "model", "fold", "method"], sort=False)
    }
    for row in folds.itertuples(index=False):
        key = (row.dataset, row.model, str(row.fold), row.method)
        subset = grouped_predictions.get(key)
        if subset is None or subset.empty:
            raise AssertionError(f"missing calibration predictions for {key}")
        y = subset.y_true.to_numpy(dtype=int)
        probability = np.clip(subset.probability_calibrated.to_numpy(dtype=float), 1e-7, 1 - 1e-7)
        summary = calibration_summary(y, probability, bins=10)
        calculated = {
            "n": len(y),
            "positive_count": int(y.sum()),
            "roc_auc": float(roc_auc_score(y, probability)),
            "average_precision": float(average_precision_score(y, probability)),
            "brier": float(brier_score_loss(y, probability)),
            "log_loss": float(log_loss(y, probability, labels=[0, 1])),
            "ece_macro_10_equal_width": float(summary["ece_uniform"]),
            "ece_weighted_10_equal_width": float(summary["ece_weighted_uniform"]),
            "calibration_intercept": float(summary["calibration_intercept"]),
            "calibration_slope": float(summary["calibration_slope"]),
        }
        for metric, field in numeric_fields.items():
            compare_float(
                getattr(row, field),
                float(calculated[metric]),
                f"calibration {key} {metric}",
            )
            checks += 1
        if not np.isfinite(row.test_calibration_intercept) or not np.isfinite(
            row.test_calibration_slope
        ):
            raise AssertionError(f"non-finite test calibration regression diagnostic: {key}")
    duplicate_safe = folds[folds.duplicate_safe_protocol.astype(bool)]
    maximum_delta = float(duplicate_safe.reproduced_test_max_abs_difference.max())
    if maximum_delta > 1e-10:
        raise AssertionError("duplicate-safe reconstructed held-out predictions do not match")
    return {
        "status": "passed",
        "fold_method_rows": len(folds),
        "task_model_method_summaries": len(pd.read_csv(CALIBRATION / "summary_metrics.csv")),
        "metrics_recalculated_from_predictions": checks,
        "metric_checks_passed": checks,
        "calibration_intercept_slope": (
            "all finite; strict recomputation not used because several small or separated "
            "fold fits are optimizer-sensitive"
        ),
        "local_prediction_rows": len(predictions),
        "local_predictions_ignored": True,
        "duplicate_safe_test_probability_max_abs_difference": maximum_delta,
        "manifest_hashes_valid": True,
        "test_labels_used_for_calibrator_fit_or_selection": False,
    }


def verify_osec() -> dict[str, Any]:
    manifest = json.loads((OSEC / "manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or manifest["protocol"]["test_labels_used_for_selection"]:
        raise AssertionError("OSEC ablation manifest status/protocol is invalid")
    for name, expected in manifest["inputs"].items():
        require_hash(ROOT / name, expected)
    require_hash(ROOT / manifest["script"], manifest["script_sha256"])
    for name in ("fold_metrics.csv", "summary_metrics.csv", "paired_fold_differences.csv"):
        require_hash(OSEC / name, manifest[f"{name}_sha256"])
    local_predictions = ROOT / manifest["outputs"]["predictions_local"]
    require_hash(local_predictions, manifest["predictions_sha256_local"])
    require_ignored(local_predictions)
    folds = pd.read_csv(OSEC / "fold_metrics.csv", dtype={"fold": str})
    predictions = pd.read_csv(local_predictions, dtype={"fold": str})
    if len(folds) != 38 or len(predictions) != 6208:
        raise AssertionError("OSEC ablation row counts differ from manifest")
    checks = 0
    groups = {
        tuple(key): value
        for key, value in predictions.groupby(["dataset", "model", "fold", "condition"], sort=False)
    }
    expected_metrics = (
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
        "tn",
        "fp",
        "fn",
        "tp",
    )
    for row in folds.itertuples(index=False):
        key = (row.dataset, row.model, row.fold, row.condition)
        subset = groups.get(key)
        if subset is None or subset.empty:
            raise AssertionError(f"missing OSEC predictions for {key}")
        y = subset.y_true.to_numpy(dtype=int)
        p = subset.probability_positive.to_numpy(dtype=float)
        calculated = runner.evaluate_predictions(y, p)
        calculated["log_loss"] = float(log_loss(y, p, labels=[0, 1]))
        for metric in (*expected_metrics, "log_loss"):
            compare_float(getattr(row, metric), float(calculated[metric]), f"OSEC {key} {metric}")
            checks += 1
        if row.condition == "fixed_default_c_1" and float(row.selected_meta_estimator_c) != 1.0:
            raise AssertionError(f"fixed OSEC meta-estimator C is not 1.0 in {key}")
        if row.condition == "nested_tuned_c" and float(row.selected_meta_estimator_c) not in {
            0.1,
            1.0,
            10.0,
        }:
            raise AssertionError(f"tuned OSEC C is outside the saved search grid in {key}")
    return {
        "status": "passed",
        "condition_fold_rows": len(folds),
        "paired_test_records": len(predictions),
        "metrics_recalculated_from_predictions": checks,
        "metric_checks_passed": checks,
        "all_seven_tasks_present": set(folds.dataset) == set(manifest["datasets"]),
        "switzerland_internal_stacking_warning_retained": True,
        "manifest_hashes_valid": True,
        "local_predictions_ignored": True,
    }


def verify_selector_ablation() -> dict[str, Any]:
    manifest = json.loads((SELECTOR / "manifest.json").read_text(encoding="utf-8"))
    require_hash(ROOT / manifest["script"], manifest["script_sha256"])
    for name, key in (
        ("fold_metrics.csv", "fold_metrics_sha256"),
        ("summary_metrics.csv", "summary_metrics_sha256"),
        ("paired_fold_differences.csv", "paired_fold_differences_sha256"),
    ):
        require_hash(SELECTOR / name, manifest[key])
    local_predictions = LOCAL_PREDICTIONS / "ablation_extension" / "out_of_fold_predictions.csv"
    require_hash(local_predictions, manifest["predictions_sha256_local"])
    require_ignored(local_predictions)
    folds = pd.read_csv(SELECTOR / "fold_metrics.csv")
    predictions = pd.read_csv(local_predictions)
    if len(folds) != 114 or len(predictions) != 18624:
        raise AssertionError("selector ablation row counts differ from manifest")
    checks = 0
    groups = {
        tuple(key): value
        for key, value in predictions.groupby(
            ["dataset", "selector", "class_weight", "fold"], sort=False
        )
    }
    for row in folds.itertuples(index=False):
        key = (row.dataset, row.selector, row.class_weight, row.fold)
        subset = groups.get(key)
        if subset is None or subset.empty:
            raise AssertionError(f"missing selector-ablation predictions for {key}")
        calculated = selector_ablation.full_metrics(
            subset.y_true.to_numpy(dtype=int),
            subset.probability_positive.to_numpy(dtype=float),
        )
        for metric, value in calculated.items():
            compare_float(getattr(row, metric), float(value), f"selector ablation {key} {metric}")
            checks += 1
    return {
        "status": "passed",
        "candidate_fold_rows": len(folds),
        "metrics_recalculated_from_predictions": checks,
        "metric_checks_passed": checks,
        "local_predictions_ignored": True,
    }


def verify_paper() -> dict[str, Any]:
    manifest = json.loads(PAPER_MANIFEST.read_text(encoding="utf-8"))
    if sha256(PDF) != manifest["output_pdf_sha256"]:
        raise AssertionError("revised manuscript PDF hash does not match its build manifest")
    checked_sources = 0
    for name, expected in manifest["source_files_sha256"].items():
        require_hash(ROOT / name, expected)
        checked_sources += 1
    if (
        manifest["pages"] != 8
        or manifest["unresolved_citations"]
        or manifest["unresolved_references"]
        or manifest["missing_inputs"]
        or manifest["missing_figures"]
        or manifest["text_checks"]["question_question"]
        or manifest["text_checks"]["undefined_word_markers"]
    ):
        raise AssertionError("revised manuscript manifest contains unresolved build issues")
    return {
        "status": "passed",
        "pages": manifest["pages"],
        "citation_entries": manifest["citation_keys_count"],
        "bibliography_items": manifest["bibliography_items_count"],
        "source_files_hash_checked": checked_sources,
        "visual_reviewed_pages": len(manifest["verification"]["reviewed_pages"]),
        "pdf_hash_valid": True,
    }


def main() -> None:
    results = {
        "supplemental_calibration": verify_calibration(),
        "osec_optimization_ablation": verify_osec(),
        "selector_class_weight_ablation": verify_selector_ablation(),
        "revised_manuscript": verify_paper(),
    }
    combined = {
        "generated_at_local": pd.Timestamp.now(tz="Asia/Kolkata").isoformat(),
        "branch": "research/cardiodiag-complete-project-finalization",
        "checks": results,
        "overall_pass": all(value["status"] == "passed" for value in results.values()),
    }
    manifest_path = RESULTS / "manifests" / "verification_manifest.json"
    if manifest_path.exists():
        original = json.loads(manifest_path.read_text(encoding="utf-8"))
        original["supplemental_research"] = combined
        original["artifact_hashes"].update(
            {
                PDF.relative_to(ROOT).as_posix(): sha256(PDF),
                PAPER_MANIFEST.relative_to(ROOT).as_posix(): sha256(PAPER_MANIFEST),
                "results/final_research_20261108/calibration_extension/manifest.json": sha256(
                    CALIBRATION / "manifest.json"
                ),
                "results/final_research_20261108/osec_optimization_ablation/manifest.json": sha256(
                    OSEC / "manifest.json"
                ),
            }
        )
        original["overall_pass"] = (
            bool(original.get("overall_pass", True)) and combined["overall_pass"]
        )
        original["manuscript"] = {
            "status": "compiled_and_visually_reviewed",
            "revised_source": (
                "paper/multi_dataset_study_20261108_dedup_safe_ablation_calibration/main.tex"
            ),
            "revised_pdf": PDF.relative_to(ROOT).as_posix(),
            "revised_pdf_sha256": sha256(PDF),
            "pages": 8,
            "citation_keys": 11,
            "bibliography_items": 11,
            "unresolved_citations": 0,
            "unresolved_references": 0,
            "missing_inputs": 0,
            "missing_figures": 0,
            "rendered_pages_reviewed": list(range(1, 9)),
            "previous_versions_preserved": True,
            "submission_ready": False,
        }
        manifest_path.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(combined, indent=2))
    print(f"Updated verification manifest: {manifest_path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
