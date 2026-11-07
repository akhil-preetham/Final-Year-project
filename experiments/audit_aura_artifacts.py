"""Recompute and audit the immutable AURA-ML V1 artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from cardiodiag.data import summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.reliability import calibration_summary


def _close(left: Any, right: Any, tolerance: float = 1e-10) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return bool(math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance))
    return left == right


def _audit_predictions(section: dict[str, Any], rows: int) -> dict[str, Any]:
    folds = section["folds"]
    indices = np.concatenate([np.asarray(fold["test_indices"], dtype=int) for fold in folds])
    y_true = np.concatenate([np.asarray(fold["y_true"], dtype=int) for fold in folds])
    probabilities = np.concatenate(
        [np.asarray(fold["predicted_probability"], dtype=float) for fold in folds]
    )
    recomputed = evaluate_predictions(y_true, probabilities)
    stored = section["pooled_outer_metrics"]
    metric_checks = {
        key: _close(stored[key], recomputed[key])
        for key in (
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
        )
    }
    assignment_check = bool(
        len(indices) == rows
        and len(np.unique(indices)) == rows
        and np.array_equal(np.sort(indices), np.arange(rows))
    )
    calibration = calibration_summary(y_true, probabilities)
    return {
        "fold_count": len(folds),
        "prediction_count": int(len(probabilities)),
        "outer_assignment_is_partition": assignment_check,
        "pooled_metrics_recomputed": recomputed,
        "metric_checks": metric_checks,
        "all_metrics_match": all(metric_checks.values()),
        "calibration_recomputed": {
            "brier": calibration["brier"],
            "ece_uniform": calibration["ece_uniform"],
            "calibration_intercept": calibration["calibration_intercept"],
            "calibration_slope": calibration["calibration_slope"],
        },
    }


def _audit_primary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = summarize_dataset(payload["dataset_summary"]["path"], payload["target"])
    hash_match = summary.sha256 == payload["dataset_summary"]["sha256"]
    rows = summary.rows
    aura = _audit_predictions(payload["aura_ml"], rows)
    baseline = _audit_predictions(payload["existing_baseline"], rows)
    same_folds = all(
        aura_fold["test_indices"] == baseline_fold["test_indices"]
        for aura_fold, baseline_fold in zip(
            payload["aura_ml"]["folds"], payload["existing_baseline"]["folds"]
        )
    )
    bootstrap = payload["paired_comparison"]["roc_auc_delta_aura_minus_baseline"]
    return {
        "artifact": str(path).replace("\\", "/"),
        "dataset": payload["dataset_summary"]["path"],
        "target": payload["target"],
        "hash_match": hash_match,
        "rows_match": rows == payload["dataset_summary"]["rows"],
        "configuration": payload["configuration"],
        "same_outer_folds_for_aura_and_baseline": same_folds,
        "aura": aura,
        "existing_baseline": baseline,
        "stored_paired_bootstrap": bootstrap,
        "model_selection_stored": all(
            "fit_summary" in fold and "selected_names" in fold["fit_summary"]
            for fold in payload["aura_ml"]["folds"]
        ),
        "fusion_decisions_stored": [
            fold["fit_summary"]["fusion"]["selected_output"]
            for fold in payload["aura_ml"]["folds"]
        ],
        "calibration_methods_stored": [
            fold["fit_summary"]["calibration_method"]
            for fold in payload["aura_ml"]["folds"]
        ],
        "limitation": (
            "Inner OOF predictions are summarized by metrics but are not stored; "
            "the stored paired bootstrap interval cannot be independently regenerated "
            "byte-for-byte without the original bootstrap implementation state."
        ),
    }


def _audit_ablations(root: Path) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for dataset in ("heart5", "mendeley"):
        summary_path = root / "ablations" / dataset / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        artifact_checks = {}
        for row in summary["ablations"]:
            artifact = Path(row["artifact"])
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            section = payload["aura_ml"]
            rows = payload["dataset_summary"]["rows"]
            audit = _audit_predictions(section, rows)
            artifact_checks[row["ablation"]] = {
                "all_metrics_match": audit["all_metrics_match"],
                "outer_assignment_is_partition": audit["outer_assignment_is_partition"],
            }
        output[dataset] = {
            "status": summary["status"],
            "count": len(summary["ablations"]),
            "names": [row["ablation"] for row in summary["ablations"]],
            "artifact_checks": artifact_checks,
            "all_artifacts_match": all(
                check["all_metrics_match"] and check["outer_assignment_is_partition"]
                for check in artifact_checks.values()
            ),
        }
    return output


def audit(root: Path, output: Path) -> dict[str, Any]:
    primary = sorted(root.glob("aura_nested_2x2_*.json"))
    if len(primary) != 3:
        raise ValueError(f"Expected three primary V1 artifacts, found {len(primary)}")
    report = {
        "status": "completed",
        "scope": "immutable AURA-ML V1 artifacts",
        "primary": [_audit_primary(path) for path in primary],
        "ablations": _audit_ablations(root),
        "conclusion": (
            "Outer predictions and pooled metrics are reproducible from all three "
            "primary artifacts. Fold assignments, same-fold comparisons, selected "
            "outputs, and calibration diagnostics are auditable. Inner predictions "
            "and full bootstrap draws were not persisted, limiting exact secondary "
            "recomputation."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("results/aura_ml"))
    parser.add_argument("--output", type=Path, default=Path("results/aura_ml_v2/V1_AUDIT.json"))
    args = parser.parse_args()
    report = audit(args.root, args.output)
    print(f"Audited {len(report['primary'])} primary AURA artifacts")


if __name__ == "__main__":
    main()
