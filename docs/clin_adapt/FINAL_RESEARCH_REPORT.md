# CLIN-ADAPT final research report — development cycle 0.1

## Executive result

CLIN-ADAPT v0.1 is a separate, reproducible adaptive clinical tabular
benchmarking framework with a provisional CASL coordination policy. It is not
yet a proven new algorithm, universal clinical predictor or external-validation
system.

## What was inspected and preserved

The repository audit covered CARDIODIAG source modules, AURA-ML, nested
validation, preprocessing, evaluation, calibration, reliability utilities,
model artifacts, frozen baseline manifests, datasets, dependencies and tests.
No historical result, frozen baseline metric, dataset or AURA implementation was
overwritten.

## Registry and execution

- 35 model records were registered.
- 20 candidates were executable locally.
- 15 neural/foundation/AutoML families were explicitly unavailable.
- All 20 local candidates ran on Heart5 and Mendeley under 3×2 nested validation.
- Six resource-priority candidates ran on 70K under 2×2 nested validation.
- Parallel jobs completed: Heart5 60/60, Mendeley 60/60, 70K 12/12.
- Runtime snapshot: 12 logical CPUs, no detected GPU backend, and no available
  memory probe in the active environment.

## Results

| Dataset | CLIN-ADAPT pooled ROC-AUC | PR-AUC | Brier | Best frozen local reference |
|---|---:|---:|---:|---:|
| Heart5 | 0.926700 | 0.925855 | 0.100377 | soft voting 0.929033 |
| Mendeley | 0.997701 | 0.998240 | 0.015325 | CatBoost 0.997828 |
| 70K priority | 0.802481 | 0.785819 | 0.179835 | tuned CatBoost 0.800432 |

These are development results under different protocols and are not pooled into
a universal score. The apparent 70K difference is unpaired and protocol-
different; it is not a superiority claim.

## Ablation conclusion

On Heart5, CASL improved a bounded no-fusion control from ROC-AUC 0.927876 to
0.928495. On Mendeley, CASL matched the no-fusion control at 0.992812 and did
not improve over single CatBoost at 0.996622. This supports conditional rather
than universal value and does not establish novelty.

## Research assessment

The engineering contribution is defensible: a separate registry, training-only
pipelines, concurrent candidate execution, failure isolation, checkpointing and
transparent validation coordination. The algorithmic contribution is
**provisional and unproven** because its mechanism overlaps known AutoML,
dynamic-selection, ensemble and calibration methods.

The real unresolved gap remains guarded clinical cross-dataset transfer with
semantic compatibility, reliability and safe refusal. Current CARDIODIAG data
do not pass that evaluation gate, so no cross-dataset result is claimed.

## Reproduction

See `docs/clin_adapt/EXPERIMENTAL_PROTOCOL.md` and the scripts under
`experiments/clin_adapt/`. Results are stored exclusively under
`results/clin_adapt/`.

## Limitations and next steps

1. Repeat the nested benchmark across fixed seeds.
2. Add calibrated reliability summaries and subgroup analysis only under an
   approved protocol.
3. Install or otherwise make executable relevant foundation/AutoML comparators
   only after dependency, licensing and hardware review.
4. Obtain an independent compatible clinical cohort and pass the existing
   cross-dataset semantic/endpoint gates.
5. Claim novelty only if CLIN-ADAPT demonstrates a distinct cohort-level
   reliability, semantic-refusal or transport advantage.

## Final QA

The complete project suite passed with 57 tests. CLIN-ADAPT-specific tests,
Ruff, Python compilation, JSON parsing, CLI registry serialization, frozen
baseline hash verification and `git diff --check` also passed.
