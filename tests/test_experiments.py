import numpy as np
import pandas as pd

from cardiodiag.experiments import build_corrected_pipeline, run_single_experiment


def make_synthetic_dataset(path):
    rng = np.random.default_rng(42)
    count = 48
    age = rng.normal(55, 12, size=count)
    sex = np.where(np.arange(count) % 2, "male", "female")
    signal = age + rng.normal(0, 10, size=count)
    target = (signal > np.median(signal)).astype(int)
    frame = pd.DataFrame({"age": age, "sex": sex, "signal": signal, "target": target})
    frame.to_csv(path, index=False)
    return frame


def test_corrected_pipeline_contains_training_only_steps() -> None:
    X = pd.DataFrame(
        {
            "age": [34, 45, 56, 67],
            "sex": ["female", "male", "female", "male"],
            "signal": [0.2, 0.5, 0.8, 0.4],
        }
    )
    pipeline = build_corrected_pipeline(X, variant="logistic", use_stable_selector=True)

    assert list(pipeline.named_steps) == [
        "cleaner",
        "preprocessor",
        "stable_xaih_drc",
        "model",
    ]


def test_single_experiment_returns_machine_readable_metrics(tmp_path) -> None:
    dataset_path = tmp_path / "synthetic.csv"
    make_synthetic_dataset(dataset_path)
    result = run_single_experiment(dataset_path, "target", "logistic", seed=42)

    assert result["metrics"]["n"] > 0
    assert 0 <= result["metrics"]["roc_auc"] <= 1
    assert result["config"]["use_stable_selector"] is False


def test_corrected_pipeline_supports_individual_model_baselines() -> None:
    import pandas as pd

    X = pd.DataFrame({"age": [30, 40, 50, 60], "sex": [0, 1, 0, 1]})
    for variant in ("knn", "svm", "random_forest"):
        pipeline = build_corrected_pipeline(X, variant=variant)
        assert pipeline.named_steps["model"] is not None
