# Updated second-stage acceptance matrix

**Assessment date:** 2026-11-06. Statuses apply to evidence, not aspirations.

| Area | Status | Current evidence |
|---|---|---|
| Root causes and machine-readable issue register | PASS | SECOND_STAGE_ROOT_CAUSE_REPORT.md and SECOND_STAGE_ISSUE_REGISTER.json; JSON parsed successfully |
| Source-only calibration alternatives | PARTIAL | Platt, isotonic, beta and temperature evaluated with equal source-domain weights; one target was already examined |
| Temperature-scaling transfer benefit | BLOCKED for confirmatory claim | AngioCAD point metrics improved, but no untouched site is available to validate this choice |
| Calibration intervals | PASS for descriptive stratified bootstrap | Frozen prediction files, 2,000 class-stratified resamples; no between-site inference |
| Broad OOD detector comparison | PARTIAL | KNN/Isolation Forest real-target audits plus synthetic KNN, Mahalanobis, Isolation Forest, PCA, domain-classifier and missingness comparison. No real-target evaluation of the broader detectors or individual error detection |
| Selective coverage diagnosis | PARTIAL | Existing component table shows singleton conformal 8.8%, KNN support 93.4%, combined 5.6%; no new source-only policy was confirmed externally |
| Generalization method improvement | BLOCKED for external conclusion | No additional independent endpoint-compatible cohort; no adaptation method may be selected on AngioCAD |
| External data acquisition | BLOCKED | MultiD4CAD requires DUA and endpoint confirmation; no access requested or data acquired |
| Historical reconstruction | PARTIAL | Existing notebook audit; exact method still blocked by conflicts and missing parameters |
| Software tests | PASS | Full pytest module invocation exited 0; warnings are openpyxl conditional-formatting warnings on read-only workbook tests |
| Ruff | PASS | Full repository check passed |
| Compilation | PASS | src, experiments and tests compile |
| Publication readiness | BLOCKED | Factual author, ethics, funding, data-use and venue confirmations remain pending; scientific external evidence is limited |

## Decision

The evidence moved forward by independently reproducing the source Platt map and testing source-only alternatives. A temperature map improved fixed metrics on the already examined AngioCAD data; this is a hypothesis for future validation, not confirmatory improvement. Reliable unseen-site prediction remains **NO-GO**. The OOD comparison and a useful selective operating point remain incomplete. No external dataset or target label was fabricated or acquired under restricted access.
