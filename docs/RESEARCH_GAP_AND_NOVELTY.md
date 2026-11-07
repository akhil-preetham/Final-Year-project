# Research gap and novelty audit

**Review date:** 2026-11-02  
**Review type:** targeted literature and repository evidence review; not a
systematic review or a guarantee of novelty or journal acceptance.

## What the base study contributes

The supplied CARDIODIAG study combines XAI-guided hybrid dimensionality
reduction with optimized ensemble classifiers for cardiovascular disease
prediction. The local repository preserves its notebooks and historical
artifacts, but the historical workflow is not bit-for-bit reproducible from the
available files: preprocessing order, split definitions, search spaces, and
saved totals are not fully consistent.

## Repository contribution categories

| Category | CARDIODIAG status | Defensible wording |
|---|---|---|
| Established method | Nested validation, one-hot preprocessing, calibration, conformal/selective prediction, Nogueira stability | Reused methodological tools with explicit boundaries |
| Reproduction | Historical OVEC/OSEC/XAIH-DRC workflows | Approximate historical reproduction; not exact numerical reproduction |
| Engineering improvement | Explicit schema manifest, training-only transformations, fail-closed external gate, machine-readable provenance | Reproducibility and leakage-control improvements |
| Empirical contribution | Paired stability and reliability analysis under matched repeated splits | Stability of selected features is tested separately from predictive/selective reliability |
| Unverified claim | New algorithmic novelty or generalization | Not claimed without broader literature comparison and independent data |

## Narrow research question

> Under a leakage-controlled evaluation protocol, does increasing feature-set
> stability in the CARDIODIAG representation produce a consistent improvement
> in discrimination, calibration, confidence ranking, or selective risk?

This is falsifiable and does not require the stable selector to win. The current
evidence is mixed for stability and does not show a consistent reliability
benefit. The appropriate contribution is therefore a **stability--reliability
decoupling audit**, not a new classifier claim.

## Literature boundary

Recent literature makes the gap narrower, not broader:

- TRIPOD+AI (2024) emphasizes complete reporting for prediction model
  development and evaluation: <https://doi.org/10.1136/bmj-2023-078378>.
- PROBAST+AI (2025) provides updated risk-of-bias and applicability assessment
  for regression and AI prediction models: <https://doi.org/10.1136/bmj-2024-082505>.
- A 2024 BMC Medicine review of cardiovascular AI models reported major
  reproducibility and independent-validation deficiencies:
  <https://doi.org/10.1186/s12916-024-03273-7>.
- A 2024--2025 review/meta-analysis of cardiovascular EHR prediction reported
  substantial heterogeneity and continuing concerns about calibration and
  external validation:
  <https://academic.oup.com/ehjdh/article/6/1/7/7845948>.
- A 2025 systematic review comparing cardiovascular risk prediction models
  found that discrimination and calibration require separate attention:
  <https://pubmed.ncbi.nlm.nih.gov/39929598/>.
- External-validation reviews show performance can decrease and vary materially
  across relatedness and setting: <https://doi.org/10.1161/CIRCOUTCOMES.121.007858>.

Feature-selection stability, conformal prediction, calibration, SHAP/LIME, and
ensembles are all established methods. Combining them in one repository is not
by itself novelty. The potentially publishable angle is the preregistered,
leakage-controlled empirical test of whether stability is a useful proxy for
reliability, including a negative or inconclusive result.

## Evidence decision

| Claim | Decision | Reason |
|---|---|---|
| Stable selector is more stable on every dataset | Reject | Internal stability advantage is dataset-conditional |
| Stable selector improves prediction reliability | Reject | Paired linkage does not show a consistent benefit |
| Confidence/abstention is empirically informative internally | Narrowly supported | Confidence-error AUC exceeds chance in saved internal repeats |
| Results generalize to new populations | Limited evidence only | One endpoint-aligned external hospital was tested; it does not establish broader transportability |
| A new algorithm is introduced | Reject | Existing components are adapted and audited, not algorithmically novel |

## Required future evidence

1. Replicate the locked evaluation across more independent hospitals or a
   prospective cohort before making a broad generalization claim.
2. Verify endpoint, predictor definitions, units, population, overlap, access,
   and license.
3. Run the one-way evaluator without fitting on external rows.
4. Compare the observed external result with the predeclared internal claim and
   retain negative results.
