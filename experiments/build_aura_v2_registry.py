"""Aggregate AURA V2 confirmatory artifacts without promoting them to V1."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def _finite(value: Any) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite value")
    elif isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)


def _paired_seed_summary(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = np.asarray(
        [
            payload["primary_paired_comparison"]["roc_auc_delta_aura_minus_baseline"]["point"]
            for payload in payloads
        ],
        dtype=float,
    )
    aura_auc = np.asarray(
        [payload["aura_ml"]["pooled_outer_metrics"]["roc_auc"] for payload in payloads]
    )
    baseline_auc = np.asarray(
        [
            payload["baselines"][payload["configuration"]["primary_baseline"]][
                "pooled_outer_metrics"
            ]["roc_auc"]
            for payload in payloads
        ]
    )
    return {
        "seed_count": len(payloads),
        "seeds": [payload["configuration"]["seed"] for payload in payloads],
        "aura_roc_auc_mean": float(aura_auc.mean()),
        "aura_roc_auc_sd": float(aura_auc.std(ddof=1)),
        "baseline_roc_auc_mean": float(baseline_auc.mean()),
        "baseline_roc_auc_sd": float(baseline_auc.std(ddof=1)),
        "paired_auc_delta_mean": float(deltas.mean()),
        "paired_auc_delta_sd": float(deltas.std(ddof=1)),
        "paired_auc_delta_min": float(deltas.min()),
        "paired_auc_delta_max": float(deltas.max()),
        "positive_delta_seeds": int(np.sum(deltas > 0)),
        "negative_delta_seeds": int(np.sum(deltas < 0)),
    }


def _validate(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    _finite(payload)
    if payload["status"] != "completed":
        raise ValueError(f"incomplete artifact: {path}")
    configuration = payload["configuration"]
    if configuration["outer_splits"] < 3 or configuration["inner_splits"] < 3:
        raise ValueError(f"not confirmatory 3x3: {path}")
    aura_folds = payload["aura_ml"]["folds"]
    for fold in aura_folds:
        if not (
            len(fold["test_indices"])
            == len(fold["y_true"])
            == len(fold["predicted_probability"])
            == fold["test_n"]
        ):
            raise ValueError(f"inconsistent AURA prediction vector: {path}")
    return payload


def build(input_dir: Path, output: Path) -> dict[str, Any]:
    paths = sorted(input_dir.glob("*.json"))
    paths = [path for path in paths if path.name != "V2_REGISTRY.json"]
    payloads = [(path, _validate(path)) for path in paths]
    by_dataset: dict[str, list[dict[str, Any]]] = {}
    for _, payload in payloads:
        by_dataset.setdefault(payload["target"], []).append(payload)
    entries = []
    for target, dataset_payloads in sorted(by_dataset.items()):
        dataset_payloads.sort(key=lambda payload: payload["configuration"]["seed"])
        first = dataset_payloads[0]
        entries.append(
            {
                "dataset": first["dataset_summary"]["path"],
                "dataset_sha256": first["dataset_summary"]["sha256"],
                "rows": first["dataset_summary"]["rows"],
                "target": target,
                "protocol": {
                    "outer_splits": first["configuration"]["outer_splits"],
                    "inner_splits": first["configuration"]["inner_splits"],
                    "seeds": [payload["configuration"]["seed"] for payload in dataset_payloads],
                },
                "primary_baseline": first["configuration"]["primary_baseline"],
                "seed_summary": _paired_seed_summary(dataset_payloads),
                "artifacts": [
                    str(path).replace("\\", "/")
                    for path, payload in payloads
                    if payload in dataset_payloads
                ],
                "calibration_methods": [
                    [
                        fold["fit_summary"]["calibration_method"]
                        for fold in payload["aura_ml"]["folds"]
                    ]
                    for payload in dataset_payloads
                ],
                "thresholds": [
                    [fold["optimized_threshold"] for fold in payload["aura_ml"]["folds"]]
                    for payload in dataset_payloads
                ],
            }
        )
    registry = {
        "status": "completed_and_validated",
        "method": "AURA-ML V2 evidence-gated adaptive policy",
        "evidence_class": "confirmatory_internal_single_seed_replicated_small_datasets",
        "interpretation": (
            "V2 uses three 3x3 runs on heart5 and Mendeley. The attempted 70K "
            "3x3 run timed out without an artifact and is not included. These are "
            "not external validation results."
        ),
        "entries": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir", type=Path, default=Path("results/aura_ml_v2/confirmatory")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/aura_ml_v2/V2_REGISTRY.json")
    )
    args = parser.parse_args()
    registry = build(args.input_dir, args.output)
    count = sum(entry["seed_summary"]["seed_count"] for entry in registry["entries"])
    print(f"Validated {count} V2 artifacts")


if __name__ == "__main__":
    main()
