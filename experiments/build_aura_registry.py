"""Validate and index AURA-ML artifacts without modifying the CARDIODIAG registry."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

METRICS = (
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


def _finite(value: Any) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite numeric value found")
    elif isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)


def _validate_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _finite(payload)
    if payload.get("status") != "completed":
        raise ValueError(f"{path} is not completed")
    if payload["configuration"]["outer_splits"] < 2:
        raise ValueError(f"{path} has fewer than two outer folds")
    for key in ("aura_ml", "existing_baseline"):
        section = payload[key]
        folds = section["folds"]
        if len(folds) != payload["configuration"]["outer_splits"]:
            raise ValueError(f"{path}: {key} has incomplete fold records")
        for fold in folds:
            lengths = {
                len(fold["test_indices"]),
                len(fold["y_true"]),
                len(fold["predicted_probability"]),
                fold["test_n"],
            }
            if len(lengths) != 1:
                raise ValueError(f"{path}: inconsistent prediction lengths")
        for metric in METRICS:
            if metric not in section["pooled_outer_metrics"]:
                raise ValueError(f"{path}: missing metric {metric}")
    return payload


def build(input_dir: Path, output: Path) -> dict[str, Any]:
    artifacts = sorted(input_dir.glob("aura_nested_2x2_*.json"))
    if len(artifacts) != 3:
        raise ValueError(f"expected three primary AURA artifacts, found {len(artifacts)}")
    entries = []
    for path in artifacts:
        payload = _validate_artifact(path)
        entries.append(
            {
                "dataset": payload["dataset_summary"]["path"],
                "dataset_sha256": payload["dataset_summary"]["sha256"],
                "rows": payload["dataset_summary"]["rows"],
                "target": payload["target"],
                "artifact": str(path).replace("\\", "/"),
                "protocol": payload["configuration"],
                "aura_ml": payload["aura_ml"]["pooled_outer_metrics"],
                "existing_baseline": payload["existing_baseline"]["pooled_outer_metrics"],
                "paired_comparison": payload["paired_comparison"],
                "runtime_seconds": payload["execution"]["runtime_seconds"],
                "selected_outputs": [
                    fold["fit_summary"]["fusion"]["selected_output"]
                    for fold in payload["aura_ml"]["folds"]
                ],
                "selected_candidates": [
                    fold["fit_summary"]["selected_names"]
                    for fold in payload["aura_ml"]["folds"]
                ],
            }
        )
    registry = {
        "status": "completed_and_validated",
        "method": "AURA-ML research prototype",
        "evidence_class": "exploratory_internal_nested_validation",
        "interpretation": (
            "AURA artifacts are separate from the authoritative CARDIODIAG registry; "
            "2x2 results do not establish superiority or external validation."
        ),
        "entries": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("results/aura_ml"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/aura_ml/AURA_ML_REGISTRY.json")
    )
    args = parser.parse_args()
    registry = build(args.input_dir, args.output)
    print(f"Validated and indexed {len(registry['entries'])} AURA artifacts")


if __name__ == "__main__":
    main()
