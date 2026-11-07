import audit_selective_policy_components as audit
import numpy as np
import pandas as pd


def test_selective_metrics_report_coverage_and_accepted_errors():
    result = audit._selective_metrics(
        labels=np.array([1, 0, 1, 0]),
        predictions=np.array([1, 1, 0, 0]),
        accepted=np.array([True, True, False, False]),
        probabilities=np.array([0.8, 0.7, 0.2, 0.1]),
        policy="test",
        status="test policy",
    )

    assert result["coverage"] == 0.5
    assert result["accepted_n"] == 2
    assert result["accepted_error_count"] == 1
    assert result["accepted_error_rate"] == 0.5
    assert result["accepted_confusion_matrix_tn_fp_fn_tp"] == [0, 1, 0, 1]


def test_domain_detection_metrics_use_source_threshold_and_report_ap_baseline():
    result = audit._domain_detection_metrics(
        source_scores=np.array([0.1, 0.2]),
        target_scores=np.array([0.8, 0.9]),
        threshold=0.3,
        recorded_metrics={
            "source_false_alert_count": 0,
            "source_false_alert_rate": 0.0,
            "target_alert_count": 2,
            "target_alert_rate": 1.0,
            "target_vs_source_auroc": 1.0,
        },
    )

    assert result["target_vs_source_auroc_recomputed_from_saved_scores"] == 1.0
    assert result["target_vs_source_average_precision"] == 1.0
    assert result["average_precision_prevalence_baseline"] == 0.5
    assert result["source_calibration"]["specificity_at_threshold"] == 1.0
    assert result["target_cohort"]["sensitivity_at_threshold"] == 1.0


def test_source_lodo_stability_summarizes_heldout_source_folds():
    metrics = {
        "source_domain_lodo": {
            "folds": [
                {
                    "heldout_source_domain": "site_a",
                    "ood": {"knn": {"target_vs_source_auroc": 0.4}},
                },
                {
                    "heldout_source_domain": "site_b",
                    "ood": {"knn": {"target_vs_source_auroc": 0.6}},
                },
            ]
        }
    }

    result = audit._source_lodo_stability(metrics, "knn")

    assert result["mean_auroc"] == 0.5
    assert result["minimum_auroc"] == 0.4
    assert result["maximum_auroc"] == 0.6


def test_registered_combination_matches_singleton_conformal_and_knn_union():
    target = pd.DataFrame(
        {
            "exploratory_calibrated_probability": [0.8, 0.4, 0.7, 0.3],
            "exploratory_conformal_prediction": [1, 0, 0, -1],
            "exploratory_conformal_abstain": [False, False, False, True],
            "exploratory_knn_ood_flag": [False, True, False, False],
            "exploratory_isolation_forest_ood_flag": [False, False, True, False],
            "exploratory_combined_abstain": [False, True, False, True],
            "exploratory_combined_prediction": [1, -1, 0, -1],
            "domain_gate_action": ["abstain"] * 4,
        }
    )

    rows = audit._make_policy_rows(target, np.array([1, 0, 1, 0]))
    by_name = {row["policy"]: row for row in rows}

    assert by_name["conformal_plus_knn_registered_combination"]["coverage"] == 0.5
    assert by_name["unknown_domain_registry_gate"]["coverage"] == 0.0
    assert by_name["conformal_plus_isolation_forest_posthoc"]["coverage"] == 0.5
