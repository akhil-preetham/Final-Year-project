import numpy as np
import pandas as pd
import pytest

from cardiodiag.aura import (
    AdaptiveStableSelector,
    AdaptiveTabularTransformer,
    AURAClassifier,
    AURAConfig,
    DatasetProfile,
    IsotonicCalibrator,
    MultiViewRepresentation,
    profile_dataset,
    reliability_gated_fusion,
)


def _table() -> tuple[pd.DataFrame, np.ndarray]:
    frame = pd.DataFrame(
        {
            "age": [40, 42, 55, 58, 61, 63, 45, 47, 68, 70, 52, 54],
            "weight": [70, 71, 92, 95, 100, 102, 75, 77, 110, 108, 85, 88],
            "group": ["a", "a", "b", "b", "b", "b", "a", "a", "c", "c", "b", "b"],
        }
    )
    frame.attrs["categorical_columns"] = ["group"]
    frame.attrs["numeric_columns"] = ["age", "weight"]
    return frame, np.array([0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1])


def test_profile_and_adaptive_transformer_are_training_only() -> None:
    frame, y = _table()
    profile = profile_dataset(frame.iloc[:8], y[:8])
    assert isinstance(profile, DatasetProfile)
    transformer = AdaptiveTabularTransformer().fit(frame.iloc[:8], y[:8])
    transformed = transformer.transform(frame.iloc[8:])
    assert transformed.shape[0] == 4
    assert transformer.policy_["numeric_scaler"] in {"standard", "robust"}


def test_multiview_and_selector_have_stable_shapes() -> None:
    frame, y = _table()
    representation = MultiViewRepresentation(view="multi").fit(frame, y)
    transformed = representation.transform(frame)
    selector = AdaptiveStableSelector(max_features=3, random_state=42).fit(transformed, y)
    assert transformed.shape[1] >= frame.shape[1]
    assert selector.transform(transformed).shape[1] <= 3
    assert selector.selection_matrix_.shape[0] == 4


def test_fusion_downweights_disagreement_without_leaking_labels() -> None:
    predictions = np.array([[0.8, 0.8], [0.9, 0.1]])
    fused = reliability_gated_fusion(predictions, np.array([0.5, 0.5]))
    assert np.isclose(fused[0], 0.8)
    assert 0.1 < fused[1] < 0.9


def test_aura_fit_is_reproducible_and_rejects_unsupported_input() -> None:
    frame, y = _table()
    config = AURAConfig(inner_splits=2, seed=42)
    first = AURAClassifier(config).fit(frame, y)
    second = AURAClassifier(config).fit(frame, y)
    assert first.selected_names_ == second.selected_names_
    np.testing.assert_allclose(first.predict_proba(frame), second.predict_proba(frame))
    with pytest.raises(TypeError):
        AURAClassifier(config).fit(frame.to_numpy(), y)


def test_isotonic_calibration_and_training_threshold_are_available() -> None:
    probabilities = np.array([0.05, 0.2, 0.7, 0.8, 0.9, 0.95])
    y = np.array([0, 0, 1, 1, 1, 1])
    calibrator = IsotonicCalibrator().fit(probabilities, y)
    calibrated = calibrator.predict(probabilities)
    assert np.all((calibrated >= 0) & (calibrated <= 1))
    frame, labels = _table()
    model = AURAClassifier(
        AURAConfig(
            inner_splits=2,
            seed=42,
            use_feature_selection=False,
            calibration_methods=("sigmoid", "isotonic"),
            threshold_mode="validation_balanced_accuracy",
        )
    ).fit(frame, labels)
    assert 0.05 <= model.decision_threshold_ <= 0.95
    assert set(model.calibration_evidence_) == {"none", "sigmoid", "isotonic"}
