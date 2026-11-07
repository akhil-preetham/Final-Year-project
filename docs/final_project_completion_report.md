# CARDIODIAG final project completion report

## What is completed

- Historical source/notebook audit and explicit separation of historical versus corrected evidence.
- Leakage-controlled package and nested internal experiments with saved predictions/splits.
- Source-distinct transfer studies, one endpoint-aligned external hospital study, calibration/shift/selective analyses, and synthetic controlled-shift diagnostics.
- Source-only Platt/isotonic/beta/temperature comparison with equal cohort weights and class-stratified target bootstrap.
- Data provenance, overlap screens, test/lint/compile checks, audit manifests, paper build and local review.
- Hostile review and explicit issue/acceptance registers.

## What experiments establish

Corrected internal discrimination is strong on the included development datasets. One AngioCAD evaluation achieved AUC 0.787, but calibration remained poor and feature-only domain discrimination was weak. Source temperature calibration improved point metrics on this already examined site only; it is exploratory. Synthetic shift detection is sensitive to some large marginal/unit shifts and weak for some variance/correlation changes. Integrated selective coverage remained 5.6%.

## Criticalities remaining

- Reliable unseen-site prediction: NO-GO; second untouched compatible hospital cohort unavailable.
- Exact original algorithm reproduction: PARTIAL/BLOCKED; original notebooks conflict and key specifications/table lineage are missing.
- Data independence: patient-level linkage unavailable across sources.
- Publication readiness: BLOCKED by factual author/institution declarations, some licensing and no selected venue.
- Release reproducibility: local tree uncommitted and connected to original-source Git history.

## Safe claims

The project provides an auditable, corrected research prototype and documents a one-site external evaluation with mixed/negative reliability results. The experimental pipeline separates internal validation, external evaluation and synthetic shift diagnostics.

## Claims not supported

Do not claim robust unseen-site generalization, reliable external calibration, dependable feature-only OOD rejection, useful selective operation, exact original-paper reproduction, a novel superior algorithm, clinical validation, or deployment readiness.

## Completion decision

**Technical research prototype:** operational with passing local QA.  
**Scientific generalization objective:** not achieved; NO-GO.  
**Journal submission:** not ready until external evidence and factual declarations are addressed.  
**Clinical readiness:** NO-GO and outside the demonstrated evidence.

See FINAL_AUTONOMOUS_PROJECT_AUDIT.md, FINAL_HOSTILE_REVIEW_REPORT.md, UPDATED_FINAL_ACCEPTANCE_MATRIX.md and USER_INPUT_AND_RESOURCE_REQUIREMENTS.md for itemized evidence and actions.
