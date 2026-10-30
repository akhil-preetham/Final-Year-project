from pathlib import Path

from cardiodiag.experiments import build_corrected_pipeline, run_single_experiment

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "MendeleyCardiovascular_Disease_Dataset.csv"


def test_corrected_pipeline_contains_training_only_steps() -> None:
    import pandas as pd

    X = pd.read_csv(DATASET).drop(columns=["target"])
    pipeline = build_corrected_pipeline(X, variant="logistic", use_stable_selector=True)

    assert list(pipeline.named_steps) == [
        "cleaner",
        "preprocessor",
        "stable_xaih_drc",
        "model",
    ]


def test_single_experiment_returns_machine_readable_metrics() -> None:
    result = run_single_experiment(DATASET, "target", "logistic", seed=42)

    assert result["metrics"]["n"] > 0
    assert 0 <= result["metrics"]["roc_auc"] <= 1
    assert result["config"]["use_stable_selector"] is False
