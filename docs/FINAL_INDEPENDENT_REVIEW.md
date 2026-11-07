# Second-stage independent review

**Review date:** 2026-11-06. The reviewer treated the reported conclusions as falsifiable and checked the current source calibration predictions, target predictions, methods and audit trail.

## Checks completed

- Reran the complete automated test command through the working Python module entrypoint; process exited 0. Three openpyxl warnings note unsupported workbook conditional-formatting extensions while reading; test files are not written.
- Reran full Ruff and Python compilation; both passed.
- Reran the CD-XD transfer artifact audit, five-seed summary audit and validity sensitivity audit; each passed.
- Added a source-only calibration comparison with equal cohort weights, then confirmed refitted Platt reproduces the frozen map to rounding.
- Confirmed target labels enter the new calibration comparison only after maps are fit, for retrospective metrics/bootstrap intervals; no target method selection was performed.
- Recorded hashes for source calibration predictions, external predictions and the new runner.

## Findings that constrain claims

The AngioCAD calibration comparison is post hoc because the cohort has already been examined. Source temperature scaling gave lower target Brier/log-loss/ECE point estimates than Platt, yet calibration slope remained 2.17 and this single site cannot establish transport improvement. The final report labels it exploratory.

The current OOD evidence concerns source-versus-target discrimination, not individual anomaly detection, prediction-error detection, or concept-shift detection. KNN and Isolation Forest do not show useful discrimination on AngioCAD. Synthetic covariate-shift experiments have not been run in this second-stage continuation.

The 5.6% integrated selective coverage is explained by conjunctive filtering: conformal-singleton coverage is 8.8%, KNN support alone accepts 93.4%, and their combination accepts 5.6%. The unregistered-domain allowlist is a separate all-abstain gate. Zero observed errors among 21 accepted, all-positive rows is not evidence of safety.

No new independent endpoint-compatible site was acquired. Exact original LoRAS/XAIH-DRC reproduction and patient-level cross-release linkage remain unavailable. The workspace remains uncommitted.

## Reviewer verdict

Software and the second-stage calibration analysis are reproducible in the local environment. The work does **not** resolve the scientific NO-GO for dependable unseen-site prediction, and it is not ready for journal submission until external cohort evidence and pending factual declarations are resolved. The updated acceptance matrix is UPDATED_FINAL_ACCEPTANCE_MATRIX.md; unresolved causes are tracked in SECOND_STAGE_ISSUE_REGISTER.json.
