
from experiments.run_internal_stage import DATASETS


def test_internal_stage_has_only_development_datasets() -> None:
    names = {name for _, _, name in DATASETS}

    assert names == {"heart5", "mendeley"}
    assert all(path.name != "external_dataset.csv" for path, _, _ in DATASETS)
