"""Run separate nested internal validation for the two new UCI tasks.

Only aggregate/fold-level metrics are persisted. Per-row labels, probabilities,
and split indices returned internally by the shared runner are removed first.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cardiodiag.nested_validation import run_nested_validation
from cardiodiag.provenance import collect_provenance

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "processed" / "new_datasets_20261107"
DEFAULT_OUTPUT = ROOT / "results" / "new_datasets_20261107"
CANDIDATES = [
    ("logistic", False, "corrected_logistic"),
    ("ovec", False, "corrected_ovec"),
    ("osec", False, "corrected_osec"),
]
ROW_LEVEL_KEYS = {
    "outer_train_indices",
    "outer_test_indices",
    "outer_test_y_true",
    "outer_test_probability",
}


def remove_row_level_payload(result: dict[str, Any]) -> dict[str, Any]:
    for candidate in result.get("candidates", {}).values():
        candidate.pop("bootstrap_ci", None)
        for fold in candidate.get("folds", []):
            for key in ROW_LEVEL_KEYS:
                fold.pop(key, None)
    return result


def run_one(
    name: str,
    source_doi: str,
    path: Path,
    target: str,
    output_dir: Path,
    outer_splits: int,
    inner_splits: int,
    seed: int,
) -> dict[str, Any]:
    raw_result = run_nested_validation(
        path,
        target,
        candidates=CANDIDATES,
        outer_splits=outer_splits,
        outer_repeats=1,
        inner_splits=inner_splits,
        seed=seed,
        shuffle_inner=True,
    )
    result = remove_row_level_payload(raw_result)
    result["study"] = {
        "dataset_id": name,
        "source_doi": source_doi,
        "validation_status": "exploratory internal nested cross-validation",
        "not_a_cardiodiag_cad_external_validation": True,
        "selection_note": "All model families are reported; no winner is claimed from these folds.",
        "row_level_predictions_persisted": False,
        "uncertainty_note": (
            "Outer-fold standard deviations are descriptive; inferential CIs are not reported."
        ),
    }
    relative_dataset_path = path.resolve().relative_to(ROOT).as_posix()
    result["config"]["dataset"] = relative_dataset_path
    result["dataset_summary"]["path"] = relative_dataset_path
    result["provenance"] = collect_provenance(
        dataset=path,
        target=target,
        experiment_type="nested_internal_validation_new_uci_task",
        configuration={
            "outer_splits": outer_splits,
            "outer_repeats": 1,
            "inner_splits": inner_splits,
            "inner_shuffle": True,
            "seed": seed,
            "scoring": "roc_auc",
            "candidates": [item[2] for item in CANDIDATES],
        },
    )
    result["provenance"]["dataset_path"] = relative_dataset_path
    destination = output_dir / f"{name}_nested_metrics.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote aggregate metrics: {destination}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--outer-splits", type=int, default=5)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    heart_failure = run_one(
        "uci_heart_failure_519",
        "10.24432/C5Z89R",
        (args.data_dir / "uci_heart_failure_519_binary_event.csv").resolve(),
        "death_event",
        output_dir,
        args.outer_splits,
        args.inner_splits,
        args.seed,
    )
    mi = run_one(
        "uci_mi_complications_579",
        "10.24432/C53P5M",
        (args.data_dir / "uci_mi_complications_579_admission_binary.csv").resolve(),
        "any_lethal_outcome",
        output_dir,
        args.outer_splits,
        args.inner_splits,
        args.seed,
    )
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": {
            "outer_cv": f"{args.outer_splits}-fold stratified shuffled; one repeat",
            "inner_cv": (
                f"{args.inner_splits}-fold stratified shuffled within each outer training set"
            ),
            "seed": args.seed,
            "selection_metric": "ROC-AUC",
            "reporting": (
                "All three model families; outer-fold mean and SD; no pooled winner selection."
            ),
            "privacy": "No row-level predictions, true labels, or split indices are written.",
        },
        "datasets": {
            "uci_heart_failure_519": {
                "target": "death_event",
                "target_counts": heart_failure["dataset_summary"]["target_counts"],
                "metrics_file": "uci_heart_failure_519_nested_metrics.json",
            },
            "uci_mi_complications_579": {
                "target": "any_lethal_outcome",
                "target_counts": mi["dataset_summary"]["target_counts"],
                "metrics_file": "uci_mi_complications_579_nested_metrics.json",
            },
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
