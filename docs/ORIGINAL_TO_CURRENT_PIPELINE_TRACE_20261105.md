# CARDIODIAG: original-to-current pipeline trace

**Audit date:** 2026-11-05  
**Purpose:** Trace the original CARDIODIAG method through the complete current research pipeline, explain each material change, and state what the evidence does and does not establish.

## 1. Versions being compared

This comparison separates three source states because they are not one continuous Git history:

| State | Identity | What it represents |
|---|---|---|
| Original authors' source | [jaffarkulachi/Cardio-Diag-Approach-Code at e63b02c8a2aba6344a48025f657696fd99ac3a5f](https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code/tree/e63b02c8a2aba6344a48025f657696fd99ac3a5f) | Audited original snapshot. It contains dataset files and four RAR archives with notebooks, not an installable Python package or one canonical end-to-end script. |
| Student's published repository | [akhil-preetham/Final-Year-project at ae30f91adc71675e00619bb5f12235841d71a4fa](https://github.com/akhil-preetham/Final-Year-project/tree/ae30f91adc71675e00619bb5f12235841d71a4fa) | Public implementation snapshot. Its Git history is separate from the original authors' repository. |
| Active local research state | This workspace, audited 2026-11-05 | Later remediation, external evaluations, audit artifacts, and manuscript work. These changes are not all in the public snapshot; the local tree is uncommitted. |

The comparison is therefore a source-and-behavior trace, not a clean Git diff between common ancestors. The original repository snapshot itself has only data and archives; its executable behavior is reconstructed from the archived notebooks. The paper's Methods section is a separate source of specifications and is not assumed to describe every notebook run. This distinction is documented in [SOURCE_PROVENANCE.md](SOURCE_PROVENANCE.md), [PROTOCOL_AUDIT.md](PROTOCOL_AUDIT.md), and [PAPER_TO_CODE_MAP.md](PAPER_TO_CODE_MAP.md).

The principal notebook evidence is Daza_Paper_Exact_Accuracy.ipynb for the SMOTE-before-split 80:20 path, Reviewer1_XAIH_DRC.ipynb and Reviewer1_Five_States_Full_Methodology.ipynb for LoRAS/XAIH-DRC/PCA variants, and Fairness_OSEC_MENDELEY_dataset.ipynb for a Mendeley workflow variant. The article's published specification is separately described in ORIGINAL_ALGORITHM_WALKTHROUGH.md. These notebooks are evidence of distinct executions, not interchangeable copies of one canonical algorithm.

## 2. Executive finding

The current work is a **corrected, generalization-focused research extension** to CARDIODIAG, not a bit-for-bit reimplementation of the original algorithm. It preserves the cardiovascular tabular prediction problem and the OVEC/OSEC ensemble families, while changing data handling, leakage boundaries, feature selection, validation, and prediction outputs. It adds transport evaluation, calibration diagnostics, feature-space shift detection, conformal sets, selective abstention, provenance, and a fail-closed domain gate.

The project has produced real, reproducible results, including one retrospective, source-distinct, endpoint-aligned hospital evaluation (AngioCAD). Those results do **not** establish dependable unseen-site generalization: the AngioCAD AUC is 0.787, its calibration remains poor, and source-versus-target OOD AUROC is only 0.589. The integrated selective policy accepts only 5.6% of AngioCAD records, while the site registry blocks all unregistered sites. This is a completed negative/limiting engineering demonstration, not success at the intended reliability claim.

## 3. End-to-end pipeline comparison

### Original notebook path (representative, not universal)

Load a CSV from a notebook/Drive path → drop missing rows or use global/class-aware imputation → manually encode categories → calculate outlier bounds and sometimes feature transforms on the whole table → apply LoRAS or SMOTE, sometimes before splitting → apply correlation/LIME/PCA feature reduction in variant-specific order → split rows 80:20 or 75:25 → tune base learners with ordinary CV → fit OVEC/OSEC → sometimes sigmoid-calibrate → score the resulting holdout and generate notebook metrics/LIME analysis.

