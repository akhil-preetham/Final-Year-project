# CLIN-ADAPT research novelty analysis

## Prior-art comparison

| Proposed capability | Established prior art | CLIN-ADAPT v0.1 status |
|---|---|---|
| Dataset profiling | AURA profiling, meta-features, AutoML algorithm recommendation | Implemented; not novel alone |
| Candidate pipeline generation | AutoML, model portfolios and TabRepo | Implemented bounded registry; not novel alone |
| Parallel execution | AutoML systems, job schedulers and benchmark frameworks | Implemented resource-limited engine; engineering contribution only |
| Validation-based fusion | Voting, stacking, dynamic ensemble selection, mixture-of-experts | Implemented CASL gate; not proven novel |
| Calibration-aware utility | Proper scoring, calibration selection and reliability-aware ensembles | Implemented; established principle |
| Failure-driven alternatives | AutoML retry/search systems and robust orchestration | Basic diagnostic recommendations only |
| Cross-schema clinical transfer | CARTE, FLAT, HyperFast and tabular foundation models | Not implemented; current data gate blocks it |
| Safe semantic refusal | Potential research gap in this project context | Not implemented or validated |

## Current novelty decision

CLIN-ADAPT/CASL is **not yet a defensible new algorithmic contribution**. The
current mechanism combines known components and has only within-dataset
development evidence. It should be described as a reproducible adaptive
benchmarking and coordination framework.

## Potential defensible gap

The strongest remaining direction is not a generic ensemble. It is a guarded
clinical transfer protocol that:

1. verifies feature semantics, units, endpoint definitions and availability;
2. refuses transfer when compatibility is uncertain;
3. evaluates source-only, unlabeled-adaptation and few-shot tracks separately;
4. reports calibration, selective risk and failure-to-map rate across independent
   cohorts;
5. compares against CARTE, FLAT, HyperFast, TabPFN-family models and strong
   target-trained baselines under declared information budgets.

This overlaps the prior SAGE-Transfer direction. Existing CARDIODIAG feasibility
artifacts show that this question is currently blocked by data compatibility, so
CLIN-ADAPT does not claim to have solved it.

## Evidence standard for a future claim

A future novelty claim requires a pre-registered dataset-level holdout, an
approved semantic map, executable existing comparators, paired cohort-level
comparisons, reliability outcomes and preserved negative results. A metric gain
on Heart5, Mendeley or 70K alone cannot establish novelty.
