from pathlib import Path

from experiments.run_stability_evidence import run_dataset

ROOT = Path(__file__).resolve().parents[1]


def test_stability_output_records_post_correction_provenance() -> None:
    result = run_dataset(
        dataset=ROOT / "MendeleyCardiovascular_Disease_Dataset.csv",
        target="target",
        n_splits=2,
        n_repeats=2,
        n_resamples=2,
        stability_threshold=0.75,
        relevance_threshold=0.02,
        seed=19,
    )

    provenance = result["provenance"]
    assert provenance["selector_protocol"] == "post_boundary_correction_v1"
    assert provenance["experiment_type"] == "stability_evidence"
    assert len(provenance["dataset_sha256"]) == 64
    assert provenance["configuration"] == {
        "n_splits": 2,
        "n_repeats": 2,
        "n_resamples": 2,
        "stability_threshold": 0.75,
        "relevance_threshold": 0.02,
        "seed": 19,
    }
    assert provenance["seed"] == 19
    assert provenance["python_version"]
    assert {
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "imbalanced-learn",
        "xgboost",
    }.issubset(provenance["package_versions"])
    assert isinstance(provenance["working_tree_dirty"], (bool, type(None)))
