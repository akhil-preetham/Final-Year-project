# Original algorithm walkthrough

This document distinguishes notebook-observed behavior from the corrected
research implementation. It does not claim that every notebook represents the
final published protocol.

## Historical workflow

1. Load the Five States/Heart5 or Mendeley CSV.
2. Encode categorical columns, including `LabelEncoder` use for nominal
   categories in several notebooks.
3. Apply missing-value and percentile-based outlier handling.
4. Balance classes using SMOTE or LoRAS variants.
5. Apply PCA and/or feature reduction.
6. Compute LIME and correlation-based relevance evidence.
7. Train voting (OVEC) or stacking (OSEC) ensembles.
8. Tune selected estimators with scikit-learn grid/randomized search.
9. Produce calibration, fairness, bootstrap, statistical, and LIME reports.

## Published-paper specification

The supplied PeerJ article specifies the following details that can be
recovered from its Methods section:

- **Percentile Method (PM):** values outside feature-wise percentile bounds
  are replaced with missing values and then mean-imputed. The paper describes
  a lower/upper percentile rule but gives an example/notation that is not fully
  consistent about the lower-tail percentage. The expanded Five States
  notebooks commonly use 1st/99th percentile bounds. Neither the paper nor
  notebook variants give one versioned, fold-local function used for every
  reported result.
- **LoRAS:** local minority neighborhoods generate perturbed “shadow” points,
  which are combined with random affine transformations to produce synthetic
  minority rows. The article does not freeze package version, neighborhood
  size, shadow count, noise/affine parameters, or a complete executable recipe.
  Some notebooks call `loras.fit_resample` on the full dataset before a later
  train/test split; this is leakage-prone for evaluation.
- **XAIH-DRC:** the paper uses absolute Pearson correlation with the target
  (reported threshold 0.072) and global absolute LIME importance (reported
  threshold 0.05). LIME uses an exponential kernel (width 3), quartile
  discretization, 1,500 perturbations per explanation, 30 instances, and five
  seeds. Features are grouped by agreement, conflict, or low relevance. A
  Spearman rank statistic over conflicting features determines whether PCA is
  activated. The paper and notebook variants do not fully agree on whether PCA
  is applied to conflicting features or the full feature matrix, or how many
  components are retained.
- **OVEC:** soft voting over KNN, random forest, logistic regression, and SVM.
  The paper describes five-fold random search; reported weights and selected
  hyperparameters are dataset-specific. Notebook variants use both weighted
  and unweighted voting and at least one uses hard voting.
- **OSEC:** the article describes Gaussian NB, AdaBoost, decision tree, and
  logistic-regression base learners, five-fold out-of-fold probabilities, and
  an XGBoost meta-learner, followed by sigmoid calibration. The older Daza
  reproduction notebook instead stacks random forest, decision tree,
  gradient boosting, and NB with logistic-regression meta-learning and applies
  calibration in a later step. These are materially different models.
- **Optimization/evaluation:** the article says OVEC uses random search and
  OSEC uses grid search, both with five-fold CV inside a 75:25 train/test
  protocol. It also reports ten runs with seed 42. The archived notebooks
  include 80:20 and 75:25 splits, inconsistent preprocessing order, and
  analyses that inspect the test set during model selection. A fixed seed is
  not evidence that ten independent train/test partitions were run.

## Components

| Component | Historical evidence | Corrected interpretation |
|---|---|---|
| Percentile method | 1st/99th percentile code in Five States notebooks | Quantiles must be fitted on training rows only |
| LoRAS/SMOTE | `loras.fit_resample` and `SMOTE` cells | Resampling belongs inside training folds |
| XAIH-DRC | Correlation, LIME, agreement, and PCA analysis cells | The paper workflow is approximated by a fold-local stable selector |
| OVEC | `VotingClassifier` workflows | Soft-voting family; weights and candidate set vary by notebook |
| OSEC | `StackingClassifier` with NB, AdaBoost, tree, logistic, and XGBoost variants | Candidate family retained; corrected defaults are explicit in `models.py` |
| Calibration | `CalibratedClassifierCV` cells | Calibration must use training/calibration data, never outer test labels |
| Bootstrap/statistics | Bootstrap, Wilcoxon, DeLong, and report cells | Results remain protocol-specific and descriptive unless paired design is explicit |

The corrected package uses `build_ovec` and `build_osec` as explicit research
baselines. The default OSEC uses logistic regression as its meta-learner to
keep the corrected baseline stable; `build_osec_xgboost` is a separate
paper-like variant. Neither should be presented as a bit-for-bit original
implementation. The stable selector is an approximation and does not call
LIME inside each fold.

## Failure modes observed

- Resampling before a later split can leak synthetic information into testing.
- Global percentile bounds, imputation, encoding, PCA, and selection can use
  information from evaluation rows.
- Target-aware class-specific imputation is unavailable at prediction time.
- Label encoding creates arbitrary geometry for nominal categories.
- Colab/Google Drive paths and undocumented environments prevent portable
  execution.
- Notebook variants disagree on split proportions, search spaces, and ensemble
  details.

The corrected code addresses these failure modes without modifying historical
notebooks or claiming that the original metrics are unbiased estimates.