### Current corrected internal path

Load and validate a dataset and its target → remove identifier columns → stratified outer fold → fit outlier handling, imputation, scaling, encoding, optional selector, and estimator on outer-training data only → choose parameters only inside inner folds → score the untouched outer fold once → save predictions, split indices, metrics, hashes, configuration, and run provenance.

### Current source-to-external research path

Harmonize explicitly documented source features and labels → split source records into model-fit and source-calibration partitions → fit the predictor, calibrator, and shift thresholds using source data only → freeze them → transform and score an external cohort once → compare probability quality and shift scores to external labels only for evaluation → optionally create conformal sets and apply a metadata allowlist/support/uncertainty gate. An unknown site is rejected before a probability is returned.

These paths answer different questions. Historical scores, internal nested scores, and external transfer scores are kept as separate evidence families and must not be ranked together as if they shared a protocol.

## 4. Detailed change trace

### 1. Dataset loading and validation

**Original behavior.** Notebook cells load Heart5/Five States or Mendeley CSVs from hard-coded Google Drive locations. The original repository snapshot holds two CSVs and archives. Notebook cells do not provide one shared loader, schema contract, validation API, or reliable source identity for every result.

**Current change — Added / Corrected.** The shared loader checks the requested target, validates binary labels, reads CSVs with delimiter handling, attaches an explicit feature schema, removes known identifier columns, and summarizes row counts, missingness, duplicates, class counts, and SHA-256. External cohort adapters add explicit endpoint derivation, feature mapping, ID joins, and expected-shape checks.

**How it works.** The primary functions are in data.py. Dataset-specific adapters form part of each frozen experiment runner. AngioCAD labels are joined by ID with a one-to-one constraint; 377 feature records match 413 labelled IDs, leaving 36 unmatched. External targets are not silently made equivalent: Z-Alizadeh Sani uses at least 50% stenosis while the source label uses greater than 50%; Duke uses at least 75%.

**Why and methodological effect.** Explicit schemas prevent IDs, targets, and nominal categories from silently entering as ordinary numeric features. Provenance checks caught duplicates: every Heart5 row matches a row in the component UCI sources, the 270-record Statlog file matches Cleveland after target harmonization, and the newer 918-row Mendeley release duplicates Heart5. These must not be represented as independent external sites.

**Result effect and new limits.** These checks change which datasets qualify as development, transfer, or external evidence; they do not improve model discrimination by themselves. Cross-release patient linkage is incomplete, several feature units/timing definitions are unknown, and some labels use different thresholds. Dataset-specific licensing and redistribution rights also remain to be confirmed for some derived/release files. An endpoint-aligned one-site cohort exists, but it cannot establish variability across hospitals.

**Preserved.** The Heart5 and Mendeley benchmark files and their cardiovascular binary-prediction task remain in the project with hashes. The 70K dataset is retained as a separate task because its label/schema are not interchangeable.

### 2. Preprocessing

**Original behavior.** Notebook versions use dropna, manual maps or LabelEncoder, percentile-based outlier replacement, global or class-specific median imputation, and occasionally paper-described mean imputation. The exact quantiles and order vary. Some transformations are computed before train/test splitting.

**Current change — Modified / Corrected.** The prediction pipeline uses a fitted TrainingOnlyCleaner, then numeric median imputation and standard scaling, plus categorical most-frequent imputation and one-hot encoding. The default cleaner estimates 1st/99th percentile cutoffs, medians, and categorical modes from only the fit partition. It has median-replacement, clipping, and no-outlier-treatment settings. It does not use labels to impute.

**How it works.** The cleaner is placed in a scikit-learn pipeline with the preprocessor. Each inner and outer fit learns its own statistics from that fit's rows. At transform time it reuses those statistics. One-hot encoding uses handle-unknown-ignore for categories absent from the training fold.

**Why and methodological effect.** This prevents evaluation rows from determining imputation, scale, category vocabulary, and outlier bounds. One-hot encoding avoids inventing a false order among nominal categories. Removing target-aware imputation makes prediction possible when the target is unknown.

