# CARDIODIAG staged completion and readiness workflow

**Assessment date:** 2026-11-05  
**Current decision:** `NO-GO — research prototype only`  
**Purpose:** finish the locally actionable work while making real-world readiness
an evidence-gated claim, not a project label.

## Problem diagnosis

The main gap is evidence and product definition, not a missing classifier.
The repository has a runnable source-only model, calibration and conformal
abstention, and a trusted-site gate. The measured limits are material:

1. The current project is scoped to offline research, but there is no approved
   clinical intended use, setting, intended user, patient population, or
   decision threshold. The experiments use different feature sets and study
   endpoints.
2. No untouched, endpoint-identical external cohort is available in the
   screened public data. CD-XD-003 tested Z-Alizadeh Sani, but its threshold is
   `>=50%` versus the source `>50%`; AngioCAD was examined before its CD-XD-006
   replay; Duke ACATH uses a different threshold; all 270 Statlog rows match
   Cleveland.
3. The feature-only shift detectors are weak. The trusted metadata gate
   abstains on every unregistered hospital, so the system currently cannot
   deliver automatic output at a new site.
4. There is no prospective clinical evaluation, subgroup safety evidence,
   human-factors work, production security/safety case, regulatory
   determination, or post-deployment monitoring plan.

These findings mean the current code can demonstrate a fail-closed research
policy, but cannot support a claim of dependable clinical generalization.

## Phase gates and current state

Every phase has a target, evidence, and an accountable role. Human owners are
currently unassigned except for the local engineering audit. Assign a named
human approver before treating a phase as passed; the ledger checker does not
verify identity or signatures. The project is real-world ready only when every
phase is `passed`.

| Phase | Accountable role (human owner unassigned) | Target | Current state | Evidence / next action |
|---|---|---|---|---|
| G0 — Diagnose and bound the claim | Project QA reviewer (local audit completed) | Accurately state what the present evidence establishes and what it does not | **Passed locally** | Current result and software evidence mapped in `MASTER_DIRECTIVE_COMPLETION_MATRIX.md`; no clinical-readiness claim |
| G1 — Intended use and requirements | Project lead + cardiology lead | One approved population, care setting, user, outcome, prediction time, action, exclusions, jurisdiction, and comparator | **Partial** | Current scope is offline research only; define and approve a clinical intended use before claiming readiness. See `INTENDED_USE_SCOPE.md` |
| G2 — Data access, provenance, and rights | Data steward + project lead | 100% of data inputs have verified provenance, lawful access, license/DUA, and redistribution rules; no unresolved patient overlap | **Partial** | A row audit maps all Heart5 records to UCI records (914 unique, 4 ambiguous); the 2026 Mendeley 918-row copy exactly duplicates Heart5. The 2021 Mendeley CSV/codebook hashes now match the official API, but that codebook omits its diagnostic reference standard. A six-ZIP audit found no byte-identical Heart5 or Kaggle 70K raw file and verified Mendeley attribution; 70K-derived result files remain in four historical packages. Heart5 transformation history, 70K rights, and cross-dataset patient linkage remain unresolved |
| G3 — Endpoint and feature alignment | Clinical informatician + cardiology lead | 100% of predictors have units, timing, codebook, and missingness policy; one explicit outcome definition; zero patient overlap across partitions | **Partial** | Freeze a common feature/endpoint map approved by clinical reviewers; the 2021 Mendeley reference standard is unspecified, CD-XD-003 and Duke have endpoint-boundary differences, and current studies use different feature sets |
| G4 — Model and policy lock | ML lead + statistician | One versioned model, feature map, calibration procedure, threshold, and abstention policy frozen before external labels are examined | **Partial** | Choose one intended-use pipeline; archive the protocol and model hash before any new external evaluation |
| G5 — Internal validation | Statistician + ML lead | Patient/group-aware nested evaluation, at least five prespecified random seeds where random splitting applies, uncertainty intervals, calibration, baselines, and subgroup accounting | **Partial** | Five 3×3 split-sensitivity runs (seeds 43–47) completed with exact prediction and metric audits; patient/group identifiers, patient-level uncertainty, and intended-subgroup accounting remain unavailable |
| G6 — Independent external evaluation | Independent site PI + statistician | At least two independent health systems or cohorts, with one fully untouched primary test; endpoint-compatible labels; sample size set by precision/power analysis | **Blocked** | CD-XD-003 is a useful source-distinct stress test (AUC 0.720), but its endpoint boundary differs; secure a compatible, untouched cohort, lock protocol first, and compute sample size to meet prespecified precision |
| G7 — Calibration, uncertainty, and operating envelope | Cardiology lead + statistician | Prespecified sensitivity/coverage/risk criteria, calibration, and shift tests meet use-specific limits; unknown or unsupported domains always fail closed | **Partial** | Agree clinically justified limits before seeing target outcomes; current AngioCAD coverage is 5.6%, Duke stress test calibration worsened, OOD separation is weak |
| G8 — Subgroup, usability, and human factors | Human-factors lead + patient/public representative | Adequate precision in each intended subgroup; workflow usability and failure communication reviewed by clinicians and representative users | **Not started** | Define groups and minimum precision from intended use; conduct structured human-factors evaluation |
| G9 — Prospective clinical evaluation | Site PI + ethics committee | Approved prospective silent-mode study at intended sites; no model-driven care; outcomes adjudicated; performance and workflow harms reported | **Not started** | Requires a clinical partner, ethics approval, protocol registration, data agreements, and prospective data collection |
| G10 — Software safety, privacy, security, and quality system | Software quality + privacy/security leads | Requirements traceability, hazard analysis, privacy/security review, tested controls, version/change control, incident handling, rollback, and release audit | **Not started** | Create a risk-based software lifecycle and quality system appropriate to intended use; close every unacceptable hazard |
| G11 — Regulatory determination and authorization | Manufacturer + regulatory affairs specialist | Qualified review determines jurisdiction/classification and all required investigation/manufacture/marketing permissions are obtained before clinical use | **Not started** | Select jurisdiction and manufacturer; obtain regulatory counsel; follow applicable authority process |
| G12 — Controlled release and monitoring | Product operations + post-market safety lead | Staged deployment, live drift/performance monitoring, escalation and rollback limits, incident review, and periodic re-evaluation | **Not started** | Begin only after G1–G11 pass; define operational owners and stop thresholds before release |

