# CARDIODIAG Multi-Dataset Experimental Evaluation Report

- **Run:** `CARDIODIAG-MULTI-DATASET-20261108` / `20261107T202404Z`
- **Status:** `completed_with_failures`
- **Generated:** `2026-11-07T20:33:58.402580+00:00`
- **Branch:** `codex/multi-dataset-evaluation-2026-11-08`
**Evaluation scope:** 7 task datasets, 42 successful dataset–model summaries, 72 directed CAD cohort transfer results, 6 recorded failure rows.

## Executive summary

This report presents new, isolated experiments using the existing CARDIODIAG training-only preprocessing and unchanged OVEC/OSEC definitions. Four UCI angiographic cohorts were evaluated separately; each was already represented in the project’s Heart5 lineage, so these are retrospective cohort stress tests rather than independent validation. Heart-failure death, myocardial-infarction lethal outcome, and SPECT imaging normal/abnormal were kept as separate tasks and were not pooled or described as CAD validation.

Nested 3-fold outer / 3-fold inner evaluation was used where supported. SPECTF retained its official 80-record training and 187-record test split. Reported “best observed” models are descriptive maxima from this comparison; no superiority or clinical-use claim follows from those rankings. The uncertainty analysis is exploratory because cohorts are small, outcome definitions differ, and the class-stratified bootstrap conditions on observed class counts.

## Research objectives

1. Compare Logistic Regression, K-Nearest Neighbors, Support Vector Machine, Random Forest, OVEC, and OSEC under training-only preprocessing.
2. Measure discrimination, thresholded classification, calibration, conformal coverage, selective risk, learning behavior, and feature-support OOD diagnostics.
3. Test source-only transfer among the four feature-compatible angiographic cohorts without tuning on target labels.
4. Record provenance, cohort overlap screening, failed runs, and reproducibility metadata.

## Repository and methodology inspection

The repository’s established architecture includes `build_corrected_pipeline`, the fold-fitted `TrainingOnlyCleaner`, numeric median imputation/scaling, categorical most-frequent imputation/one-hot encoding, and pre-existing `build_ovec` / `build_osec` implementations. This experiment adds individual baseline builders while reusing the ensemble definitions. No feature-selection stage was added to this experiment because the established corrected pipeline used here does not require a selector. No SMOTE or pre-split balancing was applied. Existing historical result files and manuscript tables were left in place; all new outputs are under `results/multi_dataset_evaluation_20261108/` and this new report path.

OVEC uses the project’s existing soft-voting estimator with KNN, Random Forest, balanced Logistic Regression, and balanced SVC constituents. OSEC uses the existing stacking architecture and meta-classifier. The implementation and exact estimator definitions remain in `src/cardiodiag/models.py` and `src/cardiodiag/experiments.py`.

## Dataset descriptions, provenance, and compatibility

The four CAD tasks share the UCI Heart Disease 13-predictor schema and binary endpoint (`num=0` versus `num=1..4`, described by UCI as disease presence at greater than 50% diameter narrowing). Question marks were treated as missing; zero resting blood pressure and cholesterol were also treated as missing under the repository’s earlier protocol. Exact feature-row comparisons found no pairwise duplicates among the four prepared cohorts. This is only a record-matching screen: no participant identifiers establish person-level independence. The source cohorts are known components of the previously evaluated Heart5 composite.

SPECTF has 44 SPECT-derived predictors and a separate normal/abnormal imaging endpoint. It is not feature-compatible with the clinical CAD cohorts. Its source-defined training/test split was preserved; the test partition has 172 positive-coded and 15 negative-coded records, which makes operating characteristics and uncertainty estimates especially sensitive to a small minority count.

Heart Failure Clinical Records includes follow-up time in the source table; time was excluded from predictors and the event of death was used as the outcome. The cohort has varying follow-up horizons. MI Complications uses admission-available variables only; identifiers, post-admission features, and outcome proxies were excluded under the source timing audit. Its endpoint is any lethal complication. Neither is a CAD endpoint.