**Result effect and new limits.** Corrected scores are not directly comparable to notebook scores because the input rows and representation differ. One-hot dimensions can be sparse in small samples; 1st/99th quantiles are a chosen approximation rather than a proven reproduction of the paper's percentile rule. Imputation cannot recover missing clinical measurements or undocumented measurement units.

**Preserved.** The general concept of missing-value handling and percentile-based outlier treatment remains, but its fitted state is fold-local and target-independent.

### 3. Class balancing

**Original behavior.** The article describes LoRAS. Archived notebook paths also use SMOTE. At least one reproduction calls SMOTE on all rows before an 80:20 split; other LoRAS/PCA paths resample before a later holdout. This creates a risk that synthetic neighbors encode information from eventual test rows.

**Current change — Removed from corrected primary run; Preserved for forensics.** The corrected internal primary pipeline does not resample. Some logistic and SVM estimators use class-weight balancing. The historical runner retains a clearly labelled SMOTE-before-split approximation; it does not claim to be leakage-safe. LoRAS remains documented in archived notebook evidence, not in the corrected active estimator.

**How it works.** In the corrected path, all preprocessing and fitting happen within the training fold; no synthetic examples are created from the full development table. The historical path intentionally reproduces the unsafe ordering to make its effect auditable.

**Why and methodological effect.** Removing pre-split sampling fixes direct synthetic train/test contamination. Class weights alter the loss contribution for some learners without generating near-duplicate observations.

**Result effect and new limits.** The class distribution seen in corrected training data is the observed distribution. This can lower minority-class sensitivity compared with oversampling; weights are not applied uniformly to every OVEC/OSEC base learner. Historical SMOTE scores remain useful only as a forensic record, not as unbiased generalization estimates.

**Preserved.** The balancing question and historical SMOTE behavior are retained in the audit. LoRAS itself is not reproduced in the primary method.

### 4. Feature selection and dimensionality reduction

**Original behavior.** The paper describes XAIH-DRC using absolute Pearson association, reported thresholds of 0.072 for correlation and 0.05 for aggregate LIME relevance, LIME kernel width 3, quartile discretization, 1,500 perturbations, 30 observations, and five seeds. Features are grouped by agreement/conflict/low relevance; a rank-correlation step can trigger PCA. Notebook variants disagree about whether PCA is fit on the full matrix or selected conflicting features and how components are retained.

**Current change — Replaced by an explicitly approximate selector.** StableXAIHDRC is a training-fold-only stability selector; it is not the original XAIH-DRC. It combines absolute point-biserial correlation with permutation importance from logistic regression. The builder uses six stratified bootstrap resamples. Features pass a selection-frequency and mean-relevance rule; a top-k fallback prevents an empty set. It keeps selected transformed columns and does not silently apply the original conditional PCA.

**How it works.** For each selector fit, the training fold is divided into internal fit and relevance-validation portions. Bootstrap samples from the internal fit train a balanced logistic model. Correlation and ROC-AUC permutation importance are measured on the internal relevance-validation rows; repeated scores produce feature frequency and mean relevance. The entire selector is itself inside the model pipeline, so outer evaluation rows do not determine selected features.

**Why and methodological effect.** Fold-local fitting fixes global feature-selection leakage. Repeated resampling makes selection stability measurable, while retaining named transformed features avoids reducing all predictors to opaque components.

**Result effect and new limits.** The selector did not provide a consistent predictive/reliability advantage; evidence is dataset-dependent. Its importance score is not the paper's LIME score, the thresholds differ, and the internal validation rows participate in feature selection within the training partition. Selection reduces dimensionality but does not establish causal or clinical relevance.

**Preserved.** The aim of XAI-guided relevance filtering is retained at a high level. The exact LIME/correlation grouping, conflict test, and conditional PCA mechanism are not preserved in the corrected predictor. Historical LIME notebooks remain archived.

### 5. Base models

