from pathlib import Path

import pandas as pd
import pytest

from cardiodiag.historical import historical_encode_heart5, run_historical_native

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not (ROOT / "heart5.csv").exists(),
    reason="heart5.csv is not bundled because redistribution terms are unresolved",
)


def test_historical_encoding_matches_notebook_schema() -> None:
    frame = pd.read_csv(ROOT / "heart5.csv")
    X, y = historical_encode_heart5(frame)

    assert X.shape == (918, 11)
    assert y.value_counts().to_dict() == {1: 508, 0: 410}
    assert set(X["ST_Slope"].unique()) <= {0, 1}


def test_historical_native_protocol_records_leakage_prone_order() -> None:
    frame = pd.read_csv(ROOT / "heart5.csv")
    result = run_historical_native(frame, model_name="osec", seed=42)

    assert result["protocol"]["resampling"] == "SMOTE before train_test_split"
    assert result["shapes"]["resampled"][0] == 1016
    assert result["metrics"]["n"] == 204
