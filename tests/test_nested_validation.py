from pathlib import Path

from cardiodiag.nested_validation import candidate_grid, run_nested_validation

ROOT = Path(__file__).resolve().parents[1]


def test_nested_grid_is_small_and_prespecified() -> None:
    assert candidate_grid("logistic", False) == {
        "model__C": [0.1, 1.0, 10.0]
    }
    assert "stable_xaih_drc__stability_threshold" in candidate_grid("osec", True)


def test_nested_validation_returns_outer_fold_records() -> None:
    result = run_nested_validation(
        ROOT / "MendeleyCardiovascular_Disease_Dataset.csv",
        "target",
        candidates=[("logistic", False, "logistic")],
        outer_splits=2,
        outer_repeats=1,
        inner_splits=2,
        seed=42,
    )

    candidate = result["candidates"]["logistic"]
    assert len(candidate["folds"]) == 2
    assert candidate["pooled_outer_metrics"]["n"] == 1000
    assert len(candidate["bootstrap_ci"]["roc_auc"]) == 3
