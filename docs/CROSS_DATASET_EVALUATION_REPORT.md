# Cross-dataset evaluation report

The evaluation includes all 12 ordered source-to-target directions among four UCI Heart Disease cohorts, each evaluated with six models (72 directed comparisons). The 13 predictors and binarized target are aligned. Models and preprocessing are fitted on source rows, with source-only inner selection and calibration. Target outcomes are excluded from OOD fitting/threshold selection; predictive AUC is computed afterward for retrospective audit.

| source_dataset | target_dataset | mean_auc | mean_ap | source_fpr | target_alert |
| --- | --- | --- | --- | --- | --- |
| UCI Hungary | UCI Cleveland | 0.896 | 0.967 | 0.034 | 0.421 |
| UCI VA Long Beach | UCI Cleveland | 0.890 | 0.982 | 0.025 | 0.448 |
| UCI Switzerland | UCI Cleveland | 0.874 | 0.988 | 0.040 | 0.612 |
| UCI VA Long Beach | UCI Hungary | 0.772 | 0.955 | 0.025 | 0.235 |
| UCI Hungary | UCI VA Long Beach | 0.727 | 0.885 | 0.034 | 0.160 |
| UCI Hungary | UCI Switzerland | 0.723 | 0.815 | 0.034 | 0.123 |
| UCI Cleveland | UCI VA Long Beach | 0.703 | 0.865 | 0.049 | 0.129 |
| UCI VA Long Beach | UCI Switzerland | 0.586 | 0.792 | 0.025 | 0.046 |
| UCI Switzerland | UCI Hungary | 0.571 | 0.943 | 0.040 | 0.122 |
| UCI Cleveland | UCI Switzerland | 0.560 | 0.696 | 0.049 | 0.045 |
| UCI Cleveland | UCI Hungary | 0.486 | 0.831 | 0.049 | 0.074 |
| UCI Switzerland | UCI VA Long Beach | 0.454 | 0.884 | 0.040 | 0.107 |

The cohorts are known components of Heart5, and patient-level linkage is unavailable. These analyses are retrospective cohort stress tests, not independent external validation. Performance varies substantially by direction and target; the lowest target AUCs are retained as failures of transfer, not removed. See `results/final_research_20261108/metrics/cross_dataset_metrics.csv` for target-label predictive results and `cross_dataset_ood_metrics.csv` for target-label-free domain diagnostics.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->
