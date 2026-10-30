# Model benchmark execution report

## Initial feasibility status

The prior custom CARDIODIAG nested workflow did not complete on the 70,000-row
dataset, including a reduced 2×2 smoke run. Its expensive components are the
five candidate pipelines, repeated fold-local preprocessing, OSEC's nested
stacking fit, and StableXAIHDRC relevance resampling. The process exceeded six
minutes before producing an artifact and was stopped.

The new benchmark runner separates generic model screening from the custom
CARDIODIAG nested workflow. It uses compact grids, one inner two-fold search,
one serial worker, fold-local preprocessing, and explicit per-model timing.

## Execution records

### Screening

- Artifact: `results/generated/kaggle70k_model_screening.json`
- Dataset: 10,000-row deterministic stratified sample from the Kaggle
  cardiovascular dataset; seed 42.
- Protocol: 3 outer folds, 2 inner folds, ROC-AUC tuning, fold-local cleaning,
  encoding, and scaling.
- Result: all 11 available candidates completed; no skipped candidates.
- Highest mean ROC-AUC: XGBoost, 0.7998 (screening only).

### Primary generic benchmark

- Artifact: `results/generated/kaggle70k_model_benchmark.json`
- Tabular exports:
  `results/generated/kaggle70k_model_summary.csv`,
  `results/generated/kaggle70k_model_fold_metrics.csv`, and
  `results/generated/kaggle70k_model_timing.csv`.
- Dataset: all 70,000 rows; seed 42.
- Protocol: 3 outer folds, 2 inner folds, ROC-AUC tuning, and the same
  fold-local preprocessing as screening.
- Result: all 11 available candidates completed; no skipped candidates.
- Mean ROC-AUC ranking (primary generic benchmark):
  XGBoost 0.80038, HistGradientBoosting 0.79957, GradientBoosting 0.79942,
  RandomForest 0.79816, MLP 0.79587, ExtraTrees 0.79405, Logistic 0.78930,
  LDA 0.78894, AdaBoost 0.78760, GaussianNB 0.74233, and Dummy 0.50000.
- Best mean PR-AUC was XGBoost (0.78561); best mean Brier score and ECE were
  also XGBoost (0.18092 and 0.01089, respectively).
- Total candidate runtimes ranged from 1.50 seconds (dummy) to 63.22 seconds
  (random forest). These are benchmark-process timings, not deployment
  performance estimates.

The primary artifact records the dataset SHA-256, target, complete
configuration, Python and package versions, Git HEAD, and a dirty-worktree
flag. The recorded worktree was dirty, so Git HEAD alone does not identify
the complete source snapshot.

The generic benchmark is not the custom CARDIODIAG nested validation. The
custom workflow on this dataset remains incomplete because its reduced smoke
run exceeded six minutes without producing an artifact. No custom OVEC, OSEC,
or stable-selector candidate is relabeled as one of these generic models.

## Interpretation rule

Screening results may establish implementation feasibility and identify
runtime-dominant candidates. They must not be used to claim definitive model
superiority, external generalization, clinical utility, or a universally best
algorithm.

The primary generic benchmark provides a prespecified 3x2 comparison of the
implemented candidates on this dataset. Its mean ROC-AUC ranking is useful for
screening and comparison, but it does not provide independent-patient
uncertainty intervals, a fully nested CARDIODIAG result, or evidence of
external generalization. Differences between nearby candidates should not be
treated as practically meaningful without additional replication.
