# CARDIODIAG complete technical research report

<!-- TECHNICAL_REPORT_DATA_INTEGRITY_NOTICE START -->
> **Data-integrity qualification.** The frozen Hungary evaluation placed an exact duplicate across development and outer test in one fold. The fold-mean comparison below uses a duplicate-safe rerun for Hungary and VA Long Beach; the original frozen metrics remain available and are not overwritten.
<!-- TECHNICAL_REPORT_DATA_INTEGRITY_NOTICE END -->

## Abstract

This report audits and completes the current CARDIODIAG machine-learning research snapshot. Six classifiers, including the preserved OVEC and OSEC definitions, were evaluated across seven distinct tabular tasks with training-only preprocessing and leakage-controlled validation. The work adds full threshold and ranking metrics, training/test diagnostics, conformal levels, directed transfer OOD metrics, runtime measurements and data-quality visualizations. Results show task-dependent rankings and substantial distribution sensitivity; the evidence does not establish universal ensemble benefit or independent external validity.

## Research questions and contribution

The study asks whether project ensembles consistently outperform four individual classifiers; whether training/test gaps suggest data-limited overfitting; whether calibration, conformal sets, OOD alerts and selective prediction remain useful under cohort shift; and how cost varies across model families. The defensible contribution is an auditable, multi-task evaluation of preserved project methods with explicit compatibility, lineage and reliability limits. It is not a newly validated clinical algorithm.

## Methods and architecture

The corrected implementation performs fold-local cleaning, imputation, encoding and scaling. The six model configurations are Logistic Regression, KNN, SVM, Random Forest, OVEC soft voting and OSEC stacking. Nested 3x3 stratified validation is used where supported. SPECTF retains its UCI 80/187 official split; its 80 training rows are divided into development and calibration rows. No test labels are used to select hyperparameters or fit transforms. Cross-cohort target labels are not used in source fitting or OOD thresholds. Details and code map are in `docs/SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md` and `docs/EXPERIMENTAL_PROTOCOL.md`.

## Dataset tasks and EDA

| dataset_id | records | predictors | class_counts | missing_predictor_cells | license | evaluation_status |
| --- | --- | --- | --- | --- | --- | --- |
| uci_cleveland | 303.000 | 13.000 | {"0": 164, "1": 139} | 6.000 | CC BY 4.0; attribution required | evaluated |
| uci_hungary | 294.000 | 13.000 | {"0": 188, "1": 106} | 782.000 | CC BY 4.0; attribution required | evaluated |
| uci_switzerland | 123.000 | 13.000 | {"0": 8, "1": 115} | 396.000 | CC BY 4.0; attribution required | evaluated |
| uci_va_long_beach | 200.000 | 13.000 | {"0": 51, "1": 149} | 748.000 | CC BY 4.0; attribution required | evaluated |
| uci_heart_failure_519 | 299.000 | 11.000 | {"0": 203, "1": 96} | 0.000 | CC BY 4.0; attribution required | evaluated |
| uci_mi_complications_579 | 1700.000 | 100.000 | {"0": 1429, "1": 271} | 15200.000 | CC BY 4.0; attribution required | evaluated |
| uci_spectf_heart | 267.000 | 44.000 | {"0": 55, "1": 212} | 0.000 | CC BY 4.0; attribution required | evaluated |

The CAD cohorts share an endpoint/schema but are known in Heart5 lineage. Heart failure, MI complications and SPECTF are separate tasks. Missingness, class counts, exact duplicates, pairwise exact feature overlaps, numeric outliers and numeric feature correlations are stored beneath `results/final_research_20261108/`. The outlier table uses the descriptive 1.5-IQR rule and removes nothing. UCI source and license records remain in the frozen manifest and focused provenance report.

## Results

### Model comparison

| task | model | pooled_roc_auc | pooled_accuracy | pooled_recall | pooled_specificity | pooled_mcc |
| --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | svm | 0.910 | 0.828 | 0.806 | 0.848 | 0.654 |
| UCI Heart Failure | ovec | 0.750 | 0.706 | 0.396 | 0.852 | 0.276 |
| UCI Hungary | ovec | 0.884 | 0.799 | 0.689 | 0.862 | 0.559 |
| UCI MI Complications | osec | 0.867 | 0.799 | 0.768 | 0.805 | 0.464 |
| UCI SPECTF Heart | ovec | 0.805 | 0.749 | 0.750 | 0.733 | 0.290 |
| UCI Switzerland | osec | 0.718 | 0.902 | 0.957 | 0.125 | 0.093 |
| UCI VA Long Beach | random_forest | 0.677 | 0.730 | 0.819 | 0.471 | 0.289 |

OVEC-minus-OSEC AUC differences change sign by task. The model maximizing AUC is not necessarily the model maximizing threshold sensitivity or specificity. Imbalance is material for the MI and SPECT tasks; a high accuracy alone is not a sufficient summary.

### Overfitting and generalization

