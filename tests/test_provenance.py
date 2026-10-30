import hashlib
import subprocess
import sys
from pathlib import Path

from cardiodiag.provenance import collect_provenance

ROOT = Path(__file__).resolve().parents[1]


def test_collect_provenance_records_corrected_protocol_and_configuration() -> None:
    configuration = {"seed": 42, "outer_splits": 3}
    result = collect_provenance(
        ROOT / "MendeleyCardiovascular_Disease_Dataset.csv",
        "target",
        "nested_validation",
        configuration,
    )

    assert result["selector_protocol"] == "post_boundary_correction_v1"
    assert result["experiment_type"] == "nested_validation"
    assert result["target"] == "target"
    assert result["dataset_sha256"] == hashlib.sha256(
        (ROOT / "MendeleyCardiovascular_Disease_Dataset.csv").read_bytes()
    ).hexdigest()
    assert result["configuration"] == configuration
    assert result["python_version"] == ".".join(map(str, sys.version_info[:3]))
    assert {
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "imbalanced-learn",
        "xgboost",
    }.issubset(result["package_versions"])
    assert "lightgbm" in result["package_versions"]
    assert "catboost" in result["package_versions"]
    assert isinstance(result["working_tree_dirty"], (bool, type(None)))


def test_nested_and_linkage_cli_arguments_remain_available() -> None:
    for script, required in (
        ("experiments/run_nested_validation.py", ["--dataset", "--target", "--output"]),
        ("experiments/run_stability_reliability_linkage.py", ["--dataset", "--target", "--output"]),
    ):
        completed = subprocess.run(
            [sys.executable, script, "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        assert all(argument in completed.stdout for argument in required)
