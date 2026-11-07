import inspect

import numpy as np
import pandas as pd
import pytest
import run_angiocad_feature_ablation_posthoc as ablation


def test_prespecified_feature_preprocessor_handles_missing_and_unknown_categories():
    source = pd.DataFrame(
        {
            "age": [40.0, 55.0, np.nan, 70.0],
            "sex": ["female", "male", "female", "male"],
            "fbs": [0, 1, 0, 1],
        }
    )
    target = pd.DataFrame({"age": [62.0, np.nan], "sex": ["unknown", "female"], "fbs": [np.nan, 1]})
    preprocessor = ablation._build_preprocessor(("age", "sex", "fbs"))

    source_matrix = preprocessor.fit_transform(source)
    target_matrix = preprocessor.transform(target)

    assert source_matrix.shape[0] == len(source)
    assert target_matrix.shape == (len(target), source_matrix.shape[1])
    assert np.isfinite(target_matrix).all()


def test_ablation_fit_function_does_not_accept_target_labels():
    parameters = inspect.signature(ablation._fit_and_score_subset).parameters

    assert "target_y" not in parameters
    assert "target_y_for_scoring" not in parameters


@pytest.mark.parametrize("features", [(), ("age", "unknown"), ("label",)])
def test_feature_preprocessor_rejects_empty_or_unregistered_features(features):
    with pytest.raises(ValueError, match="Invalid feature subset"):
        ablation._build_preprocessor(features)
