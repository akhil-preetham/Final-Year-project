# Final algorithm recommendation before implementation

## Recommendation

Do **not** implement another generic AURA/MOSAIC-style ensemble yet. The
strongest research direction is **SAGE-Transfer: Semantic Alignment and Guarded
External Transfer**, preceded by a **MetaRisk Router** benchmark layer.

The recommended project should be framed as:

> A provenance-, schema-, unit- and reliability-aware evaluation and guarded
> transfer framework for cardiovascular tabular prediction under leave-dataset-
> out and distribution-shift protocols.

## Why this is preferable to AURA-ML

1. AURA V1/V2 already showed that within-dataset adaptive selection often routes
   to a single strong baseline and does not consistently beat it.
2. Profiling, candidate selection, fusion and calibration are established prior
   art in AutoML, meta-learning and tabular foundation models.
3. The real CARDIODIAG limitation is not another model on the same rows; it is
   lack of verified transportability, compatible schema mapping and reliability
   under shift.
4. A guarded transfer mechanism can make a scientifically meaningful negative
   decision—“do not transfer”—instead of producing a confident but invalid
   prediction.
5. The contribution can be tested against TabPFN, TabICL, HyperFast, FLAT,
   CARTE, CatBoost, XGBoost, logistic regression and AutoML model portfolios.

## Required next evidence

Before implementation:

- obtain or freeze at least several genuinely compatible cardiovascular cohorts;
- document predictor units, endpoint definitions, population and overlap;
- create leave-dataset-out meta-train/meta-test partitions;
- predeclare allowed unlabeled target adaptation and labelled calibration;
- include no-transfer and refusal baselines;
- evaluate AUROC, PR-AUC, Brier, ECE, calibration slope/intercept, selective
  risk, coverage, runtime, memory and failure rate;
- compare against executable foundation models under identical data budgets;
- preserve provenance and licensing records.

## Publication readiness

The project is **not ready** to claim a new algorithm or submission readiness.
It is ready for a literature-grounded redesign proposal and a benchmark/data
freeze phase. The current AURA results should remain reported as exploratory
internal evidence and a useful negative/conditional finding.

## Decision gate

Implementation should begin only if a pilot leave-dataset-out study shows that:

1. the semantic compatibility gate can be evaluated reproducibly;
2. target adaptation rules can be frozen without label leakage;
3. there is a measurable failure mode not already handled by CARTE, FLAT,
   HyperFast, TabPFN/TabICL or standard domain adaptation;
4. the proposed gate improves a predeclared reliability or selective-risk target
   without sacrificing honest negative results.

If those conditions fail, the publishable contribution should be a rigorous
CARDIODIAG cross-dataset benchmark and audit—not a renamed model.
