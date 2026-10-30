# Model benchmark protocol

## Scope

This benchmark evaluates the separate Kaggle 70,000-record `cardio` task. It
does not pool targets or claim external validation of `heart5.csv` or the
Mendeley dataset.

## Candidate families

The available screening set contains:

- Dummy prior baseline
- Logistic regression
- Linear discriminant analysis
- Gaussian naive Bayes
- Random forest
- Extra Trees
- HistGradientBoosting
- Gradient Boosting
- AdaBoost
- MLP
- XGBoost when installed

CatBoost, LightGBM, Explainable Boosting Machine, TabM, TabPFN, TabICL, and
other optional families are recorded as unavailable when their packages are
not installed. They are not silently replaced by another model.

The existing corrected CARDIODIAG candidates remain separate evidence:
corrected OVEC, corrected OSEC, and stable-selector pipelines. They are not
silently collapsed into this generic-model benchmark.

## Evaluation

The runner is [run_model_benchmark.py](../experiments/run_model_benchmark.py).
Every model uses a fold-local `TrainingOnlyCleaner` and
`ColumnTransformer`. Hyperparameters are selected inside inner stratified
cross-validation; outer test rows are used only for final prediction.

The screening command uses a deterministic stratified sample of 10,000 rows,
three outer folds, two inner folds, seed 42, and compact predeclared grids.
This is feasibility/screening evidence, not definitive full-dataset
superiority evidence.

The primary command can use the full dataset by passing `--sample-size 70000`
with the same split structure. It should only be launched after screening
runtime and memory are reviewed.

ROC-AUC is the tuning objective and primary discrimination metric. The runner
also records PR-AUC, Brier score, uniform ten-bin ECE, classification metrics,
best inner parameters, fold sizes, fit time, total model time, and explicit
failure records.

The source `cardio_train.csv` is semicolon-delimited and retains the documented
raw anomalies. Its `id` column is excluded before modeling. No resampling is
performed.
