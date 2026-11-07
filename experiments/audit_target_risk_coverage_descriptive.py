"""Describe risk-coverage behavior on saved, previously examined transfer targets.

This runner performs no fitting and makes no threshold choices. All target-label
metrics are retrospective/descriptive and cannot establish confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "selective_audit_20261106_run2"
STUDIES = {
    "AngioCAD": {
        "path": ROOT / "results/transfer_20261105_angiocad_domain_guard/target_predictions.csv",
        "label": "label_for_scoring",
    },
    "Duke ACATH": {
        "path": ROOT / "results/transfer_20261105_duke_acath_final/target_predictions.csv",
        "label": "observed_label_for_scoring",
    },
}
GRID = np.linspace(0.05, 1.0, 20)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson_interval(successes: int, n: int, z: float = 1.959963984540054) -> list[float] | None:
    """95% Wilson score interval for a binomial proportion."""
    if n == 0:
        return None
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    radius = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return [float(max(0.0, center - radius)), float(min(1.0, center + radius))]


def risk_coverage_curve(
    labels: np.ndarray, probabilities: np.ndarray, coverages: np.ndarray = GRID
) -> list[dict[str, float | int]]:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    if labels.ndim != 1 or probabilities.shape != labels.shape or labels.size == 0:
        raise ValueError("labels and probabilities must be non-empty aligned vectors")
    if not np.isfinite(probabilities).all() or np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("probabilities must be finite and lie in [0, 1]")
    prediction = (probabilities >= 0.5).astype(int)
    confidence = np.maximum(probabilities, 1 - probabilities)
    order = np.argsort(-confidence, kind="mergesort")
    errors = (prediction != labels)[order]
    rows: list[dict[str, float | int]] = []
    for requested in coverages:
        if not 0 < requested <= 1:
            raise ValueError("coverages must lie in (0, 1]")
        count = max(1, int(np.ceil(float(requested) * len(labels))))
        error_count = int(errors[:count].sum())
        rows.append(
            {
                "requested_coverage": float(requested),
                "coverage": count / len(labels),
                "accepted_n": count,
                "accepted_error_count": error_count,
                "selective_risk": error_count / count,
                "risk_wilson_95": wilson_interval(error_count, count),
            }
        )
    return rows


def partition_summary(
    labels: np.ndarray, probabilities: np.ndarray, accepted: np.ndarray, policy: str
) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    accepted = np.asarray(accepted, dtype=bool)
    if not (labels.shape == probabilities.shape == accepted.shape):
        raise ValueError("labels, probabilities, and acceptance flags must align")
    prediction = (probabilities >= 0.5).astype(int)
    errors = prediction != labels
    accepted_n = int(accepted.sum())
    rejected_n = int((~accepted).sum())
    accepted_errors = int(errors[accepted].sum())
    rejected_errors = int(errors[~accepted].sum())
    return {
        "policy": policy,
        "n": int(len(labels)),
        "accepted_n": accepted_n,
        "rejected_n": rejected_n,
        "coverage": accepted_n / len(labels),
        "coverage_wilson_95": wilson_interval(accepted_n, len(labels)),
        "accepted_class_counts": {
            "0": int(np.count_nonzero(labels[accepted] == 0)),
            "1": int(np.count_nonzero(labels[accepted] == 1)),
        },
        "rejected_class_counts": {
            "0": int(np.count_nonzero(labels[~accepted] == 0)),
            "1": int(np.count_nonzero(labels[~accepted] == 1)),
        },
        "accepted_errors": accepted_errors,
        "accepted_risk": accepted_errors / accepted_n if accepted_n else None,
        "accepted_risk_wilson_95": wilson_interval(accepted_errors, accepted_n),
        "rejected_errors": rejected_errors,
        "rejected_risk": rejected_errors / rejected_n if rejected_n else None,
        "rejected_risk_wilson_95": wilson_interval(rejected_errors, rejected_n),
    }


def audit_study(name: str, config: dict[str, str]) -> dict[str, Any]:
    path = Path(config["path"])
    data = pd.read_csv(path, float_precision="round_trip")
    label_column = config["label"]
    required = {
        label_column,
        "exploratory_calibrated_probability",
        "exploratory_conformal_abstain",
        "exploratory_knn_ood_flag",
        "exploratory_isolation_forest_ood_flag",
        "exploratory_combined_abstain",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"{name}: missing saved prediction columns: {sorted(missing)}")
    labels = data[label_column].to_numpy(dtype=int)
    probabilities = data["exploratory_calibrated_probability"].to_numpy(dtype=float)
    conformal_accept = ~data["exploratory_conformal_abstain"].to_numpy(dtype=bool)
    knn_accept = ~data["exploratory_knn_ood_flag"].to_numpy(dtype=bool)
    forest_accept = ~data["exploratory_isolation_forest_ood_flag"].to_numpy(dtype=bool)
    combined_accept = ~data["exploratory_combined_abstain"].to_numpy(dtype=bool)
    policies = [
        partition_summary(
            labels, probabilities, np.ones(len(data), dtype=bool), "all_rows_fixed_0.5"
        ),
        partition_summary(labels, probabilities, conformal_accept, "conformal_singleton_only"),
        partition_summary(labels, probabilities, knn_accept, "knn_support_only"),
        partition_summary(labels, probabilities, forest_accept, "isolation_forest_only"),
        partition_summary(labels, probabilities, combined_accept, "registered_conformal_plus_knn"),
    ]
    return {
        "dataset": name,
        "source_predictions": path.relative_to(ROOT).as_posix(),
        "source_predictions_sha256": sha256_file(path),
        "n": int(len(data)),
        "target_label_column": label_column,
        "target_label_status": "already_examined; retrospective descriptive audit only",
        "risk_coverage_curve": risk_coverage_curve(labels, probabilities),
        "policies": policies,
    }


def main(output_dir: Path = OUTPUT) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    studies = [audit_study(name, config) for name, config in STUDIES.items()]
    result = {
        "audit_id": "SELECTIVE-RISK-COVERAGE-POSTHOC-20261106",
        "status": "descriptive_saved_target_predictions_no_refitting_or_threshold_selection",
        "runner_sha256": sha256_file(Path(__file__)),
        "coverage_grid": GRID.tolist(),
        "risk_definition": (
            "fraction of accepted rows misclassified at fixed saved probability cutoff 0.5"
        ),
        "confidence_definition": "max(p, 1-p) from saved source-calibrated probabilities",
        "confidence_intervals": "Wilson score 95% intervals, conditional on observed rows",
        "limitations": [
            "AngioCAD and Duke target labels were previously examined; all results are post-hoc.",
            (
                "The source-calibrated probabilities and all policy flags are read "
                "from frozen artifacts."
            ),
            "No target labels are used to fit a model, change a threshold, or choose a policy.",
            (
                "Intervals condition on one observed cohort and do not estimate "
                "between-site variation."
            ),
            (
                "Duke endpoint differs from source; neither cohort establishes "
                "confirmatory validation."
            ),
        ],
        "studies": studies,
    }
    (output_dir / "risk_coverage_audit.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    pd.DataFrame(
        [
            {"dataset": study["dataset"], **row}
            for study in studies
            for row in study["risk_coverage_curve"]
        ]
    ).to_csv(output_dir / "risk_coverage_curves.csv", index=False)
    pd.DataFrame(
        [{"dataset": study["dataset"], **row} for study in studies for row in study["policies"]]
    ).to_csv(output_dir / "accepted_rejected_policy_summary.csv", index=False)

    figure, axes = plt.subplots(1, len(studies), figsize=(12, 5), sharey=True)
    for axis, study in zip(np.atleast_1d(axes), studies, strict=True):
        curve = study["risk_coverage_curve"]
        axis.plot(
            [row["coverage"] for row in curve],
            [row["selective_risk"] for row in curve],
            marker="o",
            markersize=3,
            label="Confidence-ranked",
        )
        by_name = {row["policy"]: row for row in study["policies"]}
        for policy, label, marker in [
            ("conformal_singleton_only", "Conformal singleton", "s"),
            ("registered_conformal_plus_knn", "Conformal + kNN", "D"),
        ]:
            row = by_name[policy]
            axis.scatter(row["coverage"], row["accepted_risk"], marker=marker, label=label)
        axis.set(title=study["dataset"], xlabel="Coverage", xlim=(0, 1.02), ylim=(0, 1))
        axis.grid(alpha=0.25)
        axis.legend(fontsize=8)
    axes[0].set_ylabel("Observed selective risk (error rate)")
    figure.suptitle("Post-hoc risk–coverage diagnostic on saved target predictions")
    figure.tight_layout()
    figure.savefig(output_dir / "risk_coverage_descriptive.png", dpi=180)
    plt.close(figure)
    print(f"Wrote descriptive risk-coverage audit to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    main(parser.parse_args().output_dir)