**Original behavior.** The paper and notebooks contain several configurations. The reported paper families include KNN, RF, LR, and SVM for OVEC; NB, AdaBoost, decision tree, and LR as OSEC base learners. The Daza notebook uses a different OSEC base set including RF, tree, gradient boosting, and NB.

**Current change — Modified / Added.** A corrected standalone logistic baseline was added beside explicit OVEC and OSEC factories. The corrected OSEC default uses the paper-like four base learner types, with explicit AdaBoost count and tree depth, but not the original full tuned search.

**How it works.** Model creation is centralized in models.py and placed after the common data pipeline. Randomized components receive fixed seeds where applicable. Dataset schema and transformations are applied consistently across candidates.

**Why and methodological effect.** Centralizing definitions makes candidates reproducible and enables matched comparisons on the same folds. A simple logistic baseline makes ensemble gains testable.

**Result effect and new limits.** Candidate performance depends on dataset and protocol. On the corrected 3 outer × 3 inner seed-42 study, corrected OVEC mean ROC-AUC was 0.9295 on Heart5 and 0.9957 on Mendeley; stable OSEC was 0.9253 and 0.9942 respectively. These are internal values, not external validation. The high Mendeley result is not evidence that the cohort is independent or that performance will transfer.

**Preserved.** The prediction task and several original classifier families remain. Exact estimator defaults and tuned settings do not.

### 6. OVEC

**Original behavior.** OVEC is a voting ensemble of KNN, RF, LR, and SVM. The paper describes soft voting and randomized tuning; archived variants use different weights, include hard voting, or vary selected parameters.

**Current change — Modified.** The current OVEC uses soft voting with KNN(7), RF(200 trees), balanced LR, and probabilistic balanced SVC. Its default voting weights are equal. The corrected nested comparison's OVEC grid fixes weights at None; it does not reproduce the paper's broad random search.

**How it works.** Each base estimator emits class probabilities and the VotingClassifier averages them. The whole vote is fit only on the training partition and scored on untouched outer rows.

**Why and methodological effect.** A fixed, deterministic candidate enables fair shared-fold comparison and removes test-set-driven configuration changes.

**Result effect and new limits.** OVEC was a strong internal candidate, especially on Mendeley, but this does not show that the vote or its fixed hyperparameters generalize to unseen hospitals. Equal voting may underweight or overcount correlated learners.

**Preserved.** OVEC's defining soft-voting family and its four broad learner types are preserved; the original search, weights, and selected parameters are not.

### 7. OSEC

**Original behavior.** The paper's OSEC uses Gaussian NB, AdaBoost, tree, and LR base learners, five-fold out-of-fold probabilities, an XGBoost meta-learner, and sigmoid calibration. Other archived notebook variants use different bases and a logistic meta-learner.

**Current change — Modified.** The corrected OSEC uses NB, AdaBoost, depth-5 tree, and balanced LR, with scikit-learn's five-fold probability stacking. Its default meta-learner is balanced logistic regression. A separate build_osec_xgboost factory provides an XGBoost-meta analogue, but it is not the default candidate in the primary nested study. Calibration is evaluated in separate workflows.

**How it works.** During fit, stacking generates out-of-fold base probabilities and fits the final estimator to those predictions. In nested search, each stack is fitted only within the current inner-training or outer-training rows.

**Why and methodological effect.** Explicitly offering the LR-meta default improves portability and stability, while keeping an optional paper-like variant. It avoids claiming a paper match where the notebooks disagree.

**Result effect and new limits.** The 3x3 corrected internal stable-OSEC result is strong but below corrected OVEC on these datasets. The meta-learner difference and lack of integrated calibration mean it is not a reproduction of the paper's calibrated XGBoost OSEC.

**Preserved.** The stacked generalization structure, OOF probability features, five-fold internal stacking, and broad base learner family are preserved. The exact meta-learner/calibration combination varies by experiment and is not one faithful original configuration.

### 8. Hyperparameter tuning

**Original behavior.** The paper describes five-fold random search for OVEC and grid search for OSEC within a 75:25 train/test setup. Archived notebooks have different grids, 80:20 and 75:25 splits, and some repeated analysis of holdout results.

