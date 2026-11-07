from __future__ import annotations

import numpy as np
import pytest

from cardiodiag.evaluation import evaluate_predictions
from experiments.summarize_internal_seed_sensitivity import audit_candidate


def make_candidate() -> dict[str, object]:
    labels = np.array([0, 1, 0, 1, 0, 1], dtype=int)
    probabilities = np.array([0.1, 0.9, 0.2, 0.8, 0.4, 0.6], dtype=float)
    folds = []
    for start in (0, 2, 4):
        stop = start + 2
        folds.append(
            {
                "outer_test_indices": list(range(start, stop)),
                "outer_test_y_true": labels[start:stop].tolist(),
                "outer_test_probability": probabilities[start:stop].tolist(),
            }
        )
    return {
        "folds": folds,
        "pooled_outer_metrics": evaluate_predictions(labels, probabilities),
    }


def test_seed_summary_recomputes_metrics_with_exact_outer_coverage() -> None:
    metrics = audit_candidate(make_candidate(), row_count=6)
    assert metrics["n"] == 6
    assert metrics["positive_count"] == 3
    assert metrics["roc_auc"] == pytest.approx(1.0)


def test_seed_summary_rejects_duplicate_outer_test_rows() -> None:
    candidate = make_candidate()
    candidate["folds"][2]["outer_test_indices"] = [4, 4]
    with pytest.raises(ValueError, match="scores a row more than once"):
        audit_candidate(candidate, row_count=6)


def test_seed_summary_rejects_missing_outer_test_rows() -> None:
    candidate = make_candidate()
    candidate["folds"][2]["outer_test_indices"] = [4, 5]
    candidate["folds"][2]["outer_test_probability"] = [0.4]
    with pytest.raises(ValueError, match="differ in length"):
        audit_candidate(candidate, row_count=6)
