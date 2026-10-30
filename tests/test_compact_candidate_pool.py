from cardiodiag.data import load_dataset
from experiments.run_compact_candidate_pool import _candidate_specs, _pipeline

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def test_compact_pool_contains_requested_families() -> None:
    specs = _candidate_specs(seed=42, include_local=True)
    assert {
        "logistic",
        "elastic_net",
        "rbf_svm",
        "knn",
        "random_forest",
        "extra_trees",
        "xgboost",
        "catboost",
        "lightgbm",
        "hist_gradient_boosting",
        "gaussian_nb",
        "lda",
    }.issubset(specs)


def test_compact_pool_pipeline_is_training_local() -> None:
    X, _ = load_dataset(ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target")
    model, _ = _candidate_specs(seed=42, include_local=True)["elastic_net"]
    pipeline = _pipeline(X, model)
    assert list(pipeline.named_steps) == ["cleaner", "preprocessor", "model"]
