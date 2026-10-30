"""Safety gate for freezing an external validation dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = [
    "dataset_name",
    "source_url",
    "persistent_identifier",
    "version_or_release",
    "access_date",
    "license",
    "target_column",
    "target_definition",
    "features_used",
    "overlap_assessment",
    "independence_justification",
]


def validate_external_manifest(path: str | Path) -> dict[str, Any]:
    """Return a validated frozen manifest or raise a clear gate error."""

    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if not manifest.get(field)]
    if missing:
        raise ValueError(f"External manifest is incomplete: {', '.join(missing)}")
    if manifest.get("status") != "FROZEN":
        raise ValueError("External manifest must have status='FROZEN'")
    if not manifest.get("preprocessing_frozen_before_labels"):
        raise ValueError("Preprocessing must be frozen before external labels are used")
    if not manifest.get("approved_for_external_evaluation"):
        raise ValueError("External dataset has not been approved for evaluation")
    if not manifest.get("independence_justification"):
        raise ValueError("Independence justification is required")
    return manifest
