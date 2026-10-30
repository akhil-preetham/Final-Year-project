
from cardiodiag.data import load_dataset
from experiments.run_model_benchmark import _candidate_specs, _pipeline

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def test_benchmark_candidates_include_required_available_families() -> None:
    candidates = _candidate_specs(seed=42)

    assert {
        "dummy",
        "logistic",
        "lda",
        "gaussian_nb",
        "random_forest",
        "extra_trees",
        "hist_gradient_boosting",
        "gradient_boosting",
        "adaboost",
        "mlp",
    }.issubset(candidates)


def test_benchmark_pipeline_preserves_training_only_steps() -> None:
    X, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")
    model, _ = _candidate_specs(seed=42)["logistic"]
    pipeline = _pipeline(X, model)

    assert list(pipeline.named_steps) == ["cleaner", "preprocessor", "model"]
    assert isinstance(pipeline.named_steps["cleaner"].categorical_columns, tuple)
