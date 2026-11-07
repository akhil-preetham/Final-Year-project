# CLIN-ADAPT cross-dataset generalization

## Current status

No CLIN-ADAPT cross-dataset predictive run was authorized or performed. The
CARDIODIAG datasets remain:

- Heart5: historical composite development benchmark;
- Mendeley: historical replication benchmark already used by the base study;
- 70K: separate target/schema benchmark with unresolved independent provenance.

The current data therefore cannot establish leave-one-dataset-out generalization
or independent external validity.

## Required future tracks

The implementation must follow `docs/CROSS_DATASET_EVALUATION_PROTOCOL.md`:

1. frozen source-only zero-shot transfer;
2. predeclared unlabeled-target adaptation;
3. fixed-budget few-shot adaptation;
4. target-trained local upper bound;
5. one-way locked external validation.

Each target cohort must have an approved clinical feature/unit/codebook map,
endpoint definition, overlap assessment, provenance manifest, licensing status
and frozen role before labels influence decisions.

## Existing-method comparison

The future comparison must include strong source-trained local baselines and,
where executable, TabPFN, TabICL, TabDPT, HyperFast, CARTE, FLAT and shift-aware
foundation methods. CLIN-ADAPT cannot claim to solve cross-dataset learning by
selecting among local classifiers on rows from one dataset.

## Decision rule

If an existing method matches or exceeds CLIN-ADAPT's discrimination,
calibration, coverage and failure-handling outcomes under the same information
budget, the proposed contribution is not needed for that setting. If the data
cannot pass semantic or endpoint gates, the conclusion is infeasible—not
algorithmically novel.
