"""Run calibration, conformal, selective-risk, and stability analyses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sklearn.model_selection import train_test_split

from cardiodiag.data import drop_identifier_columns, load_dataset
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.reliability import calibration_summary, uncertainty_evidence
from cardiodiag.uncertainty import SplitConformalClassifier


def run_dataset(dataset: Path, target: str, seed: int) -> dict[str, Any]:
    X, y = load_dataset(dataset, target)
    X, dropped = drop_identifier_columns(X)
    X_dev, X_eval, y_dev, y_eval = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=seed
    )
    X_fit, X_cal, y_fit, y_cal = train_test_split(
        X_dev, y_dev, test_size=0.25, stratify=y_dev, random_state=seed
    )
    results: dict[str, Any] = {
        "dataset": str(dataset),
        "target": target,
        "seed": seed,
        "dropped_identifier_columns": dropped,
        "evaluation_protocol": (
            "56.25% fit, 18.75% calibration, 25% evaluation; all split before fitting"
        ),
        "candidates": {},
    }
    for variant, stable in [("osec", False), ("osec", True)]:
        name = "stable_osec" if stable else "corrected_osec"
        pipeline = build_corrected_pipeline(
            X_fit,
            variant=variant,
            seed=seed,
            use_stable_selector=stable,
        )
        conformal = SplitConformalClassifier(pipeline, alpha=0.1)
        conformal.fit(X_fit, y_fit, X_cal, y_cal)
        probabilities = conformal.predict_proba(X_eval)[:, 1]
        uncertainty = uncertainty_evidence(y_eval.to_numpy(), probabilities)
        candidate = {
            "calibration": calibration_summary(y_eval.to_numpy(), probabilities),
            "uncertainty_evidence": uncertainty,
            "selective_risk": uncertainty["selective_risk"],
            "conformal": conformal.summarize(X_eval, y_eval.to_numpy()),
            "conformal_quantile": conformal.quantile_,
        }
        results["candidates"][name] = candidate
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = run_dataset(args.dataset, args.target, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote reliability results to {args.output}")


if __name__ == "__main__":
    main()
