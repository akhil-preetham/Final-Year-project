"""Unit checks for the matched ablation helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "run_final_ablation_extension.py"
SPEC = importlib.util.spec_from_file_location("cardiodiag_final_ablation_extension", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ablation = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ablation
SPEC.loader.exec_module(ablation)


def test_one_shot_selector_fits_and_transforms_training_features() -> None:
    rng = np.random.default_rng(45)
    matrix = rng.normal(size=(80, 5))
    labels = (matrix[:, 0] - 0.4 * matrix[:, 1] > 0).astype(int)

    selector = ablation.OneShotSelector(
        relevance_threshold=0.02,
        fallback_top_k=3,
        random_state=45,
    ).fit(matrix, labels)

    transformed = selector.transform(matrix)
    assert selector.get_support().shape == (5,)
    assert 1 <= transformed.shape[1] <= 5
    assert transformed.shape == (80, int(selector.get_support().sum()))


def test_full_metrics_include_confusion_derived_and_agreement_metrics() -> None:
    labels = np.asarray([0, 0, 1, 1])
    probabilities = np.asarray([0.1, 0.8, 0.6, 0.2])

    metrics = ablation.full_metrics(labels, probabilities)

    assert metrics["tn"] == 1
    assert metrics["fp"] == 1
    assert metrics["fn"] == 1
    assert metrics["tp"] == 1
    assert metrics["false_positive_rate"] == 0.5
    assert metrics["false_negative_rate"] == 0.5
    assert metrics["mcc"] == 0.0
    assert metrics["cohen_kappa"] == 0.0


def test_pipeline_applies_requested_logistic_class_weight() -> None:
    rng = np.random.default_rng(73)
    X = pd.DataFrame(
        {
            "age": rng.normal(size=60),
            "chol": rng.normal(size=60),
            "sex": np.where(np.arange(60) % 2, "male", "female"),
        }
    )
    X.attrs["categorical_columns"] = ["sex"]

    balanced = ablation.make_pipeline(X, "uci_cleveland", "none", "balanced", 73)
    unweighted = ablation.make_pipeline(X, "uci_cleveland", "none", "unweighted", 73)

    assert balanced.get_params()["model__class_weight"] == "balanced"
    assert unweighted.get_params()["model__class_weight"] is None
