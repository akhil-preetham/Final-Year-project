from typing import cast

import numpy as np

from cardiodiag.evaluation import bootstrap_metric_ci, evaluate_predictions


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
