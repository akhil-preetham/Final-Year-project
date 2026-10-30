from cardiodiag.data import load_dataset
from experiments.run_tuned_ensemble import _models, _pipeline

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def test_priority_tuning_includes_installed_boosters() -> None:
    models = _models(seed=42)
    assert {"logistic", "random_forest", "hist_gradient_boosting", "xgboost"}.issubset(
        models
    )
    assert "lightgbm" in models
    assert "catboost" in models


def test_tuned_pipeline_keeps_preprocessing_inside_estimator() -> None:
    X, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")
    model, _ = _models(seed=42)["hist_gradient_boosting"]
    pipeline = _pipeline(X, model)
    assert list(pipeline.named_steps) == ["cleaner", "preprocessor", "model"]
