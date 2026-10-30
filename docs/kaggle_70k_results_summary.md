# Kaggle 70,000-record benchmark results summary

## Scope

This is a separate benchmark task using target `cardio`. It is not pooled with
`HeartDisease` or `target`, and no cross-dataset external-validation claim is
made. The full nested-validation workflow was not completed.

## Provenance

- Source: <https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset>
- Download date: 2026-10-29
- Archive SHA-256:
  `b78ff607480810c3e27de3e11d52c4962a3a81dbb3d69365e1cf3394a67c2b23`
- CSV SHA-256:
  `21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c`
- Rows: 70,000
- Target: `cardio`
- Target counts: 35,021 class 0; 34,979 class 1
- License: Kaggle metadata reports `Unknown`; redistribution remains
  unresolved.

The source is semicolon-delimited. `id` is treated as an identifier and
excluded before modeling. Age is recorded in days. Categorical fields are
`gender`, `cholesterol`, `gluc`, `smoke`, `alco`, and `active`; numeric fields
are `age`, `height`, `weight`, `ap_hi`, and `ap_lo`.

There are no missing values, no exact duplicate rows, and all IDs are unique.
The source contains implausible blood-pressure values, including 40 records
with `abs(ap_hi) > 250`, 953 with `abs(ap_lo) > 200`, 1,234 with
`ap_hi < ap_lo`, 7 with `ap_hi <= 0`, and 22 with `ap_lo <= 0`. No rows or
labels were removed or manually corrected.

## Completed workflows

### Stability

Artifact:
`results/generated/post_boundary_corrected_kaggle70k_stability.json`

Protocol: 5 folds × 3 repeats, 8 selector resamples, stability threshold 0.75,
relevance threshold 0.02, seed 42.

| Method | Mean repeat Nogueira | Overall Nogueira |
|---|---:|---:|
| Stable XAIHDRC | 0.8432 | 0.8557 |
| One-shot comparator | 0.8429 | 0.8514 |

Stable-minus-one-shot difference: `0.00036`, descriptive bootstrap interval
`[0.00000, 0.00109]`. The artifact's positive-evidence flag is `false`.

### Stability–reliability linkage

Artifact:
`results/generated/post_boundary_corrected_kaggle70k_linkage.json`

Protocol: seeds 42–51; fit/calibration/evaluation fractions 0.5625/0.1875/0.25;
corrected OSEC versus stable OSEC.

- Cross-seed selected-set Nogueira stability: `0.2392`.
- Stable-minus-corrected ROC-AUC: `-0.00074`
  `[-0.00100, -0.00049]`.
- Stable-minus-corrected AURC: `+0.00029`
  `[+0.00012, +0.00048]`.
- Stable-minus-corrected full-coverage risk: `+0.00074`
  `[+0.00038, +0.00114]`.
- Stable-minus-corrected ECE: `+0.00025`
  `[-0.00089, +0.00138]`.
- Stable-minus-corrected conformal coverage: `-0.00018`
  `[-0.00051, +0.00015]`.
- Rank correlations were undefined because internal selector stability was
  constant across the ten seeds.

### Nested validation

No nested artifact was generated. A reduced 2-outer-fold/2-inner-fold smoke
run did not complete after more than six minutes on this 70,000-row dataset and
was stopped. The requested 3×3 nested protocol was therefore not launched or
claimed as completed.

## Reproducibility

The reduced stability and linkage smoke runs were each repeated with identical
inputs and seeds. After excluding the provenance fields that record the
individual invocation, the JSON outputs were identical. Full stability and
linkage artifacts record selector protocol
`post_boundary_correction_v1`, dataset hash, configuration, seed(s), Python and
package versions, Git HEAD, and dirty-worktree status.

## Interpretation

The completed analyses do not establish a stability advantage or a
stability–reliability benefit on this benchmark. The dataset is a separate
internal benchmark with a different target and feature schema, not valid
cross-dataset external validation of the existing CARDIODIAG targets.
