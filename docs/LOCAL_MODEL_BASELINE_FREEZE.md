# Local-model baseline freeze

**Baseline ID:** `LOCAL_MODEL_BASELINE_2026-11-03_V1`  
**Freeze date:** 2026-11-03  
**Status:** frozen reference only

The current local-model results are now frozen as the comparison baseline for
the next research phase. The machine-readable freeze manifest is
`results/local_model_baseline_freeze.json`. It records SHA-256 hashes for the
datasets, benchmark artifacts and derived report used here.

## Frozen headline results

| Dataset | Frozen best reference | ROC-AUC | PR-AUC | Brier | ECE | Protocol caveat |
|---|---|---:|---:|---:|---:|---|
| heart5 | soft voting | 0.929033 | 0.931312 | 0.099458 | 0.038747 | 3 outer × 2 inner, seed 42 |
| Mendeley | CatBoost | 0.997828 | 0.998345 | 0.014838 | 0.122701 | 3 outer × 2 inner, seed 42 |
| cardiovascular 70K | tuned CatBoost | 0.800432 | 0.785413 | 0.180825 | 0.008961 | 3 outer × 2 inner, seed 42 |
| cardiovascular 70K | AURA V2 feasibility | 0.802842 | 0.786891 | 0.179746 | 0.006031 | comparison baselines frozen; not a superiority claim |

These values are not pooled into one score. The datasets have different targets,
schemas, provenance and roles, and the artifacts use different candidate grids
and protocol variants.

## Freeze rules

1. Do not overwrite the listed result paths or silently regenerate them under
   the same names.
2. Do not use the AURA 70K feasibility difference as evidence of superiority.
3. Do not compare the local headline values as cross-dataset transfer metrics.
4. New protocol outputs must use new paths and record their own hashes.
5. A future paper/table may cite this baseline only with its artifact path and
   protocol caveat.

The baseline is a reference point, not evidence of external validation,
clinical utility, universal superiority or a need for a new classifier.
