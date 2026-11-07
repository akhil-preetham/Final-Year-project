# Final experiment protocol

## Authoritative protocol

1. Freeze dataset hashes and schema manifests before fitting.
2. Use repeated stratified outer folds for evaluation.
3. Fit outlier handling, imputation, encoding, scaling, feature selection, and
   resampling only on outer-training data.
4. Tune model hyperparameters only in inner folds.
5. Train stacking base models with out-of-fold predictions through the
   estimator's internal cross-validation.
6. Fit calibration and threshold policies using training/validation data only.
7. Score the untouched outer test fold once.
8. Store fold metrics, pooled out-of-fold predictions, configuration, seed,
   dataset hash, and runtime.
9. Report ROC-AUC, PR-AUC, accuracy, balanced accuracy, sensitivity,
   specificity, precision, recall, F1, Brier, ECE, calibration intercept/slope,
   coverage, selective risk, confidence intervals, fold variability, and time
   where applicable.

## Development protocol

The 2x2 seed-42 reconstruction run is computationally bounded and exploratory.
It is stored under `results/generated/reconstruction_2x2/` and must not be
presented as final evidence.

## Authoritative status

Existing 3x3/3-seed artifacts are the strongest available internal evidence,
but no external protocol is currently authorized. A new confirmatory run must
use a new artifact namespace and must not overwrite frozen references.

