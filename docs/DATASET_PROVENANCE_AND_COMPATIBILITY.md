# Dataset provenance and compatibility

This report follows the prepared dataset manifest, the candidate screening table, and prior lineage/licensing audits. Raw data are local and excluded from this branch.

## Evaluated data

| dataset_id | records | predictors | class_counts | missing_predictor_cells | license | evaluation_status |
| --- | --- | --- | --- | --- | --- | --- |
| uci_cleveland | 303.000 | 13.000 | {"0": 164, "1": 139} | 6.000 | CC BY 4.0; attribution required | evaluated |
| uci_hungary | 294.000 | 13.000 | {"0": 188, "1": 106} | 782.000 | CC BY 4.0; attribution required | evaluated |
| uci_switzerland | 123.000 | 13.000 | {"0": 8, "1": 115} | 396.000 | CC BY 4.0; attribution required | evaluated |
| uci_va_long_beach | 200.000 | 13.000 | {"0": 51, "1": 149} | 748.000 | CC BY 4.0; attribution required | evaluated |
| uci_heart_failure_519 | 299.000 | 11.000 | {"0": 203, "1": 96} | 0.000 | CC BY 4.0; attribution required | evaluated |
| uci_mi_complications_579 | 1700.000 | 100.000 | {"0": 1429, "1": 271} | 15200.000 | CC BY 4.0; attribution required | evaluated |
| uci_spectf_heart | 267.000 | 44.000 | {"0": 55, "1": 212} | 0.000 | CC BY 4.0; attribution required | evaluated |

The UCI Heart Disease cohorts use the UCI binary target `num=0` versus `num=1..4`; heart failure uses a death-event endpoint, MI uses lethal complication, and SPECTF uses a normal/abnormal imaging endpoint. Outcomes are not pooled. Full class counts, per-feature missingness, exact duplicate counts and pairwise overlap screens are in the adjacent CSV files.

## Compatibility rules

The four UCI angiographic cohorts share the 13-predictor schema and target coding, so they support directed feature-level transfer stress tests. They are previously represented in Heart5 and participant independence is not established. Statlog is an exact Cleveland duplicate after harmonization. Mendeley 2026 is a Heart5 duplicate. The 2021 Mendeley target reference standard and timing are undocumented. Z-Alizadeh Sani uses a different threshold; AngioCAD has incomplete feature mapping and uncertain units; Duke ACATH uses a 75% threshold. The Kaggle 70K dataset has a distinct target and unresolved license. MIMIC-IV and MultiD4CAD access conditions were not acquired.

## Artifacts

- `results/final_research_20261108/dataset_inventory.csv`
- `results/final_research_20261108/dataset_compatibility_matrix.csv`
- `results/final_research_20261108/dataset_class_distribution.csv`
- `results/final_research_20261108/dataset_missing_value_report.csv`
- `results/final_research_20261108/dataset_duplicate_report.csv`
- `results/final_research_20261108/manifests/dataset_manifest.json`

License and attribution remain source-specific. UCI attribution is retained in the frozen manifest. This report does not grant redistribution rights for restricted or locally held data.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->

<!-- DATA_QUALITY_DETAIL START -->
## Additional leakage and data-quality checks

The target field is excluded from each recorded predictor matrix, and preprocessing/model selection remain partition-local. However, files alone cannot verify predictor timing for the death-event or MI-complication tasks. Numerical feature distribution summaries, categorical value counts, and pairwise Spearman correlations with |rho| >= 0.8 are machine-readable. Pairwise correlations are descriptive and are not variance-inflation factors or evidence of causal redundancy. `leakage_audit.csv` records these limits and the exact duplicate boundary evidence.
<!-- DATA_QUALITY_DETAIL END -->
