from __future__ import annotations

import pandas as pd
import pytest
from audit_mendeley_heart_2026_overlap import compare_rows


def test_multiset_audit_detects_exact_match_independent_of_row_order() -> None:
    candidate = pd.DataFrame(
        {
            "Age": [40, 55, 62],
            "Sex": ["M", "F", "M"],
            "HeartDisease": [0, 1, 1],
        }
    )
    baseline = candidate.iloc[::-1].reset_index(drop=True)

    result = compare_rows(candidate, baseline)

    assert result["same_labeled_row_multiset"] is True
    assert result["same_feature_row_multiset"] is True
    assert result["exact_labeled_row_pairs"] == 3
    assert result["candidate_rows_not_in_baseline"] == 0
    assert result["baseline_rows_not_in_candidate"] == 0


def test_multiset_audit_preserves_duplicate_row_multiplicity() -> None:
    row = {"Age": 40, "Sex": "M", "HeartDisease": 0}
    candidate = pd.DataFrame([row, row, {"Age": 50, "Sex": "F", "HeartDisease": 1}])
    baseline = pd.DataFrame([row, {"Age": 50, "Sex": "F", "HeartDisease": 1}])

    result = compare_rows(candidate, baseline)

    assert result["exact_labeled_row_pairs"] == 2
    assert result["candidate_rows_not_in_baseline"] == 1
    assert result["same_labeled_row_multiset"] is False


def test_audit_rejects_schema_or_target_mismatch() -> None:
    baseline = pd.DataFrame({"Age": [40], "HeartDisease": [0]})

    with pytest.raises(ValueError, match="schemas differ"):
        compare_rows(
            pd.DataFrame({"Age": [40], "HeartDisease": [0], "extra": [1]}),
            baseline,
        )
    with pytest.raises(ValueError, match="Missing target"):
        compare_rows(baseline, baseline, target="target")
