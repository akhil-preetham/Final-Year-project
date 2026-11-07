# CARDIODIAG local model exhaustion report

**Date:** 2026-11-03  
**Scope:** All compatible model families already installed or represented by
verified repository artifacts. This is not a literal execution of every model
in the world; unavailable foundation/AutoML frameworks are explicitly listed.

## Availability audit

### Executable in the local environment

- scikit-learn: Logistic Regression, Elastic Net Logistic Regression, LDA,
  Gaussian Naive Bayes, Random Forest, Extra Trees, HistGradientBoosting,
  GradientBoosting, AdaBoost, MLP, RBF-SVM and KNN.
- XGBoost 3.x.
- LightGBM 4.x.
- CatBoost 1.x.
- Existing CARDIODIAG OVEC/OSEC pipelines.
- AURA-ML V1/V2 local prototype.

### Not installed or not executable here

TabPFN, TabICL, TabDPT, HyperFast, AutoGluon, PyTorch, TensorFlow,
Transformers, FLAML, auto-sklearn, H2O, NGBoost, InterpretML and related
foundation-model packages were absent from the active `.venv`. Their papers
were reviewed separately, but no local metrics are claimed for them.

## Verified artifact coverage

| Dataset | Artifact family | Models covered | Protocol |
|---|---|---|---|
| heart5 | `results/generated/heart5_compact_candidate_pool.json` | 12 individual models + voting + stacking | 3 outer × 2 inner, seed 42 |
| Mendeley | `results/generated/mendeley_compact_candidate_pool.json` | 12 individual models + voting + stacking | 3 outer × 2 inner, seed 42 |
| Cardiovascular 70K | `results/generated/kaggle70k_model_benchmark.json` and tuned artifact | 11 screening/primary models; tuned XGBoost, LightGBM, CatBoost and ensemble | 3 outer × 2 inner, seed 42 |
| Cardiovascular 70K | `results/aura_ml_v2/70k_feasibility_3x3.json` | AURA V2 plus Logistic, RF, HGB, XGBoost, CatBoost and fixed ensemble | 3 outer × 3 inner AURA; frozen baseline fits |

Existing verified artifacts were reused rather than rerun. Metrics below are
not pooled across incompatible protocols; they are reported within artifact
families.

## Small-dataset exhaustive compact pool

### Heart5

| Model | ROC-AUC | PR-AUC | Brier | ECE |
|---|---:|---:|---:|---:|
| Soft voting | **0.929033** | 0.931312 | **0.099458** | 0.038747 |
| Random Forest | 0.927329 | 0.927249 | 0.102900 | 0.060007 |
| Elastic Net | 0.925350 | **0.932904** | 0.106880 | 0.072405 |
| Stacking | 0.924914 | 0.926034 | 0.102502 | 0.063728 |
| Logistic | 0.924626 | 0.931510 | 0.107239 | 0.057401 |
| HistGradientBoosting | 0.924337 | 0.924338 | 0.104553 | 0.040907 |
| RBF-SVM | 0.923804 | 0.927399 | 0.102220 | 0.055847 |
| LDA | 0.923353 | 0.929921 | 0.108318 | 0.078685 |
| CatBoost | 0.923281 | 0.920589 | 0.101659 | **0.037553** |
| Extra Trees | 0.923195 | 0.927050 | 0.105646 | 0.050261 |
| XGBoost | 0.923128 | 0.920558 | 0.103200 | 0.074816 |
| KNN | 0.918391 | 0.908838 | 0.104569 | 0.051209 |
| Gaussian NB | 0.912877 | 0.914799 | 0.135056 | 0.174092 |

The strongest verified heart5 result in this compact pool is the fixed soft
voting ensemble. AURA V2's three-seed confirmatory mean was 0.924449 ROC-AUC;
therefore AURA is not the best verified heart5 method.

### Mendeley

| Model | ROC-AUC | PR-AUC | Brier | ECE |
|---|---:|---:|---:|---:|
| CatBoost | **0.997828** | **0.998345** | **0.014838** | 0.122701 |
| Random Forest | 0.997330 | 0.997952 | 0.023916 | 0.112509 |
| XGBoost | 0.996979 | 0.997642 | 0.018539 | 0.121174 |
| LightGBM | 0.996884 | 0.997542 | 0.016882 | 0.177613 |
| HistGradientBoosting | 0.996741 | 0.997443 | **0.016976** | 0.211495 |
| Stacking | 0.996683 | 0.997355 | 0.017175 | 0.194736 |
| Extra Trees | 0.996229 | 0.997152 | 0.024293 | **0.076522** |
| Soft voting | 0.997155 | 0.997773 | 0.016338 | 0.084254 |
| RBF-SVM | 0.994356 | 0.995663 | 0.024622 | 0.103409 |
| Logistic | 0.992660 | 0.993911 | 0.027034 | 0.099919 |
| Elastic Net | 0.992607 | 0.993776 | 0.027480 | 0.131913 |
| LDA | 0.989331 | 0.990465 | 0.042606 | 0.301817 |
| KNN | 0.987011 | 0.987191 | 0.044483 | 0.111844 |
| Gaussian NB | 0.983239 | 0.984983 | 0.048625 | 0.231031 |

The strongest verified Mendeley result is CatBoost in the compact pool. AURA V2
achieved 0.997661 mean ROC-AUC across three seeds, slightly below this compact
pool point estimate but above corrected OVEC in its matched V2 comparison.

## 70K verified model coverage

The prior primary/tuned artifacts cover the broad local portfolio. The strongest
prior tuned standalone model is CatBoost at pooled ROC-AUC **0.800432**. The
resource-bounded AURA V2 feasibility result reached **0.802842**, but its
comparison baselines were frozen rather than inner-retuned; this is not a fair
replacement for the tuned CatBoost result.

The AURA feasibility run selected a single adaptive CatBoost model in all three
outer folds and did not use fusion. This is a useful result: the adaptive
method's best behavior on 70K is model routing to a strong tree learner, not a
new universal ensemble.

## Consistency assessment

No model dominates all datasets and all metrics:

- Heart5: soft voting/RF lead discrimination; CatBoost has the lowest compact
  ECE; AURA V2 is not the top ROC-AUC method.
- Mendeley: CatBoost leads discrimination and Brier; Extra Trees has lower ECE
  in the compact pool; AURA V2 is competitive but not clearly dominant.
- 70K: tuned CatBoost/XGBoost are near 0.80 ROC-AUC; AURA feasibility is higher
  than frozen baselines but not compared against a fully retuned V2 baseline.

The data characteristics explain much of this variation: small public datasets
have strong separability and high ceiling metrics, while 70K has balanced labels,
measurement-quality concerns and ROC-AUC around 0.80 across strong learners.

## Decision on a new algorithm

The local evidence does **not** justify building another algorithm solely to
chase a higher number. There are already worthy results:

- 0.929033 compact-pool ROC-AUC on heart5;
- 0.997828 compact-pool ROC-AUC on Mendeley;
- 0.800432 tuned CatBoost ROC-AUC on 70K;
- 0.802842 exploratory AURA V2 feasibility ROC-AUC on 70K.

What is missing is not another model name. It is fair evaluation of unavailable
foundation models, frozen compatible external cohorts, and a fully retuned 70K
3x3 comparison against AURA. Implementing a new algorithm now would risk
repackaging established methods and overfitting the small local benchmark.

## Reproducibility caveat

These are verified stored artifacts, not a single new universal experiment. The
small compact pools and 70K primary/tuned runs use related but not identical
candidate grids. Comparisons must remain within their declared artifact
protocols. All raw result files were preserved.
