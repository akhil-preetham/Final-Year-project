"""Build the authoritative experiment registry from stored JSON artifacts.

This script intentionally uses an explicit artifact allow-list.  The repository
contains archived notebook outputs, smoke runs, and superseded protocol
variants; silently treating every JSON file as a primary result would make
protocol mixing easy.  Each included artifact is checked for valid JSON,
finite numeric values, an existing source script, and a dataset hash that
matches the local manifest when a dataset is available.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

STATUS_DEFINITIONS = {
    "COMPLETED_AND_VERIFIED": (
        "Artifact parses, provenance/hash checks pass, and the documented "
        "protocol was executed successfully."
    ),
    "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED": (
        "Artifact is present and internally checked, but has not been "
        "independently rerun or is bounded/superseded evidence."
    ),
    "EXPLORATORY": "Completed analysis outside the primary CARDIODIAG endpoint.",
    "HISTORICAL": "Archived or pre-correction evidence; never pooled with corrected results.",
    "INCOMPLETE": "Attempted workflow did not finish or lacks a complete result artifact.",
    "FAILED": "Execution failed and the failure is retained as part of the audit trail.",
}


ARTIFACT_SPECS: dict[str, dict[str, Any]] = {
    # Primary corrected CARDIODIAG evidence.
    "post_boundary_corrected_nested_heart5.json": {
        "experiment_id": "nested_internal_post_boundary_heart5",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "src/cardiodiag/nested_validation.py",
        "protocol": "3 outer folds x 3 inner folds, seed 42, ROC-AUC selection",
        "method": "corrected logistic/OVEC/OSEC and stable-selector candidates",
    },
    "post_boundary_corrected_nested_mendeley.json": {
        "experiment_id": "nested_internal_post_boundary_mendeley",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "src/cardiodiag/nested_validation.py",
        "protocol": "3 outer folds x 3 inner folds, seed 42, ROC-AUC selection",
        "method": "corrected logistic/OVEC/OSEC and stable-selector candidates",
    },
    "schema_corrected_heart5_nested_2x2.json": {
        "experiment_id": "nested_schema_sensitivity_heart5",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_nested_validation.py",
        "protocol": "2 outer folds x 2 inner folds, seed 42, schema-corrected sensitivity run",
        "method": "corrected logistic/OVEC/OSEC and stable-selector candidates",
    },
    "schema_corrected_mendeley_nested_2x2.json": {
        "experiment_id": "nested_schema_sensitivity_mendeley",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_nested_validation.py",
        "protocol": "2 outer folds x 2 inner folds, seed 42, schema-corrected sensitivity run",
        "method": "corrected logistic/OVEC/OSEC and stable-selector candidates",
    },
    "post_boundary_corrected_stability_heart5.json": {
        "experiment_id": "feature_stability_post_boundary_heart5",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_stability_evidence.py",
        "protocol": "5 stratified folds x 3 repeats, six selector resamples, seed 42",
        "method": "StableXAIHDRC versus one-shot relevance selector",
    },
    "post_boundary_corrected_stability_mendeley.json": {
        "experiment_id": "feature_stability_post_boundary_mendeley",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_stability_evidence.py",
        "protocol": "5 stratified folds x 3 repeats, six selector resamples, seed 42",
        "method": "StableXAIHDRC versus one-shot relevance selector",
    },
    "schema_corrected_heart5_stability_3x6.json": {
        "experiment_id": "feature_stability_schema_sensitivity_heart5",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_stability_evidence.py",
        "protocol": "5 stratified folds x 3 repeats, six selector resamples",
        "method": "schema-corrected StableXAIHDRC versus one-shot selector",
    },
    "schema_corrected_mendeley_stability_3x6.json": {
        "experiment_id": "feature_stability_schema_sensitivity_mendeley",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_stability_evidence.py",
        "protocol": "5 stratified folds x 3 repeats, six selector resamples",
        "method": "schema-corrected StableXAIHDRC versus one-shot selector",
    },
    "post_boundary_corrected_linkage_heart5.json": {
        "experiment_id": "stability_reliability_linkage_heart5",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_stability_reliability_linkage.py",
        "protocol": "ten paired fit/calibration/evaluation seeds 42-51",
        "method": "stable OSEC versus corrected OSEC",
    },
    "post_boundary_corrected_linkage_mendeley.json": {
        "experiment_id": "stability_reliability_linkage_mendeley",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_stability_reliability_linkage.py",
        "protocol": "ten paired fit/calibration/evaluation seeds 42-51",
        "method": "stable OSEC versus corrected OSEC",
    },
    "schema_corrected_heart5_linkage_4seeds.json": {
        "experiment_id": "stability_reliability_schema_sensitivity_heart5",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_stability_reliability_linkage.py",
        "protocol": "four paired fit/calibration/evaluation seeds",
        "method": "schema-corrected stable OSEC versus corrected OSEC",
    },
    "schema_corrected_mendeley_linkage_4seeds.json": {
        "experiment_id": "stability_reliability_schema_sensitivity_mendeley",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_stability_reliability_linkage.py",
        "protocol": "four paired fit/calibration/evaluation seeds",
        "method": "schema-corrected stable OSEC versus corrected OSEC",
    },
    "schema_corrected_heart5_uncertainty_4seeds.json": {
        "experiment_id": "uncertainty_schema_sensitivity_heart5",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_uncertainty_evidence.py",
        "protocol": "four repeated fit/calibration/evaluation seeds",
        "method": "empirical confidence, calibration, and split-conformal summaries",
    },
    "schema_corrected_mendeley_uncertainty_4seeds.json": {
        "experiment_id": "uncertainty_schema_sensitivity_mendeley",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "experiments/run_uncertainty_evidence.py",
        "protocol": "four repeated fit/calibration/evaluation seeds",
        "method": "empirical confidence, calibration, and split-conformal summaries",
    },
    "schema_corrected_heart5_robustness.json": {
        "experiment_id": "evaluation_stress_test_heart5",
        "status": "EXPLORATORY",
        "script": "experiments/run_robustness.py",
        "protocol": "single clean split with evaluation-only missingness/noise perturbations",
        "method": "corrected OSEC versus stable OSEC",
    },
    "schema_corrected_mendeley_robustness.json": {
        "experiment_id": "evaluation_stress_test_mendeley",
        "status": "EXPLORATORY",
        "script": "experiments/run_robustness.py",
        "protocol": "single clean split with evaluation-only missingness/noise perturbations",
        "method": "corrected OSEC versus stable OSEC",
    },
    # Separate 70k benchmark, not a compatible external validation task.
    "kaggle70k_model_benchmark.json": {
        "experiment_id": "kaggle70k_primary_model_benchmark",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_model_benchmark.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42, ROC-AUC selection",
        "method": "11-model scalable benchmark",
    },
    "kaggle70k_tuned_priority_oof_ensemble.json": {
        "experiment_id": "kaggle70k_tuned_priority_models",
        "status": "COMPLETED_AND_VERIFIED",
        "script": "experiments/run_tuned_ensemble.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42, fixed OOF ensemble weights",
        "method": "logistic, RF, HGB, XGBoost, LightGBM, CatBoost, fixed ensemble",
    },
    "kaggle70k_compact_candidate_pool.json": {
        "experiment_id": "kaggle70k_compact_candidate_pool",
        "status": "EXPLORATORY",
        "script": "experiments/run_compact_candidate_pool.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42; SVM/KNN skipped for scale",
        "method": "compact linear, local, bagging, boosting, probabilistic, ensemble pool",
    },
    "heart5_compact_candidate_pool.json": {
        "experiment_id": "heart5_compact_candidate_pool",
        "status": "EXPLORATORY",
        "script": "experiments/run_compact_candidate_pool.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42",
        "method": "compact candidate pool including RBF SVM and KNN",
    },
    "mendeley_compact_candidate_pool.json": {
        "experiment_id": "mendeley_compact_candidate_pool",
        "status": "EXPLORATORY",
        "script": "experiments/run_compact_candidate_pool.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42",
        "method": "compact candidate pool including RBF SVM and KNN",
    },
    "post_tuning_custom_nested_kaggle70k_logistic_pair.json": {
        "experiment_id": "kaggle70k_custom_logistic_pair",
        "status": "COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED",
        "script": "src/cardiodiag/nested_validation.py",
        "protocol": "3 outer folds x 2 inner folds, seed 42; reduced custom pair",
        "method": "corrected logistic versus stable logistic",
    },
    "post_boundary_corrected_kaggle70k_stability.json": {
        "experiment_id": "kaggle70k_stability_stress_test",
        "status": "EXPLORATORY",
        "script": "experiments/run_stability_evidence.py",
        "protocol": "bounded stability analysis on separate 70k schema",
        "method": "stable selector versus one-shot selector",
    },
    "post_boundary_corrected_kaggle70k_linkage.json": {
        "experiment_id": "kaggle70k_stability_reliability_stress_test",
        "status": "EXPLORATORY",
        "script": "experiments/run_stability_reliability_linkage.py",
        "protocol": "bounded internal linkage analysis on separate 70k schema",
        "method": "stable OSEC versus corrected OSEC",
    },
    # Historical/superseded evidence retained for traceability.
    "heart5_protocol_comparison.json": {
        "experiment_id": "historical_protocol_comparison_heart5",
        "status": "HISTORICAL",
        "script": "experiments/run_protocol_comparison.py",
        "protocol": "historical notebook approximation versus corrected single split",
        "method": "historical OVEC/OSEC and corrected comparison",
    },
    "internal_stage_manifest.json": {
        "experiment_id": "internal_stage_default_attempt",
        "status": "INCOMPLETE",
        "script": "experiments/run_internal_stage.py",
        "protocol": "default two-dataset internal stage; bounded execution attempt",
        "method": "full configured internal stage",
    },
}


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot parse JSON artifact {path}: {exc}") from exc


def _assert_finite(value: Any, path: str = "root") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Non-finite numeric value at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite(item, f"{path}[{index}]")


def _git_head(root: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _manifest_hashes(root: Path) -> dict[str, str]:
    manifest = _load_json(root / "data/manifests/local_datasets.json")
    return {
        Path(item["path"]).name: item["sha256"]
        for item in manifest
        if item.get("sha256")
    }


def _dataset_info(payload: dict[str, Any], hashes: dict[str, str]) -> tuple[str, str | None]:
    summary = payload.get("dataset_summary")
    if isinstance(summary, dict):
        path = str(summary.get("path", payload.get("dataset", "unknown")))
        digest = summary.get("sha256")
    else:
        path = str(payload.get("dataset", "unknown"))
        provenance = payload.get("provenance", {})
        digest = provenance.get("dataset_sha256") if isinstance(provenance, dict) else None
    name = Path(path.replace("\\", "/")).name
    return name, str(digest or hashes.get(name)) if (digest or hashes.get(name)) else None


def _configuration(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("configuration", "config", "protocol"):
        candidate = payload.get(key)
        if isinstance(candidate, dict):
            return candidate
    return {}


def _reported_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    candidates = payload.get("candidates")
    if isinstance(candidates, dict):
        for name, result in candidates.items():
            if not isinstance(result, dict):
                continue
            selected = result.get("fold_mean") or result.get("pooled_outer_metrics")
            if isinstance(selected, dict):
                metrics[name] = {
                    key: selected[key]
                    for key in ("roc_auc", "pr_auc", "brier", "ece_uniform")
                    if key in selected
                }
    models = payload.get("models")
    if isinstance(models, dict):
        model_items = models.items()
    elif isinstance(models, list):
        model_items = (
            (item.get("model", "unknown"), item)
            for item in models
            if isinstance(item, dict)
        )
    else:
        model_items = ()
    for name, result in model_items:
        if not isinstance(result, dict):
            continue
        selected = result.get("mean_metrics") or result.get("pooled_outer_metrics")
        if isinstance(selected, dict):
            metrics[name] = {
                key: selected[key]
                for key in ("roc_auc", "pr_auc", "brier", "ece_uniform")
                if key in selected
            }
    ensemble = payload.get("ensemble")
    if isinstance(ensemble, dict) and isinstance(ensemble.get("metrics"), dict):
        metrics["fixed_oof_ensemble"] = {
            key: ensemble["metrics"][key]
            for key in ("roc_auc", "pr_auc", "brier", "ece_uniform")
            if key in ensemble["metrics"]
        }
    paired = payload.get("paired_reliability_differences")
    if isinstance(paired, dict):
        metrics["paired_stable_minus_corrected"] = {
            name: value.get("mean")
            for name, value in paired.items()
            if isinstance(value, dict) and "mean" in value
        }
    stability = payload.get("paired_stability_difference")
    if isinstance(stability, dict):
        metrics["stable_minus_one_shot_stability"] = {
            key: stability[key]
            for key in ("stable_minus_one_shot_mean", "positive_stability_evidence")
            if key in stability
        }
    return metrics


def build_registry(root: Path) -> dict[str, Any]:
    hashes = _manifest_hashes(root)
    experiments: list[dict[str, Any]] = []
    for filename, spec in ARTIFACT_SPECS.items():
        artifact = root / "results/generated" / filename
        if not artifact.exists():
            raise FileNotFoundError(f"Registry artifact is missing: {artifact}")
        payload = _load_json(artifact)
        if not isinstance(payload, dict):
            raise ValueError(f"Registry artifact must contain an object: {artifact}")
        _assert_finite(payload)
        dataset, digest = _dataset_info(payload, hashes)
        expected = hashes.get(dataset)
        hash_status = "not_applicable"
        if expected and digest:
            if digest != expected:
                raise ValueError(f"Dataset hash mismatch in {artifact}: {digest} != {expected}")
            hash_status = "matches_local_manifest"
        elif expected:
            hash_status = "missing_from_artifact"
        script = root / spec["script"]
        if not script.exists():
            raise FileNotFoundError(f"Source script is missing: {script}")
        config = _configuration(payload)
        experiments.append(
            {
                "experiment_id": spec["experiment_id"],
                "dataset": dataset,
                "dataset_sha256": digest,
                "dataset_hash_status": hash_status,
                "method": spec["method"],
                "preprocessing": (
                    "training-fold-only cleaning/imputation/encoding/scaling "
                    "where applicable"
                ),
                "validation_protocol": spec["protocol"],
                "fold_count": config.get("outer_splits"),
                "inner_fold_count": config.get("inner_splits"),
                "repeats": config.get("outer_repeats"),
                "random_seed": config.get("seed", payload.get("seed")),
                "random_seeds": payload.get("seeds", config.get("seeds")),
                "selection_metric": config.get("scoring", "not applicable"),
                "metric_aggregation": "fold mean plus pooled outer metrics when stored",
                "primary_metric": "ROC-AUC where available",
                "secondary_metrics": [
                    "PR-AUC",
                    "Brier",
                    "ECE",
                    "selective/reliability metrics where applicable",
                ],
                "reported_metrics": _reported_metrics(payload),
                "source_artifact": str(artifact.relative_to(root)).replace("\\", "/"),
                "script": spec["script"],
                "status": spec["status"],
                "notes": (
                    "Internal/development evidence only; not independent external validation."
                    if dataset != "unknown"
                    else (
                        "Artifact has no single dataset summary; status is retained "
                        "for audit traceability."
                    )
                ),
            }
        )
    return {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "repository_head_at_generation": _git_head(root),
        "scope": (
            "Authoritative index of primary stored CARDIODIAG artifacts; archived "
            "notebook outputs are excluded."
        ),
        "primary_internal_protocol": {
            "outer_folds": 3,
            "inner_folds": 3,
            "outer_repeats": 1,
            "seed": 42,
            "selection_metric": "ROC-AUC",
            "selection_rule": (
                "model selection occurs inside inner folds; outer folds are used "
                "only for final evaluation"
            ),
        },
        "status_definitions": STATUS_DEFINITIONS,
        "external_validation": {
            "status": "BLOCKED",
            "manifest": "data/manifests/external_dataset.template.json",
            "reason": "No genuinely independent compatible dataset is frozen.",
        },
        "experiments": experiments,
    }


def write_markdown(registry: dict[str, Any], path: Path) -> None:
    lines = [
        "# Authoritative experiment registry",
        "",
        f"Generated on `{registry['generated_on']}` from stored JSON artifacts.",
        (
            "Archived notebook outputs and superseded files are not silently "
            "mixed with the authoritative entries."
        ),
        "",
        "| Experiment | Dataset | Protocol | Primary metric | Status | Source artifact |",
        "|---|---|---|---|---|---|",
    ]
    for item in registry["experiments"]:
        lines.append(
            f"| `{item['experiment_id']}` | `{item['dataset']}` | {item['validation_protocol']} | "
            f"{item['primary_metric']} | `{item['status']}` | `{item['source_artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation rules",
            "",
            "- `post_boundary_corrected_*` is the primary corrected internal evidence family.",
            (
                "- `schema_corrected_*` is bounded sensitivity evidence and is "
                "not pooled with the primary family."
            ),
            (
                "- Kaggle 70k artifacts use a different target/schema and are "
                "not external validation of the CARDIODIAG tasks."
            ),
            (
                "- Historical and exploratory artifacts remain traceable but "
                "cannot support confirmatory claims."
            ),
            "- No entry supports clinical utility, safety, fairness, or deployment readiness.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/AUTHORITATIVE_METRIC_REGISTRY.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/AUTHORITATIVE_METRIC_REGISTRY.md"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    registry = build_registry(root)
    for output in (args.json_output, args.markdown_output):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    write_markdown(registry, args.markdown_output)
    print(
        f"Wrote {args.json_output} and {args.markdown_output} "
        f"({len(registry['experiments'])} entries)"
    )


if __name__ == "__main__":
    main()
