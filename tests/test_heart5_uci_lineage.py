from __future__ import annotations

import pandas as pd
from audit_heart5_uci_lineage import FEATURE_COLUMNS, audit_lineage, source_row_matches


def test_missing_uci_fields_are_unknown_and_observed_fields_must_match() -> None:
    base = {
        "Age": 40,
        "Sex": "M",
        "ChestPainType": "ATA",
        "RestingBP": 140,
        "Cholesterol": 289,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 172,
        "ExerciseAngina": "N",
        "Oldpeak": 0.0,
        "ST_Slope": "Up",
        "HeartDisease": 0,
    }
    source = dict(base)
    source["ST_Slope"] = None

    assert source_row_matches(base, source)
    source["Cholesterol"] = 288
    assert not source_row_matches(base, source)


def test_lineage_audit_counts_unique_ambiguous_and_unmatched_rows() -> None:
    row = {
        "Age": 40,
        "Sex": "M",
        "ChestPainType": "ATA",
        "RestingBP": 140,
        "Cholesterol": 289,
        "FastingBS": 0,
        "RestingECG": "Normal",
        "MaxHR": 172,
        "ExerciseAngina": "N",
        "Oldpeak": 0.0,
        "ST_Slope": "Up",
        "HeartDisease": 0,
    }
    heart5 = pd.DataFrame([row, row])
    source = [
        {"cohort": "site_a", "source_row": 1, "values": dict(row)},
        {"cohort": "site_b", "source_row": 2, "values": {**row, "ST_Slope": None}},
        {"cohort": "site_c", "source_row": 3, "values": {**row, "Cholesterol": 100}},
    ]

    result, row_map = audit_lineage(heart5, source)

    assert tuple(heart5.columns) == tuple(FEATURE_COLUMNS)
    assert result["unique_source_row_matches"] == 0
    assert result["ambiguous_source_row_matches"] == 2
    assert result["unmatched_heart5_rows"] == 0
    assert row_map[0]["match_count"] == 2