5. Complete a venue-specific TRIPOD+AI/PROBAST+AI and ethics/data-use review.

## Evidence update: November 5, 2026

The active direction selected for the project is **generalization-aware and
uncertainty-calibrated cardiovascular prediction under dataset shift**. A
fixed logistic baseline was trained on three source cohorts and evaluated on
the fourth in each of four leave-one-source-out folds. Source-only Platt
calibration improved macro Brier score from 0.202 to 0.170, while calibrated
ECE remained 0.152 on average. A source-only Isolation Forest had macro
held-out-domain AUROC 0.758, with per-domain AUROC from 0.515 to 0.980 and
alert rates from 2.4% to 86.8%. Full results and confidence intervals are in
`docs/TRANSFER_STUDY_RESULTS_20261105.md`.

This supports the feasibility of a dataset-level evaluation pipeline but does
not support a dependable abstention policy or a broad generalization claim. The
four cohorts are represented in the project's historical Heart5 composite, so
the analysis is retrospective rather than independent external validation.
The baseline uses established components; algorithmic novelty remains
unverified.

A targeted literature check further narrows the novelty claim. A 2026
uncertainty-aware feature-weighted heart-disease ensemble reports
leave-one-center-out validation across four clinical sites
([UAFE](https://pmc.ncbi.nlm.nih.gov/articles/PMC13106842/)); a 2026 preprint
evaluates calibrated multi-task CVD prediction across NHANES and MIMIC-IV
([CardioMeta](https://arxiv.org/abs/2607.15721)). Thus the broad combination
of CVD prediction, uncertainty, calibration, and dataset shift is already
occupied. A 2024 health-data study also introduced an OOD reject option and
tested rejection curves under dataset shift ([ODROP](https://arxiv.org/abs/2405.19864)).
The project's possible contribution must be more specific than combining
standard components and must be demonstrated on an independent cohort. The AHA
scientific statement likewise calls for external evaluation in a distinct,
relevant setting with aligned predictors and outcome ascertainment
([statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC13067998/)).

## Evidence update: November 5, 2026 — source-distinct cohort

The frozen `CD-XD-003` study trained on the four UCI source cohorts and scored
the Z-Alizadeh Sani cohort from a distinct Tehran hospital once. With only age,
sex, and fasting-glucose status, logistic-regression ROC-AUC was 0.720 (95%
class-stratified bootstrap CI 0.651–0.780). Source-only Platt calibration
reduced Brier score from 0.200 to 0.193, but the paired interval for the change
included zero. The source-calibrated OOD AUROC was 0.604, with 14.9% of target
rows flagged at a 5.3% source false-alert rate. Full results are in
`TRANSFER_STUDY_RESULTS_20261105_ZAS.md`.

This supplies source-distinct transport evidence, but not an endpoint-identical
external validation: UCI defines the source positive class at `>50%` stenosis,
whereas the target uses `>=50%`. The available data do not expose individual
stenosis percentages for reconciliation or patient IDs for overlap checks.
The observed discrimination is modest, calibration improvement is
inconclusive, and OOD separation is weak. The broad proposed direction has no
algorithmic novelty claim; the defensible current output is an auditable
evaluation with mixed results and an explicit validation boundary.

## Evidence update: November 5, 2026 — endpoint-aligned cohort

The frozen `CD-XD-004` evaluation used AngioCAD's artery-level labels to define
the same `>50%` stenosis target as the UCI source cohorts. The cohort is from a
separate Isfahan hospital; 377 patients had both predictors and labels, while
36 additional labeled IDs had no feature row. The locked age/sex/FBS model
achieved ROC-AUC 0.787 (95% class-stratified bootstrap interval 0.734–0.838).
Source-only Platt calibration made small, inconclusive changes to Brier and
log-loss and slightly worsened ECE. OOD AUROC was 0.589 (95% interval
0.541–0.635), which is weak separation. A separate rerun reproduced the
prediction CSVs byte-for-byte. See
`docs/TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.

This closes the endpoint-aligned cohort acquisition/evaluation gap for one
site, not the reliability or external replication gaps. The method contribution
is an auditable, source-only, multi-dataset transport and reliability
evaluation. The classifier, Platt scaling, and Isolation Forest are established
methods; no algorithmic novelty is claimed. OOD detection and calibration are
not dependable on the held-out site, and broader generalization remains
unverified.