UCI sources: [Heart Disease (ID 45)](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease), [SPECTF Heart (ID 96)](https://archive.ics.uci.edu/dataset/96/spectf%2Bheart), [Heart Failure Clinical Records (ID 519)](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords), and [Myocardial Infarction Complications (ID 579)](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications). Their UCI dataset pages state CC BY 4.0; attribution is retained in the manifest. Dataset screening decisions are summarized below and fully represented in `dataset_comparison.csv`.

| Dataset | Records | Predictors | Target / task | Class counts | Missing cells | License/access | Lineage and compatibility | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UCI Heart Disease | 303 | 13 | UCI num=0 vs num=1..4; >50% stenosis as coded by UCI. | {"0": 164, "1": 139} | 6 | CC BY 4.0; attribution required | Legacy angiographic CAD cohort; retrospective source stress test. | Included as its own task; no cross-task pooling | included |
| UCI Heart Disease | 294 | 13 | UCI num=0 vs num=1..4; >50% stenosis as coded by UCI. | {"0": 188, "1": 106} | 782 | CC BY 4.0; attribution required | Legacy angiographic CAD cohort; retrospective source stress test. | Included as its own task; no cross-task pooling | included |
| UCI Heart Disease | 123 | 13 | UCI num=0 vs num=1..4; >50% stenosis as coded by UCI. | {"0": 8, "1": 115} | 396 | CC BY 4.0; attribution required | Legacy angiographic CAD cohort; retrospective source stress test. | Included as its own task; no cross-task pooling | included |
| UCI Heart Disease | 200 | 13 | UCI num=0 vs num=1..4; >50% stenosis as coded by UCI. | {"0": 51, "1": 149} | 748 | CC BY 4.0; attribution required | Legacy angiographic CAD cohort; retrospective source stress test. | Included as its own task; no cross-task pooling | included |
| UCI Heart Failure Clinical Records | 299 | 11 | Separate death-event task; varying follow-up horizons; not CAD validation. | {"0": 203, "1": 96} | 0 | CC BY 4.0; attribution required | Separate death-event task; varying follow-up horizons; not CAD validation. | Included as its own task; no cross-task pooling | included |
| UCI Myocardial Infarction Complications | 1700 | 100 | Separate MI lethal-outcome task; admission variables only; not CAD validation. | {"0": 1429, "1": 271} | 15200 | CC BY 4.0; attribution required | Separate MI lethal-outcome task; admission variables only; not CAD validation. | Included as its own task; no cross-task pooling | included |
| UCI SPECTF Heart | 267 | 44 | UCI OVERALL_DIAGNOSIS: 0/1 normal/abnormal SPECT classification. | {"0": 55, "1": 212} | 0 | CC BY 4.0; attribution required | Separate SPECT normal/abnormal task; official 80/187 split is retained. | Included as its own task; no cross-task pooling | included |
| UCI Statlog Heart | 270 | 13 | CAD classification; Cleveland-compatible labels | — | — | CC BY 4.0 | All 270 records match Cleveland after harmonization; duplicate cohort | Excluded from added evaluation | excluded_or_not_acquired |
| Mendeley Heart Disease 2026 | 918 | — | Binary target; composite lineage | — | — | CC BY 4.0 | Exact 918/918 labeled-row multiset match with Heart5; duplicate historical benchmark, not a new cohort | Excluded; prior benchmark only | excluded_or_not_acquired |
| Mendeley Cardiovascular 2021 | 1000 | — | Binary cardiovascular label | — | — | CC BY 4.0 per project source audit | No verified angiographic reference standard or predictor timing; previously examined | Excluded from new experiment | excluded_or_not_acquired |
| Z-Alizadeh Sani | 303 | 54 | CAD threshold >=50% | — | — | CC BY 4.0 | Previously examined; endpoint differs from UCI >50% rule; no patient linkage | Excluded from new run; historical transfer remains separate | excluded_or_not_acquired |
| AngioCAD | 413 | — | Coronary segment stenosis bins; 377 feature matches | — | — | CC BY 4.0; dataset and article attribution required | Previously examined; incomplete ID-feature matching and uncertain age/FBS units; post-hoc analyses | Excluded from new run; historical stress test remains separate | excluded_or_not_acquired |
| Duke ACATH | 3504 | — | Significant disease at >=75% stenosis | — | — | Provider permits use with attribution; redistribution terms unspecified | Endpoint mismatch versus UCI; previously examined | Excluded from new run; historical stress test remains separate | excluded_or_not_acquired |
| Cardio Train (Kaggle 70K) | 70000 | 11 | Distinct binary risk label | — | — | Dataset card reports license Unknown | Target and clinical timing not equivalent to angiographic CAD; license unresolved | Excluded | excluded_or_not_acquired |
| MIMIC-IV | — | — | Hospital EHR; derived task required | — | — | Credentialed access, training, and data-use agreement required | Access credentials and data-use agreement were not available in this run | Not acquired | excluded_or_not_acquired |
| MultiD4CAD | — | — | Multi-center CAD records | — | — | Controlled access; data-use agreement required | Controlled-access agreement was not acquired | Not acquired | excluded_or_not_acquired |

Statlog Heart was excluded because the project’s exact matching audit found all 270 harmonized records match Cleveland. Previously evaluated Mendeley, Z-Alizadeh Sani, AngioCAD, and Duke ACATH data were excluded from this new run to prevent post-hoc reuse from being presented as fresh evidence; their endpoint, provenance, measurement, or rights limits remain in prior project audits. The Kaggle 70K task has a distinct target and unresolved license. MIMIC-IV and MultiD4CAD require access steps or agreements not acquired for this run.

## Experimental design and preprocessing

For each supported task, the outer split is stratified 3-fold cross-validation (seed `20261108`). Within each outer training partition, 20% was held out for conformal and OOD threshold calibration. Hyperparameter selection used stratified 3-fold CV only on the remaining development rows. The untouched outer fold was scored once. The candidate grids and selected settings by fold are in `metrics/fold_metrics.csv` and `model_metrics.csv`.

Imputation, scaling, category encoding, and the established 1st/99th percentile training-only median replacement were fitted inside each pipeline. The held-out fold did not inform preprocessing, tuning, calibration, or thresholds. Cross-cohort experiments used source-only training, source-only inner CV, and source calibration; target features and labels were not used for selection. All 12 ordered source-to-target directions among the four compatible CAD cohorts were attempted for each model. These cohorts have matching feature schema and endpoint coding, but their known Heart5 lineage means the transfers are not independent external validations.

The individual baseline grids were Logistic Regression C ∈ {0.1, 1, 10}, KNN k ∈ {3, 5, 7} with uniform/distance weighting, SVM C ∈ {0.1, 1, 10} with linear/RBF kernels, and Random Forest with square-root/all-feature subsampling and leaf size 1/3. OVEC’s project configuration was fixed; OSEC’s existing final-estimator regularization parameter was selected from C ∈ {0.1, 1, 10}. See the experiment manifest for software versions and hashes.

## Main model comparison

The table reports the mean across outer folds and fold standard deviation. For SPECTF, the value comes from one official held-out test partition; no fold SD exists. Full fold-level results and confusion-matrix counts are in the machine-readable files.

| Dataset | Model | n | Accuracy | Precision | Recall | Specificity | F1 | ROC-AUC | PR-AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 303 | 0.809 ± 0.029 | 0.819 ± 0.033 | 0.748 ± 0.033 | 0.860 ± 0.029 | 0.782 ± 0.032 | 0.889 ± 0.031 | 0.873 ± 0.027 |
| UCI Cleveland | Logistic Regression | 303 | 0.812 ± 0.026 | 0.797 ± 0.054 | 0.798 ± 0.034 | 0.823 ± 0.066 | 0.796 ± 0.018 | 0.911 ± 0.031 | 0.909 ± 0.030 |
| UCI Cleveland | OSEC | 303 | 0.825 ± 0.055 | 0.829 ± 0.091 | 0.791 ± 0.033 | 0.853 ± 0.099 | 0.808 ± 0.047 | 0.903 ± 0.029 | 0.901 ± 0.024 |
| UCI Cleveland | OVEC | 303 | 0.818 ± 0.035 | 0.808 ± 0.063 | 0.799 ± 0.024 | 0.835 ± 0.067 | 0.802 ± 0.029 | 0.909 ± 0.033 | 0.902 ± 0.031 |
| UCI Cleveland | Random Forest | 303 | 0.802 ± 0.030 | 0.795 ± 0.071 | 0.777 ± 0.035 | 0.823 ± 0.084 | 0.783 ± 0.016 | 0.911 ± 0.032 | 0.902 ± 0.031 |
| UCI Cleveland | Support Vector Machine | 303 | 0.828 ± 0.049 | 0.822 ± 0.073 | 0.806 ± 0.019 | 0.847 ± 0.078 | 0.813 ± 0.043 | 0.909 ± 0.039 | 0.908 ± 0.031 |
| UCI Heart Failure | K-Nearest Neighbors | 299 | 0.685 ± 0.034 | 0.508 ± 0.125 | 0.229 ± 0.095 | 0.901 ± 0.009 | 0.314 ± 0.115 | 0.661 ± 0.020 | 0.457 ± 0.033 |
| UCI Heart Failure | Logistic Regression | 299 | 0.682 ± 0.046 | 0.508 ± 0.055 | 0.656 ± 0 | 0.695 ± 0.068 | 0.572 ± 0.036 | 0.735 ± 0.039 | 0.580 ± 0.073 |
| UCI Heart Failure | OSEC | 299 | 0.719 ± 0.033 | 0.554 ± 0.049 | 0.656 ± 0.054 | 0.749 ± 0.043 | 0.600 ± 0.044 | 0.736 ± 0.041 | 0.556 ± 0.018 |
| UCI Heart Failure | OVEC | 299 | 0.706 ± 0.015 | 0.559 ± 0.033 | 0.396 ± 0.036 | 0.852 ± 0.014 | 0.463 ± 0.033 | 0.752 ± 0.027 | 0.575 ± 0.024 |
| UCI Heart Failure | Random Forest | 299 | 0.696 ± 0.013 | 0.534 ± 0.019 | 0.396 ± 0.100 | 0.838 ± 0.038 | 0.450 ± 0.074 | 0.739 ± 0.037 | 0.544 ± 0.043 |
| UCI Heart Failure | Support Vector Machine | 299 | 0.679 ± 0.002 | 0 ± 0 | 0 ± 0 | 1 ± 0 | 0 ± 0 | 0.565 ± 0.324 | 0.455 ± 0.212 |
| UCI Hungary | K-Nearest Neighbors | 294 | 0.813 ± 0.021 | 0.790 ± 0.113 | 0.688 ± 0.106 | 0.882 ± 0.089 | 0.725 ± 0.018 | 0.876 ± 0.020 | 0.816 ± 0.039 |
| UCI Hungary | Logistic Regression | 294 | 0.793 ± 0.041 | 0.715 ± 0.086 | 0.735 ± 0.068 | 0.824 ± 0.091 | 0.720 ± 0.029 | 0.879 ± 0.040 | 0.822 ± 0.077 |
| UCI Hungary | OSEC | 294 | 0.806 ± 0.018 | 0.705 ± 0.034 | 0.802 ± 0.031 | 0.808 ± 0.044 | 0.749 ± 0.008 | 0.876 ± 0.031 | 0.821 ± 0.049 |
| UCI Hungary | OVEC | 294 | 0.799 ± 0.039 | 0.749 ± 0.087 | 0.688 ± 0.052 | 0.861 ± 0.077 | 0.713 ± 0.031 | 0.890 ± 0.033 | 0.837 ± 0.055 |
| UCI Hungary | Random Forest | 294 | 0.803 ± 0.046 | 0.748 ± 0.092 | 0.707 ± 0.093 | 0.856 ± 0.086 | 0.721 ± 0.053 | 0.880 ± 0.042 | 0.824 ± 0.062 |
| UCI Hungary | Support Vector Machine | 294 | 0.796 ± 0.047 | 0.759 ± 0.102 | 0.660 ± 0.052 | 0.872 ± 0.085 | 0.702 ± 0.043 | 0.877 ± 0.043 | 0.839 ± 0.057 |
| UCI MI Complications | K-Nearest Neighbors | 1700 | 0.851 ± 0.004 | 0.798 ± 0.189 | 0.096 ± 0.025 | 0.994 ± 0.006 | 0.169 ± 0.038 | 0.736 ± 0.023 | 0.415 ± 0.039 |
| UCI MI Complications | Logistic Regression | 1700 | 0.807 ± 0.010 | 0.438 ± 0.017 | 0.727 ± 0.026 | 0.822 ± 0.017 | 0.546 ± 0.008 | 0.854 ± 0.006 | 0.565 ± 0.030 |
| UCI MI Complications | OSEC | 1700 | 0.799 ± 0.007 | 0.428 ± 0.009 | 0.768 ± 0.021 | 0.805 ± 0.012 | 0.550 ± 0.003 | 0.868 ± 0.009 | 0.615 ± 0.014 |
| UCI MI Complications | OVEC | 1700 | 0.874 ± 0.006 | 0.686 ± 0.016 | 0.380 ± 0.039 | 0.967 ± 0.001 | 0.489 ± 0.036 | 0.866 ± 0.006 | 0.597 ± 0.011 |
| UCI MI Complications | Random Forest | 1700 | 0.869 ± 0.012 | 0.829 ± 0.064 | 0.236 ± 0.114 | 0.990 ± 0.009 | 0.356 ± 0.124 | 0.869 ± 0.008 | 0.625 ± 0.015 |
| UCI MI Complications | Support Vector Machine | 1700 | 0.862 ± 0.006 | 0.638 ± 0.054 | 0.321 ± 0.040 | 0.965 ± 0.010 | 0.426 ± 0.036 | 0.846 ± 0.017 | 0.537 ± 0.023 |
| UCI SPECTF Heart | K-Nearest Neighbors | 187 | 0.529 ± — | 0.988 ± — | 0.494 ± — | 0.933 ± — | 0.659 ± — | 0.729 ± — | 0.964 ± — |
| UCI SPECTF Heart | Logistic Regression | 187 | 0.738 ± — | 0.949 ± — | 0.756 ± — | 0.533 ± — | 0.841 ± — | 0.758 ± — | 0.975 ± — |
| UCI SPECTF Heart | OSEC | 187 | 0.733 ± — | 0.969 ± — | 0.733 ± — | 0.733 ± — | 0.834 ± — | 0.797 ± — | 0.980 ± — |
| UCI SPECTF Heart | OVEC | 187 | 0.749 ± — | 0.970 ± — | 0.750 ± — | 0.733 ± — | 0.846 ± — | 0.805 ± — | 0.980 ± — |
| UCI SPECTF Heart | Random Forest | 187 | 0.743 ± — | 0.956 ± — | 0.756 ± — | 0.600 ± — | 0.844 ± — | 0.796 ± — | 0.979 ± — |
| UCI SPECTF Heart | Support Vector Machine | 187 | 0.727 ± — | 0.948 ± — | 0.744 ± — | 0.533 ± — | 0.834 ± — | 0.788 ± — | 0.978 ± — |
| UCI Switzerland | K-Nearest Neighbors | 123 | 0.935 ± 0.014 | 0.935 ± 0.014 | 1 ± 0 | 0 ± 0 | 0.966 ± 0.007 | 0.530 ± 0.120 | 0.937 ± 0.026 |
| UCI Switzerland | Logistic Regression | 123 | 0.846 ± 0.061 | 0.938 ± 0.026 | 0.897 ± 0.092 | 0.167 ± 0.289 | 0.914 ± 0.038 | 0.772 ± 0.097 | 0.981 ± 0.011 |
| UCI Switzerland | OSEC | 123 | 0.902 ± 0.049 | 0.940 ± 0.030 | 0.956 ± 0.031 | 0.167 ± 0.289 | 0.948 ± 0.027 | 0.751 ± 0.183 | 0.976 ± 0.022 |
| UCI Switzerland | OVEC | 123 | 0.935 ± 0.014 | 0.935 ± 0.014 | 1 ± 0 | 0 ± 0 | 0.966 ± 0.007 | 0.732 ± 0.125 | 0.974 ± 0.017 |
| UCI Switzerland | Random Forest | 123 | 0.894 ± 0.037 | 0.941 ± 0.026 | 0.948 ± 0.068 | 0.167 ± 0.289 | 0.943 ± 0.022 | 0.736 ± 0.096 | 0.975 ± 0.015 |
| UCI Switzerland | Support Vector Machine | 123 | 0.935 ± 0.014 | 0.935 ± 0.014 | 1 ± 0 | 0 ± 0 | 0.966 ± 0.007 | 0.569 ± 0.312 | 0.945 ± 0.061 |
| UCI VA Long Beach | K-Nearest Neighbors | 200 | 0.715 ± 0.013 | 0.759 ± 0.008 | 0.906 ± 0.041 | 0.157 ± 0.068 | 0.826 ± 0.013 | 0.641 ± 0.046 | 0.815 ± 0.027 |
| UCI VA Long Beach | Logistic Regression | 200 | 0.610 ± 0.030 | 0.788 ± 0.008 | 0.651 ± 0.050 | 0.490 ± 0.034 | 0.713 ± 0.031 | 0.623 ± 0.026 | 0.812 ± 0.032 |
| UCI VA Long Beach | OSEC | 200 | 0.650 ± 0.061 | 0.845 ± 0.042 | 0.658 ± 0.143 | 0.627 ± 0.180 | 0.731 ± 0.080 | 0.612 ± 0.023 | 0.805 ± 0.027 |
| UCI VA Long Beach | OVEC | 200 | 0.720 ± 0.021 | 0.760 ± 0.012 | 0.913 ± 0.046 | 0.157 ± 0.090 | 0.829 ± 0.017 | 0.655 ± 0.041 | 0.818 ± 0.039 |
| UCI VA Long Beach | Random Forest | 200 | 0.730 ± 0.068 | 0.818 ± 0.017 | 0.819 ± 0.100 | 0.471 ± 0.059 | 0.817 ± 0.055 | 0.679 ± 0.037 | 0.838 ± 0.027 |
| UCI VA Long Beach | Support Vector Machine | 200 | 0.755 ± 0.008 | 0.753 ± 0.006 | 1 ± 0 | 0.039 ± 0.034 | 0.859 ± 0.004 | 0.633 ± 0.036 | 0.816 ± 0.026 |

### Highest observed ROC-AUC by task

| Dataset | Highest observed model | n | ROC-AUC mean | Fold SD | PR-AUC mean | Protocol |
| --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | Random Forest | 303 | 0.911 | 0.032 | 0.902 | 3x3 nested stratified CV |
| UCI Heart Failure | OVEC | 299 | 0.752 | 0.027 | 0.575 | 3x3 nested stratified CV |
| UCI Hungary | OVEC | 294 | 0.890 | 0.033 | 0.837 | 3x3 nested stratified CV |
| UCI MI Complications | Random Forest | 1700 | 0.869 | 0.008 | 0.625 | 3x3 nested stratified CV |
| UCI SPECTF Heart | OVEC | 187 | 0.805 | — | 0.980 | official 80/187 source split |
| UCI Switzerland | Logistic Regression | 123 | 0.772 | 0.097 | 0.981 | 3x3 nested stratified CV |
| UCI VA Long Beach | Random Forest | 200 | 0.679 | 0.037 | 0.838 | 3x3 nested stratified CV |

These are descriptive rankings on the evaluated partitions. They do not establish that an ensemble is better than an individual model, and they are not evidence of clinical utility.

## OVEC versus OSEC

| Dataset | OVEC ROC-AUC | OSEC ROC-AUC | OVEC − OSEC |
| --- | --- | --- | --- |
| UCI Cleveland | 0.909 | 0.903 | 0.006 |
| UCI Heart Failure | 0.752 | 0.736 | 0.016 |
| UCI Hungary | 0.890 | 0.876 | 0.014 |
| UCI MI Complications | 0.866 | 0.868 | -0.001 |
| UCI SPECTF Heart | 0.805 | 0.797 | 0.009 |
| UCI Switzerland | 0.732 | 0.751 | -0.018 |
| UCI VA Long Beach | 0.655 | 0.612 | 0.043 |

The sign of `OVEC − OSEC` varies by task where both estimates exist. Differences are small-sample, descriptive comparisons, not significance tests. If an entry is missing, the corresponding model did not complete and appears in the failure table.

## Overfitting and learning behavior

Training resubstitution scores are measured on the development subset used to fit the selected pipeline; selected inner-CV scores are tuning-stage validation estimates; outer-test scores are the held-out estimates. The differences are diagnostic and not independent comparisons. A positive train–test gap alone does not prove overfitting. The 3-fold learning curves use fixed default estimators and are descriptive, not part of hyperparameter selection.

| Dataset | Model | Train resub. AUC | Inner CV AUC | Outer/official AUC | Train − test | Selected CV − test |
| --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 1 | 0.899 | 0.889 | 0.111 | 0.010 |
| UCI Cleveland | Logistic Regression | 0.950 | 0.919 | 0.911 | 0.039 | 0.008 |
| UCI Cleveland | OSEC | 0.960 | 0.910 | 0.903 | 0.057 | 0.008 |
| UCI Cleveland | OVEC | 0.989 | 0.916 | 0.909 | 0.081 | 0.007 |
| UCI Cleveland | Random Forest | 0.991 | 0.916 | 0.911 | 0.081 | 0.005 |
| UCI Cleveland | Support Vector Machine | 0.958 | 0.912 | 0.909 | 0.049 | 0.003 |
| UCI Heart Failure | K-Nearest Neighbors | 0.936 | 0.640 | 0.661 | 0.275 | -0.021 |
| UCI Heart Failure | Logistic Regression | 0.774 | 0.660 | 0.735 | 0.039 | -0.075 |
| UCI Heart Failure | OSEC | 0.919 | 0.681 | 0.736 | 0.183 | -0.055 |
| UCI Heart Failure | OVEC | 0.972 | 0.686 | 0.752 | 0.220 | -0.066 |
| UCI Heart Failure | Random Forest | 1 | 0.725 | 0.739 | 0.261 | -0.014 |
| UCI Heart Failure | Support Vector Machine | 0.624 | 0.707 | 0.565 | 0.059 | 0.142 |
| UCI Hungary | K-Nearest Neighbors | 0.968 | 0.871 | 0.876 | 0.092 | -0.005 |
| UCI Hungary | Logistic Regression | 0.932 | 0.883 | 0.879 | 0.053 | 0.004 |
| UCI Hungary | OSEC | 0.926 | 0.875 | 0.876 | 0.051 | -0.000 |
| UCI Hungary | OVEC | 0.981 | 0.887 | 0.890 | 0.091 | -0.002 |
| UCI Hungary | Random Forest | 0.972 | 0.891 | 0.880 | 0.092 | 0.011 |
| UCI Hungary | Support Vector Machine | 0.934 | 0.891 | 0.877 | 0.058 | 0.015 |
| UCI MI Complications | K-Nearest Neighbors | 1 | 0.738 | 0.736 | 0.264 | 0.003 |
| UCI MI Complications | Logistic Regression | 0.925 | 0.847 | 0.854 | 0.071 | -0.007 |
| UCI MI Complications | OSEC | 0.948 | 0.855 | 0.868 | 0.080 | -0.013 |
| UCI MI Complications | OVEC | 0.997 | 0.861 | 0.866 | 0.131 | -0.006 |
| UCI MI Complications | Random Forest | 1.000 | 0.860 | 0.869 | 0.130 | -0.010 |
| UCI MI Complications | Support Vector Machine | 0.999 | 0.850 | 0.846 | 0.154 | 0.004 |
| UCI SPECTF Heart | K-Nearest Neighbors | 0.854 | 0.645 | 0.729 | 0.126 | -0.083 |
| UCI SPECTF Heart | Logistic Regression | 0.994 | 0.928 | 0.758 | 0.236 | 0.170 |
| UCI SPECTF Heart | OSEC | 0.993 | 0.850 | 0.797 | 0.197 | 0.054 |
| UCI SPECTF Heart | OVEC | 1 | 0.881 | 0.805 | 0.195 | 0.076 |
| UCI SPECTF Heart | Random Forest | 1 | 0.816 | 0.796 | 0.204 | 0.020 |
| UCI SPECTF Heart | Support Vector Machine | 0.998 | 0.821 | 0.788 | 0.210 | 0.033 |
| UCI Switzerland | K-Nearest Neighbors | 0.923 | 0.553 | 0.530 | 0.393 | 0.023 |
| UCI Switzerland | Logistic Regression | 0.990 | 0.702 | 0.772 | 0.218 | -0.070 |
| UCI Switzerland | OSEC | 0.333 | 0.532 | 0.751 | -0.417 | -0.218 |
| UCI Switzerland | OVEC | 1 | 0.646 | 0.732 | 0.268 | -0.086 |
| UCI Switzerland | Random Forest | 0.994 | 0.758 | 0.736 | 0.259 | 0.022 |
| UCI Switzerland | Support Vector Machine | 0.662 | 0.746 | 0.569 | 0.093 | 0.177 |
| UCI VA Long Beach | K-Nearest Neighbors | 1 | 0.664 | 0.641 | 0.359 | 0.024 |
| UCI VA Long Beach | Logistic Regression | 0.834 | 0.684 | 0.623 | 0.211 | 0.060 |
| UCI VA Long Beach | OSEC | 0.752 | 0.532 | 0.612 | 0.140 | -0.080 |
| UCI VA Long Beach | OVEC | 0.982 | 0.661 | 0.655 | 0.328 | 0.006 |
| UCI VA Long Beach | Random Forest | 0.982 | 0.687 | 0.679 | 0.303 | 0.008 |
| UCI VA Long Beach | Support Vector Machine | 0.932 | 0.709 | 0.633 | 0.299 | 0.076 |

Learning curves are saved as vector PDF and PNG and as the per-size CSV in `metrics/learning_curve_metrics.csv`. They can reveal high training / lower validation performance or data-limited behavior, but the small cohorts do not support strong asymptotic learning claims.

## Calibration and uncertainty

Brier score and two ten-bin ECE variants are computed from pooled held-out predictions. “Uniform” ECE denotes equal-width probability bins; weighted ECE weights occupied bins by their sample share. Calibration bins are included in `metrics/calibration_bins.csv`.

Split-conformal prediction uses nonconformity `1 − p(true class)` and a finite-sample 90% threshold from the held-out calibration partition in each outer fold. Coverage and set size are reported as empirical values. Exchangeability between calibration and evaluation data is an assumption; it is not assured across sites or time.

| Dataset | Model | Pooled Brier | ECE, uniform bins | Weighted ECE | Mean conformal coverage | Mean set size | Singleton rate | OOD alert rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 0.131 | 0.080 | 0.068 | 0.931 | 1.290 | 0.710 | 0.050 |
| UCI Cleveland | Logistic Regression | 0.121 | 0.082 | 0.054 | 0.927 | 1.254 | 0.746 | 0.050 |
| UCI Cleveland | OSEC | 0.129 | 0.129 | 0.083 | 0.914 | 1.254 | 0.746 | 0.050 |
| UCI Cleveland | OVEC | 0.120 | 0.069 | 0.050 | 0.911 | 1.228 | 0.772 | 0.050 |
| UCI Cleveland | Random Forest | 0.126 | 0.070 | 0.071 | 0.911 | 1.241 | 0.759 | 0.050 |
| UCI Cleveland | Support Vector Machine | 0.120 | 0.085 | 0.055 | 0.894 | 1.201 | 0.799 | 0.050 |
| UCI Heart Failure | K-Nearest Neighbors | 0.215 | 0.139 | 0.090 | 0.896 | 1.548 | 0.452 | 0.043 |
| UCI Heart Failure | Logistic Regression | 0.210 | 0.187 | 0.150 | 0.890 | 1.535 | 0.465 | 0.043 |
| UCI Heart Failure | OSEC | 0.219 | 0.183 | 0.173 | 0.893 | 1.585 | 0.415 | 0.043 |
| UCI Heart Failure | OVEC | 0.184 | 0.085 | 0.051 | 0.893 | 1.418 | 0.582 | 0.043 |
| UCI Heart Failure | Random Forest | 0.191 | 0.096 | 0.074 | 0.896 | 1.444 | 0.556 | 0.043 |
| UCI Heart Failure | Support Vector Machine | 0.215 | 0.082 | 0.067 | 0.910 | 1.616 | 0.384 | 0.043 |
| UCI Hungary | K-Nearest Neighbors | 0.135 | 0.083 | 0.074 | 0.888 | 1.173 | 0.820 | 0.041 |
| UCI Hungary | Logistic Regression | 0.142 | 0.086 | 0.078 | 0.918 | 1.296 | 0.704 | 0.041 |
| UCI Hungary | OSEC | 0.139 | 0.123 | 0.091 | 0.908 | 1.296 | 0.704 | 0.041 |
| UCI Hungary | OVEC | 0.131 | 0.100 | 0.060 | 0.884 | 1.156 | 0.844 | 0.041 |
| UCI Hungary | Random Forest | 0.139 | 0.059 | 0.053 | 0.881 | 1.190 | 0.810 | 0.041 |
| UCI Hungary | Support Vector Machine | 0.140 | 0.050 | 0.037 | 0.891 | 1.194 | 0.806 | 0.041 |
| UCI MI Complications | K-Nearest Neighbors | 0.119 | 0.108 | 0.069 | 0.916 | 1.174 | 0.826 | 0.039 |
| UCI MI Complications | Logistic Regression | 0.140 | 0.249 | 0.160 | 0.911 | 1.270 | 0.730 | 0.039 |
| UCI MI Complications | OSEC | 0.147 | 0.250 | 0.212 | 0.916 | 1.347 | 0.653 | 0.039 |
| UCI MI Complications | OVEC | 0.095 | 0.069 | 0.034 | 0.920 | 1.115 | 0.885 | 0.039 |
| UCI MI Complications | Random Forest | 0.099 | 0.119 | 0.047 | 0.905 | 1.086 | 0.914 | 0.039 |
| UCI MI Complications | Support Vector Machine | 0.101 | 0.056 | 0.017 | 0.922 | 1.157 | 0.843 | 0.039 |
| UCI SPECTF Heart | K-Nearest Neighbors | 0.329 | 0.425 | 0.455 | 1 | 2 | 0 | 0.005 |
| UCI SPECTF Heart | Logistic Regression | 0.168 | 0.339 | 0.233 | 0.925 | 1.428 | 0.572 | 0.032 |
| UCI SPECTF Heart | OSEC | 0.174 | 0.334 | 0.274 | 1 | 1.561 | 0.439 | 0.021 |
| UCI SPECTF Heart | OVEC | 0.193 | 0.398 | 0.312 | 0.861 | 1.348 | 0.652 | 0.374 |
| UCI SPECTF Heart | Random Forest | 0.170 | 0.320 | 0.298 | 0.791 | 1.128 | 0.872 | 0.005 |
| UCI SPECTF Heart | Support Vector Machine | 0.179 | 0.383 | 0.271 | 0.818 | 1.182 | 0.818 | 0.032 |
| UCI Switzerland | K-Nearest Neighbors | 0.070 | 0.146 | 0.082 | 0.976 | 1.496 | 0.504 | 0.195 |
| UCI Switzerland | Logistic Regression | 0.109 | 0.428 | 0.118 | 0.951 | 1.285 | 0.667 | 0.195 |
| UCI Switzerland | OSEC | 0.145 | 0.308 | 0.286 | 0.976 | 1.846 | 0.154 | 0.195 |
| UCI Switzerland | OVEC | 0.062 | 0.226 | 0.036 | 0.959 | 1.154 | 0.846 | 0.195 |
| UCI Switzerland | Random Forest | 0.077 | 0.264 | 0.056 | 0.967 | 1.268 | 0.732 | 0.195 |
| UCI Switzerland | Support Vector Machine | 0.062 | 0.044 | 0.017 | 0.976 | 1.439 | 0.561 | 0.195 |
| UCI VA Long Beach | K-Nearest Neighbors | 0.205 | 0.223 | 0.117 | 0.970 | 1.843 | 0.157 | 0.055 |
| UCI VA Long Beach | Logistic Regression | 0.235 | 0.241 | 0.195 | 0.900 | 1.659 | 0.341 | 0.055 |
| UCI VA Long Beach | OSEC | 0.236 | 0.194 | 0.216 | 0.925 | 1.770 | 0.230 | 0.055 |
| UCI VA Long Beach | OVEC | 0.182 | 0.160 | 0.083 | 0.945 | 1.595 | 0.405 | 0.055 |
| UCI VA Long Beach | Random Forest | 0.189 | 0.192 | 0.128 | 0.935 | 1.596 | 0.404 | 0.055 |
| UCI VA Long Beach | Support Vector Machine | 0.182 | 0.157 | 0.047 | 0.950 | 1.645 | 0.355 | 0.055 |

| Dataset | Model | Empirical coverage | Average set size | Singleton fraction |
| --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 0.931 | 1.290 | 0.710 |
| UCI Cleveland | Logistic Regression | 0.927 | 1.254 | 0.746 |
| UCI Cleveland | OSEC | 0.914 | 1.254 | 0.746 |
| UCI Cleveland | OVEC | 0.911 | 1.228 | 0.772 |
| UCI Cleveland | Random Forest | 0.911 | 1.241 | 0.759 |
| UCI Cleveland | Support Vector Machine | 0.894 | 1.201 | 0.799 |
| UCI Heart Failure | K-Nearest Neighbors | 0.896 | 1.548 | 0.452 |
| UCI Heart Failure | Logistic Regression | 0.890 | 1.535 | 0.465 |
| UCI Heart Failure | OSEC | 0.893 | 1.585 | 0.415 |
| UCI Heart Failure | OVEC | 0.893 | 1.418 | 0.582 |
| UCI Heart Failure | Random Forest | 0.896 | 1.444 | 0.556 |
| UCI Heart Failure | Support Vector Machine | 0.910 | 1.616 | 0.384 |
| UCI Hungary | K-Nearest Neighbors | 0.888 | 1.173 | 0.820 |
| UCI Hungary | Logistic Regression | 0.918 | 1.296 | 0.704 |
| UCI Hungary | OSEC | 0.908 | 1.296 | 0.704 |
| UCI Hungary | OVEC | 0.884 | 1.156 | 0.844 |
| UCI Hungary | Random Forest | 0.881 | 1.190 | 0.810 |
| UCI Hungary | Support Vector Machine | 0.891 | 1.194 | 0.806 |
| UCI MI Complications | K-Nearest Neighbors | 0.916 | 1.174 | 0.826 |
| UCI MI Complications | Logistic Regression | 0.911 | 1.270 | 0.730 |
| UCI MI Complications | OSEC | 0.916 | 1.347 | 0.653 |
| UCI MI Complications | OVEC | 0.920 | 1.115 | 0.885 |
| UCI MI Complications | Random Forest | 0.905 | 1.086 | 0.914 |
| UCI MI Complications | Support Vector Machine | 0.922 | 1.157 | 0.843 |
| UCI SPECTF Heart | K-Nearest Neighbors | 1 | 2 | 0 |
| UCI SPECTF Heart | Logistic Regression | 0.925 | 1.428 | 0.572 |
| UCI SPECTF Heart | OSEC | 1 | 1.561 | 0.439 |
| UCI SPECTF Heart | OVEC | 0.861 | 1.348 | 0.652 |
| UCI SPECTF Heart | Random Forest | 0.791 | 1.128 | 0.872 |
| UCI SPECTF Heart | Support Vector Machine | 0.818 | 1.182 | 0.818 |
| UCI Switzerland | K-Nearest Neighbors | 0.976 | 1.496 | 0.504 |
| UCI Switzerland | Logistic Regression | 0.951 | 1.285 | 0.667 |
| UCI Switzerland | OSEC | 0.976 | 1.846 | 0.154 |
| UCI Switzerland | OVEC | 0.959 | 1.154 | 0.846 |
| UCI Switzerland | Random Forest | 0.967 | 1.268 | 0.732 |
| UCI Switzerland | Support Vector Machine | 0.976 | 1.439 | 0.561 |
| UCI VA Long Beach | K-Nearest Neighbors | 0.970 | 1.843 | 0.157 |
| UCI VA Long Beach | Logistic Regression | 0.900 | 1.659 | 0.341 |
| UCI VA Long Beach | OSEC | 0.925 | 1.770 | 0.230 |
| UCI VA Long Beach | OVEC | 0.945 | 1.595 | 0.405 |
| UCI VA Long Beach | Random Forest | 0.935 | 1.596 | 0.404 |
| UCI VA Long Beach | Support Vector Machine | 0.950 | 1.645 | 0.355 |

## Selective prediction and OOD diagnostics

Confidence-ranked risk–coverage curves retain the most confident predictions at each coverage level. The OOD score is mean distance to the five nearest development observations after the fitted feature transformation; its alert cutoff is the 95th percentile of source calibration scores. This is a simple feature-support diagnostic. It is not a validated shift detector or safety gate. Within-task alert/error associations and source-to-target domain discrimination are summarized below and in `metrics/ood_diagnostics.csv` / `cross_dataset_metrics.csv`.

| Dataset | Model | Alert rate | Overall error rate | Error rate if alerted | Error rate if unflagged | Error capture | OOD score / error AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 0.050 | 0.191 | 0.133 | 0.194 | 0.034 | 0.608 |
| UCI Cleveland | Logistic Regression | 0.050 | 0.188 | 0.133 | 0.191 | 0.035 | 0.621 |
| UCI Cleveland | OSEC | 0.050 | 0.175 | 0.133 | 0.177 | 0.038 | 0.595 |
| UCI Cleveland | OVEC | 0.050 | 0.182 | 0.133 | 0.184 | 0.036 | 0.583 |
| UCI Cleveland | Random Forest | 0.050 | 0.198 | 0.200 | 0.198 | 0.050 | 0.612 |
| UCI Cleveland | Support Vector Machine | 0.050 | 0.172 | 0.067 | 0.177 | 0.019 | 0.575 |
| UCI Heart Failure | K-Nearest Neighbors | 0.043 | 0.314 | 0.538 | 0.304 | 0.074 | 0.628 |
| UCI Heart Failure | Logistic Regression | 0.043 | 0.318 | 0.615 | 0.304 | 0.084 | 0.572 |
| UCI Heart Failure | OSEC | 0.043 | 0.281 | 0.692 | 0.262 | 0.107 | 0.572 |
| UCI Heart Failure | OVEC | 0.043 | 0.294 | 0.692 | 0.276 | 0.102 | 0.618 |
| UCI Heart Failure | Random Forest | 0.043 | 0.304 | 0.538 | 0.294 | 0.077 | 0.597 |
| UCI Heart Failure | Support Vector Machine | 0.043 | 0.321 | 0.538 | 0.311 | 0.073 | 0.652 |
| UCI Hungary | K-Nearest Neighbors | 0.041 | 0.187 | 0.167 | 0.188 | 0.036 | 0.593 |
| UCI Hungary | Logistic Regression | 0.041 | 0.207 | 0.333 | 0.202 | 0.066 | 0.566 |
| UCI Hungary | OSEC | 0.041 | 0.194 | 0.250 | 0.191 | 0.053 | 0.535 |
| UCI Hungary | OVEC | 0.041 | 0.201 | 0.417 | 0.191 | 0.085 | 0.582 |
| UCI Hungary | Random Forest | 0.041 | 0.197 | 0.500 | 0.184 | 0.103 | 0.603 |
| UCI Hungary | Support Vector Machine | 0.041 | 0.204 | 0.583 | 0.188 | 0.117 | 0.606 |
| UCI MI Complications | K-Nearest Neighbors | 0.039 | 0.149 | 0.379 | 0.140 | 0.098 | 0.735 |
| UCI MI Complications | Logistic Regression | 0.039 | 0.193 | 0.379 | 0.185 | 0.076 | 0.672 |
| UCI MI Complications | OSEC | 0.039 | 0.201 | 0.394 | 0.193 | 0.076 | 0.659 |
| UCI MI Complications | OVEC | 0.039 | 0.126 | 0.258 | 0.121 | 0.079 | 0.692 |
| UCI MI Complications | Random Forest | 0.039 | 0.131 | 0.258 | 0.125 | 0.077 | 0.701 |
| UCI MI Complications | Support Vector Machine | 0.039 | 0.138 | 0.318 | 0.130 | 0.090 | 0.699 |
| UCI SPECTF Heart | K-Nearest Neighbors | 0.005 | 0.471 | 0 | 0.473 | 0 | 0.204 |
| UCI SPECTF Heart | Logistic Regression | 0.032 | 0.262 | 0 | 0.271 | 0 | 0.151 |
| UCI SPECTF Heart | OSEC | 0.021 | 0.267 | 0 | 0.273 | 0 | 0.142 |
| UCI SPECTF Heart | OVEC | 0.374 | 0.251 | 0.029 | 0.385 | 0.043 | 0.158 |
| UCI SPECTF Heart | Random Forest | 0.005 | 0.257 | 0 | 0.258 | 0 | 0.147 |
| UCI SPECTF Heart | Support Vector Machine | 0.032 | 0.273 | 0 | 0.282 | 0 | 0.118 |
| UCI Switzerland | K-Nearest Neighbors | 0.195 | 0.065 | 0.042 | 0.071 | 0.125 | 0.634 |
| UCI Switzerland | Logistic Regression | 0.195 | 0.154 | 0.167 | 0.152 | 0.211 | 0.601 |
| UCI Switzerland | OSEC | 0.195 | 0.098 | 0.042 | 0.111 | 0.083 | 0.506 |
| UCI Switzerland | OVEC | 0.195 | 0.065 | 0.042 | 0.071 | 0.125 | 0.634 |
| UCI Switzerland | Random Forest | 0.195 | 0.106 | 0.125 | 0.101 | 0.231 | 0.579 |
| UCI Switzerland | Support Vector Machine | 0.195 | 0.065 | 0.042 | 0.071 | 0.125 | 0.634 |
| UCI VA Long Beach | K-Nearest Neighbors | 0.055 | 0.285 | 0.455 | 0.275 | 0.088 | 0.522 |
| UCI VA Long Beach | Logistic Regression | 0.055 | 0.390 | 0.636 | 0.376 | 0.090 | 0.500 |
| UCI VA Long Beach | OSEC | 0.055 | 0.350 | 0.636 | 0.333 | 0.100 | 0.458 |
| UCI VA Long Beach | OVEC | 0.055 | 0.280 | 0.455 | 0.270 | 0.089 | 0.541 |
| UCI VA Long Beach | Random Forest | 0.055 | 0.270 | 0.545 | 0.254 | 0.111 | 0.469 |
| UCI VA Long Beach | Support Vector Machine | 0.055 | 0.245 | 0.455 | 0.233 | 0.102 | 0.545 |

Combined singleton-conformal and in-support accepted predictions are also reported:

| Dataset | Model | Confidence AURC | Risk at 80% coverage | Singleton + OOD accepted n | Accepted coverage | Accepted error rate |
| --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | K-Nearest Neighbors | 0.083 | 0.128 | 206 | 0.680 | 0.102 |
| UCI Cleveland | Logistic Regression | 0.066 | 0.107 | 214 | 0.706 | 0.103 |
| UCI Cleveland | OSEC | 0.073 | 0.128 | 215 | 0.710 | 0.116 |
| UCI Cleveland | OVEC | 0.061 | 0.103 | 223 | 0.736 | 0.121 |
| UCI Cleveland | Random Forest | 0.063 | 0.119 | 220 | 0.726 | 0.123 |
| UCI Cleveland | Support Vector Machine | 0.062 | 0.103 | 231 | 0.762 | 0.139 |
| UCI Heart Failure | K-Nearest Neighbors | 0.215 | 0.287 | 129 | 0.431 | 0.202 |
| UCI Heart Failure | Logistic Regression | 0.216 | 0.267 | 129 | 0.431 | 0.209 |
| UCI Heart Failure | OSEC | 0.244 | 0.250 | 115 | 0.385 | 0.217 |
| UCI Heart Failure | OVEC | 0.155 | 0.250 | 166 | 0.555 | 0.163 |
| UCI Heart Failure | Random Forest | 0.164 | 0.258 | 161 | 0.538 | 0.174 |
| UCI Heart Failure | Support Vector Machine | 0.224 | 0.312 | 114 | 0.381 | 0.228 |
| UCI Hungary | K-Nearest Neighbors | 0.077 | 0.123 | 233 | 0.793 | 0.129 |
| UCI Hungary | Logistic Regression | 0.096 | 0.140 | 203 | 0.690 | 0.113 |
| UCI Hungary | OSEC | 0.115 | 0.131 | 200 | 0.680 | 0.125 |
| UCI Hungary | OVEC | 0.077 | 0.119 | 241 | 0.820 | 0.137 |
| UCI Hungary | Random Forest | 0.082 | 0.148 | 231 | 0.786 | 0.143 |
| UCI Hungary | Support Vector Machine | 0.093 | 0.136 | 230 | 0.782 | 0.126 |
| UCI MI Complications | K-Nearest Neighbors | 0.064 | 0.096 | 1375 | 0.809 | 0.099 |
| UCI MI Complications | Logistic Regression | 0.093 | 0.142 | 1186 | 0.698 | 0.112 |
| UCI MI Complications | OSEC | 0.105 | 0.153 | 1061 | 0.624 | 0.120 |
| UCI MI Complications | OVEC | 0.037 | 0.069 | 1462 | 0.860 | 0.087 |
| UCI MI Complications | Random Forest | 0.042 | 0.079 | 1505 | 0.885 | 0.099 |
| UCI MI Complications | Support Vector Machine | 0.045 | 0.083 | 1406 | 0.827 | 0.089 |
| UCI SPECTF Heart | K-Nearest Neighbors | 0.452 | 0.507 | 0 | 0 | — |
| UCI SPECTF Heart | Logistic Regression | 0.108 | 0.227 | 101 | 0.540 | 0.139 |
| UCI SPECTF Heart | OSEC | 0.107 | 0.220 | 79 | 0.422 | 0 |
| UCI SPECTF Heart | OVEC | 0.183 | 0.253 | 60 | 0.321 | 0.433 |
| UCI SPECTF Heart | Random Forest | 0.115 | 0.213 | 162 | 0.866 | 0.241 |
| UCI SPECTF Heart | Support Vector Machine | 0.162 | 0.227 | 147 | 0.786 | 0.231 |
| UCI Switzerland | K-Nearest Neighbors | 0.043 | 0.071 | 53 | 0.431 | 0.057 |
| UCI Switzerland | Logistic Regression | 0.037 | 0.061 | 68 | 0.553 | 0.044 |
| UCI Switzerland | OSEC | 0.055 | 0.071 | 17 | 0.138 | 0.176 |
| UCI Switzerland | OVEC | 0.036 | 0.051 | 87 | 0.707 | 0.057 |
| UCI Switzerland | Random Forest | 0.030 | 0.051 | 78 | 0.634 | 0.051 |
| UCI Switzerland | Support Vector Machine | 0.052 | 0.071 | 52 | 0.423 | 0.058 |
| UCI VA Long Beach | K-Nearest Neighbors | 0.178 | 0.231 | 31 | 0.155 | 0.194 |
| UCI VA Long Beach | Logistic Regression | 0.271 | 0.325 | 61 | 0.305 | 0.246 |
| UCI VA Long Beach | OSEC | 0.315 | 0.369 | 41 | 0.205 | 0.293 |
| UCI VA Long Beach | OVEC | 0.168 | 0.194 | 76 | 0.380 | 0.118 |
| UCI VA Long Beach | Random Forest | 0.166 | 0.237 | 75 | 0.375 | 0.133 |
| UCI VA Long Beach | Support Vector Machine | 0.176 | 0.237 | 67 | 0.335 | 0.119 |

The alert rate is determined without target labels, while error capture and error rates use labels only for retrospective scoring. Small or zero accepted groups should not be interpreted as a safe operating point. All risk–coverage coordinates are in `metrics/selective_prediction_metrics.csv`.

## Cross-dataset evaluation

The following table shows each directed transfer. Selection, preprocessing, and calibration were source-only; target labels were used only to calculate final metrics. The class-stratified percentile intervals use 1,000 bootstrap replicates over target predictions and condition on observed class counts. Because observations come from small, historical source files and patient linkage cannot be checked, intervals are descriptive rather than population-level uncertainty estimates. No p-values or fold-level significance claims are made.

| Source | Target | Model | Target n | ROC-AUC | PR-AUC | ROC-AUC CI low | ROC-AUC CI high | OOD alert rate | Domain OOD AUROC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UCI Cleveland | UCI Hungary | K-Nearest Neighbors | 294 | 0.873 | 0.829 | 0.830 | 0.921 | 0.061 | 0.456 |
| UCI Cleveland | UCI Hungary | Logistic Regression | 294 | 0.884 | 0.838 | 0.839 | 0.921 | 0.075 | 0.481 |
| UCI Cleveland | UCI Hungary | OSEC | 294 | 0.859 | 0.808 | 0.804 | 0.907 | 0.058 | 0.548 |
| UCI Cleveland | UCI Hungary | OVEC | 294 | 0.902 | 0.848 | 0.861 | 0.938 | 0.051 | 0.419 |
| UCI Cleveland | UCI Hungary | Random Forest | 294 | 0.903 | 0.857 | 0.865 | 0.941 | 0.061 | 0.519 |
| UCI Cleveland | UCI Hungary | Support Vector Machine | 294 | 0.893 | 0.854 | 0.850 | 0.931 | 0.136 | 0.494 |
| UCI Cleveland | UCI Switzerland | K-Nearest Neighbors | 123 | 0.639 | 0.949 | 0.399 | 0.850 | 0.089 | 0.628 |
| UCI Cleveland | UCI Switzerland | Logistic Regression | 123 | 0.733 | 0.973 | 0.537 | 0.903 | 0.016 | 0.559 |
| UCI Cleveland | UCI Switzerland | OSEC | 123 | 0.697 | 0.971 | 0.521 | 0.863 | 0.024 | 0.512 |
| UCI Cleveland | UCI Switzerland | OVEC | 123 | 0.729 | 0.973 | 0.540 | 0.898 | 0.033 | 0.578 |
| UCI Cleveland | UCI Switzerland | Random Forest | 123 | 0.741 | 0.975 | 0.533 | 0.900 | 0.008 | 0.512 |
| UCI Cleveland | UCI Switzerland | Support Vector Machine | 123 | 0.741 | 0.975 | 0.558 | 0.913 | 0.098 | 0.572 |
| UCI Cleveland | UCI VA Long Beach | K-Nearest Neighbors | 200 | 0.709 | 0.863 | 0.631 | 0.787 | 0.165 | 0.660 |
| UCI Cleveland | UCI VA Long Beach | Logistic Regression | 200 | 0.724 | 0.854 | 0.637 | 0.805 | 0.125 | 0.765 |
| UCI Cleveland | UCI VA Long Beach | OSEC | 200 | 0.692 | 0.852 | 0.602 | 0.776 | 0.215 | 0.735 |
| UCI Cleveland | UCI VA Long Beach | OVEC | 200 | 0.733 | 0.866 | 0.650 | 0.815 | 0.070 | 0.708 |
| UCI Cleveland | UCI VA Long Beach | Random Forest | 200 | 0.729 | 0.856 | 0.647 | 0.810 | 0.095 | 0.691 |
| UCI Cleveland | UCI VA Long Beach | Support Vector Machine | 200 | 0.727 | 0.863 | 0.645 | 0.801 | 0.105 | 0.661 |
| UCI Hungary | UCI Cleveland | K-Nearest Neighbors | 303 | 0.820 | 0.811 | 0.770 | 0.867 | 0.386 | 0.879 |
| UCI Hungary | UCI Cleveland | Logistic Regression | 303 | 0.839 | 0.812 | 0.790 | 0.882 | 0.551 | 0.914 |
| UCI Hungary | UCI Cleveland | OSEC | 303 | 0.839 | 0.837 | 0.794 | 0.883 | 0.482 | 0.896 |
| UCI Hungary | UCI Cleveland | OVEC | 303 | 0.852 | 0.857 | 0.807 | 0.892 | 0.294 | 0.899 |
| UCI Hungary | UCI Cleveland | Random Forest | 303 | 0.837 | 0.824 | 0.788 | 0.878 | 0.254 | 0.854 |
| UCI Hungary | UCI Cleveland | Support Vector Machine | 303 | 0.873 | 0.869 | 0.832 | 0.910 | 0.561 | 0.934 |
| UCI Hungary | UCI Switzerland | K-Nearest Neighbors | 123 | 0.688 | 0.956 | 0.435 | 0.903 | 0.114 | 0.667 |
| UCI Hungary | UCI Switzerland | Logistic Regression | 123 | 0.772 | 0.975 | 0.545 | 0.939 | 0.114 | 0.729 |
| UCI Hungary | UCI Switzerland | OSEC | 123 | 0.783 | 0.980 | 0.606 | 0.947 | 0.081 | 0.725 |
| UCI Hungary | UCI Switzerland | OVEC | 123 | 0.772 | 0.970 | 0.530 | 0.964 | 0.260 | 0.742 |
| UCI Hungary | UCI Switzerland | Random Forest | 123 | 0.800 | 0.976 | 0.577 | 0.969 | 0.081 | 0.751 |
| UCI Hungary | UCI Switzerland | Support Vector Machine | 123 | 0.720 | 0.971 | 0.520 | 0.878 | 0.089 | 0.724 |
| UCI Hungary | UCI VA Long Beach | K-Nearest Neighbors | 200 | 0.689 | 0.836 | 0.603 | 0.769 | 0.155 | 0.709 |
| UCI Hungary | UCI VA Long Beach | Logistic Regression | 200 | 0.693 | 0.863 | 0.616 | 0.775 | 0.155 | 0.728 |
| UCI Hungary | UCI VA Long Beach | OSEC | 200 | 0.734 | 0.892 | 0.660 | 0.811 | 0.290 | 0.743 |
| UCI Hungary | UCI VA Long Beach | OVEC | 200 | 0.729 | 0.863 | 0.644 | 0.813 | 0.210 | 0.728 |
| UCI Hungary | UCI VA Long Beach | Random Forest | 200 | 0.690 | 0.841 | 0.601 | 0.768 | 0.010 | 0.707 |
| UCI Hungary | UCI VA Long Beach | Support Vector Machine | 200 | 0.739 | 0.885 | 0.655 | 0.813 | 0.140 | 0.746 |
| UCI Switzerland | UCI Cleveland | K-Nearest Neighbors | 303 | 0.559 | 0.496 | 0.506 | 0.607 | 0.611 | 0.873 |
| UCI Switzerland | UCI Cleveland | Logistic Regression | 303 | 0.534 | 0.498 | 0.473 | 0.603 | 0.719 | 0.913 |
| UCI Switzerland | UCI Cleveland | OSEC | 303 | 0.611 | 0.512 | 0.547 | 0.671 | 0.551 | 0.839 |
| UCI Switzerland | UCI Cleveland | OVEC | 303 | 0.674 | 0.602 | 0.609 | 0.726 | 0.696 | 0.913 |
| UCI Switzerland | UCI Cleveland | Random Forest | 303 | 0.773 | 0.697 | 0.718 | 0.823 | 0.389 | 0.825 |
| UCI Switzerland | UCI Cleveland | Support Vector Machine | 303 | 0.659 | 0.590 | 0.597 | 0.721 | 0.706 | 0.883 |
| UCI Switzerland | UCI Hungary | K-Nearest Neighbors | 294 | 0.654 | 0.453 | 0.600 | 0.706 | 0.048 | 0.565 |
| UCI Switzerland | UCI Hungary | Logistic Regression | 294 | 0.860 | 0.732 | 0.815 | 0.903 | 0.037 | 0.575 |
| UCI Switzerland | UCI Hungary | OSEC | 294 | 0.660 | 0.451 | 0.595 | 0.721 | 0.146 | 0.560 |
| UCI Switzerland | UCI Hungary | OVEC | 294 | 0.758 | 0.594 | 0.698 | 0.812 | 0.170 | 0.569 |
| UCI Switzerland | UCI Hungary | Random Forest | 294 | 0.774 | 0.599 | 0.716 | 0.830 | 0.204 | 0.555 |
| UCI Switzerland | UCI Hungary | Support Vector Machine | 294 | 0.859 | 0.744 | 0.810 | 0.903 | 0.126 | 0.603 |
| UCI Switzerland | UCI VA Long Beach | K-Nearest Neighbors | 200 | 0.561 | 0.769 | 0.501 | 0.626 | 0.095 | 0.458 |
| UCI Switzerland | UCI VA Long Beach | Logistic Regression | 200 | 0.564 | 0.768 | 0.477 | 0.660 | 0.015 | 0.357 |
| UCI Switzerland | UCI VA Long Beach | OSEC | 200 | 0.491 | 0.728 | 0.396 | 0.584 | 0.110 | 0.507 |
| UCI Switzerland | UCI VA Long Beach | OVEC | 200 | 0.578 | 0.800 | 0.494 | 0.664 | 0.185 | 0.401 |
| UCI Switzerland | UCI VA Long Beach | Random Forest | 200 | 0.549 | 0.748 | 0.446 | 0.650 | 0.065 | 0.443 |
| UCI Switzerland | UCI VA Long Beach | Support Vector Machine | 200 | 0.484 | 0.751 | 0.396 | 0.571 | 0.175 | 0.560 |
| UCI VA Long Beach | UCI Cleveland | K-Nearest Neighbors | 303 | 0.775 | 0.709 | 0.723 | 0.824 | 0.541 | 0.897 |
| UCI VA Long Beach | UCI Cleveland | Logistic Regression | 303 | 0.832 | 0.822 | 0.784 | 0.875 | 0.472 | 0.888 |
| UCI VA Long Beach | UCI Cleveland | OSEC | 303 | 0.764 | 0.759 | 0.711 | 0.814 | 0.389 | 0.899 |
| UCI VA Long Beach | UCI Cleveland | OVEC | 303 | 0.851 | 0.837 | 0.806 | 0.891 | 0.660 | 0.934 |
| UCI VA Long Beach | UCI Cleveland | Random Forest | 303 | 0.779 | 0.774 | 0.728 | 0.828 | 0.231 | 0.815 |
| UCI VA Long Beach | UCI Cleveland | Support Vector Machine | 303 | 0.238 | 0.333 | 0.184 | 0.296 | 0.396 | 0.910 |
| UCI VA Long Beach | UCI Hungary | K-Nearest Neighbors | 294 | 0.752 | 0.564 | 0.701 | 0.803 | 0.320 | 0.787 |
| UCI VA Long Beach | UCI Hungary | Logistic Regression | 294 | 0.853 | 0.745 | 0.809 | 0.896 | 0.075 | 0.733 |
| UCI VA Long Beach | UCI Hungary | OSEC | 294 | 0.865 | 0.804 | 0.817 | 0.908 | 0.497 | 0.802 |
| UCI VA Long Beach | UCI Hungary | OVEC | 294 | 0.868 | 0.782 | 0.827 | 0.907 | 0.146 | 0.751 |
| UCI VA Long Beach | UCI Hungary | Random Forest | 294 | 0.836 | 0.728 | 0.790 | 0.880 | 0.109 | 0.748 |
| UCI VA Long Beach | UCI Hungary | Support Vector Machine | 294 | 0.702 | 0.543 | 0.639 | 0.760 | 0.265 | 0.813 |
| UCI VA Long Beach | UCI Switzerland | K-Nearest Neighbors | 123 | 0.610 | 0.951 | 0.410 | 0.817 | 0.041 | 0.583 |
| UCI VA Long Beach | UCI Switzerland | Logistic Regression | 123 | 0.680 | 0.963 | 0.464 | 0.876 | 0.024 | 0.570 |
| UCI VA Long Beach | UCI Switzerland | OSEC | 123 | 0.680 | 0.970 | 0.505 | 0.834 | 0.065 | 0.562 |
| UCI VA Long Beach | UCI Switzerland | OVEC | 123 | 0.658 | 0.948 | 0.425 | 0.861 | 0.033 | 0.604 |
| UCI VA Long Beach | UCI Switzerland | Random Forest | 123 | 0.711 | 0.963 | 0.481 | 0.896 | 0.073 | 0.563 |
| UCI VA Long Beach | UCI Switzerland | Support Vector Machine | 123 | 0.634 | 0.956 | 0.405 | 0.860 | 0.041 | 0.633 |

The heatmaps display target ROC-AUC by source, target, and model. OOD heatmaps display mean model results for the source-versus-target feature-score discrimination AUROC and target alert rate. A high domain-detection AUROC indicates score separation in these samples; a low AUROC does not prove absence of clinically relevant shift.

## Figures

- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/roc_curves.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/roc_curves.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/precision_recall_curves.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/precision_recall_curves.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/confusion_matrices.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/confusion_matrices.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/model_performance_comparison.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/model_performance_comparison.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/training_validation_gaps.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/training_validation_gaps.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/learning_curves.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/learning_curves.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/calibration_curves.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/calibration_curves.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/risk_coverage_curves.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/risk_coverage_curves.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_roc_auc_heatmaps.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_roc_auc_heatmaps.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_ood_heatmaps.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_ood_heatmaps.png`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_mean_auc_heatmap.pdf`
- `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/cross_dataset_mean_auc_heatmap.png`

Every figure is created from the saved metric, fold, or prediction tables in this run. The prediction files contain row-level labels and outputs and are intentionally local / gitignored; aggregate tables and figures are release artifacts. The experiment manifest links predictions, assignments, checksums, model configurations, software versions, and logs.

## Failed experiments and exclusions

| Dataset / transfer | Model | Stage | Failure | Reason |
| --- | --- | --- | --- | --- |
| uci_switzerland | logistic | learning_curve | ValueError | This solver needs samples of at least 2 classes in the data, but the data contains only one class: np.int64(1) |
| uci_switzerland | knn | learning_curve | ValueError | Got predict_proba of shape (41, 1), but need classifier with two classes. |
| uci_switzerland | svm | learning_curve | ValueError | The number of classes has to be greater than one; got 1 class |
| uci_switzerland | random_forest | learning_curve | ValueError | Got predict_proba of shape (41, 1), but need classifier with two classes. |
| uci_switzerland | ovec | learning_curve | ValueError | This solver needs samples of at least 2 classes in the data, but the data contains only one class: np.int64(0) |
| uci_switzerland | osec | learning_curve | ValueError | This solver needs samples of at least 2 classes in the data, but the data contains only one class: np.int64(0) |

Any failure caused by class counts or a fixed ensemble internal-CV requirement is reported as a failure rather than silently omitted. Switzerland contains only 8 negative examples; therefore three-fold validation is technically possible but estimates are highly unstable, and stack fitting may fail for an inner split. Dataset incompatibilities and access exclusions are recorded in the compatibility table.

An initial execution attempt (`20261107T202151Z`) was stopped after the learning-curve score array was indexed along the wrong axis. Its partial checkpoints and execution log remain under the ignored experiment directory for audit; they were excluded from all reported metrics. The corrected complete run is `20261107T202404Z`. The six failures above are from the completed run and are the Switzerland learning-curve configurations.

## Main findings and conclusions

- The four UCI CAD cohorts can be evaluated separately with the same feature schema and coded endpoint, but this run cannot establish independent external validation because they overlap historically with Heart5 and do not contain participant linkage keys.
- No model should be declared generally superior from the observed rankings. OVEC and OSEC performance varies by task and the sample sizes limit precision.
- SPECTF, heart-failure mortality, and MI lethal outcomes provide additional model-behavior experiments but answer different prediction questions and must remain separate from CAD claims.
- Training–validation gaps, calibration, conformal sets, selective risk, and OOD alerts provide complementary diagnostics. None establishes deployment safety, prospective benefit, or clinical readiness.
- The strongest next scientific step is a pre-registered evaluation on a genuinely independent, endpoint-aligned clinical cohort with documented prediction time, participant-level identifiers or overlap controls, and a fixed operating protocol. Secure-access data require approved access and governance.

## Limitations

1. Small and historical public cohorts, substantial missingness in some sites, and severe class imbalance in Switzerland and SPECTF.
2. Patient-level independence cannot be verified. Exact-row scans find no cross-cohort duplicates among the four UCI prepared tables, but they cannot detect transformed or near-duplicate participants.
3. The UCI datasets have historical clinical workflows and do not establish the intended prospective prediction time. UCI endpoint documentation is not enough to infer deployment suitability.
4. Heart-failure follow-up is not a uniform horizon; MI mortality labels concern a separate clinical stage; SPECTF is an imaging endpoint.
5. Bootstrap intervals condition on the observed target case mix and do not model site sampling or between-site variation.
6. OOD alert thresholds and selective diagnostics are experimental, not safety-certified. Conformal guarantees rely on exchangeability.
7. No external clinical deployment, prospective study, fairness analysis, or clinician-reviewed utility evaluation was performed.

## Reproducibility and verification

Run from the repository root in the project Python environment:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location).Path 'src')
python experiments/prepare_multi_dataset_evaluation.py
python experiments/run_multi_dataset_evaluation.py
python experiments/finalize_multi_dataset_evaluation.py
```

The raw datasets are not included in the public repository; they must be acquired from the cited UCI pages and their archive hashes must match `datasets/dataset_manifest.json`. Row-level predictions and fold assignments are local ignored files because they contain record-level output. Aggregate results, code, and figures are versionable. Python, NumPy, pandas, scikit-learn, and SciPy versions are stored in `manifests/experiment_manifest.json`.

Verification status: **passed**. Source archive entries verified: 7; prepared-file checksums verified: 9. Ground-truth labels match the prepared files for 42 within-task and 72 transfer groups. Pooled metrics were recomputed for 42 within-task groups and 72 transfer groups. Fold-assignment groups checked: 24. No previously existing experiment paths were written.

## Exact deliverables

- Dataset compatibility table: `results/multi_dataset_evaluation_20261108/dataset_comparison.csv`.
- Dataset provenance and checksum manifest: `results/multi_dataset_evaluation_20261108/datasets/dataset_manifest.json`.
- Model, fold, transfer, calibration, conformal, learning-curve, selective-risk, OOD, and failure tables: `results/multi_dataset_evaluation_20261108/metrics/`.
- Fold-level predictions and assignments: `results/multi_dataset_evaluation_20261108/predictions/20261107T202404Z/` (local, gitignored).
- Per-experiment checkpoints: `results/multi_dataset_evaluation_20261108/experiments/20261107T202404Z/` (local, gitignored).
- Experiment logs and manifest: `results/multi_dataset_evaluation_20261108/logs/` and `results/multi_dataset_evaluation_20261108/manifests/`.
- Figure pack: `results/multi_dataset_evaluation_20261108/figures/20261107T202404Z/`.
- This report: `docs/MULTI_DATASET_EXPERIMENTAL_EVALUATION_REPORT.md` and `results/multi_dataset_evaluation_20261108/reports/`.

- Compiled six-page research manuscript PDF: `output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108.pdf`.
- Complete LaTeX source bundle and build manifest: `paper/multi_dataset_study_20261108/`.