**Current change — Corrected / Modified.** The primary nested stage uses three outer stratified folds and three inner folds with ROC-AUC as the inner search objective. Candidate grids are intentionally small: LR C values, OSEC final-LR C values, and stable-selector thresholds. The current OVEC grid fixes its weights rather than conducting the original random search.

**How it works.** GridSearchCV receives the full pipeline; each inner fit therefore refits cleaning, encoding, feature selection, and estimator inside the inner-training rows. The selected setting is refit on outer-training rows and scored on outer-test rows once. All candidates are reported.

**Why and methodological effect.** This separates model choice from outer performance estimation and reduces selection optimism compared with tuning on a reused holdout.

**Result effect and new limits.** The resulting metric estimates a nested row-level internal protocol, not the paper's 75:25 ten-run metric. Three folds and small samples yield uncertain estimates. No grouped/patient split is possible for all records; the same observations appear in different model comparisons and across seed-sensitivity runs, so those estimates are dependent.

**Preserved.** Cross-validation-based parameter selection is preserved. The original search distributions, grid, repetition design, and final split are not.

### 9. Data leakage and split boundaries

**Original behavior.** Several notebook paths resample before splitting and compute imputation, percentile bounds, PCA, or feature relevance on full data. Some use class-specific imputation requiring labels. The paper's stated fold-local claims cannot be mapped to one exact notebook lineage.

**Current change — Corrected for the named corrected protocols.** Preprocessing, feature selection, model tuning, and outer scoring are separated. Source calibration and external target scoring are also disjoint in the transfer studies. The historical runner intentionally preserves an unsafe SMOTE-before-split ordering and labels it as historical.

**How it works.** The pipeline is refit inside each inner and outer training boundary. The external model and thresholds are frozen before target labels are opened for evaluation. Stored indices and predictions permit audit of which rows were scored.

**Why and methodological effect.** This fixes direct evaluation contamination in the corrected path and makes the validation estimate more defensible.

**Result effect and new limits.** Removing leakage can lower metrics; that is an expected correction, not evidence of a weaker implementation. It does not fix duplicate people or source overlap: Heart5 is a UCI composite, and full patient-level linkage across every release is unavailable. Therefore row-level CV can still overstate performance for unseen patients/sites.

**Preserved.** The original historical behavior is retained in notebooks and a clearly labelled forensic runner for comparison; it is not mixed with corrected results.

### 10. Explainability

**Original behavior.** LIME supports the paper's feature-relevance analysis and local explanations in notebooks. Variants aggregate feature weights and use them in XAIH-DRC.

**Current change — Replaced in selection; Removed from the active prediction path.** The current corrected predictor does not emit LIME explanations per patient. StableXAIHDRC uses correlation and permutation importance for feature selection. Archived LIME notebooks and their analyses remain available as historical evidence.

**How it works.** Permutation importance measures the change in validation ROC-AUC when a transformed feature is shuffled; correlation measures marginal association. Neither is a faithful local explanation of an individual prediction.

**Why and methodological effect.** This avoids treating a global notebook explanation analysis as an explanation guaranteed to match each deployed prediction, and keeps selection inside training folds.

**Result effect and new limits.** LIME is not part of the current prediction output and therefore does not affect the main predictor's scores. The project cannot claim original XAIH-DRC reproduction or per-case explanations from the current domain-guard API. Permutation importance and correlation are associational and can be unstable with correlated predictors.

**Preserved.** The general goal of making feature relevance inspectable survives. The exact LIME explanation method is retained only in archival analyses, not in the corrected runtime.

### 11. Probability calibration

**Original behavior.** Some original notebooks use CalibratedClassifierCV with sigmoid calibration and five-fold CV. The precise data used for calibration and its relationship to every reported metric are not recoverable as one protocol.

**Current change — Added as a separate evaluated layer.** The corrected internal nested candidates are generally scored as fitted; calibration diagnostics are measured, not assumed fixed. Transfer studies reserve source-only calibration rows and fit Platt scaling without external target labels.

