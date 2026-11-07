from pathlib import Path

from cardiodiag.nested_validation import candidate_grid, run_nested_validation

ROOT = Path(__file__).resolve().parents[1]


def test_nested_grid_is_small_and_prespecified() -> None:
    assert candidate_grid("logistic", False) == {"model__C": [0.1, 1.0, 10.0]}
    assert "stable_xaih_drc__stability_threshold" in candidate_grid("osec", True)


def test_nested_validation_returns_outer_fold_records() -> None:
    result = run_nested_validation(
        ROOT / "heart5.csv",
        "HeartDisease",
        candidates=[("logistic", False, "logistic")],
        outer_splits=2,
        outer_repeats=1,
        inner_splits=2,
        seed=42,
    )

    candidate = result["candidates"]["logistic"]
    assert len(candidate["folds"]) == 2
    assert candidate["pooled_outer_metrics"]["n"] == 918
    assert len(candidate["bootstrap_ci"]["roc_auc"]) == 3
    for fold in candidate["folds"]:
        assert len(fold["outer_test_indices"]) == fold["test_n"]
        assert len(fold["outer_test_y_true"]) == fold["test_n"]
        assert len(fold["outer_test_probability"]) == fold["test_n"]
        assert fold["fit_tune_and_score_runtime_seconds"] >= 0
    assert candidate["runtime_seconds"] >= 0


def test_nested_validation_records_excluded_features() -> None:
    result = run_nested_validation(
        ROOT / "MendeleyCardiovascular_Disease_Dataset.csv",
        "target",
        candidates=[("logistic", False, "logistic")],
        outer_splits=2,
        outer_repeats=1,
        inner_splits=2,
        seed=42,
        exclude_features=["noofmajorvessels"],
    )

    assert result["excluded_features"] == ["noofmajorvessels"]
    assert result["config"]["excluded_features"] == ("noofmajorvessels",)
    assert result["candidates"]["logistic"]["pooled_outer_metrics"]["n"] == 1000
