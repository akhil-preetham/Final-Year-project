# CARDIODIAG research-direction decision

**Decision date:** 2026-10-27

## Decision

Use **Candidate A, a leakage-controlled stability/reliability audit of XAIH-DRC**
as the primary contribution, with **Candidate C, a separately calibrated
selective-prediction analysis**, as one complementary contribution. Treat the
fold-local baseline correction as a required methodological foundation. Do not
promote the work to a new classifier claim, and do not use Candidate D’s name
for an external-validation claim while no independent cohort is frozen.

## Why this direction is strongest

- It addresses the most distinctive and least reproducible part of the original
  CARDIODIAG workflow rather than adding another generic ensemble.
- It can be evaluated using the available data without pretending that Mendeley
  or the Five States composite is independent external evidence.
- It has a falsifiable success condition: improved selected-set stability must be
  reported together with predictive, calibration, and selective-reliability
  outcomes; a failure to translate is itself a result.
- Existing results already show that performance gains are not uniform, making a
  reliability/stability decoupling question more defensible than an accuracy
  optimization claim.
- Candidate C provides practical reliability information without conflating
  conformal coverage or confidence ranking with clinical safety.

## Candidate comparison

| Direction | Gap | Expected contribution | Cost | Main confounder | Falsifiable hypothesis | Decision |
|---|---|---|---|---|---|---|
| A: stable XAIH-DRC | Reproducibility of CARDIODIAG’s distinctive reduction under correct data boundaries | Dataset-conditional stability evidence and its relationship to held-out reliability | Moderate/high; repeated inner relevance fits | Selection thresholds and correlated features | Stable selection improves stability without materially worsening primary discrimination and improves at least one prespecified reliability endpoint | **Primary** |
| B: calibration-aware selection | Existing candidates are chosen on ROC-AUC while reliability is post hoc | Protocol-level comparison of discrimination/reliability trade-offs | Moderate; dedicated calibration folds and multi-objective tuning | Objective weighting, overfitting calibration, multiplicity | A prespecified calibration guardrail improves Brier/calibration slope while preserving a non-inferior ROC-AUC margin | Defer; useful ablation if compute permits |
| C: selective prediction | Reliability under an explicit abstention policy is underreported | Internal risk–coverage and split-conformal evidence with assumptions | Low/moderate | Exchangeability and finite calibration sample | Lower coverage reduces error risk and nominal conformal coverage is observed internally, with degradation exposed under shift | **Complementary** |
| D: distribution shift | Transportability is untested | Robustness and external-validation evidence | High; needs compatible frozen cohort | Target leakage and endpoint mismatch | Performance/calibration remain useful under prespecified shift | Defer until eligible data are frozen |

## Primary endpoint and acceptance rules

Primary endpoint: paired difference in **ROC-AUC** between stable and matched
one-shot/corrected candidates on identical outer evaluation partitions. Report
the mean difference and a paired interval; do not select a headline method from
the pooled outer score alone.

Secondary endpoints: Nogueira stability, selected-feature count, PR-AUC, Brier
score, calibration intercept/slope, ECE with its binning definition,
confidence-error AUC, AURC, risk at fixed coverage, and conformal coverage and
set size.

Positive stability evidence requires the prespecified paired stability interval
to exclude zero. A practical performance claim additionally requires no
meaningful deterioration in the primary discrimination endpoint and must be
reported separately from stability. A positive result on only one benchmark is
dataset-conditional. A mixed or null result is the expected honest outcome if
the evidence does not support superiority.

## Required implementation and validation sequence

1. Add explicit feature-type manifests for both local datasets and ensure coded
   nominal/ordinal columns are not treated as continuous.
2. Make the stable selector’s relevance estimate validation-only within each
   training resample; retain the current one-shot comparator as a matched
   baseline.
3. Add scientific-invariant tests for feature typing and the no-in-sample
   relevance boundary.
4. Rerun smoke tests, nested internal validation, repeated stability evidence,
   repeated reliability evidence, and paired linkage using the corrected schema.
5. Rebuild all summary tables directly from the new artifacts.
6. Run synthetic missingness/measurement perturbation analyses only as stress
   tests, labeling them separately from external validation.
7. Reassess the claim with the hostile reviewer checklist. Freeze an external
   manifest only if an independent compatible cohort is actually supplied.

## Explicit non-goals

- No deep-learning or transformer addition without a scientific need.
- No selection of an algorithm, threshold, or feature rule after seeing external
  labels.
- No use of ensemble disagreement as a calibrated uncertainty probability.
- No clinical-readiness, causal, fairness, or prospective-utility claim from
  the current benchmark evidence.
