# Duplicate file report

## Exact duplicates

The SHA-256 scan found exact duplicates primarily in generated distributions.
Representative duplicate groups include:

- `src/cardiodiag/feature_selection.py` and its copies in both expanded
  distribution trees.
- `results/generated/kaggle70k_tuned_model_comparison.csv` and its copy in
  `dist/CARDIODIAG_Original_Kaggle/`.
- The four LIME ZIP pairs documented in `ARCHIVE_AUDIT.md`.

These are packaging copies, not evidence that the active source has duplicate
implementations.

## Same-name files requiring semantic review

Repeated names such as `calibration.py`, `evaluation.py`, `preprocessing.py`,
and `reliability.py` occur across separate CARDIODIAG, AURA-ML, and CLIN-ADAPT
namespaces. They must not be merged solely because their names match.

Likewise, `summary.json` and ablation JSON files occur under distinct dataset
directories. Their paths are part of their meaning and should remain distinct.

## Decision

No active source or research result is classified as safe to delete based on
filename or hash alone. Distribution copies are candidates for a later
generated-artifact policy; historical notebook and result files remain KEEP or
UNCERTAIN until their provenance is mapped.

