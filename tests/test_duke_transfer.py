from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from run_duke_transfer import source_split

from cardiodiag.domain_guard import DomainAwareSelectivePredictor
from cardiodiag.uncertainty import (
    conformal_prediction_sets,
    conformal_selective_summary,
    domain_robust_threshold,
    finite_sample_upper_quantile,
)


def test_finite_sample_upper_quantile_uses_conformal_rank() -> None:
    assert finite_sample_upper_quantile(np.arange(1, 10), alpha=0.2) == 8.0
    assert np.isinf(finite_sample_upper_quantile([1.0, 2.0], alpha=0.1))


def test_domain_robust_threshold_uses_worst_source_domain() -> None:
    threshold, by_domain = domain_robust_threshold(
        values=[0.1, 0.2, 0.8, 0.9],
        domains=["a", "a", "b", "b"],
        alpha=0.5,
    )
    assert by_domain == {"a": 0.2, "b": 0.9}
    assert threshold == 0.9


def test_conformal_sets_and_selective_summary() -> None:
    probabilities = np.array([[0.95, 0.05], [0.52, 0.48], [0.1, 0.9]])
    prediction_sets = conformal_prediction_sets(probabilities, threshold=0.53)
    assert prediction_sets.tolist() == [[True, False], [True, True], [False, True]]
    summary = conformal_selective_summary([0, 1, 1], prediction_sets)
    assert summary["empirical_set_coverage"] == pytest.approx(1.0)
    assert summary["singleton_coverage"] == pytest.approx(2 / 3)
    assert summary["selective_risk"] == 0.0


@pytest.mark.parametrize(
    ("values", "domains", "alpha"),
    [([], [], 0.1), ([1.0], ["a", "b"], 0.1), ([1.0], ["a"], 1.0)],
)
def test_domain_robust_threshold_rejects_invalid_inputs(values, domains, alpha) -> None:
    with pytest.raises(ValueError):
        domain_robust_threshold(values, domains, alpha)


def test_conformal_prediction_sets_reject_invalid_probability_rows() -> None:
    with pytest.raises(ValueError, match="sum to one"):
        conformal_prediction_sets([[0.4, 0.4]], threshold=0.9)


def test_source_split_keeps_probability_and_conformal_calibration_disjoint() -> None:
    labels = np.tile([0, 1], 50)
    cohort = {
        "X": pd.DataFrame(
            {"age": np.arange(100), "sex": np.tile(["female", "male"], 50), "chol": 200.0}
        ),
        "y": labels,
        "row_index": np.arange(100),
    }
    split = source_split({"site": cohort}, ("site",))
    record = split["splits"]["site"]
    fit = set(record["fit_row_indices"])
    platt = set(record["probability_calibration_row_indices"])
    conformal = set(record["conformal_calibration_row_indices"])
    assert len(fit) == 70
    assert len(platt) == 15
    assert len(conformal) == 15
    assert fit.isdisjoint(platt)
    assert fit.isdisjoint(conformal)
    assert platt.isdisjoint(conformal)
    assert fit | platt | conformal == set(range(100))


class _IdentityPreprocessor:
    def transform(self, frame):
        return np.zeros((len(frame), 1))


class _FixedProbabilities:
    def predict_proba(self, matrix):
        return np.tile([0.1, 0.9], (len(matrix), 1))


class _FixedNeighbors:
    def kneighbors(self, matrix, return_distance=True):
        return np.full((len(matrix), 10), 0.1), np.zeros((len(matrix), 10), dtype=int)


def _predictor(ood_threshold: float = 0.5) -> DomainAwareSelectivePredictor:
    return DomainAwareSelectivePredictor(
        {
            "preprocessor": _IdentityPreprocessor(),
            "predictor": _FixedProbabilities(),
            "calibrator": _FixedProbabilities(),
            "neighbors": _FixedNeighbors(),
            "source_domains": ["site_a"],
            "conformal_thresholds_by_domain": {"site_a": 0.2},
            "ood_thresholds_by_domain": {"site_a": ood_threshold},
            "features": ["age", "sex", "chol"],
        }
    )


def test_domain_guard_classifies_only_known_singleton_in_support_rows() -> None:
    rows = pd.DataFrame({"age": [55], "sex": ["male"], "chol": [220]})
    result = _predictor().predict(rows, "site_a")[0]
    assert result["action"] == "classify"
    assert result["prediction"] == 1
    assert result["probability"] == pytest.approx(0.9)


def test_domain_guard_fails_closed_for_unknown_domain_and_ood_rows() -> None:
    rows = pd.DataFrame({"age": [55], "sex": ["male"], "chol": [220]})
    unknown = _predictor().predict(rows, "new_site")[0]
    assert unknown["action"] == "abstain"
    assert unknown["reason"] == "domain_not_in_source_registry"
    assert unknown["probability"] is None

    outside = _predictor(ood_threshold=0.05).predict(rows, "site_a")[0]
    assert outside["action"] == "abstain"
    assert outside["reason"] == "outside_source_feature_support"
    assert outside["probability"] is None
    assert outside["prediction_set"] == []


def test_domain_guard_withholds_probability_for_non_singleton_set() -> None:
    predictor = _predictor()
    predictor.bundle["conformal_thresholds_by_domain"] = {"site_a": 1.0}
    rows = pd.DataFrame({"age": [55], "sex": ["male"], "chol": [220]})

    result = predictor.predict(rows, "site_a")[0]

    assert result["action"] == "abstain"
    assert result["reason"] == "non_singleton_conformal_set"
    assert result["probability"] is None
    assert result["prediction_set"] == [0, 1]


def test_domain_guard_supports_a_different_harmonized_feature_schema() -> None:
    bundle = _predictor().bundle.copy()
    bundle.update(
        {
            "features": ["age", "sex", "fbs"],
            "numeric_features": ["age"],
            "categorical_features": ["sex", "fbs"],
            "allowed_categories": {
                "sex": ["female", "male"],
                "fbs": ["gt_120_mg_dl", "le_120_mg_dl"],
            },
        }
    )
    example = pd.DataFrame({"age": [55], "sex": ["male"], "fbs": ["le_120_mg_dl"]})
    result = DomainAwareSelectivePredictor(bundle).predict(example, "site_a")[0]
    assert result["action"] == "classify"
