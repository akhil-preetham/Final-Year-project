# Candidate new algorithm directions

These are research directions only. No direction is implemented in this phase.

## 1. SAGE-Transfer: Semantic Alignment and Guarded External Transfer

**Hypothesis:** A model should adapt across cardiovascular tables only after
explicitly aligning feature semantics, units, missingness mechanisms and target
definitions; otherwise it should abstain.

**Mechanism:** Learn a schema graph with typed feature nodes and unit/endpoint
constraints; transfer representations only across an approved mapping. Use a
conformal or risk-controlled gate to refuse incompatible mappings.

**Mathematical idea:** Optimize target risk plus mapping uncertainty and a hard
compatibility constraint; estimate a transport bound from source/target feature
and label-shift diagnostics.

**Difference from prior work:** CARTE/FLAT transfer across heterogeneous schema;
the potential gap is a clinically typed, fail-closed semantic and reliability
gate with explicit non-transfer decisions.

**Difficulty/cost:** High; requires verified multi-cohort data and ontology/unit
work. **Risk:** semantic mapping becomes hand-coded and not general.

## 2. MetaRisk Router

**Hypothesis:** A dataset-level router trained on leave-dataset-out tasks can
choose among target-trained GBDT, linear, retrieval, PFN and abstention strategies
more reliably than a static meta-feature model.

**Mechanism:** Train a meta-learner on TabRepo/OpenML/TALENT task records using
out-of-fold performance, calibration, runtime and failure indicators. Predict a
distribution over candidate utility, not only a point score.

**Mathematical idea:** Minimize a proper scoring rule for candidate utility and
constrain regret/abstention probability on held-out datasets.

**Difference:** More rigorous than AURA's within-dataset inner utility; directly
tests leave-dataset-out model selection.

**Difficulty/cost:** Medium-high; repository-scale data engineering. **Risk:**
meta-dataset leakage and poor transfer beyond benchmark families.

## 3. ShiftCal-Tab

**Hypothesis:** Jointly estimating covariate/label shift and calibration drift
can improve external probability reliability without changing ranking.

**Mechanism:** A frozen source predictor feeds a shift detector, prevalence
estimator and recalibration head; a conformal/selective layer abstains when
shift uncertainty is high.

**Mathematical idea:** Minimize proper scoring loss under a distributionally robust
set of shift weights, with a coverage constraint for selective predictions.

**Difference:** Focuses on calibrated transport and refusal, not generic model
fusion. Related to Drift-Resilient TabPFN but could be architecture-agnostic.

**Difficulty/cost:** Medium. **Risk:** shift estimators need unlabeled/labelled
target assumptions that may fail clinically.

## 4. PriorAudit-TabPFN

**Hypothesis:** A dataset-profiled choice or mixture of tabular foundation-model
priors can reduce failure on clinical distributions while preserving zero-shot
speed.

**Mechanism:** Select among pretrained PFN/ICL models or prior mixtures using
training-only meta-features and a small calibration context; maintain a fallback
to CatBoost/GLM when prior mismatch is detected.

**Mathematical idea:** Bayesian model averaging over prior families with a
calibration/shift evidence penalty and a utility-cost Pareto rule.

**Difference:** Builds on TabPFN/TabICL/Mitra rather than claiming an original
foundation model; novelty could be prior-mismatch auditing and fallback safety.

**Difficulty/cost:** High GPU/dependency burden. **Risk:** model licenses,
version drift and target-data leakage.

## 5. RelationalCardio Memory

**Hypothesis:** When cardiovascular records share entities, institutions,
measurements or longitudinal visits, a provenance-aware relational memory can
improve transfer while preventing patient-level leakage.

**Mechanism:** A graph/table representation retrieves only source entities that
   pass privacy, time and cohort compatibility constraints; a frozen or lightly
   adapted predictor uses memory with an abstention gate.

**Mathematical idea:** Constrained retrieval objective with graph distance,
domain compatibility and leakage barriers; uncertainty increases when no safe
neighbors exist.

**Difference:** Extends CARTE/TabR-like retrieval with explicit clinical
provenance and no-neighbor refusal.

**Difficulty/cost:** High and data-dependent. **Risk:** patient overlap/privacy
and unavailable relational identifiers.

## Ranking matrix

| Direction | Novelty potential | Defensibility | Generalization | Feasibility | Compute | Publication potential |
|---|---:|---:|---:|---:|---:|---:|
| SAGE-Transfer | 5 | 5 | 5 | 2 | 3 | 5 |
| MetaRisk Router | 4 | 4 | 5 | 4 | 3 | 5 |
| ShiftCal-Tab | 4 | 5 | 4 | 4 | 3 | 5 |
| PriorAudit-TabPFN | 3 | 4 | 4 | 2 | 1 | 4 |
| RelationalCardio Memory | 5 | 3 | 4 | 1 | 2 | 4 |

Scores are qualitative (1 low, 5 high) and reflect evidence, not measured
performance.
