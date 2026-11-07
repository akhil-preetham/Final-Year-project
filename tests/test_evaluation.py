from typing import cast

import numpy as np

from cardiodiag.evaluation import (
    bootstrap_metric_ci,
    evaluate_predictions,
    uniform_bin_calibration_errors,
)


def test_evaluation_reports_clinically_relevant_metrics() -> None:
    y = np.array([0, 0, 1, 1])
    probabilities = np.array([0.1, 0.4, 0.6, 0.9])

    metrics = evaluate_predictions(y, probabilities)

    assert metrics["n"] == 4
    assert metrics["roc_auc"] == 1.0
    assert cast(float, metrics["brier"]) < 0.1
    assert metrics["tn"] == metrics["tp"] == 2


def test_bootstrap_ci_returns_ordered_interval() -> None:
    y = np.array([0, 0, 1, 1, 0, 1])
    probabilities = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7])

    point, low, high = bootstrap_metric_ci(y, probabilities, lambda a, b: float(np.mean(b)))

    assert low <= point <= high


def test_uniform_bin_ece_reports_macro_and_sample_weighted_values() -> None:
    y = np.array([0, 0, 1])
    probabilities = np.array([0.05, 0.15, 0.85])

    macro, weighted = uniform_bin_calibration_errors(y, probabilities, bins=2)
    metrics = evaluate_predictions(y, probabilities, calibration_bins=2)

    assert np.isclose(macro, 0.125)
    assert np.isclose(weighted, 0.35 / 3)
    assert metrics["ece_uniform"] == macro
    assert np.isclose(float(metrics["ece_weighted_uniform"]), weighted)


def test_evaluation_rejects_nonbinary_fractional_labels() -> None:
    with np.testing.assert_raises_regex(ValueError, "binary labels"):
        evaluate_predictions(np.array([0.5, 1.0]), np.array([0.2, 0.8]))
