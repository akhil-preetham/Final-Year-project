"""Build a CLIN-ADAPT result summary without changing historical artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/clin_adapt/summary.json")
    parser.add_argument("--csv", default="results/clin_adapt/comparison.csv")
    args = parser.parse_args()
    artifact_paths = [
        "results/clin_adapt/heart5_nested.json",
        "results/clin_adapt/mendeley_nested.json",
        "results/clin_adapt/cardiovascular_70k_nested_priority.json",
    ]
    freeze = json.loads(
        Path("results/local_model_baseline_freeze.json").read_text(encoding="utf-8")
    )
    baseline_by_dataset = {
        "heart5.csv": 0.929033,
        "MendeleyCardiovascular_Disease_Dataset.csv": 0.997828,
        "data/kaggle_cardiovascular_70k/cardio_train.csv": 0.800432,
    }
    artifacts: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for artifact_path in artifact_paths:
        data = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        dataset_path = data["dataset_summary"]["path"]
        dataset_key = str(Path(dataset_path)).replace("\\", "/")
        fold_records = data["folds"]
        completed = sum(
            record["status"] == "completed"
            for fold in fold_records
            for record in fold["execution_records"]
        )
        attempted = sum(len(fold["execution_records"]) for fold in fold_records)
        artifact = {
            "artifact": artifact_path,
            "dataset": dataset_path,
            "configuration": data["configuration"],
            "candidate_count": len(data["candidate_registry"]),
            "pooled_metrics": data["pooled_metrics"],
            "runtime_seconds": data["runtime_seconds"],
            "selected_by_fold": [fold["coordination"]["selected_names"] for fold in fold_records],
            "parallel_jobs_completed": completed,
            "parallel_jobs_attempted": attempted,
            "failed_or_noncompleted_jobs": attempted - completed,
            "unpaired_point_difference_vs_frozen_reference": (
                data["pooled_metrics"]["roc_auc"] - baseline_by_dataset[dataset_key]
            ),
            "comparison_warning": (
                "Not a paired comparison; folds and candidate protocols differ "
                "from the frozen baseline."
            ),
        }
        artifacts.append(artifact)
        rows.append(
            {
                "artifact": artifact_path,
                "dataset": dataset_path,
                "roc_auc": data["pooled_metrics"]["roc_auc"],
                "pr_auc": data["pooled_metrics"]["pr_auc"],
                "brier": data["pooled_metrics"]["brier"],
                "log_loss": data["pooled_metrics"]["log_loss"],
                "runtime_seconds": data["runtime_seconds"],
                "candidate_count": len(data["candidate_registry"]),
                "failed_or_noncompleted_jobs": attempted - completed,
            }
        )
    summary = {
        "status": "completed",
        "framework": "CLIN-ADAPT",
        "framework_version": "clin-adapt-v0.1-provisional",
        "baseline_id": freeze["baseline_id"],
        "artifacts": artifacts,
        "available_model_count": len(
            json.loads(Path("results/clin_adapt/model_registry.json").read_text(encoding="utf-8"))[
                "available_models"
            ]
        ),
        "unavailable_model_count": len(
            json.loads(Path("results/clin_adapt/model_registry.json").read_text(encoding="utf-8"))[
                "unavailable_models"
            ]
        ),
        "algorithm_status": "provisional CASL validation coordinator; no established novelty claim",
        "cross_dataset_status": (
            "not run; current CARDIODIAG feasibility gates do not authorize transfer"
        ),
        "interpretation": (
            "Within-dataset development evidence only. The point differences are "
            "descriptive and not paired statistical comparisons."
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    csv_path = Path(args.csv)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"summary": str(output), "csv": str(csv_path), "artifacts": len(artifacts)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
