# Baseline reproduction report

**Status:** Phase 2 initial report, 2026-10-25.  
**Evidence:** local notebooks, published paper, and generated protocol comparison at `results/generated/heart5_protocol_comparison.json`.

## Executive conclusion

The historical implementation can be reconstructed sufficiently to expose its
data-processing order, model families, and evaluation boundary, but not as a
bit-for-bit reproduction. The available source is a collection of Colab
notebooks with hard-coded paths, repeated cells, missing dependency/version
metadata, changing model configurations, and inconsistent saved outputs.

Therefore, historical results are labelled **native historical protocol** and
corrected results are labelled **corrected common split**. They must not be
presented as a single leaderboard.

## Historical protocol reconstructed from code

The primary Five States reproduction path observed in the notebooks is:

1. Load the already deduplicated `heart5.csv` file.
2. Drop missing rows.
3. Apply global manual maps and `LabelEncoder` to categorical columns.
4. Apply percentile-based treatment and/or class-separated imputation in
   later notebook sections.
5. Apply SMOTE or LoRAS before the train/test split in the available baseline
   paths.
6. Fit PCA globally in some paths.
7. Split the resampled data using `train_test_split`, usually with
   `test_size=0.25` in the full-methodology notebooks and `test_size=0.20` in
   the historical reproduction notebook.
8. Tune models with ordinary 5-fold `GridSearchCV` or randomized search.
9. Build OVEC or OSEC and evaluate on the resulting test partition.

The exact paper configuration cannot be recovered unambiguously because the
notebooks contain repeated/contradictory model blocks. Examples include
different OSEC meta-learners, changing search grids, global versus fold-local
preprocessing claims, and different test-set sizes.

## Native historical run performed

The function `cardiodiag.historical.run_historical_native` explicitly records a
representative historical path:

- global manual/category encoding;
- SMOTE before `train_test_split`;
- 80/20 split with seed 42 and no stratification;
- OSEC or OVEC-style ensemble;
- no claim that this is leakage-safe.

For `heart5.csv`, the run produced 1,016 rows after SMOTE and a 204-row test
partition. The native OSEC result was accuracy 0.8873, ROC-AUC 0.9516, and
Brier score 0.0890. The native OVEC result was accuracy 0.8627, ROC-AUC
0.9163, and Brier score 0.1236. These values are **reproduction artifacts of
the specified native protocol**, not corrected estimates of generalization.

## Corrected common-split run performed

The corrected pipeline uses:

- a stratified 75/25 split;
- identifier removal;
- training-only numeric outlier replacement and imputation;
- training-only one-hot encoding for nominal categorical variables;
- no resampling in the current default corrected run;
- training-only model fitting;
- an optional training-only stability-aware selector.

On the same seed and dataset, corrected OSEC achieved accuracy 0.8957,
ROC-AUC 0.9348, and Brier score 0.0875. The stability-aware OSEC variant
achieved accuracy 0.9000, ROC-AUC 0.9360, and Brier score 0.0864 in this one
internal split. These are promising but not confirmatory: repeated-seed
results previously showed no uniform advantage for the selector, so the
contribution remains inconclusive.

## Reproduction discrepancies requiring explicit reporting

1. The paper reports both 75/25 evaluation and averages over repeated runs,
   while the source notebooks use multiple split sizes and fixed seeds.
2. The available notebooks apply or describe preprocessing before splitting in
   several paths, while the paper claims a leakage-controlled fold-local
   procedure in later text.
3. The Mendeley results notebooks contain blocks that load or display the Five
   States schema, so the Mendeley reproduction cannot be accepted without a
   separate dataset-specific audit.
4. The paper and notebooks do not fully specify LoRAS parameters, redundancy
   thresholds, PCA variance rules, or calibration separation.
5. Some saved result tables have incompatible sample totals and metrics.

## Phase 2 decision

**Gate 1: partially satisfied.** The historical behavior, corrected behavior,
data hashes, and runnable comparison are now recorded. **Gate 2 is not yet
fully satisfied** for the full research program because nested selection,
calibration separation, group/duplicate independence checks, and independent
external validation still need to be implemented and verified.
