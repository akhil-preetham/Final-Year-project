"""Run a one-way evaluation on a frozen external dataset.

The external rows are never passed to ``fit``. The development dataset is split
into fitting and calibration subsets, then the frozen pipeline and conformal
layer are applied to the external rows for metrics only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sklearn.model_selection import train_test_split

from cardiodiag.data import drop_identifier_columns, load_dataset, summarize_dataset
from cardiodiag.evaluation import evaluate_predictions
from cardiodiag.experiments import build_corrected_pipeline
from cardiodiag.external_gate import validate_external_manifest
from cardiodiag.reliability import calibration_summary, uncertainty_evidence
from cardiodiag.uncertainty import SplitConformalClassifier


def run_external_evaluation(
    development_dataset: Path,
    development_target: str,
    external_dataset: Path,
    external_target: str,
    manifest: Path,
    variant: str,
    stable_selector: bool,
    seed: int,
    alpha: float,
) -> dict[str, Any]:
    """Evaluate a development-frozen pipeline without external fitting."""

    frozen_manifest = validate_external_manifest(manifest)
    if frozen_manifest["target_column"] != external_target:
        raise ValueError(
            "External target does not match the frozen manifest: "
            f"{external_target!r} != {frozen_manifest['target_column']!r}"
        )

    X_dev, y_dev = load_dataset(development_dataset, development_target)
    X_external, y_external = load_dataset(external_dataset, external_target)
    X_dev, dropped_dev = drop_identifier_columns(X_dev)
    X_external, dropped_external = drop_identifier_columns(X_external)
    missing = sorted(set(X_dev.columns) - set(X_external.columns))
    if missing:
        raise ValueError(f"External dataset is missing development features: {missing}")
    extra = sorted(set(X_external.columns) - set(X_dev.columns))
    X_external = X_external.loc[:, X_dev.columns]

    X_fit, X_cal, y_fit, y_cal = train_test_split(
        X_dev,
        y_dev,
        test_size=0.25,
        stratify=y_dev,
        random_state=seed,
    )
    pipeline = build_corrected_pipeline(
        X_fit,
        variant=variant,
        seed=seed,
        use_stable_selector=stable_selector,
    )
    conformal = SplitConformalClassifier(pipeline, alpha=alpha)
    conformal.fit(X_fit, y_fit, X_cal, y_cal)
    probabilities = conformal.predict_proba(X_external)[:, 1]
    labels = y_external.to_numpy()
    return {
        "manifest": frozen_manifest,
        "protocol": {
            "development_dataset": str(development_dataset),
            "external_dataset": str(external_dataset),
            "variant": variant,
            "stable_selector": stable_selector,
            "seed": seed,
            "alpha": alpha,
            "external_fit_called": False,
            "external_labels_used_for_fitting_or_calibration": False,
            "external_extra_features_ignored": extra,
        },
        "development_summary": summarize_dataset(development_dataset, development_target).to_dict(),
        "external_summary": summarize_dataset(external_dataset, external_target).to_dict(),
        "dropped_identifier_columns": {
            "development": dropped_dev,
            "external": dropped_external,
        },
        "metrics": evaluate_predictions(labels, probabilities),
        "calibration": calibration_summary(labels, probabilities),
        "uncertainty_evidence": uncertainty_evidence(labels, probabilities),
        "conformal": conformal.summarize(X_external, labels),
        "conformal_quantile": conformal.quantile_,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-dataset", type=Path, required=True)
    parser.add_argument("--development-target", required=True)
    parser.add_argument("--external-dataset", type=Path, required=True)
    parser.add_argument("--external-target", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", choices=["logistic", "ovec", "osec"], default="osec")
    parser.add_argument("--stable-selector", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alpha", type=float, default=0.1)
    args = parser.parse_args()
    result = run_external_evaluation(
        development_dataset=args.development_dataset,
        development_target=args.development_target,
        external_dataset=args.external_dataset,
        external_target=args.external_target,
        manifest=args.manifest,
        variant=args.variant,
        stable_selector=args.stable_selector,
        seed=args.seed,
        alpha=args.alpha,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote external evaluation to {args.output}")


if __name__ == "__main__":
    main()
