"""Validation-only probability calibration for CLIN-ADAPT."""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from .evaluation import evaluate_binary_predictions


def choose_calibration(
    y: np.ndarray,
    probabilities: np.ndarray,
    seed: int = 42,
    minimum_brier_improvement: float = 1e-4,
) -> tuple[str, np.ndarray, dict[str, float]]:
    """Select none, sigmoid or isotonic using cross-fitted inner predictions."""

    y = np.asarray(y, dtype=int)
    probabilities = np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    outputs = {"sigmoid": np.empty_like(probabilities), "isotonic": np.empty_like(probabilities)}
    for train, valid in cv.split(probabilities, y):
        for method in outputs:
            calibrator = _fit_calibrator(method, probabilities[train], y[train])
            outputs[method][valid] = _apply_calibrator(calibrator, method, probabilities[valid])
    raw_brier = float(evaluate_binary_predictions(y, probabilities)["brier"])
    briers = {"none": raw_brier}
    briers.update(
        {
            method: float(evaluate_binary_predictions(y, values)["brier"])
            for method, values in outputs.items()
        }
    )
    selected = min(briers, key=lambda name: (briers[name], name))
    if selected != "none" and briers[selected] + minimum_brier_improvement >= raw_brier:
        selected = "none"
    selected_values = probabilities if selected == "none" else outputs[selected]
    return selected, selected_values, briers


def fit_full_calibrator(method: str, probabilities: np.ndarray, y: np.ndarray) -> object | None:
    """Fit the selected calibrator on inner-only predictions for outer use."""

    if method == "none":
        return None
    return _fit_calibrator(method, np.asarray(probabilities, dtype=float), np.asarray(y, dtype=int))


def apply_calibrator(
    calibrator: object | None, method: str, probabilities: np.ndarray
) -> np.ndarray:
    if calibrator is None or method == "none":
        return np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1 - 1e-6)
    return _apply_calibrator(calibrator, method, np.asarray(probabilities, dtype=float))


def _fit_calibrator(method: str, probabilities: np.ndarray, y: np.ndarray) -> object:
    if method == "sigmoid":
        model = LogisticRegression(C=1.0, solver="lbfgs")
        model.fit(_logit(probabilities).reshape(-1, 1), y)
        return model
    if method == "isotonic":
        return IsotonicRegression(out_of_bounds="clip").fit(probabilities, y)
    raise ValueError(f"Unsupported calibration method: {method}")


def _apply_calibrator(calibrator: object, method: str, probabilities: np.ndarray) -> np.ndarray:
    if method == "sigmoid":
        output = calibrator.predict_proba(_logit(probabilities).reshape(-1, 1))[:, 1]
    else:
        output = calibrator.predict(probabilities)
    return np.clip(np.asarray(output, dtype=float), 1e-6, 1 - 1e-6)


def _logit(probabilities: np.ndarray) -> np.ndarray:
    clipped = np.clip(probabilities, 1e-6, 1 - 1e-6)
    return np.log(clipped / (1.0 - clipped))
