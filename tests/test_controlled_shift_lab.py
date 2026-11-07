"""Checks for the source-only novelty detector used in synthetic shift studies."""

from __future__ import annotations

import numpy as np
import pytest

from experiments.controlled_shift_lab import local_outlier_factor_scores


def test_lof_novelty_scores_rank_a_large_shift_as_more_anomalous() -> None:
    rng = np.random.default_rng(9)
    train = rng.normal(size=(100, 3))
    source_eval = rng.normal(size=(30, 3))
    shifted_eval = rng.normal(loc=8.0, size=(30, 3))

    scores = local_outlier_factor_scores(train, source_eval, shifted_eval)

    assert scores.shape == (60,)
    assert np.isfinite(scores).all()
    assert scores[30:].mean() > scores[:30].mean()


def test_lof_novelty_scores_reject_incompatible_inputs() -> None:
    with pytest.raises(ValueError, match="at least three"):
        local_outlier_factor_scores(np.ones((2, 3)), np.ones((2, 3)), np.ones((2, 3)))
    with pytest.raises(ValueError, match="feature counts must match"):
        local_outlier_factor_scores(np.ones((5, 3)), np.ones((2, 2)), np.ones((2, 3)))
