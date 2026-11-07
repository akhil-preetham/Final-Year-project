# CARDIODIAG final acceptance matrix

**Assessment date:** 2026-11-05. Statuses use the directive definitions: PASS, PARTIAL, BLOCKED, FAIL, NOT APPLICABLE. A PASS applies only to the specific verified criterion, not to clinical validity.

| Acceptance area | Status | Evidence and reason |
|---|---|---|
| Research question | PASS | Generalization-aware reliability assessment is specified in INTENDED_USE_SCOPE.md and research reports |
| Defensible novelty | PARTIAL | Integrated evaluation contribution is supportable; no novel universally superior algorithm established |
| Original method reconstruction | PARTIAL | Notebook behavior documented; exact LoRAS/LIME/PCA and table lineage unavailable |
| Dataset lineage and hashes | PASS | Manifests and QA verify available files; source imputation history and some semantics remain open |
| Patient overlap | PARTIAL | Heart5/UCI, Statlog/Cleveland and Mendeley/Heart5 duplication checked; cross-release patient linkage unavailable |
| Licensing and attribution | PARTIAL | Attribution audits exist; some derived 70K redistribution rights unresolved |
| Training-only preprocessing | PASS for corrected path | Cleaner/encoding/selection are fitted inside training partitions; historical leakage-prone path remains labelled |
| Leakage control | PASS for audited corrected experiments | Nested split and saved-index audits found no direct target/fold leakage; patient independence is not guaranteed |
| Models and OVEC/OSEC | PASS for documented variants | Reproducible factories and matched comparisons; not exact original tuning |
| Nested validation | PASS for executed internal protocol | 3x3 seed-42 artifacts and predictions exist; small row-level datasets limit inference |
| External evaluation | PARTIAL | One endpoint-aligned AngioCAD evaluation; one hospital, 377 matched records, no cross-source IDs |
| Statistical analysis | PARTIAL | Bootstrap intervals and sensitivity analyses exist; full patient-level inference, multiplicity and confirmatory comparisons remain incomplete |
| Calibration under shift | PARTIAL | Source-only calibration evaluated; AngioCAD and Duke results show poor/inconsistent target calibration |
| OOD detection | PARTIAL | Source thresholds and external tests exist; AngioCAD AUROC 0.589, weak recognition |
| Conformal implementation | PASS for implementation checks; PARTIAL for validity claim | Finite-sample quantile and separation tested; exchangeability after shift unsupported |
| Selective prediction | PARTIAL | Component audit complete; AngioCAD combined coverage 5.6%; useful operating point not shown |
| Ablations | PARTIAL | Several comparisons completed; original A–L key and full common factorial absent |
| Robustness | PARTIAL | Missingness/noise and feature ablations exist; units, concept shift, and broad site robustness unresolved |
| Software quality | PASS for recorded local QA | 106 tests, Ruff, compilation, lock and artifact checks recorded; not an independent fresh-environment audit |
| Reproducibility package | PARTIAL | Commands, manifests, lockfile and artifacts exist; local tree uncommitted and external fresh install not demonstrated |
| Provenance | PASS for recorded stages | Hashes and prediction-level audits exist; original publication lineage and patient linkage incomplete |
| Manuscript | PARTIAL | 14-page research draft and rendered review recorded; submission facts remain pending |
| References | PASS for current PDF build checks | QA reports no unresolved references; venue-specific review pending |
| Final independent audit | PARTIAL | Local independent recalculation/audit scripts exist; no external team or fresh operator audit |
| Clinical/real-world readiness | BLOCKED | Gate reports NO-GO; no clinical partner, prospective validation, or governance approval |

## Final decision

- **Offline engineering prototype:** PASS within the bounded scope documented in QA_REPORT.md.
- **Reliable prediction on unseen sites:** FAIL as an established research claim; only one endpoint-aligned external site was evaluated, and its reliability evidence is weak.
- **Exact original-paper reproduction:** PARTIAL/BLOCKED.
- **Journal submission readiness:** BLOCKED by pending factual author, ethics, funding, data-use, conflict, and venue information, plus remaining scientific limitations.
- **Clinical readiness:** BLOCKED/NO-GO.

No PASS is assigned to a claim based solely on code existence or test success. The current negative external results are preserved as findings. The project has no scientifically defensible basis to claim robust unseen-site generalization, reliable external calibration, useful selective coverage, or clinical validation.

## Highest-priority closure conditions

1. Produce a reviewed, project-owned clean snapshot without pushing to the original authors' upstream remote.
2. Obtain another untouched endpoint-compatible external cohort with codebook, units, license, and overlap assessment.
3. Resolve author/institution declarations and data redistribution rights before submission.
4. Keep the manuscript's contribution framed as an auditable evaluation/reliability study unless new confirmatory evidence supports a stronger method claim.
