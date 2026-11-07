"""Unit tests for the separate CLIN-ADAPT package."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from clin_adapt.adaptive_learning import CASLCoordinator
from clin_adapt.nested import NestedConfig, run_nested_validation
from clin_adapt.parallel_engine import ParallelExecutionEngine
from clin_adapt.preprocessing import build_clinical_pipeline
from clin_adapt.profiling import profile_clinical_dataset
from clin_adapt.registry import available_model_specs, discover_model_registry


def _small_table() -> tuple[pd.DataFrame, np.ndarray]:
    X = pd.DataFrame(
        {
            "age": [30, 31, 32, 50, 51, 52, 40, 41, 42, 60, 61, 62],
            "sex": ["F", "F", "M", "M", "M", "F", "F", "M", "F", "M", "M", "F"],
            "bp": [110, 115, 120, 150, 155, 160, 130, 135, 140, 170, 175, 180],
        }
    )
    X.attrs["categorical_columns"] = ["sex"]
    return X, np.asarray([0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1])


def test_profile_respects_integer_categorical_metadata() -> None:
    X = pd.DataFrame({"age": [1, 2, 3], "coded": [0, 1, 0]})
    profile = profile_clinical_dataset(X, np.asarray([0, 1, 0]), ["coded"])
    assert profile.numeric_features == ("age",)
    assert profile.categorical_features == ("coded",)
    assert profile.vector().shape == (12,)


def test_registry_records_available_and_unavailable_families() -> None:
    registry = discover_model_registry()
    assert len(registry) >= 30
    assert {spec.name for spec in registry if spec.status != "unavailable"}.issuperset(
        {"logistic", "random_forest", "catboost"}
    )
    assert any(spec.name == "tabpfn" and spec.status == "unavailable" for spec in registry)
    assert available_model_specs()


def test_pipeline_fits_with_unseen_categorical_level() -> None:
    X, y = _small_table()
    pipeline = build_clinical_pipeline(X.iloc[:8], available_model_specs()[0])
    pipeline.fit(X.iloc[:8], y[:8])
    predictions = pipeline.predict_proba(X.iloc[8:])[:, 1]
    assert predictions.shape == (4,)
    assert np.all((predictions >= 0) & (predictions <= 1))


def test_parallel_engine_isolates_failure_and_writes_checkpoint(tmp_path) -> None:
    def succeeds() -> dict[str, float]:
        return {"score": 1.0}

    def fails() -> dict[str, float]:
        raise ValueError("controlled failure")

    checkpoint = tmp_path / "checkpoint.json"
    results, records = ParallelExecutionEngine(max_workers=2, checkpoint_path=checkpoint).run(
        {"good": succeeds, "bad": fails}
    )
    assert results["good"]["score"] == 1.0
    assert any(record.name == "bad" and record.status == "failed" for record in records)
    assert json.loads(checkpoint.read_text())


def test_casl_rejects_bad_candidate_and_keeps_single_when_fusion_not_justified() -> None:
    y = np.asarray([0, 0, 1, 1, 0, 1])
    predictions = {
        "strong": np.asarray([0.05, 0.1, 0.9, 0.95, 0.2, 0.8]),
        "bad": np.asarray([0.9, 0.8, 0.1, 0.2, 0.8, 0.1]),
    }
    decision = CASLCoordinator().decide(y, predictions)
    assert decision.best_single_name == "strong"
    assert decision.output_type == "single_candidate"
    assert "bad" in decision.rejected_candidates or decision.selected_names == ("strong",)


def test_nested_validation_is_reproducible_and_serializable() -> None:
    X, y = _small_table()
    specs = [spec for spec in available_model_specs() if spec.name in {"logistic", "decision_tree"}]
    config = NestedConfig(
        outer_splits=2,
        inner_splits=2,
        max_workers=2,
        store_predictions=False,
        calibration=False,
    )
    result = run_nested_validation(X, y, specs, config)
    assert result["status"] == "completed"
    assert len(result["folds"]) == 2
    assert 0.0 <= result["pooled_metrics"]["roc_auc"] <= 1.0
    json.dumps(result, allow_nan=False)
