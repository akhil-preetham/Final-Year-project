from pathlib import Path

import numpy as np
import pandas as pd

from experiments.run_robustness import make_evaluation_perturbations

ROOT = Path(__file__).resolve().parents[1]


def test_robustness_perturbations_do_not_mutate_fit_or_eval_inputs() -> None:
    fit = pd.DataFrame({"age": [40, 50, 60], "gender": [0, 1, 1]})
    evaluation = pd.DataFrame({"age": [45, 55], "gender": [1, 0]})
    fit_before = fit.copy(deep=True)
    evaluation_before = evaluation.copy(deep=True)

    result = make_evaluation_perturbations(fit, evaluation, seed=7)

    pd.testing.assert_frame_equal(fit, fit_before)
    pd.testing.assert_frame_equal(evaluation, evaluation_before)
    assert set(result) == {"clean", "missing_10pct", "numeric_noise_5pct_sd"}
    assert np.array_equal(result["clean"].to_numpy(), evaluation.to_numpy())


def test_robustness_rejects_invalid_perturbation_parameters() -> None:
    frame = pd.DataFrame({"age": [40, 50], "gender": [0, 1]})

    try:
        make_evaluation_perturbations(frame, frame, seed=1, missing_rate=1.1)
    except ValueError as error:
        assert "missing_rate" in str(error)
    else:
        raise AssertionError("Expected an invalid missing-rate error")
