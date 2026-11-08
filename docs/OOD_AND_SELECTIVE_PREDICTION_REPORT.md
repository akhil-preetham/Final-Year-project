# OOD and selective-prediction report

Two distinct OOD questions are retained. Within-task analysis asks whether the support score flags model errors on held-out records. Cross-dataset analysis asks whether a nearest-neighbor distance score distinguishes source-calibration feature vectors from target-cohort feature vectors. Target outcome labels are not used to compute the cross-domain score or threshold.

## Directed transfer domain detection

The table reports the mean over six models for each direction. Average precision depends on the sampled source/target mixture, so it is a ranking diagnostic rather than a population-prevalence-calibrated value.

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

The threshold is the source-calibration 95th percentile. Its alert rate is approximately the nominal 5% by construction up to finite-sample ties; target alert rates vary by direction. Detection quality is heterogeneous and does not guarantee safe rejection. Selective prediction tables report coverage, accepted-set size, risk and AURC; in some historical external evaluations very little coverage remained. There is no demonstrated operating point that establishes reliable use under shift.

Detailed outputs: `metrics/ood_metrics.csv`, `metrics/cross_dataset_ood_metrics.csv`, `metrics/selective_prediction_metrics.csv`, and `metrics/selective_prediction_diagnostics.csv`. The 72 OOD refits and scores are reproducible from source features and saved settings.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->
