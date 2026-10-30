# Final model comparison

Source: `results/generated/kaggle70k_tuned_priority_oof_ensemble.json`.

| Model | Mean ROC-AUC | Mean PR-AUC | Mean Brier | Mean ECE | Pooled ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CatBoost | 0.80048 | 0.78560 | 0.18082 | 0.01151 | 0.80043 |
| XGBoost | 0.80029 | 0.78604 | 0.18098 | 0.01075 | 0.80022 |
| HistGradientBoosting | 0.79992 | 0.78521 | 0.18106 | 0.01426 | 0.79983 |
| LightGBM | 0.79961 | 0.78379 | 0.18113 | 0.00948 | 0.79952 |
| Random Forest | 0.79740 | 0.78032 | 0.18215 | 0.01432 | 0.79733 |
| Logistic regression | 0.78930 | 0.77382 | 0.18776 | 0.03600 | 0.78928 |

CatBoost is numerically highest by mean and pooled ROC-AUC in this run, but
its pooled advantage over the prior XGBoost benchmark is approximately
0.00005. This is not sufficient to claim meaningful superiority.

The fixed OOF ensemble of XGBoost, HistGradientBoosting, and Logistic
regression achieved pooled ROC-AUC 0.79897 and is not preferred.