**How it works.** A source model produces probabilities on a reserved calibration partition. A logistic sigmoid maps source scores to calibrated probabilities. That mapping is frozen before external scoring. Brier score, log loss, calibration slope/intercept, and ECE are checked.

**Why and methodological effect.** Calibration is essential to the uncertainty/risk claim and must not use outer test or external labels to fit the mapping.

**Result effect and new limits.** Calibration transfers inconsistently. On AngioCAD, Brier moved from 0.190 to 0.185 but its paired interval included no change; ECE worsened from 0.211 to 0.216. On Duke, Brier worsened from 0.216 to 0.241 and ECE from 0.119 to 0.198. Source calibration therefore does not establish reliable target probabilities.

**Preserved.** Sigmoid/Platt calibration remains conceptually present, but it is fit and evaluated in a new source-only protocol rather than assumed to reproduce the original calibration.

### 12. Out-of-distribution and shift detection

**Original behavior.** The original algorithm has no validated feature-space OOD detector or unknown-site gate.

**Current change — Added.** K-nearest-neighbor distance and Isolation Forest scores are evaluated with thresholds derived from source calibration data. A separate runtime guard requires the supplied domain identifier to appear in a trusted source-domain registry.

**How it works.** Feature detectors compare transformed target rows to source fit/calibration distributions. The guard checks site identity before inference; only registered domains proceed to model scoring. For registered cases, distance/support thresholds can force abstention.

**Why and methodological effect.** The additions address the core requirement that the system should recognize unsupported inputs and withhold scores rather than present all predictions as valid.

**Result effect and new limits.** Feature-only detection is weak on the endpoint-aligned AngioCAD site: source-versus-target AUROC was 0.589 for the primary Isolation Forest study (0.580 for the later KNN diagnostic). On the leave-one-UCI-cohort pilot, average OOD AUROC was 0.758 but target alert rates varied from 2.4% to 86.8%. These scores do not reliably identify individual errors or guarantee behavior under concept shift. The metadata gate detects registration status, not distribution novelty.

**Preserved.** No original OOD behavior is preserved; this is entirely new functionality.

### 13. Uncertainty and selective prediction

**Original behavior.** The paper has probability calibration, but no validated conformal prediction set or policy for abstaining on unsupported predictions.

**Current change — Added.** Split conformal sets, singleton-only prediction, confidence/risk-coverage analysis, and abstention were added. The domain guard withholds probabilities on abstentions and rejects unknown domains before model execution.

**How it works.** A model is fit on development rows; nonconformity scores and finite-sample quantiles are computed from a distinct calibration partition. A test row can receive a set containing zero, one, or both classes. Only a singleton, in-support, registered-domain prediction is released as a class and probability.

**Why and methodological effect.** This makes uncertainty operational: uncertain or unsupported rows can be withheld instead of forced into a binary output.

**Result effect and new limits.** Under source calibration, conformal assumptions require exchangeability; they do not assure nominal coverage after dataset shift. On AngioCAD, conformal-plus-KNN coverage was only 5.6% (21/377), with all 21 accepted rows positive. The unknown-site runtime gate has 0% coverage by design. Such selective results do not show a useful general-purpose operating point or estimate safety from a one-class accepted subset.

**Preserved.** The original probabilistic prediction framing remains, now with an explicit abstain action. Conformal validity under shift is not established.

### 14. Cross-dataset and external evaluation

**Original behavior.** The paper and notebooks report separate within-dataset holdouts; they do not establish a locked train-on-multiple-datasets/test-on-an-unseen-site protocol.

**Current change — Added.** The project added leave-one-UCI-source-cohort-out evaluation (CD-XD-002), a source-distinct Z-Alizadeh Sani stress test (CD-XD-003), endpoint-aligned AngioCAD evaluation (CD-XD-004), and endpoint-mismatched Duke stress testing (CD-XD-005). AngioCAD has a later post-hoc reliability/selective replay (CD-XD-006).

