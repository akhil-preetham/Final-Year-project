# CLIN-ADAPT experimental protocol

**Protocol:** `CLIN-ADAPT-NESTED-v1`  
**Role:** development benchmark; not external validation

## Dataset roles

Heart5, Mendeley and cardiovascular 70K retain their CARDIODIAG roles. They are
not merged and are not treated as independent cross-dataset validation. The
existing `CD-XD-001` protocol remains the authority for future compatible
cross-dataset work.

## Within-dataset benchmark

1. Load the declared target and remove only explicit identifiers.
2. Preserve explicit categorical schema metadata.
3. Split with stratified outer folds.
4. For each outer training partition, run stratified inner folds.
5. Fit every candidate's imputer, encoder, scaler and model inside each inner
   training fold.
6. Execute candidates concurrently with fixed worker count and seed.
7. Select a candidate or validation-justified fusion using inner predictions.
8. Fit selected outer-training pipelines and score the untouched outer test fold.
9. Aggregate outer predictions and report classification and probability metrics.

## Primary metrics

ROC-AUC and Brier score are primary development metrics. PR-AUC, balanced
accuracy, sensitivity, specificity, F1, log loss and confusion counts are also
stored. Accuracy is descriptive, not an optimization target.

## Configurations actually run

| Dataset | Outer/inner | Candidates | Predictions stored |
|---|---|---:|---|
| Heart5 | 3×2, seed 42 | 20 | Yes |
| Mendeley | 3×2, seed 42 | 20 | Yes |
| 70K | 2×2, seed 42 | 6 priority | No |

The 70K candidate subset was chosen for resource control and is explicitly not a
claim of exhaustive 70K coverage.

## Cross-dataset prohibition

No train-on-one-local-file/test-on-another run was performed. The required
semantic feature and endpoint gates from `CD-XD-001` are not passed. A future
cross-dataset run must use a new artifact namespace and dataset-level holdout.

## Reproduction commands

```text
./.venv/Scripts/python.exe experiments/clin_adapt/run_model_discovery.py --output results/clin_adapt/model_registry.json
./.venv/Scripts/python.exe experiments/clin_adapt/run_nested_validation.py --dataset heart5.csv --target HeartDisease --output results/clin_adapt/heart5_nested.json --outer-splits 3 --inner-splits 2 --max-workers 4
./.venv/Scripts/python.exe experiments/clin_adapt/run_nested_validation.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/clin_adapt/mendeley_nested.json --outer-splits 3 --inner-splits 2 --max-workers 4
./.venv/Scripts/python.exe experiments/clin_adapt/run_nested_validation.py --dataset data/kaggle_cardiovascular_70k/cardio_train.csv --target cardio --output results/clin_adapt/cardiovascular_70k_nested_priority.json --outer-splits 2 --inner-splits 2 --max-workers 3 --models logistic random_forest hist_gradient_boosting xgboost lightgbm catboost --no-predictions
./.venv/Scripts/python.exe experiments/clin_adapt/build_report.py
```
