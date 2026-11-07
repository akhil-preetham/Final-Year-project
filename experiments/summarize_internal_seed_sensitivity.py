"""Audit and summarize the frozen five-seed internal sensitivity runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from cardiodiag.evaluation import evaluate_predictions

ROOT = Path(__file__).resolve().parents[1]
REPEAT_ROOT = ROOT / "results" / "internal_seed_sensitivity_20261105"
SEEDS = (43, 44, 45, 46, 47)
DATASETS = {
    "heart5": {"file": "heart5_nested_validation.json", "target": "HeartDisease"},
    "mendeley": {"file": "mendeley_nested_validation.json", "target": "target"},
}
METRICS = ("roc_auc", "pr_auc", "brier", "ece_uniform", "balanced_accuracy")
MATCHED_METRICS = ("accuracy", *METRICS)
TOLERANCE = 1e-10


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_candidate(candidate: dict[str, Any], row_count: int) -> dict[str, float | int]:
    """Recompute pooled metrics and require exactly-once outer-test coverage."""

    fold_records = candidate.get("folds")
    if not isinstance(fold_records, list) or len(fold_records) != 3:
        raise ValueError("Each candidate must contain exactly three outer folds")

    indices: list[int] = []
    labels: list[int] = []
    probabilities: list[float] = []
    for fold in fold_records:
        fold_indices = [int(value) for value in fold["outer_test_indices"]]
        fold_labels = [int(value) for value in fold["outer_test_y_true"]]
        fold_probabilities = [float(value) for value in fold["outer_test_probability"]]
        if not (len(fold_indices) == len(fold_labels) == len(fold_probabilities)):
            raise ValueError("Outer-test indices, labels, and predictions differ in length")
        if len(fold_indices) != len(set(fold_indices)):
            raise ValueError("An outer fold scores a row more than once")
        indices.extend(fold_indices)
        labels.extend(fold_labels)
        probabilities.extend(fold_probabilities)

    if sorted(indices) != list(range(row_count)):
        raise ValueError("Outer folds must score every dataset row exactly once")
    y_true = np.asarray(labels, dtype=int)
    y_probability = np.asarray(probabilities, dtype=float)
    if not np.all(np.isfinite(y_probability)):
        raise ValueError("Outer-test predictions contain non-finite probabilities")

    calculated = evaluate_predictions(y_true, y_probability)
    stored = candidate.get("pooled_outer_metrics", {})
    for metric in MATCHED_METRICS:
        actual = float(calculated[metric])
        recorded = float(stored[metric])
        if not np.isclose(actual, recorded, rtol=0.0, atol=TOLERANCE):
            raise ValueError(
                f"Recomputed {metric} {actual:.15g} differs from stored {recorded:.15g}"
            )
    return {metric: float(calculated[metric]) for metric in METRICS} | {
        "n": int(calculated["n"]),
        "positive_count": int(calculated["positive_count"]),
    }


def _read_seed(seed: int) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    output_dir = REPEAT_ROOT / f"seed_{seed}"
    manifest_path = output_dir / "internal_stage_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing seed manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise ValueError(f"Seed {seed} is not complete")
    expected_parameters = {
        "seed": seed,
        "outer_splits": 3,
        "inner_splits": 3,
    }
    if any(
        manifest.get("parameters", {}).get(key) != value
        for key, value in expected_parameters.items()
    ):
        raise ValueError(f"Seed {seed} has unexpected run parameters")
    execution = manifest.get("execution_metadata") or {}
    provenance = {
        "source_bundle_sha256": execution.get("source_bundle_sha256"),
        "uv_lock_sha256": execution.get("uv_lock_sha256"),
        "source_file_count": execution.get("source_file_count"),
    }
    if not provenance["source_bundle_sha256"] or not provenance["uv_lock_sha256"]:
        raise ValueError(f"Seed {seed} is missing source or lockfile provenance")

    experiments = manifest.get("experiments", [])
    if len(experiments) != len(DATASETS):
        raise ValueError(f"Seed {seed} manifest does not list both dataset artifacts")
    for experiment in experiments:
        artifact_path = (ROOT / Path(experiment["result_artifact"])).resolve()
        if not artifact_path.is_relative_to(ROOT):
            raise ValueError(f"Seed {seed} artifact path escapes the repository")
        if not artifact_path.is_file() or sha256_file(artifact_path) != experiment["result_sha256"]:
            raise ValueError(f"Seed {seed} artifact hash mismatch: {artifact_path}")

    results: dict[str, dict[str, Any]] = {}
    for name, dataset_config in DATASETS.items():
        path = output_dir / dataset_config["file"]
        if not path.is_file():
            raise FileNotFoundError(f"Seed {seed} is missing {name}: {path}")
        result = json.loads(path.read_text(encoding="utf-8"))
        config = result["config"]
        if (
            config.get("seed") != seed
            or config.get("outer_splits") != 3
            or config.get("outer_repeats") != 1
            or config.get("inner_splits") != 3
            or config.get("target") != dataset_config["target"]
        ):
            raise ValueError(f"Seed {seed} {name} result has unexpected configuration")
        if result.get("provenance", {}).get("source_bundle_sha256") != provenance[
            "source_bundle_sha256"
        ]:
            raise ValueError(f"Seed {seed} {name} result source hash differs from its manifest")
        if summary_hash := result.get("dataset_summary", {}).get("sha256"):
            if summary_hash != next(
                (
                    item["dataset_sha256"]
                    for item in experiments
                    if Path(item["result_artifact"]).name == dataset_config["file"]
                ),
                None,
            ):
                raise ValueError(f"Seed {seed} {name} dataset hash differs from its manifest")
        results[name] = result
    return {"manifest": manifest, "provenance": provenance}, results


def build_summary(seeds: tuple[int, ...] = SEEDS) -> dict[str, Any]:
    if seeds != SEEDS:
        raise ValueError(f"This frozen protocol requires seeds {list(SEEDS)}")
    runs = {seed: _read_seed(seed) for seed in seeds}
    seed_provenance = {seed: record[0]["provenance"] for seed, record in runs.items()}
    bundle_hashes = {value["source_bundle_sha256"] for value in seed_provenance.values()}
    lock_hashes = {value["uv_lock_sha256"] for value in seed_provenance.values()}
    if len(bundle_hashes) != 1 or len(lock_hashes) != 1:
        raise ValueError("Repeated runs do not share one source bundle and lockfile")

    historical_manifest = json.loads(
        (ROOT / "results" / "master_directive_20261105_serial" / "internal_stage_manifest.json")
        .read_text(encoding="utf-8")
    )
    historical_execution = historical_manifest["execution_metadata"]
    historical_excluded = (
        historical_execution.get("source_bundle_sha256") not in bundle_hashes
        or historical_execution.get("uv_lock_sha256") not in lock_hashes
    )
    if not historical_excluded:
        raise ValueError("Seed 42 no longer matches the documented provenance exclusion")

    output_datasets: dict[str, Any] = {}
    for dataset_name in DATASETS:
        first_result = runs[seeds[0]][1][dataset_name]
        row_count = int(first_result["dataset_summary"]["rows"])
        dataset_hash = first_result["dataset_summary"]["sha256"]
        candidate_names = tuple(first_result["candidates"])
        by_candidate: dict[str, Any] = {}
        for seed in seeds:
            result = runs[seed][1][dataset_name]
            summary = result["dataset_summary"]
            if int(summary["rows"]) != row_count or summary["sha256"] != dataset_hash:
                raise ValueError(f"{dataset_name} identity differs across seed runs")
            if tuple(result["candidates"]) != candidate_names:
                raise ValueError(f"{dataset_name} candidate set differs in seed {seed}")
        for candidate_name in candidate_names:
            per_seed: dict[str, Any] = {}
            for seed in seeds:
                result = runs[seed][1][dataset_name]
                candidate = result["candidates"][candidate_name]
                per_seed[str(seed)] = audit_candidate(candidate, row_count)
            metrics_summary: dict[str, Any] = {}
            for metric in METRICS:
                values = np.asarray([per_seed[str(seed)][metric] for seed in seeds], dtype=float)
                metrics_summary[metric] = {
                    "mean": float(values.mean()),
                    "sample_sd": float(values.std(ddof=1)),
                    "minimum": float(values.min()),
                    "maximum": float(values.max()),
                }
            by_candidate[candidate_name] = {
                "seed_metrics": per_seed,
                "across_seed_summary": metrics_summary,
            }
        output_datasets[dataset_name] = {
            "dataset_sha256": dataset_hash,
            "rows": row_count,
            "target": DATASETS[dataset_name]["target"],
            "candidates": by_candidate,
        }

    protocol_path = ROOT / "docs" / "INTERNAL_VALIDATION_REPEAT_PROTOCOL_20261105.md"
    source_file_counts = {x["source_file_count"] for x in seed_provenance.values()}
    if len(source_file_counts) != 1:
        raise ValueError("Repeated runs have different source-file counts")

    return {
        "protocol_id": "CD-IV-001",
        "decision_scope": (
            "Exploratory internal split-seed sensitivity; not confirmatory or "
            "external validation."
        ),
        "seeds_in_aggregate": list(seeds),
        "seed_42_excluded": {
            "excluded": historical_excluded,
            "reason": "Its source-bundle and/or uv.lock hash differs from the five repeated runs.",
            "source_bundle_sha256": historical_execution.get("source_bundle_sha256"),
            "uv_lock_sha256": historical_execution.get("uv_lock_sha256"),
        },
        "shared_provenance": {
            "source_bundle_sha256": next(iter(bundle_hashes)),
            "uv_lock_sha256": next(iter(lock_hashes)),
            "source_file_count": next(iter(source_file_counts)),
            "protocol_sha256": sha256_file(protocol_path),
        },
        "outer_test_coverage": (
            "Every row exactly once per seed and dataset, verified from saved "
            "fold indices."
        ),
        "metric_recalculation_tolerance": TOLERANCE,
        "aggregation_note": (
            "Mean, sample SD, minimum, and maximum across five seed-level "
            "pooled out-of-fold metrics; no confidence intervals or p-values "
            "across seeds."
        ),
        "datasets": output_datasets,
        "limitations": [
            (
                "Repeated random splits do not establish patient-level "
                "independence or external transportability."
            ),
            "Source datasets lack verified patient-linkage keys for all records.",
            (
                "Seed 42 is a historical result under different code/lock "
                "provenance and is not pooled."
            ),
            (
                "This sensitivity analysis was run after earlier seed-42 "
                "results had been examined and is exploratory."
            ),
        ],
        "audited_utc": datetime.now(UTC).isoformat(),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# CD-IV-001 five-seed internal sensitivity summary",
        "",
        (
            "**Interpretation:** exploratory split-seed sensitivity, not "
            "confirmatory or external validation."
        ),
        "",
        "Seeds: " + ", ".join(str(seed) for seed in summary["seeds_in_aggregate"]) + ".",
        "Seed 42 is excluded because its source-bundle and lockfile provenance differs.",
        (
            "Values are mean ± sample SD across seed-level pooled out-of-fold "
            "metrics; ranges are shown in parentheses."
        ),
        "No confidence intervals or p-values are computed across seeds.",
        "",
        "| Dataset | Candidate | ROC-AUC | PR-AUC | Brier | ECE | Balanced accuracy |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for dataset, dataset_result in summary["datasets"].items():
        for candidate, candidate_result in dataset_result["candidates"].items():
            metrics = candidate_result["across_seed_summary"]
            formatted = []
            for metric in METRICS:
                item = metrics[metric]
                formatted.append(
                    f"{item['mean']:.3f} ± {item['sample_sd']:.3f} "
                    f"({item['minimum']:.3f}–{item['maximum']:.3f})"
                )
            lines.append(
                f"| {dataset} | {candidate} | " + " | ".join(formatted) + " |"
            )
    lines.extend(
        [
            "",
            (
                "Every saved outer test row was scored once per seed. Pooled "
                "metrics were recomputed from saved labels and probabilities "
                "and matched the stored results within `1e-10`."
            ),
            (
                "Repeated splits do not substitute for patient-level "
                "resampling, external validation, or clinical evaluation."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=REPEAT_ROOT / "seed_repeat_summary.json")
    parser.add_argument("--markdown", type=Path, default=REPEAT_ROOT / "seed_repeat_summary.md")
    args = parser.parse_args()
    summary = build_summary()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render_markdown(summary), encoding="utf-8")
    print(f"Audited {len(SEEDS)} seeds across {len(DATASETS)} datasets; wrote {args.json}")


if __name__ == "__main__":
    main()