**How it works.** Source-only features, model, calibration, and OOD thresholds are frozen before target scoring. External labels are used for retrospective metrics only. AngioCAD is mapped from age, sex, and fasting-glucose status to a patient label derived from artery stenosis bins.

**Why and methodological effect.** This directly tests transfer, the central research objective, rather than inferring it from within-dataset random splits.

**Result effect and new limits.** CD-XD-002 macro AUC was 0.760, but its UCI cohorts overlap the Heart5 source material. CD-XD-003 AUC was 0.720 with a 50% endpoint-boundary mismatch. CD-XD-004 AngioCAD AUC was 0.787 on 377 matched records, with poor calibration and weak OOD separation; 36 of 413 label IDs lack features, the FBS unit is undocumented, and only one hospital is tested. CD-XD-005 Duke AUC was 0.661 with a 75% versus greater-than-50% endpoint mismatch. Thus, one endpoint-aligned site evaluation **is demonstrated**, but reliable generalization across unseen sites is **not established**.

**Preserved.** The underlying binary cardiovascular risk prediction task is preserved. Cross-site evaluation is new; historical within-dataset results remain separately reportable.

### 15. Engineering, reproducibility, and auditability

**Original behavior.** The original source snapshot is archive/notebook oriented, with hard-coded paths, changing cells, and no unified locked environment or reproducible experiment runner. It lacks a complete automated test and result-provenance framework.

**Current change — Added.** The active local project has a Python package, experiment entrypoints, a locked dependency environment, manifests, machine-readable metrics, prediction files and split indices, input/code/output hashes, audit reports, demos, and tests. It also keeps notebooks and raw/source assets in explicit archives.

**How it works.** Each experiment records configuration, dataset identity, fold indices, predictions, metrics, environment/code hashes, and output manifests. Independent audit scripts recompute stored metrics and verify artifact hashes. The 2026-11-05 QA report records 106 passing collected tests, Ruff, compilation, lock checks, transfer-artifact recalculation, data hashes, and manuscript checks.

**Why and methodological effect.** These changes make runs inspectable and repeatable and exposed mismatches in dataset lineage, labels, and metric interpretation.

**Result effect and new limits.** The checks support software and artifact integrity; they do not prove that a target is representative, labels are clinically valid, or a model generalizes. The November local remediation state is uncommitted and is ahead of the public repository snapshot; cloning the public commit alone will not recover every current artifact.

**Preserved.** Original archives, datasets, and prior outputs are retained. The historical and corrected evidence families are explicitly separated.

### 16. Research question, novelty, and claim evolution

**Original focus.** Cardiovascular diagnosis on tabular benchmarks using XAI-guided dimensionality reduction, optimized voting/stacking ensembles, and reported classification metrics.

**Current focus.** Generalization-aware and uncertainty-calibrated cardiovascular prediction under dataset shift: train on source datasets, test on untouched datasets, quantify calibration and distribution shift, and reject inputs outside an evidenced operating domain.

**What was added.** The research workflow now has multi-source/leave-domain-out experiments, source-only calibration, OOD scoring, conformal sets, selective prediction, a domain allowlist guard, provenance and validity audits, and negative-result reporting.

**Novelty and limitations.** The implementation is a research prototype built from established components; the present evidence does not establish a novel universally superior classifier or a new clinically validated method. A defensible contribution is the end-to-end, auditable evaluation of prediction, calibration, shift warnings, and abstention on these cardiovascular datasets—including the finding that the current OOD/selective behavior is inadequate. A method novelty claim would need a prespecified, matched comparison and an untouched compatible external cohort.

**Result effect.** The added stages showed where the original within-dataset performance narrative does not transfer: moderate ranking at one endpoint-aligned site, poor target calibration, weak feature-only OOD detection, and very low integrated selective coverage.