## Required quantitative targets

These are project gate targets, not universal clinical cutoffs. Clinical
acceptance limits must be selected before external evaluation by the intended
clinical owners and statistician.

- **Data integrity:** zero patient overlap between training, calibration, and
  external test; 100% input files hashed and traced; all label and predictor
  definitions reviewed.
- **Evaluation design:** no target-label-driven model, feature, threshold,
  or calibration selection; one prespecified primary metric; report confidence
  intervals and all planned secondary metrics.
- **External sample size:** for planning, target a 95% confidence-interval
  half-width no greater than `0.05` for ROC-AUC and `0.20` for calibration
  slope. Also require the lower confidence bound for the use-specific primary
  safety metric to meet its clinician-approved minimum. These are provisional
  study-planning precision targets, not universal performance or safety
  cutoffs; the clinical protocol may require stricter limits. Compute sample
  size from expected prevalence and positive/negative counts rather than a
  fixed total row count.
- **Selective operation:** set minimum automatic coverage `C_min` and maximum
  selective error `R_max` with clinicians. Require the lower confidence bound
  on coverage to meet `C_min` and the upper confidence bound on selective risk
  to be below `R_max`; report by site and intended subgroup.
- **Calibration:** prespecify acceptable calibration intercept/slope, Brier
  score, and calibration curves relative to a baseline. Any recalibration must
  use a separate calibration sample and be evaluated on a later untouched
  sample.
- **Domain safety:** 100% of unknown-site, invalid-schema, missing-required
  input, and out-of-support cases return no actionable score and a clear
  abstention reason. Any new-site gate threshold must be validated on held-out
  sites, not just synthetic examples.
- **Software release:** zero open unacceptable hazards, zero unresolved
  critical security findings, all safety requirements traceable to tests, and
  a verified rollback/incident path.

## Step-by-step execution order

1. **Keep the current release research-only.** Run
   `uv run python experiments/evaluate_readiness.py`; it must report
   `real_world_ready: false` while any gate remains open.
2. **Resolve G1 before further modeling.** Get the intended-use, population,
   action, outcome, and jurisdiction approved. If the project remains a
   non-clinical research prototype, say so explicitly and do not describe it as
   deployable.
3. **Resolve G2–G3 before training for a clinical claim.** CD-XD-003 already
   supplies a source-distinct transport stress test, but its `>=50%` target
   does not exactly match the source `>50%` endpoint and patient-level linkage
   is unavailable. For a clinical claim, obtain authorized compatible data,
   check overlap, codebook, endpoint, timing, and units, then freeze the
   harmonization map. If no compatible cohort can be obtained, limit the claim
   to the existing stress-test evidence instead of relabeling an incompatible
   dataset.
4. **Freeze G4.** Register the exact protocol, model, calibration, uncertainty
   policy, and acceptance limits before opening the external test labels.
5. **Complete G5–G7.** Run repeated internal validation and then the untouched
   external evaluation; publish all outcomes, including failure and abstention.
6. **Complete G8–G9 with the clinical partner.** Evaluate subgroup precision,
   usability, and prospective silent-mode performance before any model output
   can influence patient care.
7. **Complete G10–G12.** Establish software lifecycle controls, privacy and
   security review, jurisdiction-specific authorization, controlled release,
   monitoring, and rollback. A performance paper alone does not satisfy these
   gates.

## Current machine-readable gate record

`docs/real_world_readiness_gates.json` holds each phase status and evidence
path. `src/cardiodiag/readiness.py` checks that ledger and evidence files;
`experiments/evaluate_readiness.py` prints the computed overall decision and
writes a report with the ledger and evidence SHA-256 values to
`results/REAL_WORLD_READINESS_REPORT.json`. The checker verifies evidence-file
existence and hash capture; it does not replace clinical, statistical, ethical,
or regulatory review.

## Reference basis

- TRIPOD+AI is a reporting checklist for prediction-model development and
  evaluation; it does not certify clinical readiness: [statement](https://www.bmj.com/content/385/bmj-2023-078378).
- IMDRF describes clinical evaluation for software as a medical device:
  [final framework](https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation).
- For India, CDSCO publishes medical-device software guidance under the
  Medical Devices Rules, 2017: [CDSCO guidance index](https://cdsco.gov.in/opencms/opencms/en/Medical-Device-Diagnostics/InVitro-Diagnostics/).
- FDA's CDS guidance is relevant only if the intended product/function falls
  within US jurisdiction: [final guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software).

This document is an engineering workflow, not legal, clinical, or regulatory
approval. The project owner's current scope input is recorded in
`INTENDED_USE_SCOPE.md`; it limits current use to offline research and does not
define a future clinical product.
