# Cross-dataset generalization and domain adaptation review

## Problem distinctions

| Setting | Source labels | Target rows | Target labels | Is it external validation? |
|---|---|---|---|---|
| IID within-dataset split | Yes | Same population | Held out | No; internal validation |
| Leave-dataset-out meta-test | Many source datasets | New dataset | Few-shot or withheld | Evidence for cross-dataset generalization |
| Unsupervised domain adaptation | Source labels | Unlabeled target rows | Not used for selection | Conditional transfer evidence |
| Test-time adaptation | Source model/data | Streaming target rows | Usually unavailable | Requires explicit adaptation protocol |
| External validation | Development data | Frozen compatible cohort | Used only for final evaluation | Yes |
| CARDIODIAG current artifacts | Dataset-specific labels | Same local datasets | Outer labels | Internal evidence only |
| `CD-XD-002` | Three UCI source cohorts | Fourth UCI cohort held out by source | Used only for final scoring within each fold | Retrospective domain-holdout evidence; not independent external validation because the cohorts overlap prior Heart5 project data |
| `CD-XD-003` | Cleveland, Hungary, Switzerland, and VA Long Beach | Z-Alizadeh Sani, 303 patients at a distinct Tehran hospital | Used only after source-only fitting, calibration, and OOD threshold freeze | Source-distinct transport stress test; modest discrimination (AUC 0.720), weak OOD separation (AUROC 0.604), and `>=50%` vs `>50%` endpoint mismatch |
| `CD-XD-004` | Same four UCI source cohorts | AngioCAD, 377 matched records from a distinct Isfahan hospital | Used only after source-only fitting, calibration, and OOD threshold freeze | Endpoint aligned; 36 of 413 labeled IDs lack features; moderate AUC (0.787), poor calibration, and weak OOD separation (AUROC 0.589) |

## Relevant prior art

- **CARTE** addresses heterogeneous relational tables without requiring strict
  column correspondences through graph representations and open-vocabulary
  entry/column embeddings.
- **FLAT** explicitly learns dataset and column embeddings and generates a target
  predictor for heterogeneous feature spaces.
- **HyperFast** generates a target classifier from a dataset representation.
- **TabPFN/TabICL/APT/Mitra/TabDPT** learn a task prior and condition on target
  context; they are the strongest “unseen table” comparators.
- **Drift-Resilient TabPFN** targets temporal distribution shifts using shifted
  synthetic causal priors.
- **CrossAdapt** targets online architecture transfer and stream adaptation in
  recommendation systems.
- Classical domain-generalization/robust-learning methods—IRM, domain
  adversarial alignment, distributionally robust optimization and multi-source
  adaptation—are relevant conceptual baselines, but their assumptions require
  multiple source domains and a declared target-shift model.

## Cardiovascular applicability gaps

The three local CARDIODIAG files do not form three independent domains for a
clean transfer experiment. They differ in schema, endpoint naming, coding,
population/provenance and likely source overlap. A legitimate cross-dataset
study would need:

1. predictor semantic mapping and unit harmonization;
2. compatible endpoint definitions and label direction;
3. patient-overlap and source-provenance checks;
4. a frozen target adaptation policy declared before labels are read;
5. target-domain calibration and abstention evaluation;
6. temporal, geographic or institution-level split evidence.

Without those controls, “train on heart5, test on Mendeley” would be an
unjustified schema transfer experiment, not external validation.

## Evidence update: November 5, 2026

The `CD-XD-002` pilot now provides a fixed-protocol leave-one-source-out
baseline across the four UCI component cohorts. Macro ROC-AUC was 0.760;
source-only calibration reduced mean Brier score from 0.202 to 0.170. OOD
detection was inconsistent across held-out cohorts (AUROC 0.515–0.980; target
alert rate 2.4%–86.8%). Because the cohorts were already represented in
Heart5, these results do not count as new external validation. See
`TRANSFER_STUDY_RESULTS_20261105.md`.

The additional `CD-XD-003` external-cohort stress test is described in
`TRANSFER_STUDY_RESULTS_20261105_ZAS.md`. Using a documented three-feature map,
the model achieved ROC-AUC 0.720 (95% CI 0.651–0.780). Source-only Platt
calibration improved Brier and ECE point estimates, but paired intervals
included no change. The OOD detector had AUROC 0.604 and flagged 14.9% of
target rows. This provides real, source-distinct transport evidence, but it is
weak and the endpoint cut point is not identical. It does not support a claim
of reliable external generalization.

The one-way `CD-XD-004` evaluation tested AngioCAD artery-label bins against
the source `>50%` target definition. Of 413 labeled AngioCAD IDs, 377 had
clinical predictors; the source-only model achieved ROC-AUC 0.787 but had
calibration intercept/slope 1.219/1.436 after Platt scaling and ECE 0.216.
Paired calibration deltas were inconclusive. OOD AUROC was 0.589, so the
current warning does not reliably separate the unseen site. A separate run
reproduced saved predictions exactly. The study satisfies the project’s
endpoint-aligned one-site evaluation objective, while multi-hospital
generalization and dependable calibration/rejection remain open. See
`TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.

## Defensible research gap

A useful CARDIODIAG contribution could be a **schema-, unit- and reliability-
aware cross-dataset benchmark** rather than another generic ensemble. The method
would be evaluated on leave-dataset-out tasks and would have to report when
adaptation is unsafe or impossible. The benchmark itself would be valuable if
it preserves negative results and distinguishes unlabeled covariate adaptation
from label-based tuning.

## Sources

- [CARTE](https://arxiv.org/abs/2402.16785)
- [FLAT](https://arxiv.org/abs/2311.10051)
- [HyperFast](https://arxiv.org/abs/2402.14335)
- [Drift-Resilient TabPFN](https://arxiv.org/abs/2411.10634)
- [CrossAdapt](https://arxiv.org/abs/2602.01775)
- [TabPFN](https://arxiv.org/abs/2207.01848)
