"""Compare frozen CARDIODIAG abstention components on already-scored targets.

This is a post-hoc audit of saved predictions. It does not refit models, alter
source-derived thresholds, or choose a deployment policy from target labels.
Target-label performance is descriptive because the evaluated target cohorts
have already been examined in this project.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "validity_audit_20261105" / "selective_policy_components"
STUDIES = {
    "AngioCAD": {
        "directory": ROOT / "results" / "transfer_20261105_angiocad_domain_guard",
        "protocol": ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD_DOMAIN_GUARD.md",
        "label_column": "label_for_scoring",
        "source_file": "source_conformal_predictions.csv",
        "knn_metric": "knn_domain_robust",
    },
    "Duke ACATH": {
        "directory": ROOT / "results" / "transfer_20261105_duke_acath_final",
        "protocol": ROOT / "docs" / "TRANSFER_STUDY_PROTOCOL_20261105_DUKE.md",
        "label_column": "observed_label_for_scoring",
        "source_file": "source_calibration_predictions.csv",
        "knn_metric": "primary_knn_domain_robust",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selective_metrics(
    labels: np.ndarray,
    predictions: np.ndarray,
    accepted: np.ndarray,
    probabilities: np.ndarray,
    policy: str,
    status: str,
) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=int)
    predictions = np.asarray(predictions, dtype=int)
    accepted = np.asarray(accepted, dtype=bool)
    probabilities = np.asarray(probabilities, dtype=float)
    if not (len(labels) == len(predictions) == len(accepted) == len(probabilities)):
        raise ValueError("labels, predictions, acceptance flags, and probabilities must align")
    n = len(labels)
    accepted_n = int(accepted.sum())
    y = labels[accepted]
    pred = predictions[accepted]
    prob = probabilities[accepted]
    errors = int(np.count_nonzero(y != pred))
    tn, fp, fn, tp = (
        confusion_matrix(y, pred, labels=[0, 1]).ravel() if accepted_n else (0, 0, 0, 0)
    )
    positive_n = int(np.count_nonzero(y == 1))
    negative_n = int(np.count_nonzero(y == 0))
    return {
        "policy": policy,
        "status": status,
        "n": n,
        "accepted_n": accepted_n,
        "abstained_n": n - accepted_n,
        "coverage": accepted_n / n if n else None,
        "accepted_error_count": errors,
        "accepted_error_rate": errors / accepted_n if accepted_n else None,
        "accepted_accuracy": float(accuracy_score(y, pred)) if accepted_n else None,
        "accepted_balanced_accuracy": (
            float(balanced_accuracy_score(y, pred)) if positive_n and negative_n else None
        ),
        "accepted_sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "accepted_specificity": float(tn / (tn + fp)) if tn + fp else None,
        "accepted_roc_auc": (float(roc_auc_score(y, prob)) if positive_n and negative_n else None),
        "accepted_average_precision": (
            float(average_precision_score(y, prob)) if positive_n and negative_n else None
        ),
        "accepted_class_counts": {"0": negative_n, "1": positive_n},
        "accepted_confusion_matrix_tn_fp_fn_tp": [int(tn), int(fp), int(fn), int(tp)],
    }


def _make_policy_rows(target: pd.DataFrame, labels: np.ndarray) -> list[dict[str, Any]]:
    probability = target["exploratory_calibrated_probability"].to_numpy(dtype=float)
    point_prediction = (probability >= 0.5).astype(int)
    conformal_prediction = target["exploratory_conformal_prediction"].to_numpy(dtype=int)
    conformal_accept = ~target["exploratory_conformal_abstain"].to_numpy(dtype=bool)
    knn_alert = target["exploratory_knn_ood_flag"].to_numpy(dtype=bool)
    forest_alert = target["exploratory_isolation_forest_ood_flag"].to_numpy(dtype=bool)
    registry_accept = target["domain_gate_action"].eq("score").to_numpy(dtype=bool)

    policies = [
        (
            "fixed_probability_0.5",
            point_prediction,
            np.ones(len(target), dtype=bool),
            "saved source-calibrated probability; fixed cutoff 0.5; no abstention",
        ),
        (
            "conformal_singleton_only",
            conformal_prediction,
            conformal_accept,
            "frozen source-domain-robust conformal set; accept singleton sets",
        ),
        (
            "knn_domain_robust_only",
            point_prediction,
            ~knn_alert,
            "frozen source-domain-robust kNN alert; point class uses fixed 0.5 cutoff",
        ),
        (
            "isolation_forest_domain_robust_only",
            point_prediction,
            ~forest_alert,
            "frozen source-domain-robust Isolation Forest alert; fixed 0.5 cutoff",
        ),
        (
            "conformal_plus_knn_registered_combination",
            target["exploratory_combined_prediction"].to_numpy(dtype=int),
            ~target["exploratory_combined_abstain"].to_numpy(dtype=bool),
            "registered research combination: singleton conformal set and no kNN alert",
        ),
        (
            "conformal_plus_isolation_forest_posthoc",
            conformal_prediction,
            conformal_accept & ~forest_alert,
            "post-hoc composition of frozen components; not the registered combination",
        ),
        (
            "conformal_plus_either_detector_posthoc",
            conformal_prediction,
            conformal_accept & ~knn_alert & ~forest_alert,
            "post-hoc composition of frozen components; not the registered combination",
        ),
        (
            "unknown_domain_registry_gate",
            point_prediction,
            registry_accept,
            "runtime registry gate; unknown target site is expected to abstain before scoring",
        ),
    ]

    combined_expected = ~conformal_accept | knn_alert
    combined_accept = ~target["exploratory_combined_abstain"].to_numpy(dtype=bool)
    if not np.array_equal(combined_accept, ~combined_expected):
        raise ValueError(
            "Saved integrated-combination flags do not match the conformal plus primary kNN policy"
        )
    rows = []
    for name, predictions, accepted, status in policies:
        result = _selective_metrics(labels, predictions, accepted, probability, name, status)
        result["target_label_use"] = "evaluation_only; post-hoc, descriptive, not policy selection"
        rows.append(result)
    return rows


def _domain_detection_metrics(
    source_scores: np.ndarray,
    target_scores: np.ndarray,
    threshold: float,
    recorded_metrics: dict[str, Any],
) -> dict[str, Any]:
    source_scores = np.asarray(source_scores, dtype=float)
    target_scores = np.asarray(target_scores, dtype=float)
    domain_labels = np.concatenate(
        [np.zeros(len(source_scores), dtype=int), np.ones(len(target_scores), dtype=int)]
    )
    scores = np.concatenate([source_scores, target_scores])
    recomputed_auroc = float(roc_auc_score(domain_labels, scores))
    source_recomputed_count = int(np.count_nonzero(source_scores > threshold))
    target_recomputed_count = int(np.count_nonzero(target_scores > threshold))
    recorded_auroc = float(recorded_metrics["target_vs_source_auroc"])
    recorded_source_count = int(recorded_metrics["source_false_alert_count"])
    recorded_target_count = int(recorded_metrics["target_alert_count"])
    if source_recomputed_count != recorded_source_count:
        raise ValueError("Round-trip source scores do not reproduce the frozen false-alert count")
    if target_recomputed_count != recorded_target_count:
        raise ValueError("Round-trip target scores do not reproduce the frozen alert count")
    if not np.isclose(recomputed_auroc, recorded_auroc, rtol=0.0, atol=1e-12):
        raise ValueError("Round-trip scores do not reproduce the frozen target-vs-source AUROC")
    source_fpr = float(recorded_metrics["source_false_alert_rate"])
    target_sensitivity = float(recorded_metrics["target_alert_rate"])
    return {
        "score_semantics": (
            "Anomaly score; larger means less source-like, not a calibrated probability."
        ),
        "threshold": float(threshold),
        "threshold_origin": "frozen source-only per-domain 95th-percentile rule",
        "target_vs_source_auroc_recomputed_from_saved_scores": recomputed_auroc,
        "target_vs_source_auroc_recorded_in_frozen_run": recorded_auroc,
        "auroc_recomputation_matches_frozen_metrics": True,
        "target_vs_source_average_precision": float(average_precision_score(domain_labels, scores)),
        "average_precision_prevalence_baseline": float(np.mean(domain_labels)),
        "source_calibration": {
            "n": int(len(source_scores)),
            "false_alert_count_recorded": recorded_source_count,
            "false_alert_count_recomputed_from_round_trip_csv": source_recomputed_count,
            "recomputation_matches_frozen_metrics": True,
            "false_positive_rate_recorded": source_fpr,
            "specificity_at_threshold": 1.0 - source_fpr,
        },
        "target_cohort": {
            "n": int(len(target_scores)),
            "detected_count_recorded": recorded_target_count,
            "detected_count_recomputed_from_round_trip_csv": target_recomputed_count,
            "recomputation_matches_frozen_metrics": True,
            "sensitivity_at_threshold": target_sensitivity,
            "alert_rate": target_sensitivity,
        },
        "score_calibration": {
            "status": "not applicable: detector scores are anomaly scores, not probabilities",
            "reason": "No independent site-labeled calibration cohort is available.",
        },
    }


def _source_lodo_stability(metrics: dict[str, Any], detector: str) -> dict[str, Any]:
    lodo = metrics.get("source_domain_lodo", metrics.get("lodo_source_domain_stress_test", {}))
    folds = lodo.get("folds", [])
    key = "knn" if detector == "knn" else "isolation_forest"
    values = [float(fold["ood"][key]["target_vs_source_auroc"]) for fold in folds]
    return {
        "fold_auroc_by_heldout_source_domain": {
            str(fold["heldout_source_domain"]): float(fold["ood"][key]["target_vs_source_auroc"])
            for fold in folds
        },
        "fold_count": len(values),
        "mean_auroc": float(np.mean(values)) if values else None,
        "minimum_auroc": float(np.min(values)) if values else None,
        "maximum_auroc": float(np.max(values)) if values else None,
        "interpretation": (
            "Retrospective source-cohort stress check; the four UCI cohorts overlap the "
            "historical Heart5 composite and are not independent external sites."
        ),
    }


def _audit_study(name: str, config: dict[str, Any]) -> dict[str, Any]:
    directory = config["directory"]
    target_path = directory / "target_predictions.csv"
    metrics_path = directory / "study_metrics.json"
    source_path = directory / config["source_file"]
    target = pd.read_csv(target_path, float_precision="round_trip")
    source = pd.read_csv(source_path, float_precision="round_trip")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    labels = target[config["label_column"]].to_numpy(dtype=int)
    ood = metrics["ood"]
    knn = ood[config["knn_metric"]]
    forest = ood["isolation_forest_domain_robust"]

    thresholds = {
        "knn_domain_robust": float(knn["threshold"]),
        "isolation_forest_domain_robust": float(forest["threshold"]),
    }
    source_alert_audits = {}
    target_alert_audits = {}
    detector_metrics = {}
    for detector_name, column, metric in (
        ("knn_domain_robust", "knn_support_score", knn),
        ("isolation_forest_domain_robust", "isolation_forest_score", forest),
    ):
        threshold = thresholds[detector_name]
        source_scores = source[column].to_numpy(dtype=float)
        recomputed_count = int(np.count_nonzero(source_scores > threshold))
        recorded_count = int(metric["source_false_alert_count"])
        if recomputed_count != recorded_count:
            raise ValueError(
                f"{name}: round-trip CSV source alert count differs from frozen run metrics"
            )
        source_alert_audits[detector_name] = {
            "csv_round_trip_strict_greater_count": recomputed_count,
            "recorded_frozen_false_alert_count": recorded_count,
            "recorded_frozen_false_alert_rate": float(metric["source_false_alert_rate"]),
            "recomputation_matches_frozen_metrics": True,
        }
        target_flag_column = (
            "exploratory_knn_ood_flag"
            if detector_name == "knn_domain_robust"
            else "exploratory_isolation_forest_ood_flag"
        )
        saved_target_count = int(target[target_flag_column].astype(bool).sum())
        recorded_target_count = int(metric["target_alert_count"])
        if saved_target_count != recorded_target_count:
            raise ValueError(f"{name}: target alert flags do not match the frozen run metrics")
        target_alert_audits[detector_name] = {
            "target_flag_count": saved_target_count,
            "target_alert_rate": float(metric["target_alert_rate"]),
            "score_recomputation_matches_saved_flags": True,
        }
        target_score_column = (
            "exploratory_knn_support_score"
            if detector_name == "knn_domain_robust"
            else "exploratory_isolation_forest_score"
        )
        detector_metrics[detector_name] = _domain_detection_metrics(
            source_scores,
            target[target_score_column].to_numpy(dtype=float),
            threshold,
            metric,
        )
    return {
        "dataset": name,
        "study_id": metrics.get("study_id"),
        "target_rows": int(len(target)),
        "target_class_counts": {
            str(int(k)): int(v) for k, v in pd.Series(labels).value_counts().sort_index().items()
        },
        "endpoint_note": (
            metrics.get("endpoint_compatibility", {}).get("status")
            if isinstance(metrics.get("endpoint_compatibility"), dict)
            else "see frozen study protocol; endpoint comparability is limited"
        ),
        "frozen_thresholds": thresholds,
        "source_calibration_alert_reconciliation": source_alert_audits,
        "target_alert_reconciliation": target_alert_audits,
        "ood_detection_metrics": detector_metrics,
        "source_cohort_lodo_stability": {
            "knn_domain_robust": _source_lodo_stability(metrics, "knn"),
            "isolation_forest_domain_robust": _source_lodo_stability(metrics, "isolation_forest"),
        },
        "source_calibration_rows": int(len(source)),
        "unknown_target_domain_registry": {
            "registered_source_domains": metrics["domain_registry_gate"].get(
                "registered_source_domains",
                metrics["domain_registry_gate"].get("source_domains", []),
            ),
            "target_domain_id": metrics["domain_registry_gate"].get("target_domain_id"),
            "target_action_counts": metrics["domain_registry_gate"].get("action_counts"),
        },
        "policies": _make_policy_rows(target, labels),
        "inputs_sha256": {
            "target_predictions.csv": _sha256(target_path),
            config["source_file"]: _sha256(source_path),
            "study_metrics.json": _sha256(metrics_path),
            config["protocol"].name: _sha256(config["protocol"]),
        },
    }


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Selective Policy Component Audit",
        "",
        (
            "Generated from frozen prediction and metrics files. Target-label results "
            "are post-hoc descriptive summaries; they did not select thresholds, "
            "features, models, or policies."
        ),
        "",
        (
            "The domain registry is the runtime action: each target is an unregistered "
            "site, so its deployed path abstains for every row. The exploratory rows "
            "below are diagnostic analyses only."
        ),
        "",
        "## Results",
        "",
    ]
    for study in result["studies"]:
        lines.extend(
            [
                f"### {study['dataset']} ({study['study_id']})",
                "",
                (
                    f"Rows: {study['target_rows']}; labels for retrospective scoring: "
                    f"{study['target_class_counts']}."
                ),
                "",
                (
                    "| Policy | Coverage | Accepted n | Errors | Error rate | "
                    "Bal. acc. | Sens. | Spec. |"
                ),
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for policy in study["policies"]:

            def fmt(value: Any) -> str:
                return "—" if value is None else f"{value:.3f}"

            cells = [
                f"`{policy['policy']}`",
                fmt(policy["coverage"]),
                str(policy["accepted_n"]),
                str(policy["accepted_error_count"]),
                fmt(policy["accepted_error_rate"]),
                fmt(policy["accepted_balanced_accuracy"]),
                fmt(policy["accepted_sensitivity"]),
                fmt(policy["accepted_specificity"]),
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.extend(
            [
                "",
                "Detector thresholds are frozen from source-only partitions:",
                "",
                "| Detector | Source false alerts | Target alerts | Recalculation |",
                "|---|---:|---:|---:|",
                *[
                    "| `{}` | {}/{} ({:.1%}) | {}/{} ({:.1%}) | {} |".format(
                        detector,
                        audit["recorded_frozen_false_alert_count"],
                        study["source_calibration_rows"],
                        audit["recorded_frozen_false_alert_rate"],
                        study["target_alert_reconciliation"][detector]["target_flag_count"],
                        study["target_rows"],
                        study["target_alert_reconciliation"][detector]["target_alert_rate"],
                        "matches frozen metrics",
                    )
                    for detector, audit in study["source_calibration_alert_reconciliation"].items()
                ],
                "",
                (
                    "Thresholds and alert definitions are unchanged. CSV scores were "
                    "parsed in round-trip mode; source counts, target flags, and saved "
                    "run metrics agree."
                ),
                "",
                (
                    "Source-vs-target detector metrics use target-cohort membership as "
                    "the positive domain label:"
                ),
                "",
                "| Detector | AUROC | AUPRC | AUPRC baseline | Sensitivity | Specificity |",
                "|---|---:|---:|---:|---:|---:|",
                *[
                    "| `{}` | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(
                        detector,
                        audit["target_vs_source_auroc_recomputed_from_saved_scores"],
                        audit["target_vs_source_average_precision"],
                        audit["average_precision_prevalence_baseline"],
                        audit["target_cohort"]["sensitivity_at_threshold"],
                        audit["source_calibration"]["specificity_at_threshold"],
                    )
                    for detector, audit in study["ood_detection_metrics"].items()
                ],
                "",
                (
                    "AUPRC baseline depends on the source/target sample ratio. "
                    "Detector scores are not calibrated probabilities."
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation limits",
            "",
            (
                "- Coverage and accepted error are cohort-specific summaries; they do "
                "not establish safe individual decisions."
            ),
            (
                "- The endpoint and population definitions differ. Consult each frozen "
                "protocol before comparing performance."
            ),
            (
                "- Composite post-hoc policies were not prespecified or deployed. "
                "These results cannot select a policy from previously examined labels."
            ),
            (
                "- A zero-error subset with low coverage and one observed class cannot "
                "estimate discrimination, calibration, or population safety."
            ),
            (
                "- Zero coverage from the unknown-site gate is fail-closed behavior, "
                "not successful predictive validation."
            ),
            "",
            "## Reproduction",
            "",
            "```powershell",
            "uv run python experiments/audit_selective_policy_components.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def run(output_dir: Path = OUTPUT) -> None:
    expected_outputs = {
        "selective_policy_component_audit.json",
        "selective_policy_component_audit.csv",
        "SELECTIVE_POLICY_COMPONENT_AUDIT.md",
        "reproduction_manifest.json",
    }
    if output_dir.exists():
        unexpected = {path.name for path in output_dir.iterdir()} - expected_outputs
        if unexpected:
            raise FileExistsError(
                f"Refusing to overwrite unexpected artifacts in {output_dir}: {sorted(unexpected)}"
            )
    studies = [_audit_study(name, config) for name, config in STUDIES.items()]
    result = {
        "audit_id": "CARDIODIAG-SELECTIVE-COMPONENT-AUDIT-POSTHOC-20261105",
        "status": "completed_posthoc_audit_of_frozen_predictions",
        "threshold_selection": (
            "source-only; all component thresholds were read from frozen study metrics"
        ),
        "target_label_use": "evaluation only; no policy selection or threshold tuning",
        "runner_sha256": _sha256(Path(__file__).resolve()),
        "studies": studies,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "selective_policy_component_audit.json"
    csv_path = output_dir / "selective_policy_component_audit.csv"
    markdown_path = output_dir / "SELECTIVE_POLICY_COMPONENT_AUDIT.md"
    json_path.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    rows = [
        {"dataset": study["dataset"], **policy} for study in studies for policy in study["policies"]
    ]
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    markdown_path.write_text(_render_markdown(result), encoding="utf-8")
    manifest = {
        "audit_id": result["audit_id"],
        "runner_sha256": result["runner_sha256"],
        "study_inputs_sha256": {study["dataset"]: study["inputs_sha256"] for study in studies},
        "generated_outputs_sha256": {
            path.name: _sha256(path) for path in (json_path, csv_path, markdown_path)
        },
    }
    (output_dir / "reproduction_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(f"Wrote selective-policy component audit to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    run(parser.parse_args().output_dir)
