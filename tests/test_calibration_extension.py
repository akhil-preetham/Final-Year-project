"""Tests for source-only calibration extension helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCRIPT = ROOT / "experiments" / "run_calibration_extension.py"
SPEC = importlib.util.spec_from_file_location("cardiodiag_calibration_extension", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
calibration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = calibration
SPEC.loader.exec_module(calibration)


def test_calibration_maps_return_bounded_probabilities() -> None:
    probabilities = np.asarray([0.08, 0.17, 0.29, 0.41, 0.56, 0.68, 0.82, 0.93])
    labels = np.asarray([0, 0, 0, 0, 1, 1, 1, 1])

    for method in calibration.METHODS:
        mapper, _ = calibration.fit_calibrator(method, probabilities, labels)
        mapped = mapper(probabilities)
        assert mapped.shape == probabilities.shape
        assert np.all(np.isfinite(mapped))
        assert np.all((mapped >= 0) & (mapped <= 1))


def test_uncalibrated_map_preserves_input_probabilities() -> None:
    probabilities = np.asarray([0.2, 0.7])
    mapper, _ = calibration.fit_calibrator("uncalibrated", probabilities, np.asarray([0, 1]))

    np.testing.assert_allclose(mapper(probabilities), probabilities)


def test_calibration_fit_rejects_single_class_calibration_labels() -> None:
    with np.testing.assert_raises_regex(ValueError, "both outcome classes"):
        calibration.fit_calibrator("platt", np.asarray([0.2, 0.3]), np.asarray([0, 0]))
