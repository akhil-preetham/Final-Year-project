# Kaggle 70,000-record claim-to-evidence audit

| Proposed claim | Evidence | Status and scope |
|---|---|---|
| The dataset is a separate 70,000-record binary classification benchmark | `data/manifests/local_datasets.json`; dataset summary | Supported: target is `cardio`, not `HeartDisease` or `target` |
| The dataset has no exact duplicate rows or missing values | Dataset validation output and manifest | Supported for the downloaded CSV; source provenance remains limited |
| The corrected selector can run on the new semicolon-delimited schema | `src/cardiodiag/data.py`; dataset schema tests; smoke artifacts | Supported: delimiter detection, identifier removal, explicit categorical schema, and selector protocol metadata verified |
| Stable XAIHDRC is more stable than the one-shot comparator | `post_boundary_corrected_kaggle70k_stability.json` | Not established: difference 0.00036, interval touches zero, positive-evidence flag false |
| Stable XAIHDRC improves predictive reliability | `post_boundary_corrected_kaggle70k_linkage.json` | Unsupported: ROC-AUC, AURC, and full-coverage risk differences favor corrected OSEC; other intervals are mixed |
| Stability predicts reliability across seeds | Linkage rank-correlation fields | Not testable in this run: selector internal stability is constant, so correlations are undefined |
| The new dataset is independent external validation | Dataset provenance and target/schema comparison | Unsupported: target and predictors are incompatible with existing tasks, source overlap cannot be ruled out, and no one-way external evaluation was performed |
| The complete research pipeline has been rerun | Stability and linkage artifacts; absent nested artifact | Unsupported: nested validation did not complete |
| The new benchmark proves generalization or clinical utility | All artifacts | Unsupported: internal benchmark evidence only; no external cohort, prospective evaluation, or clinical utility analysis |

## Required review decisions

1. Whether to retain the dataset locally while Kaggle reports an unknown
   license.
2. Whether the extreme blood-pressure values should remain in the benchmark
   protocol or receive a prespecified sensitivity analysis.
3. Whether a full nested run is computationally justified or requires an
   explicitly approved, scientifically documented scaling protocol.
4. Whether any future cross-dataset analysis is meaningful given the different
   outcome definitions.
