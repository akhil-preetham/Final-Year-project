import json
from pathlib import Path

import pytest

from cardiodiag.external_gate import validate_external_manifest
from experiments.run_external_evaluation import run_external_evaluation


def qualified_manifest() -> dict[str, object]:
    return {
        "status": "FROZEN",
        "eligibility_decision": "QUALIFIED",
        "dataset_name": "Independent test",
        "source_url": "https://example.org/data",
        "persistent_identifier": "doi:10.0000/example",
        "version_or_release": "1",
        "access_date": "2026-10-25",
        "license": "CC BY 4.0",
        "population": "Consecutive adults undergoing coronary angiography",
        "recruitment_period": "2020-2022",
        "target_column": "target",
        "target_definition": ">50% stenosis in a major coronary artery",
        "endpoint_compatibility_evidence": "Same threshold and outcome ascertainment",
        "features_used": ["age"],
        "feature_mapping": [
            {
                "model_feature": "age",
                "dataset_feature": "age_years",
                "units": "years",
                "prediction_time": "before angiography",
                "compatible": True,
            }
        ],
        "unit_compatibility_evidence": "Age is recorded in completed years in both schemas",
        "evaluation_access_authorization": "Institutional DUA ref TEST-001",
        "overlap_assessment": "No overlap identified using approved linkage procedure",
        "patient_independence_evidence": "Separate recruiting institution and cohort records",
        "independence_justification": "Independent source cohort",
        "prior_label_exposure_evidence": "Target labels withheld until protocol freeze",
        "prior_label_exposure": False,
        "preprocessing_frozen_before_labels": True,
        "approved_for_external_evaluation": True,
        "endpoint_identical": True,
        "feature_units_compatible": True,
        "patient_independence_confirmed": True,
        "evaluation_access_authorized_flag": True,
        "labels_unseen_until_freeze": True,
        "access_conditions_reviewed": True,
    }


def test_template_manifest_is_rejected(tmp_path: Path) -> None:
    manifest = {"status": "NOT_FROZEN"}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="incomplete"):
        validate_external_manifest(path)


def test_frozen_manifest_is_accepted(tmp_path: Path) -> None:
    manifest = qualified_manifest()
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    assert validate_external_manifest(path)["status"] == "FROZEN"


def test_manifest_fails_closed_without_independence_evidence(tmp_path: Path) -> None:
    manifest = qualified_manifest()
    manifest["patient_independence_confirmed"] = False
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="patient_independence_confirmed"):
        validate_external_manifest(path)


def test_manifest_rejects_prior_label_exposure(tmp_path: Path) -> None:
    manifest = qualified_manifest()
    manifest["prior_label_exposure"] = True
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="Prior target-label exposure"):
        validate_external_manifest(path)


def test_manifest_requires_units_and_complete_feature_mapping(tmp_path: Path) -> None:
    manifest = qualified_manifest()
    manifest["feature_mapping"] = [{"model_feature": "age", "compatible": True}]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="feature mapping must specify"):
        validate_external_manifest(path)


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
