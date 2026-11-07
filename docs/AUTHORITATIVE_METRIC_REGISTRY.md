# Authoritative experiment registry

Generated on `2026-11-02` from stored JSON artifacts.
Archived notebook outputs and superseded files are not silently mixed with the authoritative entries.

| Experiment | Dataset | Protocol | Primary metric | Status | Source artifact |
|---|---|---|---|---|---|
| `nested_internal_post_boundary_heart5` | `heart5.csv` | 3 outer folds x 3 inner folds, seed 42, ROC-AUC selection | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_nested_heart5.json` |
| `nested_internal_post_boundary_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | 3 outer folds x 3 inner folds, seed 42, ROC-AUC selection | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_nested_mendeley.json` |
| `nested_schema_sensitivity_heart5` | `heart5.csv` | 2 outer folds x 2 inner folds, seed 42, schema-corrected sensitivity run | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_heart5_nested_2x2.json` |
| `nested_schema_sensitivity_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | 2 outer folds x 2 inner folds, seed 42, schema-corrected sensitivity run | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_mendeley_nested_2x2.json` |
| `feature_stability_post_boundary_heart5` | `heart5.csv` | 5 stratified folds x 3 repeats, six selector resamples, seed 42 | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_stability_heart5.json` |
| `feature_stability_post_boundary_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | 5 stratified folds x 3 repeats, six selector resamples, seed 42 | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_stability_mendeley.json` |
| `feature_stability_schema_sensitivity_heart5` | `heart5.csv` | 5 stratified folds x 3 repeats, six selector resamples | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_heart5_stability_3x6.json` |
| `feature_stability_schema_sensitivity_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | 5 stratified folds x 3 repeats, six selector resamples | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_mendeley_stability_3x6.json` |
| `stability_reliability_linkage_heart5` | `heart5.csv` | ten paired fit/calibration/evaluation seeds 42-51 | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_linkage_heart5.json` |
| `stability_reliability_linkage_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | ten paired fit/calibration/evaluation seeds 42-51 | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/post_boundary_corrected_linkage_mendeley.json` |
| `stability_reliability_schema_sensitivity_heart5` | `heart5.csv` | four paired fit/calibration/evaluation seeds | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_heart5_linkage_4seeds.json` |
| `stability_reliability_schema_sensitivity_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | four paired fit/calibration/evaluation seeds | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_mendeley_linkage_4seeds.json` |
| `uncertainty_schema_sensitivity_heart5` | `heart5.csv` | four repeated fit/calibration/evaluation seeds | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_heart5_uncertainty_4seeds.json` |
| `uncertainty_schema_sensitivity_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | four repeated fit/calibration/evaluation seeds | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/schema_corrected_mendeley_uncertainty_4seeds.json` |
| `evaluation_stress_test_heart5` | `heart5.csv` | single clean split with evaluation-only missingness/noise perturbations | ROC-AUC where available | `EXPLORATORY` | `results/generated/schema_corrected_heart5_robustness.json` |
| `evaluation_stress_test_mendeley` | `MendeleyCardiovascular_Disease_Dataset.csv` | single clean split with evaluation-only missingness/noise perturbations | ROC-AUC where available | `EXPLORATORY` | `results/generated/schema_corrected_mendeley_robustness.json` |
| `kaggle70k_primary_model_benchmark` | `cardio_train.csv` | 3 outer folds x 2 inner folds, seed 42, ROC-AUC selection | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/kaggle70k_model_benchmark.json` |
| `kaggle70k_tuned_priority_models` | `cardio_train.csv` | 3 outer folds x 2 inner folds, seed 42, fixed OOF ensemble weights | ROC-AUC where available | `COMPLETED_AND_VERIFIED` | `results/generated/kaggle70k_tuned_priority_oof_ensemble.json` |
| `kaggle70k_compact_candidate_pool` | `cardio_train.csv` | 3 outer folds x 2 inner folds, seed 42; SVM/KNN skipped for scale | ROC-AUC where available | `EXPLORATORY` | `results/generated/kaggle70k_compact_candidate_pool.json` |
| `heart5_compact_candidate_pool` | `heart5.csv` | 3 outer folds x 2 inner folds, seed 42 | ROC-AUC where available | `EXPLORATORY` | `results/generated/heart5_compact_candidate_pool.json` |
| `mendeley_compact_candidate_pool` | `MendeleyCardiovascular_Disease_Dataset.csv` | 3 outer folds x 2 inner folds, seed 42 | ROC-AUC where available | `EXPLORATORY` | `results/generated/mendeley_compact_candidate_pool.json` |
| `kaggle70k_custom_logistic_pair` | `cardio_train.csv` | 3 outer folds x 2 inner folds, seed 42; reduced custom pair | ROC-AUC where available | `COMPLETED_BUT_NOT_INDEPENDENTLY_VERIFIED` | `results/generated/post_tuning_custom_nested_kaggle70k_logistic_pair.json` |
| `kaggle70k_stability_stress_test` | `cardio_train.csv` | bounded stability analysis on separate 70k schema | ROC-AUC where available | `EXPLORATORY` | `results/generated/post_boundary_corrected_kaggle70k_stability.json` |
| `kaggle70k_stability_reliability_stress_test` | `cardio_train.csv` | bounded internal linkage analysis on separate 70k schema | ROC-AUC where available | `EXPLORATORY` | `results/generated/post_boundary_corrected_kaggle70k_linkage.json` |
| `historical_protocol_comparison_heart5` | `heart5.csv` | historical notebook approximation versus corrected single split | ROC-AUC where available | `HISTORICAL` | `results/generated/heart5_protocol_comparison.json` |
| `internal_stage_default_attempt` | `unknown` | default two-dataset internal stage; bounded execution attempt | ROC-AUC where available | `INCOMPLETE` | `results/generated/internal_stage_manifest.json` |

## Interpretation rules

- `post_boundary_corrected_*` is the primary corrected internal evidence family.
- `schema_corrected_*` is bounded sensitivity evidence and is not pooled with the primary family.
- Kaggle 70k artifacts use a different target/schema and are not external validation of the CARDIODIAG tasks.
- Historical and exploratory artifacts remain traceable but cannot support confirmatory claims.
- No entry supports clinical utility, safety, fairness, or deployment readiness.
