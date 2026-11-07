from pathlib import Path

from experiments.build_authoritative_registry import build_registry

ROOT = Path(__file__).resolve().parents[1]


def test_authoritative_registry_validates_allowlisted_artifacts() -> None:
    registry = build_registry(ROOT)

    assert len(registry["experiments"]) == 26
    assert all(
        item["dataset_hash_status"] in {"matches_local_manifest", "not_applicable"}
        for item in registry["experiments"]
    )
    assert registry["external_validation"]["status"] == "BLOCKED"
    assert any(
        item["experiment_id"] == "nested_internal_post_boundary_heart5"
        and item["status"] == "COMPLETED_AND_VERIFIED"
        for item in registry["experiments"]
    )
