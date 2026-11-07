"""Reliability-gated prediction fusion."""

from __future__ import annotations

import numpy as np


def reliability_gated_fusion(
    predictions: np.ndarray,
    base_weights: np.ndarray,
    disagreement_penalty: float = 2.0,
) -> np.ndarray:
    """Fuse model probabilities while down-weighting disagreement outliers.

    ``base_weights`` are learned from inner validation.  For each row, a model
    is down-weighted exponentially by its absolute distance from the weighted
    consensus.  This is a deterministic gate, not a learned test-set rule.
    """

    matrix = np.asarray(predictions, dtype=float)
    weights = np.asarray(base_weights, dtype=float)
    if matrix.ndim != 2 or matrix.shape[1] != weights.size:
        raise ValueError("predictions must be [n_samples, n_models] and match weights")
    if np.any((matrix < 0) | (matrix > 1)) or np.any(weights < 0) or not weights.sum() > 0:
        raise ValueError("invalid probabilities or weights")
    normalized = weights / weights.sum()
    consensus = matrix @ normalized
    disagreement = np.abs(matrix - consensus[:, None])
    gated = normalized[None, :] * np.exp(-disagreement_penalty * disagreement)
    return np.sum(gated * matrix, axis=1) / np.maximum(gated.sum(axis=1), 1e-12)
