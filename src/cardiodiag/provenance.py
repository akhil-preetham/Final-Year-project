"""Reproducibility metadata for generated experiment artifacts."""

from __future__ import annotations

import hashlib
import importlib.metadata
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


def collect_provenance(
    dataset: str | Path,
    target: str,
    experiment_type: str,
    configuration: dict[str, Any],
) -> dict[str, Any]:
    """Collect dataset, software, source, and working-tree provenance."""

    dataset_path = Path(dataset).resolve()
    repository_root = Path(__file__).resolve().parents[2]
    package_names = {
        "numpy": "numpy",
        "pandas": "pandas",
        "scikit-learn": "scikit-learn",
        "scipy": "scipy",
        "imbalanced-learn": "imbalanced-learn",
        "xgboost": "xgboost",
        "lightgbm": "lightgbm",
        "catboost": "catboost",
    }
    package_versions = {}
    for label, distribution in package_names.items():
        try:
            package_versions[label] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            package_versions[label] = None

    source_digest = hashlib.sha256()
    source_file_count = 0
    source_roots = [repository_root / "src", repository_root / "experiments"]
    source_files = sorted(
        path
        for root in source_roots
        if root.exists()
        for path in root.rglob("*.py")
    )
    for path in source_files:
        relative = path.relative_to(repository_root).as_posix()
        file_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source_digest.update(relative.encode("utf-8"))
        source_digest.update(b"\0")
        source_digest.update(file_digest.encode("ascii"))
        source_digest.update(b"\n")
        source_file_count += 1

    lockfile = repository_root / "uv.lock"

    try:
        git_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        git_status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
        working_tree_dirty = bool(git_status.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        git_head = None
        working_tree_dirty = None

    metadata = {
        "selector_protocol": "post_boundary_correction_v1",
        "experiment_type": experiment_type,
        "dataset_path": str(dataset_path),
        "dataset_sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
        "target": target,
        "configuration": configuration,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hardware": {
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "logical_cpu_count": os.cpu_count(),
        },
        "package_versions": package_versions,
        "uv_lock_sha256": (
            hashlib.sha256(lockfile.read_bytes()).hexdigest() if lockfile.exists() else None
        ),
        "source_bundle_sha256": source_digest.hexdigest(),
        "source_file_count": source_file_count,
        "git_head": git_head,
        "working_tree_dirty": working_tree_dirty,
    }
    if "seed" in configuration:
        metadata["seed"] = configuration["seed"]
    if "seeds" in configuration:
        metadata["seeds"] = configuration["seeds"]
    return metadata
