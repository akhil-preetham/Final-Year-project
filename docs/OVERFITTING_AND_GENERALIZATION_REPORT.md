# Overfitting and generalization report

<!-- OVERFITTING_DATA_INTEGRITY_NOTICE START -->
> **Data-integrity qualification.** This report uses leakage-qualified folds for Hungary and VA Long Beach. Detailed inputs are in results/final_research_20261108/metrics/final_analysis_fold_metrics.csv. Duplicate-safe refits record training AUC and accuracy; resubstitution precision, recall, and F1 for those 12 sensitivity configurations were not generated, so these quantities remain partially completed.
<!-- OVERFITTING_DATA_INTEGRITY_NOTICE END -->

Training values are resubstitution scores on the selected development subset. Test values are untouched outer-fold or official SPECTF test predictions. Differences are diagnostics, not independent estimates. Tuning-stage inner-CV results are separate and included in the full CSV.

| dataset | model | train AUC | test AUC | train − test AUC | train − test accuracy | basis |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| UCI Switzerland | knn | 0.923 | 0.530 | +0.393 | +0.019 | frozen_primary |
| UCI VA Long Beach | ovec | 0.981 | 0.662 | +0.319 | +0.150 | duplicate_safe_rerun |
| UCI VA Long Beach | knn | 0.912 | 0.605 | +0.307 | +0.161 | duplicate_safe_rerun |
| UCI VA Long Beach | random_forest | 0.985 | 0.694 | +0.291 | +0.206 | duplicate_safe_rerun |
| UCI Heart Failure | knn | 0.936 | 0.661 | +0.275 | +0.229 | frozen_primary |
| UCI Switzerland | ovec | 1.000 | 0.732 | +0.268 | +0.004 | frozen_primary |
| UCI MI Complications | knn | 1.000 | 0.736 | +0.264 | +0.149 | frozen_primary |
| UCI Heart Failure | random_forest | 1.000 | 0.739 | +0.261 | +0.304 | frozen_primary |
| UCI Switzerland | random_forest | 0.994 | 0.736 | +0.259 | +0.065 | frozen_primary |
| UCI VA Long Beach | osec | 0.863 | 0.620 | +0.244 | +0.151 | duplicate_safe_rerun |
| UCI SPECTF Heart | logistic | 0.994 | 0.758 | +0.236 | +0.215 | frozen_primary |
| UCI VA Long Beach | svm | 0.888 | 0.660 | +0.227 | +0.072 | duplicate_safe_rerun |
| UCI Heart Failure | ovec | 0.972 | 0.752 | +0.220 | +0.188 | frozen_primary |
| UCI Switzerland | logistic | 0.990 | 0.772 | +0.218 | +0.108 | frozen_primary |
| UCI SPECTF Heart | svm | 0.998 | 0.788 | +0.210 | +0.241 | frozen_primary |
| UCI SPECTF Heart | random_forest | 1.000 | 0.796 | +0.204 | +0.257 | frozen_primary |
| UCI SPECTF Heart | osec | 0.993 | 0.797 | +0.197 | +0.205 | frozen_primary |
| UCI SPECTF Heart | ovec | 1.000 | 0.805 | +0.195 | +0.220 | frozen_primary |
| UCI Heart Failure | osec | 0.919 | 0.736 | +0.183 | +0.126 | frozen_primary |
| UCI VA Long Beach | logistic | 0.837 | 0.658 | +0.179 | +0.108 | duplicate_safe_rerun |

Positive AUC gaps occur frequently, particularly for KNN, tree models and small cohorts. Switzerland results are especially unstable because there are only eight negative records overall; the same cohort's smallest learning subsets triggered six documented failures. SPECTF shows large train/test gaps for several models under its single official test partition. A negative gap does not establish the absence of overfitting; it can reflect split variability.

Learning curves and train/validation plots from the frozen run are retained in `results/final_research_20261108/figures/primary_*`. The current replayed training/validation metrics, including accuracy, precision, sensitivity, specificity, F1, AUC, Brier/log loss and confusion counts, are in `metrics/training_validation_metrics.csv`. The plots and numbers do not identify leakage, patient overlap or causality by themselves. The corrected pipeline fits all transforms and model selection within training partitions; no person identifier is available to guarantee patient-grouped splitting.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->

<!-- FINAL_DUPLICATE_SAFE_GAPS START -->
## Final leakage-qualified training/test gaps

The table aggregates train resubstitution and outer-test fold AUC and accuracy gaps from the mixed-basis fold table. These are diagnostics and do not identify a single cause. Training precision, recall, and F1 were not regenerated for the 12 duplicate-safe sensitivity configurations.

| dataset | model | train AUC | test AUC | train − test AUC | train − test accuracy | basis |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| UCI Switzerland | knn | 0.923 | 0.530 | +0.393 | +0.019 | frozen_primary |
| UCI VA Long Beach | ovec | 0.981 | 0.662 | +0.319 | +0.150 | duplicate_safe_rerun |
| UCI VA Long Beach | knn | 0.912 | 0.605 | +0.307 | +0.161 | duplicate_safe_rerun |
| UCI VA Long Beach | random_forest | 0.985 | 0.694 | +0.291 | +0.206 | duplicate_safe_rerun |
| UCI Heart Failure | knn | 0.936 | 0.661 | +0.275 | +0.229 | frozen_primary |
| UCI Switzerland | ovec | 1.000 | 0.732 | +0.268 | +0.004 | frozen_primary |
| UCI MI Complications | knn | 1.000 | 0.736 | +0.264 | +0.149 | frozen_primary |
| UCI Heart Failure | random_forest | 1.000 | 0.739 | +0.261 | +0.304 | frozen_primary |
| UCI Switzerland | random_forest | 0.994 | 0.736 | +0.259 | +0.065 | frozen_primary |
| UCI VA Long Beach | osec | 0.863 | 0.620 | +0.244 | +0.151 | duplicate_safe_rerun |
| UCI SPECTF Heart | logistic | 0.994 | 0.758 | +0.236 | +0.215 | frozen_primary |
| UCI VA Long Beach | svm | 0.888 | 0.660 | +0.227 | +0.072 | duplicate_safe_rerun |
| UCI Heart Failure | ovec | 0.972 | 0.752 | +0.220 | +0.188 | frozen_primary |
| UCI Switzerland | logistic | 0.990 | 0.772 | +0.218 | +0.108 | frozen_primary |
| UCI SPECTF Heart | svm | 0.998 | 0.788 | +0.210 | +0.241 | frozen_primary |
| UCI SPECTF Heart | random_forest | 1.000 | 0.796 | +0.204 | +0.257 | frozen_primary |
| UCI SPECTF Heart | osec | 0.993 | 0.797 | +0.197 | +0.205 | frozen_primary |
| UCI SPECTF Heart | ovec | 1.000 | 0.805 | +0.195 | +0.220 | frozen_primary |
| UCI Heart Failure | osec | 0.919 | 0.736 | +0.183 | +0.126 | frozen_primary |
| UCI VA Long Beach | logistic | 0.837 | 0.658 | +0.179 | +0.108 | duplicate_safe_rerun |
<!-- FINAL_DUPLICATE_SAFE_GAPS END -->
