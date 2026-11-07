
import pytest

from experiments.run_internal_stage import DATASETS, _ensure_outputs_available


def test_internal_stage_has_only_development_datasets() -> None:
    names = {name for _, _, name in DATASETS}

    assert names == {"heart5", "mendeley"}
    assert all(path.name != "external_dataset.csv" for path, _, _ in DATASETS)


def test_internal_stage_refuses_to_overwrite_existing_artifact(tmp_path) -> None:
    output_dir = tmp_path / "stage"
    output_dir.mkdir()
    (output_dir / "heart5_nested_validation.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        _ensure_outputs_available(output_dir)
