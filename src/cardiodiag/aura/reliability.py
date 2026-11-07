"""Reliability scoring used for inner-only AURA-ML decisions."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def reliability_objective(
    y: np.ndarray,
    probabilities: np.ndarray,
    fold_roc_auc: list[float] | np.ndarray,
    runtime_seconds: float = 0.0,
    prevalence: float | None = None,
) -> dict[str, float]:
    """Return the predeclared utility and its components.

    The utility rewards discrimination and PR performance, penalizes Brier/ECE,
    fold instability, and a very small runtime term.  It is used only on inner
    validation predictions; outer labels never enter this calculation.
    """

    y = np.asarray(y, dtype=int)
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    prevalence = float(y.mean()) if prevalence is None else prevalence
    roc = float(roc_auc_score(y, p))
    pr = float(average_precision_score(y, p))
    brier = float(np.mean((y - p) ** 2))
    bins = np.linspace(0.0, 1.0, 11)
    ece_terms = []
    for low, high in zip(bins[:-1], bins[1:]):
        mask = (p >= low) & ((p < high) if high < 1 else (p <= high))
        if mask.any():
            ece_terms.append(
                float(mask.mean()) * abs(float(y[mask].mean()) - float(p[mask].mean()))
            )
    ece = float(sum(ece_terms))
    fold_std = (
        float(np.std(np.asarray(fold_roc_auc, dtype=float), ddof=1))
        if len(fold_roc_auc) > 1
        else 0.0
    )
    utility = (
        0.60 * roc
        + 0.20 * ((pr - prevalence) / max(1e-6, 1.0 - prevalence))
        + 0.10 * (1.0 - brier)
        + 0.05 * (1.0 - ece)
        - 0.10 * fold_std
        - 0.00001 * np.log1p(max(0.0, runtime_seconds))
    )
    return {
        "utility": float(utility),
        "roc_auc": roc,
        "pr_auc": pr,
        "brier": brier,
        "ece": ece,
        "fold_roc_auc_std": fold_std,
        "runtime_seconds": float(runtime_seconds),
    }
