import json
from pathlib import Path

import pandas as pd

from experiments.run_dataset_shift import _categorical_summary, _numeric_summary


def test_numeric_shift_summary_reports_distribution_metrics():
    summary = _numeric_summary(
        pd.Series([1.0, 2.0, 3.0]),
        pd.Series([3.0, 4.0, 5.0]),
    )

    assert summary["standardized_mean_difference"] > 0
    assert 0 <= summary["ks_statistic"] <= 1
    assert summary["psi"] >= 0


def test_categorical_shift_summary_aligns_categories():
    summary = _categorical_summary(pd.Series(["a", "a", "b"]), pd.Series(["b", "c", "c"]))

    assert summary["categories"] == ["a", "b", "c"]
    assert summary["psi"] > 0


def test_shift_artifact_blocks_predictive_transfer():
    artifact = Path("results/generated/dataset_shift.json")
    result = json.loads(artifact.read_text(encoding="utf-8"))

    assert result["protocol"].startswith("distribution-only")
    assert all(not pair["predictive_transfer_authorized"] for pair in result["pairs"].values())
