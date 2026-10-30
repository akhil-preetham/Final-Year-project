"""Repeat the reliability split to quantify uncertainty-evidence variability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_reliability import run_dataset

from cardiodiag.reliability import bootstrap_mean_ci


def _extract_metrics(result: dict[str, Any], candidate: str) -> dict[str, float]:
    record = result["candidates"][candidate]
    evidence = record["uncertainty_evidence"]
    curve = evidence["selective_risk"]
    return {
        "confidence_error_auc": float(evidence["confidence_error_auc"]),
        "aurc": float(evidence["aurc"]),
        "full_coverage_risk": float(curve[-1]["risk"]),
        "conformal_coverage": float(record["conformal"]["coverage"]),
        "abstention_rate": float(record["conformal"]["abstention_rate"]),
        "ece_uniform": float(record["calibration"]["ece_uniform"]),
    }


def _summarize_metric(values: list[float]) -> dict[str, Any]:
    mean, low, high = bootstrap_mean_ci(values, random_state=42)
    return {"mean": mean, "bootstrap_ci": {"low": low, "high": high}}


def run_repeated(
    dataset: Path,
    target: str,
    seeds: list[int],
) -> dict[str, Any]:
    if len(seeds) < 2:
        raise ValueError("At least two seeds are required for repeated evidence")
    records = [run_dataset(dataset, target, seed) for seed in seeds]
    candidates = ["corrected_osec", "stable_osec"]
    summaries: dict[str, Any] = {}
    for candidate in candidates:
        metric_records = [_extract_metrics(result, candidate) for result in records]
        metric_names = metric_records[0].keys()
        summaries[candidate] = {
            metric: _summarize_metric([record[metric] for record in metric_records])
            for metric in metric_names
        }
    return {
        "dataset": str(dataset),
        "target": target,
        "seeds": seeds,
        "protocol": (
            "Repeated internal 56.25% fit, 18.75% calibration, 25% evaluation "
            "splits; no test labels used for fitting or calibration"
        ),
        "candidates": summaries,
        "per_seed": [
            {
                "seed": seed,
                "candidates": {
                    candidate: _extract_metrics(result, candidate)
                    for candidate in candidates
                },
            }
            for seed, result in zip(seeds, records)
        ],
        "interpretation": (
            "These are repeated internal reliability estimates. They can show "
            "confidence/error association and coverage variability, but cannot "
            "establish external validity or semantic understanding of uncertainty."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(42, 52)))
    args = parser.parse_args()
    result = run_repeated(args.dataset, args.target, args.seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote repeated uncertainty evidence to {args.output}")


if __name__ == "__main__":
    main()