**Preserved.** The cardiovascular binary task, Heart5/Mendeley development history, OVEC/OSEC model families, and original LIME/LoRAS evidence remain visible. The current primary algorithm no longer uses LoRAS or the original LIME/PCA XAIH-DRC path. AURA-ML and CLIN-ADAPT are exploratory separate workstreams, not proof that the core CARDIODIAG transport objective has succeeded.

## 5. Results: what changed and what may be concluded

| Evidence family | Representative result | Interpretation |
|---|---|---|
| Historical Heart5 approximation | OSEC AUC 0.9516 and OVEC AUC 0.9163 after SMOTE-before-split | Reproduces one notebook-like protocol; leakage risk makes these unsuitable as unbiased performance estimates and they are not the paper's exact metrics. |
| Corrected internal nested study | Corrected OVEC AUC 0.9295 Heart5 / 0.9957 Mendeley; stable OSEC 0.9253 / 0.9942 | Pipeline-clean internal comparison, not external generalization; do not compare numerically to the historical run as a head-to-head victory. |
| UCI leave-one-cohort-out | Macro AUC 0.760; source calibration Brier 0.202 to 0.170 | Retrospective stress test; source cohorts overlap Heart5 and OOD alert rate varies greatly. |
| Z-Alizadeh Sani | AUC 0.720 | Source-distinct hospital, but endpoint boundary differs. |
| AngioCAD | AUC 0.787; calibrated ECE 0.216; OOD AUROC 0.589 | One retrospective endpoint-aligned external site. Moderate ranking does not imply reliable probabilities or a dependable shift detector. |
| Duke ACATH | AUC 0.661 | Stress test with a stricter endpoint, not endpoint-identical validation. |
| Selective policy | AngioCAD combined coverage 5.6%; unknown-site gate 0% | Explicitly exposes low utility and fail-closed behavior; not a successful deployment operating point. |

The full evidence trail is in [MASTER_DIRECTIVE_COMPLETION_MATRIX.md](MASTER_DIRECTIVE_COMPLETION_MATRIX.md), [CROSS_DATASET_VALIDATION.md](CROSS_DATASET_VALIDATION.md), [TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md](TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md), and [SELECTIVE_POLICY_COMPONENT_AUDIT.md](../results/validity_audit_20261105/selective_policy_components/SELECTIVE_POLICY_COMPONENT_AUDIT.md).

## 6. What is still the original CARDIODIAG algorithm?

| Component | Status in current project |
|---|---|
| Cardiovascular binary prediction from tabular clinical features | Preserved |
| OVEC soft-voting family (KNN, RF, LR, SVM) | Preserved with explicit fixed defaults; original search/weights are not |
| OSEC stacking family and five-fold OOF base probabilities | Preserved in modified form |
| XGBoost OSEC meta-learner | Available as a separate optional variant; not the primary default |
| Percentile-based outlier handling | Modified to training-only fitted bounds |
| LoRAS | Archived/documented; not part of the corrected primary pipeline and not exactly reproducible |
| SMOTE | Retained in a historical forensic runner with leakage-prone ordering, not the corrected primary run |
| XAIH-DRC with LIME, conflict groups, and conditional PCA | Historical evidence preserved; current stable selector is an approximation, not the original algorithm |
| Sigmoid calibration | Concept retained in separate source-calibration studies; not a faithful reproduction of every original run |
| External/OOD/conformal/selective/domain guard | Entirely new |

## 7. Overall disposition

The software and offline research demonstration are operational and reproducibility checks are recorded. Exact reproduction of the original paper is incomplete because source notebooks conflict and the full LoRAS/LIME/PCA setup and article-table lineage are not recoverable. One source-distinct, endpoint-aligned external evaluation is complete, but the central claim of dependable prediction at unseen sites remains **NO-GO**. Feature-only OOD recognition is weak, calibration transfers poorly, and selective coverage is too low to demonstrate useful operation. Clinical readiness is also **NO-GO**.

The most accurate project description is: **a reproducible research prototype that preserves selected CARDIODIAG ensemble families, corrects key evaluation leakage risks, adds cross-dataset calibration/shift/abstention experiments, and documents that reliable unseen-site operation has not yet been established.**
