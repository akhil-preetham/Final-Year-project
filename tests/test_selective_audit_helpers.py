"""Unit checks for descriptive post-hoc selective metric helpers."""

from __future__ import annotations

import numpy as np
import pytest

from experiments.audit_target_risk_coverage_descriptive import (
    partition_summary,
    risk_coverage_curve,
    wilson_interval,
)


def test_wilson_interval_is_conservative_for_zero_observed_errors() -> None:
    interval = wilson_interval(0, 21)

    assert interval is not None
    assert interval[0] == 0
    assert interval[1] == pytest.approx(0.1546, abs=0.0001)


def test_risk_coverage_curve_orders_by_confidence_and_reports_counts() -> None:
    labels = np.array([0, 1, 1, 0])
    probabilities = np.array([0.51, 0.99, 0.75, 0.1])

    curve = risk_coverage_curve(labels, probabilities, np.array([0.5, 1.0]))

    assert curve[0]["accepted_n"] == 2
    assert curve[0]["accepted_error_count"] == 0
    assert curve[0]["selective_risk"] == 0
    assert curve[1]["accepted_n"] == 4
    assert curve[1]["accepted_error_count"] == 1


def test_partition_summary_compares_accepted_and_rejected_rows() -> None:
    result = partition_summary(
        np.array([0, 1, 1, 0]),
        np.array([0.1, 0.9, 0.8, 0.7]),
        np.array([True, True, False, False]),
        "unit_test",
    )

    assert result["coverage"] == 0.5
    assert result["accepted_errors"] == 0
    assert result["rejected_errors"] == 1
    assert result["accepted_class_counts"] == {"0": 1, "1": 1}
