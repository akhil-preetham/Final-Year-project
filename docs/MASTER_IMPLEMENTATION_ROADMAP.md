# CARDIODIAG implementation roadmap and stage disposition

**Updated:** 2026-11-06. The roadmap distinguishes repository work completed from scientific/rights gates that require new external evidence.

| Stage | Work and current evidence | Status | Remaining action / dependency |
|---|---|---|---|
| 1. Inventory and baseline | Project tree, Git baseline, source packages, results, paper and release archives inventoried; 106 tests, Ruff, compilation and lock passed before app work | PASS with repository-state warning | Review the untracked working tree with the project team; preserve backup/history. |
| 2. Original method reconstruction | `ORIGINAL_ALGORITHM_WALKTHROUGH.md`, `METHOD_REPRODUCTION_AUDIT.md`, `ORIGINAL_REPRODUCTION_MATRIX_20261105.md` document paper/code disagreements and corrections | PARTIAL / exact reproduction blocked | Exact LoRAS/XAIH-DRC/split/search configurations and original metric lineage remain unavailable or divergent. |
| 3. Dataset and cohort audit | Provenance, license, compatibility, overlap and acquisition documents; patient/endpoint mismatches explicit | PASS for audit; external validation BLOCKED | Resolve Heart5/Kaggle/Duke rights and obtain independence evidence/new compatible data. |
| 4. Protocol | Frozen experiment families and boundaries in `FINAL_EXPERIMENTAL_PROTOCOL.md`; source-only transfer protocols | PASS for existing studies | Any new confirmatory study requires pre-label frozen protocol and new untouched data. |
| 5. Leakage-controlled pipeline | Training-fold preprocessing, nested CV, model and selector tests | PASS for audited implementations | Do not generalize beyond tested pathways; original historical leakage remains historical evidence. |
| 6. Models and selection | OVEC/OSEC, logistic baselines, stable selector, model benchmarks and ablation artifacts | PASS as research implementation | No consistent improvement claim beyond actual paired evidence; preserve baseline. |
| 7. Reliability | Calibration, uncertainty, conformal, OOD and selective studies/artifacts; weak target detector and low coverage recorded | PASS as evaluation; reliability GO not met | New independent validation required. |
| 8. External validation | AngioCAD, ZAS, Duke and UCI source-transfer stress studies recorded | NO-GO for confirmatory generalization | No qualifying untouched, endpoint-identical patient-independent cohort. |
| 9. Statistics and explanations | Bootstrap/sensitivity/stability/ablation material exists; caveats on conditional intervals and post hoc use | PARTIAL | More target sites and confirmatory protocol needed; local explanations are not clinically validated. |
| 10. Demonstration | Added offline Tk app over frozen `DomainAwareSelectivePredictor`, aggregate metrics and plots; tests added | IMPLEMENTED; final GUI inspection pending | Inspect app screens and run tests; no patient data or deployment. |
| 11. Quality/reproducibility | Baseline suite and tooling passed; app tests now require post-change rerun | IN PROGRESS | Re-run test, Ruff, compile, lock and demo smoke check; update acceptance matrix. |
| 12. Manuscript | Consolidated 15-page PDF built from verified tables and audited | PASS for build; NOT READY for submission | Confirm author/institution declarations and venue; do not strengthen claims. |
| 13. Release | Data release allow-list and attribution notices exist; existing ZIPs excluded | BLOCKED | Confirm code rights and clean-room scan; unresolved data rights need written evidence. |
| 14. Closure | Strict acceptance matrix separates engineering, science, release and publication | Pending app checks | Close repository-controlled phase with honest NO-GO/BLOCKED statuses. |

## Priority order

1. Complete and inspect the offline demonstration application and its tests.
2. Re-run full software/reproducibility checks and update final report/acceptance.
3. Preserve the conclusion that independent generalization and reliable unseen-site prediction are not demonstrated.
4. Record external decisions in `USER_DECISIONS_REQUIRED.md`; do not fabricate dataset rights, cohort independence, ethics decisions or author declarations.

New confirmatory experiments should not be run on already inspected target labels. They require a new cohort, protocol freeze before target outcomes are examined, a clean provenance record and appropriate access authority.
