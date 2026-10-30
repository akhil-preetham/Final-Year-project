# CARDIODIAG initial baseline audit

**Audit date:** 2026-10-25  
**Scope:** local checkout, published CardioDiag article, repository metadata, and the two checked-in CSV files.

## 1. Evidence inspected

- Published article: Khan, Raza, and Nadeem, *CardioDiag: a machine learning approach for cardiovascular disease diagnosis using XAI-guided hybrid dimensionality reduction and optimized-based ensemble classifiers*, PeerJ Computer Science 12:e4059 (2026), DOI `10.7717/peerj-cs.4059`.
- Author repository: `https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code`.
- Associated Mendeley record: `https://data.mendeley.com/datasets/dzz48mvjht/1`, DOI `10.17632/dzz48mvjht.1`, CC BY 4.0.
- Local notebooks under `Daza_Base_Paper_Reproduced/`, `Five States Results/`, `MENDELEY Results/`, and `Paper 1 Code LIME with Diagrams/`.
- Local data: `heart5.csv` and `MendeleyCardiovascular_Disease_Dataset.csv`.

The checkout is notebook-centric. It contains no Python package, requirements file, `pyproject.toml`, test suite, documented command-line entry point, or README beyond the repository title. The checked-out working tree currently has expanded archive directories and deleted tracked `.rar` entries; these are pre-existing working-tree changes and were not modified by this audit.

## 2. Local inventory and data dictionary

| Asset | Observed contents |
|---|---|
| `heart5.csv` | 918 rows, 12 columns: 11 predictors plus `HeartDisease`; no empty fields or exact duplicate rows in the checked-in file; target counts 410/508. |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 rows, 14 columns: 13 predictors plus `target`; no empty fields or exact duplicate rows in the checked-in file; target counts 420/580; `patientid` is unique for all 1,000 rows. |
| `Daza_Base_Paper_Reproduced/...ipynb` | SMOTE baseline reproduction, 80/20 split after oversampling, GridSearchCV, stacking model, and saved outputs/warnings. |
| `Five States Results/...ipynb` | Full-methodology notebooks with percentile processing, class-separated imputation, LoRAS, PCA, optimized stacking/voting, calibration, fairness, bootstrap, and reviewer analyses. |
| `MENDELEY Results/...ipynb` | Mendeley-specific ablation, fairness, clinical-utility, and statistical-analysis notebooks. |
| `Paper 1 Code LIME with Diagrams/...` | LIME reports, stability outputs, diagrams, and a reviewer notebook concerning XAIH-DRC. |

The local `heart5.csv` contains the already-deduplicated 918-row representation described in the paper. The paper attributes the 1,190-row source to five public heart-disease datasets (Cleveland, Hungarian, Switzerland, Long Beach VA, and Statlog), with 272 exact duplicate rows removed. This means a UCI heart-disease file from one of those component sources cannot automatically be treated as independent external validation.

## 3. Paper-to-code traceability snapshot

| Paper component | Local implementation evidence | Reproduction status |
|---|---|---|
| Five States ingestion | `data = pd.read_csv('/content/drive/MyDrive/heart5.csv')` in the Five States notebooks | Present, but hard-coded to Google Drive/Colab. |
| Mendeley ingestion | Local CSV is present; Mendeley notebooks contain the corresponding workflow | Present, exact notebook-to-paper mapping still needs a machine-readable extraction. |
| Missing-value handling | `dropna()` appears in the baseline notebook; later workflow marks numeric outliers as `NaN` and imputes separately by target class | Inconsistent implementations. |
| Categorical encoding | Manual maps for `Sex`, `ExerciseAngina`, and `ST_Slope`; `LabelEncoder` for `ChestPainType` and `RestingECG` | Present; encoding is fit globally and imposes ordinal codes on nominal categories. |
| Percentile treatment | 1st/99th percentile code appears in `FiveStates_PAIRED_BOOTSTRAP_95_CI.ipynb` | Present, but thresholds are estimated before splitting and are applied to encoded categorical columns in parts of the workflow. |
| LoRAS | `loras.fit_resample(...)` appears in the Five States notebook | Present, but package version, parameters, generated counts, and fold-local use are not recorded. |
| XAIH-DRC | Paper describes Pearson/LIME relevance, Spearman agreement, and conditional PCA; local reviewer notebooks contain XAI analyses | Not yet mapped into a reusable implementation. |
| OVEC | Voting workflow appears in reviewer notebooks | Present in notebook form; exact weights/probability rule require extraction. |
| OSEC | Stacking workflow with GaussianNB, AdaBoost, Decision Tree, Logistic Regression, and XGBoost meta-learner appears in the Five States notebook | Present in notebook form. |
| Tuning | `GridSearchCV(..., cv=5, scoring='accuracy')` and randomized searches | Present, but not nested and not consistently aligned with the claimed search spaces. |
| Calibration | `CalibratedClassifierCV(..., method='sigmoid', cv=5)` appears in the stacking workflow | Present, but the final evaluation protocol and calibration separation are not fully specified. |
| Statistical validation | Bootstrap, DeLong/Wilcoxon, fairness, DCA, and LIME notebooks are present | Present as analysis artifacts; results need reconciliation against common frozen splits. |

## 4. Confirmed methodological risks

These are implementation observations, not claims that the published results are invalid in every respect.

1. **Resampling before splitting in the reproduced baseline.** The baseline notebook calls `SMOTE.fit_resample(X, y)` before `train_test_split`. Synthetic or interpolated information can therefore influence the later test partition.
2. **Full-data preprocessing before splitting.** The Five States workflow computes percentile limits, outlier replacement, class-specific medians, LoRAS, and PCA before the train/test split. These operations must be moved inside the training portion of each split/fold for the corrected experiment.
3. **Target-aware imputation.** The full-methodology notebook separates rows by `HeartDisease` and fits one median imputer per target class. That uses the label to determine feature values and is not a valid prediction-time preprocessing operation.
4. **Encoded categorical values treated as continuous.** `LabelEncoder` codes are passed to Pearson/Spearman calculations, percentile rules, PCA, and distance-based resampling. This creates arbitrary numerical geometry for nominal categories.
5. **Non-reproducible XAI feature selection.** The paper specifies LIME settings and thresholds but the notebooks do not expose a fold-local, reusable transformer that can be fitted only on training data.
6. **Ambiguous PCA and redundancy rule.** The paper does not give a reproducible numeric rule for “high redundancy,” and the local workflow uses `PCA(n_components=9)` after global fitting.
7. **Test-set and CV protocol mismatch.** The paper claims 75/25 splitting and 5-fold CV, while the original reproduction contains an 80/20 split after SMOTE. Several saved outputs use different sample totals and metrics.
8. **Hyperparameter inconsistencies.** The paper and saved outputs contain search-space/result combinations that do not always agree, including invalid or absent candidate values.
9. **Calibration evidence is mixed.** The paper reports a Five States OVEC calibration slope of approximately 4.10, which is not consistent with a broad claim of reliable calibration.
10. **No independent clinical external validation.** Both datasets used in the paper are benchmark/public datasets; Mendeley is already part of the original study and cannot be counted as new external evidence for this extension.

## 5. Reproduction boundary

The original notebooks are not currently executable as a portable local experiment because they depend on Colab/Google Drive paths and an undocumented environment. The first implementation stage should therefore preserve them as archival evidence and create a separately labelled, leakage-controlled reproduction rather than silently editing the historical notebooks.

No empirical claim about improved performance is made at this stage. All result fields in the future manuscript must be generated from frozen experiment artifacts.
