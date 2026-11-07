from experiments.build_code_ownership_matrix import classify_path


def test_ownership_matrix_keeps_untracked_source_as_unknown() -> None:
    category, _, release = classify_path("src/cardiodiag/new_module.py", tracked=False)
    assert category == "unknown_ownership"
    assert release == "exclude_pending_contributor_confirmation"


def test_ownership_matrix_marks_tracked_base_files_as_snapshot_not_owner_proof() -> None:
    category, evidence, release = classify_path("README.md", tracked=True)
    assert category == "original_upstream_snapshot"
    assert "not copyright ownership" in evidence
    assert release == "exclude_pending_owner_and_license_review"


def test_ownership_matrix_excludes_generated_and_dataset_files() -> None:
    generated, _, _ = classify_path("results/model.joblib", tracked=False)
    data, _, _ = classify_path("data/external/site.xlsx", tracked=False)
    assert generated == "generated_artifact"
    assert data == "third_party_code_or_data"
