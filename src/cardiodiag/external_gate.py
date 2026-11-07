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
    "population",
    "recruitment_period",
    "target_column",
    "target_definition",
    "endpoint_compatibility_evidence",
    "features_used",
    "feature_mapping",
    "unit_compatibility_evidence",
    "evaluation_access_authorization",
    "overlap_assessment",
    "patient_independence_evidence",
    "independence_justification",
    "prior_label_exposure_evidence",
]

REQUIRED_TRUE_FLAGS = [
    "preprocessing_frozen_before_labels",
    "approved_for_external_evaluation",
    "endpoint_identical",
    "feature_units_compatible",
    "patient_independence_confirmed",
    "evaluation_access_authorized_flag",
    "labels_unseen_until_freeze",
    "access_conditions_reviewed",
]


def validate_external_manifest(path: str | Path) -> dict[str, Any]:
    """Return a validated frozen manifest or raise a clear gate error."""

    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED_FIELDS if not manifest.get(field)]
    if missing:
        raise ValueError(f"External manifest is incomplete: {', '.join(missing)}")
    if manifest.get("status") != "FROZEN":
        raise ValueError("External manifest must have status='FROZEN'")
    if manifest.get("eligibility_decision") != "QUALIFIED":
        raise ValueError("External dataset must have eligibility_decision='QUALIFIED'")
    failed_flags = [flag for flag in REQUIRED_TRUE_FLAGS if manifest.get(flag) is not True]
    if failed_flags:
        raise ValueError(f"External qualification flags must be true: {', '.join(failed_flags)}")
    if manifest.get("prior_label_exposure") is not False:
        raise ValueError("Prior target-label exposure must be explicitly false")
    if not isinstance(manifest.get("features_used"), list) or not manifest["features_used"]:
        raise ValueError("features_used must be a non-empty list")
    mappings = manifest.get("feature_mapping")
    if not isinstance(mappings, list) or not mappings:
        raise ValueError("feature_mapping must be a non-empty list")
    required_mapping_fields = ("model_feature", "dataset_feature", "units", "prediction_time")
    mapped_features: set[str] = set()
    for mapping in mappings:
        incomplete = not isinstance(mapping, dict) or any(
            not mapping.get(key) for key in required_mapping_fields
        )
        if incomplete:
            raise ValueError(
                "Each feature mapping must specify model_feature, dataset_feature, "
                "units, and prediction_time"
            )
        if mapping.get("compatible") is not True:
            raise ValueError("Every feature mapping must be explicitly marked compatible")
        mapped_features.add(mapping["model_feature"])
    if mapped_features != set(manifest["features_used"]):
        raise ValueError("feature_mapping must cover exactly the features_used")
    return manifest
