# Model tuning and ensemble report

## Scope

The verified primary artifact is
`results/generated/kaggle70k_model_benchmark.json`. It evaluates the separate
70,000-row `cardio` task with three shared stratified outer folds, two inner
folds, seed 42, ROC-AUC tuning, and fold-local cleaning, encoding, and scaling.
The runner's compact, model-specific grids are therefore inner-validation
tuning, not a single training-score comparison.

## Tuning status

The completed run includes:

- Logistic regression: fixed `C=1.0` under the existing balanced logistic
  specification.
- Gaussian NB: two `var_smoothing` values.
- Random forest and Extra Trees: two `max_depth` values.
- HistGradientBoosting: two `max_leaf_nodes` values.
- Gradient Boosting: two `max_depth` values.
- AdaBoost: two learning rates.
- MLP: two regularization values.
- XGBoost: two `max_depth` values.

All 11 available candidates completed all three outer folds. The full
configuration and selected parameters are stored per fold in the JSON
artifact. No outer-test labels were used for grid selection.

The optional booster installation was completed reliably in the existing
environment: LightGBM 4.7.0 and CatBoost 1.2.10. Both were included in the
new bounded run. Optuna and the other modern optional packages remain
unavailable; a larger search was not launched because the existing custom
selector has a documented runtime bottleneck and an expanded search would
require a new measured budget and untouched evaluation stage.

### Results

Artifact:
`results/generated/kaggle70k_tuned_priority_oof_ensemble.json`

| Model | Mean ROC-AUC | Mean PR-AUC | Mean Brier | Mean ECE |
|---|---:|---:|---:|---:|
| CatBoost | 0.80048 | 0.78560 | 0.18082 | 0.01151 |
| XGBoost | 0.80029 | 0.78604 | 0.18098 | 0.01075 |
| HistGradientBoosting | 0.79992 | 0.78521 | 0.18106 | 0.01426 |
| LightGBM | 0.79961 | 0.78379 | 0.18113 | 0.00948 |
| Random Forest | 0.79740 | 0.78032 | 0.18215 | 0.01432 |
| Logistic regression | 0.78930 | 0.77382 | 0.18776 | 0.03600 |

CatBoost's pooled outer ROC-AUC was 0.80043, compared with 0.80038 for the
prior XGBoost baseline. This is a marginal descriptive improvement, not
evidence of a statistically or practically meaningful win.

## Ensemble status

The new run evaluates a prespecified uniform out-of-fold ensemble of XGBoost,
HistGradientBoosting, and logistic regression on identical outer folds. Its
pooled ROC-AUC is 0.79897, below the XGBoost pooled ROC-AUC of 0.80022 in the
same run. Its pooled PR-AUC is 0.78297 and Brier score is 0.18176. The
ensemble therefore does not improve the standalone model and is not retained
as a preferred result.

No outer-test labels were used to fit ensemble weights. The member set was
prespecified from complementary model families before evaluating the outer
predictions.

## Interpretation

XGBoost has the highest descriptive mean ROC-AUC (0.80038), PR-AUC (0.78561),
and lowest mean Brier score (0.18092) and ECE (0.01089) in this 3x2 generic
benchmark. These are paired fold summaries, not independent-patient
uncertainty intervals or evidence of universal superiority.
