"""One-command internal research stage runner.

This command performs only development-data work. It never evaluates an
external dataset and never changes the final research claim automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from cardiodiag.nested_validation import run_nested_validation
from cardiodiag.provenance import collect_provenance

DATASETS = [
    (Path("heart5.csv"), "HeartDisease", "heart5"),
    (Path("MendeleyCardiovascular_Disease_Dataset.csv"), "target", "mendeley"),
]


def _default_output_dir() -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return Path("results") / f"internal_stage_{timestamp}"


def _ensure_outputs_available(output_dir: Path) -> None:
    expected = [
        output_dir / f"{name}_nested_validation.json"
        for _, _, name in DATASETS
    ]
    expected.append(output_dir / "internal_stage_manifest.json")
    collisions = [path for path in expected if path.exists()]
    if collisions:
        paths = ", ".join(str(path) for path in collisions)
        raise FileExistsError(f"Refusing to overwrite existing experiment artifacts: {paths}")
    output_dir.mkdir(parents=True, exist_ok=True)


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--outer-splits", type=int, default=3)
    parser.add_argument("--inner-splits", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = args.output_dir or _default_output_dir()
    _ensure_outputs_available(output_dir)
    manifest_path = output_dir / "internal_stage_manifest.json"
    artifacts = []
    experiments = []
    stage_started = perf_counter()
    execution_metadata = None
    manifest: dict[str, Any] = {
        "stage": "internal_nested_validation",
        "status": "running",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "completed_at_utc": None,
        "external_validation": False,
        "parameters": {
            "outer_splits": args.outer_splits,
            "inner_splits": args.inner_splits,
            "seed": args.seed,
        },
        "artifacts": artifacts,
        "experiments": experiments,
        "execution_metadata": execution_metadata,
        "runtime_seconds": 0.0,
        "next_gate": "review nested metrics and complete/freeze an independent external manifest",
    }
    _write_manifest(manifest_path, manifest)
    current_dataset = None
    try:
        for dataset, target, name in DATASETS:
            current_dataset = str(dataset)
            output = output_dir / f"{name}_nested_validation.json"
            experiment_started = perf_counter()
            result = run_nested_validation(
                dataset,
                target,
                outer_splits=args.outer_splits,
                outer_repeats=1,
                inner_splits=args.inner_splits,
                seed=args.seed,
            )
            configuration = {
                "outer_splits": args.outer_splits,
                "outer_repeats": 1,
                "inner_splits": args.inner_splits,
                "seed": args.seed,
                "scoring": result["config"]["scoring"],
                "candidates": list(result["candidates"]),
            }
            provenance = collect_provenance(
                dataset, target, "internal_nested_validation", configuration
            )
            result["provenance"] = provenance
            output.write_text(json.dumps(result, indent=2), encoding="utf-8")
            artifacts.append(str(output))
            experiment_runtime = float(perf_counter() - experiment_started)
            experiments.append(
                {
                    "dataset": str(dataset),
                    "target": target,
                    "dataset_sha256": provenance["dataset_sha256"],
                    "result_artifact": str(output),
                    "result_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                    "runtime_seconds": experiment_runtime,
                    "candidate_names": list(result["candidates"]),
                    "prediction_vectors_saved": True,
                }
            )
            if execution_metadata is None:
                execution_metadata = {
                    "git_head": provenance["git_head"],
                    "working_tree_dirty": provenance["working_tree_dirty"],
                    "source_bundle_sha256": provenance["source_bundle_sha256"],
                    "source_file_count": provenance["source_file_count"],
                    "uv_lock_sha256": provenance["uv_lock_sha256"],
                    "python_version": provenance["python_version"],
                    "platform": provenance["platform"],
                    "hardware": provenance["hardware"],
                    "package_versions": provenance["package_versions"],
                }
            manifest.update(
                {
                    "artifacts": artifacts,
                    "experiments": experiments,
                    "execution_metadata": execution_metadata,
                    "runtime_seconds": float(perf_counter() - stage_started),
                }
            )
            _write_manifest(manifest_path, manifest)
    except BaseException as error:
        manifest.update(
            {
                "status": "interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
                "completed_at_utc": datetime.now(UTC).isoformat(),
                "failed_dataset": current_dataset,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "artifacts": artifacts,
                "experiments": experiments,
                "execution_metadata": execution_metadata,
                "runtime_seconds": float(perf_counter() - stage_started),
            }
        )
        _write_manifest(manifest_path, manifest)
        raise
    manifest.update(
        {
            "status": "complete",
            "completed_at_utc": datetime.now(UTC).isoformat(),
            "artifacts": artifacts,
            "experiments": experiments,
            "execution_metadata": execution_metadata,
            "runtime_seconds": float(perf_counter() - stage_started),
        }
    )
    _write_manifest(manifest_path, manifest)
    print(f"Completed internal stage; wrote {len(artifacts)} result files and {manifest_path}")


if __name__ == "__main__":
    main()
