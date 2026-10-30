import numpy as np

from cardiodiag.reliability import (
    calibration_summary,
    nogueira_stability,
    selective_risk_curve,
    uncertainty_evidence,
)


def test_calibration_summary_returns_intercept_and_slope() -> None:
    y = np.array([0, 0, 1, 1, 0, 1])
    probabilities = np.array([0.1, 0.2, 0.8, 0.9, 0.4, 0.7])

    result = calibration_summary(y, probabilities)

    assert result["n"] == 6
    assert "calibration_intercept" in result
    assert "calibration_slope" in result


def test_selective_risk_decreases_or_stays_stable_at_lower_coverage() -> None:
    y = np.array([0, 0, 1, 1, 1, 0])
    probabilities = np.array([0.1, 0.2, 0.8, 0.9, 0.6, 0.4])

    curve = selective_risk_curve(y, probabilities)

    assert curve[0]["coverage"] <= curve[-1]["coverage"]
    assert all(0 <= row["risk"] <= 1 for row in curve)


def test_nogueira_stability_is_one_for_identical_selection_sets() -> None:
    selection = np.tile(np.array([[1, 0, 1, 0]], dtype=float), (4, 1))

    assert nogueira_stability(selection) == 1.0


def test_uncertainty_evidence_reports_confidence_ranking() -> None:
    y = np.array([0, 0, 1, 1])
    probabilities = np.array([0.05, 0.4, 0.6, 0.95])

    result = uncertainty_evidence(y, probabilities)
    curve = result["selective_risk"]

    assert isinstance(result["confidence_error_auc"], (int, float))
    assert isinstance(result["aurc"], (int, float))
    assert result["confidence_error_auc"] > 0.5
    assert result["aurc"] <= 0.5
    assert isinstance(curve, list)
    assert len(curve) == 6
