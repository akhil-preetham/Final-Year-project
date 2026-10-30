import json
from pathlib import Path

import pytest

from cardiodiag.external_gate import validate_external_manifest
from experiments.run_external_evaluation import run_external_evaluation


def test_template_manifest_is_rejected(tmp_path: Path) -> None:
    manifest = {"status": "NOT_FROZEN"}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete"):
        validate_external_manifest(path)


def test_frozen_manifest_is_accepted(tmp_path: Path) -> None:
    manifest = {
        "status": "FROZEN",
        "dataset_name": "Independent test",
        "source_url": "https://example.org/data",
        "persistent_identifier": "doi:10.0000/example",
        "version_or_release": "1",
        "access_date": "2026-10-25",
        "license": "CC BY 4.0",
        "target_column": "target",
        "target_definition": "binary outcome",
        "features_used": ["age"],
        "overlap_assessment": "no overlap identified",
        "independence_justification": "independent source cohort",
        "preprocessing_frozen_before_labels": True,
        "approved_for_external_evaluation": True,
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    assert validate_external_manifest(path)["status"] == "FROZEN"


def test_external_evaluation_fails_before_reading_unfrozen_data(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"status": "NOT_FROZEN"}), encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete"):
        run_external_evaluation(
            development_dataset=tmp_path / "missing-development.csv",
            development_target="target",
            external_dataset=tmp_path / "missing-external.csv",
            external_target="target",
            manifest=manifest,
            variant="osec",
            stable_selector=False,
            seed=42,
            alpha=0.1,
        )
