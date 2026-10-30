import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

import cardiodiag.feature_selection as feature_selection
from cardiodiag.feature_selection import StableXAIHDRC, one_shot_selection_mask


def test_stable_selector_is_reproducible_and_selects_signal() -> None:
    rng = np.random.default_rng(7)
    signal = rng.normal(size=80)
    X = np.column_stack([signal, rng.normal(size=(80, 4))])
    y = (signal > 0).astype(int)

    first = StableXAIHDRC(n_resamples=4, fallback_top_k=2, random_state=11).fit(X, y)
    second = StableXAIHDRC(n_resamples=4, fallback_top_k=2, random_state=11).fit(X, y)

    assert np.array_equal(first.get_support(), second.get_support())
    assert first.get_support().any()
    assert first.selection_frequency_[0] >= 0.75
    assert first.selection_matrix_.shape == (4, 5)


def test_selector_keeps_original_validation_rows_out_of_bootstrap_fit(
    monkeypatch,
) -> None:
    X = np.arange(240, dtype=float).reshape(60, 4)
    y = np.tile([0, 1], 30)
    fitted_rows = []
    validation_rows = []
    original_fit = LogisticRegression.fit

    def recording_fit(model, values, target):
        fitted_rows.append(values.copy())
        return original_fit(model, values, target)

    def recording_importance(model, values, target, **kwargs):
        validation_rows.append(values.copy())
        return type("Importance", (), {"importances_mean": np.zeros(values.shape[1])})()

    monkeypatch.setattr(LogisticRegression, "fit", recording_fit)
    monkeypatch.setattr(feature_selection, "permutation_importance", recording_importance)

    selector = StableXAIHDRC(
        n_resamples=3,
        fallback_top_k=2,
        random_state=13,
    ).fit(X, y)

    fit_indices = set(selector.relevance_fit_indices_.tolist())
    validation_indices = set(selector.relevance_validation_indices_.tolist())
    assert fit_indices.isdisjoint(validation_indices)
    assert all(set(sample.tolist()).issubset(fit_indices) for sample in selector.bootstrap_indices_)
    assert all(
        set(rows[:, 0].astype(int).tolist()).issubset(
            {int(X[index, 0]) for index in selector.bootstrap_indices_[sample_id]}
        )
        for sample_id, rows in enumerate(fitted_rows)
    )
    expected_validation = X[selector.relevance_validation_indices_]
    assert all(np.array_equal(rows, expected_validation) for rows in validation_rows)


def test_selector_provenance_uses_positions_with_nonconsecutive_duplicate_labels() -> None:
    rng = np.random.default_rng(14)
    X = pd.DataFrame(
        rng.normal(size=(80, 4)),
        index=[10, 10, 25, 25] * 20,
    )
    y = pd.Series(np.tile([0, 1], 40), index=X.index)

    selector = StableXAIHDRC(n_resamples=3, fallback_top_k=2, random_state=15).fit(X, y)

    assert selector.relevance_fit_indices_.dtype.kind in "iu"
    assert selector.relevance_validation_indices_.dtype.kind in "iu"
    assert set(selector.relevance_fit_indices_).isdisjoint(
        selector.relevance_validation_indices_
    )
    assert all(
        set(sample).issubset(selector.relevance_fit_indices_)
        for sample in selector.bootstrap_indices_
    )
    assert all(
        0 <= position < len(X)
        for sample in selector.bootstrap_indices_
        for position in sample
    )


def test_stable_selector_rejects_non_binary_targets() -> None:
    X = np.eye(3)
    y = np.array([0, 1, 2])

    try:
        StableXAIHDRC().fit(X, y)
    except ValueError as error:
        assert "binary" in str(error)
    else:
        raise AssertionError("Expected a binary-target error")


def test_one_shot_selector_returns_a_reproducible_nonempty_mask() -> None:
    rng = np.random.default_rng(8)
    X = rng.normal(size=(60, 4))
    y = (X[:, 0] - X[:, 1] > 0).astype(int)

    first = one_shot_selection_mask(X, y, fallback_top_k=2, random_state=12)
    second = one_shot_selection_mask(X, y, fallback_top_k=2, random_state=12)

    assert np.array_equal(first, second)
    assert first.dtype == bool
    assert first.any()
