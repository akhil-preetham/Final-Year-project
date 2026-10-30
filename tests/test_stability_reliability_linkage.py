from pathlib import Path

from experiments.run_stability_reliability_linkage import run_dataset

ROOT = Path(__file__).resolve().parents[1]


def test_linkage_analysis_reports_paired_reliability_and_stability() -> None:
    result = run_dataset(
        ROOT / "MendeleyCardiovascular_Disease_Dataset.csv", "target", [42, 43, 44]
    )

    assert len(result["per_seed"]) == 3
    assert "roc_auc" in result["paired_reliability_differences"]
    assert -1 <= result["stability"]["cross_seed_selected_set_nogueira"] <= 1
    assert "confidence_error_auc" in result["stability_reliability_rank_correlations"]
