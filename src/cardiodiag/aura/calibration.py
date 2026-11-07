"""Training-side calibration for AURA-ML."""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class SigmoidCalibrator:
    """Platt-style calibrator fitted only on inner out-of-fold predictions."""

    def fit(self, probabilities: np.ndarray, y: np.ndarray) -> SigmoidCalibrator:
        probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
        y = np.asarray(y, dtype=int)
        if probabilities.shape != y.shape:
            raise ValueError("probabilities and y must have identical shapes")
        self.model_ = LogisticRegression(C=1.0, solver="lbfgs")
        self.model_.fit(_logit(probabilities).reshape(-1, 1), y)
        return self

    def predict(self, probabilities: np.ndarray) -> np.ndarray:
        if not hasattr(self, "model_"):
            raise RuntimeError("SigmoidCalibrator must be fitted first")
        probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
        return self.model_.predict_proba(_logit(probabilities).reshape(-1, 1))[:, 1]


class IsotonicCalibrator:
    """Monotone calibration fitted only on training-side predictions."""

    def fit(self, probabilities: np.ndarray, y: np.ndarray) -> IsotonicCalibrator:
        probabilities = np.asarray(probabilities, dtype=float)
        y = np.asarray(y, dtype=int)
        if probabilities.shape != y.shape:
            raise ValueError("probabilities and y must have identical shapes")
        self.model_ = IsotonicRegression(y_min=1e-6, y_max=1 - 1e-6, out_of_bounds="clip")
        self.model_.fit(probabilities, y)
        return self

    def predict(self, probabilities: np.ndarray) -> np.ndarray:
        if not hasattr(self, "model_"):
            raise RuntimeError("IsotonicCalibrator must be fitted first")
        return np.asarray(self.model_.predict(np.asarray(probabilities, dtype=float)), dtype=float)


def _logit(probabilities: np.ndarray) -> np.ndarray:
    return np.log(probabilities / (1.0 - probabilities))
