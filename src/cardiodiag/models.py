"""Baseline and proposed estimators used by the research experiments."""

from __future__ import annotations

from sklearn.ensemble import (
    AdaBoostClassifier,
    RandomForestClassifier,
    StackingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def build_ovec(random_state: int = 42) -> VotingClassifier:
    """Build the historical OVEC family with deterministic defaults."""

    return VotingClassifier(
        estimators=[
            ("knn", KNeighborsClassifier(n_neighbors=7)),
            ("rf", RandomForestClassifier(n_estimators=200, random_state=random_state)),
            (
                "lr",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
            ("svc", SVC(probability=True, class_weight="balanced", random_state=random_state)),
        ],
        voting="soft",
        n_jobs=-1,
    )


def build_osec(random_state: int = 42) -> StackingClassifier:
    """Build a reproducible OSEC-style stacking ensemble.

    The original paper uses an XGBoost meta-learner in some notebooks. The
    default here uses logistic regression to keep the corrected baseline stable
    across machines; ``build_osec_xgboost`` provides the optional analogue.
    """

    base_estimators = [
        ("nb", GaussianNB()),
        ("ada", AdaBoostClassifier(n_estimators=100, random_state=random_state)),
        ("tree", DecisionTreeClassifier(max_depth=5, random_state=random_state)),
        (
            "lr",
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
        ),
    ]
    return StackingClassifier(
        estimators=base_estimators,
        final_estimator=LogisticRegression(max_iter=2000, class_weight="balanced"),
        cv=5,
        stack_method="predict_proba",
        n_jobs=-1,
    )


def build_osec_xgboost(random_state: int = 42) -> StackingClassifier:
    """Build the XGBoost-meta-learner variant described by the paper."""

    from xgboost import XGBClassifier

    base = build_osec(random_state=random_state)
    base.final_estimator = XGBClassifier(
        n_estimators=150,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=random_state,
    )
    return base
