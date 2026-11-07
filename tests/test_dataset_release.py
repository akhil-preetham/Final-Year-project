import json
from pathlib import Path

import pytest

from experiments.check_dataset_release import check_dataset_ids


def test_dataset_release_checker_blocks_unresolved_and_excluded_rights(tmp_path: Path) -> None:
    registry = tmp_path / "datasets.json"
    registry.write_text(
        json.dumps({"datasets": [
            {"id": "unknown_rights", "redistribution": "blocked"},
            {"id": "allowed", "redistribution": "approved_for_redistribution"},
        ]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Dataset release blocked"):
        check_dataset_ids(["unknown_rights"], registry)


def test_dataset_release_checker_rejects_unknown_ids(tmp_path: Path) -> None:
    registry = tmp_path / "datasets.json"
    registry.write_text(json.dumps({"datasets": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="not present in registry"):
        check_dataset_ids(["unregistered"], registry)


def test_dataset_release_checker_requires_explicit_allow_status(tmp_path: Path) -> None:
    registry = tmp_path / "datasets.json"
    approved = {"datasets": [{"id": "approved", "redistribution": "approved_for_redistribution"}]}
    registry.write_text(json.dumps(approved), encoding="utf-8")
    check_dataset_ids(["approved"], registry)


