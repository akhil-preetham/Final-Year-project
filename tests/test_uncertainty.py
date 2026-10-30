import numpy as np
from sklearn.linear_model import LogisticRegression

from cardiodiag.uncertainty import SplitConformalClassifier


def test_split_conformal_classifier_can_abstain() -> None:
    rng = np.random.default_rng(4)
    X = rng.normal(size=(80, 2))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    estimator = LogisticRegression(max_iter=1000)
    conformal = SplitConformalClassifier(estimator, alpha=0.1).fit(
        X[:50], y[:50], X[50:65], y[50:65]
    )

    summary = conformal.summarize(X[65:], y[65:])

    assert summary["n"] == 15
    assert 0 <= summary["coverage"] <= 1
    assert 0 <= summary["abstention_rate"] <= 1


def test_split_conformal_rejects_non_binary_estimator() -> None:
    rng = np.random.default_rng(5)
    X = rng.normal(size=(30, 2))
    y = np.arange(30) % 3

    try:
        SplitConformalClassifier(LogisticRegression(max_iter=1000)).fit(
            X[:20], y[:20], X[20:], y[20:]
        )
    except ValueError as error:
        assert "binary" in str(error)
    else:
        raise AssertionError("Expected a binary-class error")
