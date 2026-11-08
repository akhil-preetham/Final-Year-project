# Complete model comparison report

<!-- MODEL_DATA_INTEGRITY_NOTICE START -->
> **Data-integrity qualification.** The frozen Hungary estimate includes an exact duplicate crossing development and outer test in one fold. Use the duplicate-safe values for Hungary and VA Long Beach. The complete 42-row mixed-basis comparison is in results/final_research_20261108/metrics/final_analysis_model_metrics.csv.
<!-- MODEL_DATA_INTEGRITY_NOTICE END -->

All six candidates use the frozen task-specific evaluation protocol. Binary threshold metrics use probability 0.5; positive labels follow each dataset's stated target. ROC-AUC is threshold-independent. Cross-task metrics are not combined into one score.

## Frozen primary pooled AUC per task (Hungary and VA qualified)

These descriptive pooled maxima preserve the frozen primary run. Hungary is directly affected by an exact duplicate crossing development/test; Hungary and VA values are superseded for the final fold-mean comparison below. Do not use the frozen Hungary/VA estimates as unqualified performance claims.

| task | model | pooled_roc_auc | pooled_accuracy | pooled_recall | pooled_specificity | pooled_mcc |
| --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | svm | 0.910 | 0.828 | 0.806 | 0.848 | 0.654 |
| UCI Heart Failure | ovec | 0.750 | 0.706 | 0.396 | 0.852 | 0.276 |
| UCI Hungary | ovec | 0.884 | 0.799 | 0.689 | 0.862 | 0.559 |
| UCI MI Complications | osec | 0.867 | 0.799 | 0.768 | 0.805 | 0.464 |
| UCI SPECTF Heart | ovec | 0.805 | 0.749 | 0.750 | 0.733 | 0.290 |
| UCI Switzerland | osec | 0.718 | 0.902 | 0.957 | 0.125 | 0.093 |
| UCI VA Long Beach | random_forest | 0.677 | 0.730 | 0.819 | 0.471 | 0.289 |

## Frozen primary OVEC and OSEC comparison (Hungary/VA qualified)

| dataset | ovec_auc | osec_auc | ovec_minus_osec_auc |
| --- | --- | --- | --- |
| UCI Cleveland | 0.909 | 0.903 | 0.006 |
| UCI Heart Failure | 0.752 | 0.736 | 0.016 |
| UCI Hungary | 0.890 | 0.876 | 0.014 |
| UCI MI Complications | 0.866 | 0.868 | -0.001 |
| UCI SPECTF Heart | 0.805 | 0.797 | 0.009 |
| UCI Switzerland | 0.732 | 0.751 | -0.018 |
| UCI VA Long Beach | 0.655 | 0.612 | 0.043 |

This frozen primary table is superseded for the Hungary and VA fold means by the duplicate-safe comparison below. Across all tasks, results do not show consistent ensemble superiority. Accuracy can conceal poor minority sensitivity, especially for heart failure and MI; use the full metrics CSV, including specificity, MCC, kappa, false-positive and false-negative rates.

## Evidence and interpretation

The machine-readable full model table is `results/final_research_20261108/metrics/model_metrics.csv`; fold detail is `.../fold_metrics.csv`. The primary held-out predictions are `results/multi_dataset_evaluation_20261108/predictions/20261107T202404Z/out_of_fold_and_official_predictions.csv`. The verification manifest checks metric reconstruction against these predictions. Confidence intervals in the frozen report use a class-stratified bootstrap; they are descriptive and do not make CV folds independent.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->

<!-- FINAL_FOLD_MEAN_COMPARISON START -->
## Leakage-qualified fold-mean comparison

The table uses fold means for nested tasks and the single official held-out SPECTF score. Hungary and VA Long Beach use the duplicate-safe reruns; the other five tasks retain the frozen evaluation. All 42 model rows and 114 fold/test rows are included in final_analysis_model_metrics.csv and final_analysis_fold_metrics.csv with an evaluation_basis column. Model selection maxima are descriptive.

| task | fold-mean AUC winner | fold-mean ROC-AUC | pooled ROC-AUC | basis |
| --- | --- | ---: | ---: | --- |
| UCI Cleveland | Random Forest | 0.911 | 0.909 | frozen_primary |
| UCI Heart Failure | OVEC | 0.752 | 0.750 | frozen_primary |
| UCI Hungary | Logistic Regression | 0.897 | 0.890 | duplicate_safe_rerun |
| UCI MI Complications | Random Forest | 0.869 | 0.851 | frozen_primary |
| UCI SPECTF Heart | OVEC | 0.805 | 0.805 | frozen_primary |
| UCI Switzerland | Logistic Regression | 0.772 | 0.705 | frozen_primary |
| UCI VA Long Beach | Random Forest | 0.694 | 0.689 | duplicate_safe_rerun |

### OVEC versus OSEC on the same fold-mean scale

| task | OVEC fold-mean AUC | OSEC fold-mean AUC | OVEC − OSEC |
| --- | ---: | ---: | ---: |
| UCI Cleveland | 0.909 | 0.903 | +0.006 |
| UCI Hungary | 0.891 | 0.896 | -0.005 |
| UCI Switzerland | 0.732 | 0.751 | -0.018 |
| UCI VA Long Beach | 0.662 | 0.620 | +0.042 |
| UCI Heart Failure | 0.752 | 0.736 | +0.016 |
| UCI MI Complications | 0.866 | 0.868 | -0.001 |
| UCI SPECTF Heart | 0.805 | 0.797 | +0.009 |

No consistent ensemble advantage is supported.
<!-- FINAL_FOLD_MEAN_COMPARISON END -->
