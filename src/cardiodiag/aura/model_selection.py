"""Candidate model definitions and AURA-ML selection utilities."""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression


def available_models(seed: int = 42) -> dict[str, Any]:
    """Return bounded, single-threaded candidates available in this environment."""

    models: dict[str, Any] = {
        "logistic": LogisticRegression(
            C=1.0, max_iter=1500, class_weight="balanced", random_state=seed
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=180, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=30,
            l2_regularization=1.0, random_state=seed,
        ),
    }
    try:
        from catboost import CatBoostClassifier

        models["catboost"] = CatBoostClassifier(
            iterations=220, depth=5, learning_rate=0.05, l2_leaf_reg=3.0,
            random_strength=0.0, loss_function="Logloss", verbose=False,
            thread_count=1, random_seed=seed,
        )
    except ImportError:
        pass
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=220, max_depth=3, learning_rate=0.05, min_child_weight=3,
            subsample=0.85, colsample_bytree=0.85, reg_lambda=1.0,
            eval_metric="logloss", n_jobs=1, random_state=seed,
        )
    except ImportError:
        pass
    return models
