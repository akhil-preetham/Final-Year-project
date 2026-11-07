"""Independently verify saved domain-guard results and their manifests."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
STUDIES = {
    "CD-XD-005": {
        "directory": ROOT / "results" / "transfer_20261105_duke_acath_final",
        "label_column": "observed_label_for_scoring",
        "raw_column": "exploratory_raw_probability",
        "calibrated_column": "exploratory_calibrated_probability",
        "raw_metric_key": "raw_source_model_metrics_on_target",
        "calibrated_metric_key": "source_platt_calibrated_metrics_on_target",
    },
    "CD-XD-006": {
        "directory": ROOT / "results" / "transfer_20261105_angiocad_domain_guard",
        "label_column": "label_for_scoring",
        "raw_column": "exploratory_raw_probability",
        "calibrated_column": "exploratory_calibrated_probability",
        "raw_metric_key": "raw_source_model_metrics_on_target",
        "calibrated_metric_key": "platt_calibrated_metrics_on_target",
    },
}
METRICS = {
    "roc_auc": roc_auc_score,
    "average_precision": average_precision_score,
    "brier_score": brier_score_loss,
    "log_loss": log_loss,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_repo_path(value: str) -> Path:
    return ROOT.joinpath(*value.replace("\\", "/").split("/"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def score(y: np.ndarray, probability: np.ndarray) -> dict[str, float]:
    edges = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    for index in range(10):
        in_bin = (probability >= edges[index]) & (
            (probability <= edges[index + 1]) if index == 9 else (probability < edges[index + 1])
        )
        if in_bin.any():
            ece += float(in_bin.sum() / len(y)) * abs(
                float(probability[in_bin].mean()) - float(y[in_bin].mean())
            )
    return {
        **{key: float(metric(y, probability)) for key, metric in METRICS.items()},
        "ece_10_bins": ece,
    }


def verify_metric_group(
    calculated: dict[str, float], recorded: dict[str, Any], name: str
) -> dict[str, dict[str, float]]:
    differences: dict[str, dict[str, float]] = {}
    for key, value in calculated.items():
        expected = float(recorded[key])
        delta = abs(value - expected)
        if not math.isclose(value, expected, rel_tol=0.0, abs_tol=1e-12):
            raise AssertionError(f"{name}.{key} differs by {delta:.3g}")
        differences[key] = {"recomputed": value, "recorded": expected, "abs_delta": delta}
    return differences


def audit_study(study_id: str, config: dict[str, str | Path]) -> dict[str, Any]:
    directory = Path(config["directory"])
    manifest = read_json(directory / "run_manifest.json")
    metrics = read_json(directory / "study_metrics.json")
    verified_hashes: dict[str, dict[str, str]] = {}
    for group in ("input_hashes", "code_hashes", "output_hashes"):
        checks: dict[str, str] = {}
        for raw_path, expected in manifest.get(group, {}).items():
            path = resolve_repo_path(raw_path)
            if not path.is_file():
                raise FileNotFoundError(f"Missing {group} artifact: {path}")
            actual = sha256_file(path)
            if actual != expected:
                raise AssertionError(f"SHA-256 mismatch for {path}")
            checks[raw_path] = actual
        verified_hashes[group] = checks

    import csv

    with (directory / "target_predictions.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != int(metrics["target_rows"]):
        raise AssertionError(f"Target row count mismatch for {study_id}")
    label_column = str(config["label_column"])
    raw_column = str(config["raw_column"])
    calibrated_column = str(config["calibrated_column"])
    y = np.asarray([int(row[label_column]) for row in rows], dtype=int)
    raw = np.asarray([float(row[raw_column]) for row in rows], dtype=float)
    calibrated = np.asarray([float(row[calibrated_column]) for row in rows], dtype=float)
    if not all(0 <= value <= 1 for value in (*raw, *calibrated)):
        raise AssertionError(f"Probability outside [0, 1] for {study_id}")

    actions = [row["domain_gate_action"] for row in rows]
    deployment_scores = [row["deployment_probability"] for row in rows]
    if any(action != "abstain" for action in actions) or any(deployment_scores):
        raise AssertionError(f"Unknown-domain gate did not fail closed for {study_id}")

    raw_key = str(config["raw_metric_key"])
    calibrated_key = str(config["calibrated_metric_key"])
    return {
        "study_id": study_id,
        "target_rows": len(rows),
        "target_class_counts": {
            "0": int(np.sum(y == 0)),
            "1": int(np.sum(y == 1)),
        },
        "unknown_site_gate": {
            "all_rows_abstained": True,
            "rows_with_deployment_probability": 0,
        },
        "recomputed_metrics": {
            "raw": verify_metric_group(score(y, raw), metrics[raw_key], f"{study_id}.raw"),
            "source_platt": verify_metric_group(
                score(y, calibrated), metrics[calibrated_key], f"{study_id}.platt"
            ),
        },
        "verified_sha256": verified_hashes,
    }


def main() -> None:
    studies = {study_id: audit_study(study_id, config) for study_id, config in STUDIES.items()}
    output = {
        "audit_date": datetime.now(UTC).date().isoformat(),
        "auditor": "experiments/audit_domain_guard_artifacts.py",
        "audit_code_sha256": sha256_file(Path(__file__)),
        "status": "PASS",
        "interpretation": (
            "Saved artifact integrity and metric arithmetic verified. This does "
            "not establish clinical validity, unseen-site utility, or endpoint "
            "compatibility."
        ),
        "studies": studies,
    }
    destination = ROOT / "results" / "DOMAIN_GUARD_FINAL_AUDIT.json"
    destination.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"PASS: verified both studies and wrote {destination}")


if __name__ == "__main__":
    main()
