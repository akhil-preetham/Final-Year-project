# Compact candidate-pool experiment

## Protocol

This exploratory comparison uses three shared stratified outer folds, two inner
folds, seed 42, ROC-AUC for inner model selection, and fold-local cleaning,
imputation, scaling, and encoding. The classification threshold is the
predeclared 0.5 threshold; it was not selected from outer-test labels.
Reported metrics include ROC-AUC, average precision, Brier score, log loss,
uniform ten-bin ECE, and the thresholded classification metrics stored in each
JSON artifact.

The candidate pool was intentionally compact:

- Logistic regression and Elastic Net.
- RBF SVM and KNN on the two small datasets only.
- Random Forest and Extra Trees.
- XGBoost, CatBoost, LightGBM, and HistGradientBoosting.
- Gaussian NB and LDA.
- A small MLP was not repeated here because it was already evaluated in the
  prior benchmark and is not required to answer the compact-pool comparison.

Soft voting uses fixed one-quarter weights for CatBoost, XGBoost,
HistGradientBoosting, and Logistic regression. Stacking uses those same base
families, generates base predictions with inner `cv=2` within each outer
training partition, and fits a logistic meta-learner. Neither ensemble uses
outer-test labels for member or weight selection.

## 70k results

Artifact:
`results/generated/kaggle70k_compact_candidate_pool.json`

| Candidate | Pooled ROC-AUC | Pooled PR-AUC | Brier | Log loss |
|---|---:|---:|---:|---:|
| Stacking | 0.80028 | 0.78519 | 0.18107 | 0.54264 |
| XGBoost | 0.80008 | 0.78484 | 0.18104 | 0.54233 |
| CatBoost | 0.79998 | 0.78500 | 0.18102 | 0.54226 |
| HistGradientBoosting | 0.79973 | 0.78492 | 0.18110 | 0.54251 |
| Soft voting | 0.79943 | 0.78359 | 0.18143 | 0.54348 |
| LightGBM | 0.79940 | 0.78372 | 0.18120 | 0.54280 |
| Random Forest | 0.79730 | 0.78016 | 0.18217 | 0.54538 |
| Extra Trees | 0.79634 | 0.77668 | 0.18532 | 0.55372 |
| Elastic Net | 0.78928 | 0.77366 | 0.18776 | 0.56167 |
| Logistic | 0.78928 | 0.77366 | 0.18776 | 0.56168 |
| LDA | 0.78892 | 0.77272 | 0.18831 | 0.56212 |
| Gaussian NB | 0.74210 | 0.70866 | 0.29480 | 1.22984 |

RBF SVM and KNN were explicitly skipped above 5,000 rows because kernel
probability fitting and all-pairs neighbour prediction are not computationally
bounded for 70,000 observations under the available setup.

The stacking result is slightly above the compact-run XGBoost result by
approximately 0.00020 ROC-AUC, but remains below the earlier tuned CatBoost
result (0.80043) and is not evidence of practical superiority.

## Smaller-dataset results

Artifacts:

- `results/generated/heart5_compact_candidate_pool.json`
- `results/generated/mendeley_compact_candidate_pool.json`

On heart5, soft voting had the highest pooled ROC-AUC (0.92903), followed by
Random Forest (0.92733). On Mendeley, CatBoost had the highest pooled ROC-AUC
(0.99783), followed by Random Forest (0.99733). These datasets have only 918
and 1,000 observations, so their three-fold estimates are particularly
unstable and should not be treated as model-selection confirmation.

The small-dataset outcomes do not justify pooling model rankings with the 70k
task. They also do not establish external validation because the datasets
have different provenance, schemas, and outcome definitions.

## Interpretation

The compact pool supports using CatBoost/XGBoost/HistGradientBoosting as the
primary 70k candidates, with calibration and runtime reported alongside
discrimination. No ensemble is retained as a universally preferred method:
soft voting underperformed boosted standalone models, while stacking's small
70k gain over compact-run XGBoost was smaller than the differences between
the prior and current exploratory protocols.