Train resubstitution AUC frequently exceeds held-out AUC; the largest gaps occur in small or unstable tasks and flexible models. Learning curves are descriptive. The six Switzerland small-subset learning-curve failures remain in the failure ledger. These findings motivate caution but do not identify a single cause.

### Feature selection and ablations

The supplemental matched study compared no selection, one-shot relevance selection and StableXAIHDRC, each with balanced or unweighted downstream Logistic Regression. It used six configurations across all seven tasks, shared outer partitions, a training-only three-fold inner search for C, and duplicate-safe Hungary/VA folds. Across tasks, no-weight versus balanced baseline AUC differences ranged from −0.020 to +0.009; one-shot balanced versus no-selection balanced ranged from −0.015 to +0.017; StableXAIHDRC balanced ranged from −0.021 to +0.012. Mean changes were −0.002, −0.001, and −0.006 respectively. Effects varied by task and did not establish a general benefit. A separate OSEC ablation compared fixed default meta-estimator C=1 with inner tuning over {0.1, 1, 10}; macro task-level fixed-minus-tuned changes were −0.004 AUC, +0.006 Brier, and +0.016 log loss. Tuning effects varied by task, and Switzerland’s five-fold internal stacking warnings remain. The 114 selector/class-weight fold records were checked against local predictions across 15 metrics; the OSEC fixed-C predictions and metrics are saved in the supplemental ablation artifacts. The earlier 70K feature-stability comparison and matched Heart5/Mendeley results remain separate historical analyses. The original A–L design and exact LoRAS/LIME/XAIH-DRC settings remain unavailable, so full component attribution is still partial.

### Calibration and conformal uncertainty

| nominal_coverage | empirical_coverage_min | empirical_coverage_mean | empirical_coverage_max | average_set_size_mean | group_n |
| --- | --- | --- | --- | --- | --- |
| 0.800 | 0.529 | 0.815 | 0.951 | 1.081 | 114 |
| 0.900 | 0.791 | 0.920 | 1.000 | 1.383 | 114 |
| 0.950 | 0.898 | 0.973 | 1.000 | 1.700 | 114 |

Coverage is empirical and conditional on an exchangeability assumption that may fail across cohorts. Brier and ECE are retained; ECE depends on binning. Class-conditional coverage and set size vary by task and fold.

A held-out source-calibration comparison fit Platt, isotonic, beta, and temperature probability maps on the dedicated calibration partitions and scored matched outer-test or official-test predictions across 42 task/model groups. Platt reduced pooled Brier in 28/42 groups and reduced mean weighted ECE by 0.044, but increased mean log loss by 0.015. Temperature scaling reduced mean log loss by 0.092 while changing Brier by only +0.0003 on average. Isotonic calibration increased mean log loss by 0.428 and lowered Brier in 15/42 groups, indicating instability at these calibration sample sizes. The evidence supports no universally preferred map. Because the same data are used for probability calibration and the existing conformal threshold, calibrated probabilities are not used to claim conformal coverage in this comparison. Full fold metrics, fitted parameters, figures, hashes and protocol are in `results/final_research_20261108/calibration_extension/`.

### OOD, selective prediction and transfer

There are 72 directed source/target/model comparisons among the four UCI CAD cohorts. Domain ROC-AUC and average precision vary by direction; no single threshold makes target features uniformly detectable. Selective prediction provides a coverage-risk tradeoff, but useful coverage under shift is not established. Since cohort linkage is unavailable and all cohorts are represented in Heart5, this is not independent external validation.

### Computational performance

| model | median_fit_s | median_us_per_row | median_pipeline_bytes |
| --- | --- | --- | --- |
| knn | 0.046 | 333.063 | 34327.000 |
| logistic | 0.051 | 184.969 | 9407.000 |
| osec | 1.571 | 332.620 | 90504.000 |
| ovec | 0.511 | 518.978 | 1101566.000 |
| random_forest | 0.465 | 356.499 | 607062.000 |
| svm | 0.046 | 269.790 | 30011.000 |

Peak memory is not measured. Historical 70K timings are separated from this multi-dataset refit analysis.

## Software, tests, demo and reproducibility

The module inventory and dependency graph are machine generated from Python ASTs. Full pytest, Ruff, Python compilation, lockfile, manifest, metric/prediction and guarded offline demo checks are reported in `docs/FINAL_PROJECT_ACCEPTANCE_MATRIX.md` and `results/final_research_20261108/manifests/verification_manifest.json`. Raw datasets, access requests, checkpoints and row-level derived artifacts remain local and are not part of the release commit.

## Limitations and conclusion

The datasets are small and legacy; endpoint definitions differ across task families, Switzerland has only eight negatives, public files lack stable participant identifiers, and the primary CAD cohorts overlap Heart5 lineage. The original method cannot be reconstructed exactly from available notebooks. The full original ablation design, independent contemporary validation, peak-memory profiling, authorship/institution declarations and some data redistribution permissions remain unresolved. The current work supports reproducible algorithm comparisons on specified benchmark tasks and demonstrates that transfer and reliability degrade unevenly. It does not support clinical use, broad unseen-site generalization, universal OVEC/OSEC superiority or external validation.

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
