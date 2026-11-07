# Second-stage remediation experiment matrix

| Study | Data boundary | Method(s) | Current execution/evidence | Disposition |
|---|---|---|---|---|
| Source calibration comparison | Fit all maps on 185 source-calibration rows; score frozen 377-row AngioCAD predictions | Platt, isotonic, beta, temperature, raw baseline | Executed 2026-11-06; equal total source-domain weights; 2,000 class-stratified target bootstrap replicates; full metrics, curves and hashes saved | PARTIAL, exploratory because target already examined |
| Calibration refit parity | Same source rows | Refit Platt versus originally frozen Platt | Brier 0.185146 versus 0.185146; scores reproduce to rounding | PASS consistency check |
| Feature-only domain separation | Source calibration versus AngioCAD | Isolation Forest and KNN distance | Existing independent audit: AUROC 0.589 and 0.580 respectively | FAIL for useful detector claim |
| Selective component ablation | Frozen AngioCAD labels used only for post-hoc audit | Conformal, KNN, Isolation Forest, combinations, registration gate | Existing component audit: conformal 8.8%, KNN 93.4%, combined KNN+conformal 5.6% coverage | PARTIAL; no threshold selection from target |
| Cross-site transfer | Four UCI cohorts to one site | Locked predictor, source calibration, source OOD threshold | Existing CD-XD-004 AUC 0.787, weak calibration/OOD | PARTIAL; one site only |
| Controlled synthetic shift | Not rerun in this stage | Feature/noise/missingness shifts were already represented in robustness artifacts | No fresh detector-stability experiment in this continuation | PARTIAL; do not equate with clinical external validation |
| Additional endpoint-aligned cohort | Would require acquired dataset | Independent-site test | No eligible public downloadable cohort verified; MultiD4CAD restricted and endpoint uncertain | BLOCKED |

## Interpretation rule

No candidate was chosen using AngioCAD labels. Source temperature scaling improved the retrospective point metrics, while isotonic worsened them. A predeclared replication on an untouched compatible cohort is required before any method can be described as improving transport calibration.
