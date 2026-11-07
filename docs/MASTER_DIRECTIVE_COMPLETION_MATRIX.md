# Master directive completion matrix

**Assessment date:** 2026-11-05
**Engineering-prototype decision:** `GO` for the declared offline final-year
scope: the local workflow is reproducible and has a retrospective
source-distinct, endpoint-aligned evaluation and a fail-closed unknown-site
demonstration. **Research objective decision:** `NO-GO`; reliable
cross-dataset generalization, useful feature-only OOD recognition, and external
calibration are not established. No clinical-use claim is supported.

The 2026-11-05 validity audit found no direct target, identifier, or fold
leakage in the corrected evaluation path. It found unresolved endpoint and
feature-timing provenance for the 2021 Mendeley benchmark, weak feature-only
OOD separation on AngioCAD, and one-site-only external evidence. The project is
complete as an engineering prototype that exposes these failures and fails
closed for unknown sites; reliable unseen-site prediction is not established.

**Broader status:** The original master directive remains partially complete
because exact historical reproduction, a full factorial analysis, a pristine
compatible external test for the final model, and project-team metadata remain
unresolved. Clinical/real-world readiness is `NO_GO`.

This matrix maps the directive to evidence already present in the repository.
“Complete” refers only to the named local engineering or audit task; it does
not imply clinical validity.

| Directive part | Status | Evidence and remaining work |
|---|---|---|
| 1. Project identity | Complete | Supplied article and DOI are recorded in `SOURCE_PROVENANCE.md`; local article claims are mapped by page in `PROTOCOL_AUDIT.md`. |
| 2. Preserve existing work | Complete locally; uncommitted | Historical notebooks, source provenance, datasets, prior results, release snapshot, and original archives remain. Four original RARs were restored from the checked-out source commit. The source tree is still dirty and uncommitted; no commit or push was made to the original authors' upstream remote. |
| 3. Reconstruct original method | Partially complete | `ORIGINAL_ALGORITHM_WALKTHROUGH.md`, `PAPER_TO_CODE_MAP.md`, `historical.py`, and `baseline_reproduction_report.md` document a representative notebook path. No bit-for-bit LoRAS/LIME/PCA reconstruction exists because notebook variants conflict and the LoRAS parameters/environment are not frozen. |
| 4. Audit original research | Complete as an audit; reproduction partial | `PROTOCOL_AUDIT.md` compares the article’s 75:25/5-fold/ten-run claims to notebook code showing pre-split resampling and other variants. Exact article table provenance is unavailable, so exact metric reproduction remains unverified. |
| 5. Research architecture | Partially complete | Modules for loading, preprocessing, feature selection, ensembles, nested evaluation, reliability, uncertainty, shift diagnostics, and provenance exist. `ARCHITECTURE.md` describes boundaries. The implementation remains a compact tabular package, not every suggested subsystem/API. |
| 6. Research contributions | Partially complete | Stability, calibration, selective prediction, robustness, AURA-ML, and CLIN-ADAPT have separate artifacts. The supported result is mixed stability/reliability evidence; LoRAS/LIME are not authoritative components and no new universal algorithm is supported. |
| 7. Dataset validation | Partially complete | Hashes, schemas, targets, counts, missingness, duplicate rows, identifier handling, and license notes are in `DATA_PROVENANCE.md` and `DATASET_COMPATIBILITY.md`. The new Mendeley audit classifies all predictors and finds no documented timing/reference standard. The AngioCAD compatibility audit preserves all 36 unmatched IDs, verifies one-to-one ID merging, and records absent age/FBS units and the stenosis-bin boundary. Cross-dataset patient linkage and several rights remain unresolved. |
| 8. Shift and cross-dataset generalization | Prototype implemented; generalization claim not established | `CD-XD-003` evaluates 303 source-distinct Z-Alizadeh Sani records (AUC 0.720; OOD AUROC 0.604), but its `>=50%` endpoint differs from the source `>50%` boundary. `CD-XD-004` and post-hoc `CD-XD-006` evaluate AngioCAD (377 matched records; AUC 0.787/0.790). `CD-XD-005` evaluates fresh Duke ACATH (AUC 0.661) with a >=75% vs >50% endpoint mismatch. Source-domain conformal sets and a trusted metadata gate are implemented; feature-only OOD AUROC remains weak, and the gate blocks every unknown-site row. No untouched, endpoint-identical external cohort is available in the checked public sources. |
| 9. Statistical validation | Partially complete | Corrected nested runs and a five-seed (43–47) split-sensitivity analysis now report recalculated pooled metrics, ranges, calibration, and baselines for both development datasets. This remains exploratory; splits are row-level, patient/group IDs are incomplete, across-seed values are not independent patient samples, and subgroup accounting, patient-level intervals, and full confirmatory/multiplicity work remain incomplete. See `INTERNAL_VALIDATION_REPEAT_PROTOCOL_20261105.md` and `results/internal_seed_sensitivity_20261105/seed_repeat_summary.md`. |
| 10. Metric preservation without overfitting | Complete for the documented comparisons | Historical and corrected metrics remain separated. Model selection is nested; negative and dataset-conditional findings are retained. No outer-test optimization or historical-score target is used. |
| 11. Ablation and contribution analysis | Partially complete | `ABLATION_REPORT.md`, AURA ablations, CLIN-ADAPT ablations, the seven-subset AngioCAD sensitivity, and frozen selective-component comparison exist. The original A--L key was not found; the new matrix is explicitly a workstream crosswalk. A full matched factorial remains absent. |
| 12. Limitation resolution | Partially complete | `LIMITATION_RESOLUTION_MATRIX.md` marks each limitation and required intervention. External validity, clinical utility, concept shift, source overlap, and broad fairness remain unresolved. |
| 13. Engineering and reproducibility | Complete for the new local transfer prototype | `DomainAwareSelectivePredictor`, locked dependencies, data manifests, disjoint source partitions, serialized inference bundles, per-run hashes, runnable transfer commands, and synthetic known/unknown-domain demos exist. The checkout remains uncommitted. |
| 14. Quality assurance | Complete for local software and artifact checks | `QA_REPORT.md` records the current test, Ruff, compilation, lockfile, data/code/output hash, independently recalculated transfer and sensitivity, inference-demo, and manuscript checks. These checks establish software and artifact integrity only. |
| 15. Literature positioning | Partially complete | Literature and model registries and gap analyses are in `docs/`. They support a restrained contribution framing, not a confirmed novel algorithm. A submission-target systematic review is not complete. |
| 16. Final deliverables | Complete as a negative offline engineering result; paper submission pending | Scientific audit, predictor provenance, statistical consistency, original-reproduction/A--L crosswalk, author checklist, manuscript tables, revised 14-page PDF, extractable-text check, full-page render inspection, and publication manifest are complete locally. Submission remains NO-GO: author order/affiliations, ethics/data-use determination, funding, coauthor contributions, conflicts, all-author approval, and venue remain pending. |
| 17. Autonomous execution | Complete for locally available evidence; broad claim remains unproven | The fresh 3x3 run completed. CD-XD-002–004 were rerun and audited; CD-XD-005/006 add source-only disjoint calibration, conformal sets, a domain registry guard, target predictions, serialized inference bundles, and an independent result audit. Provenance, ablation, and policy audits are complete for available files; exact historical reproduction, full factorial ablations, and a pristine endpoint-compatible external evaluation require unavailable source materials/data. |
| 18. Completion criteria | Engineering prototype complete; research objective and submission are NO-GO | A reproducible fail-closed prototype, retrospective source-shift evaluation, validity threat checks, provenance audits, post-hoc ablations, selective-policy comparisons, demos, and a verified research draft are present. The negative result on the one endpoint-aligned site is moderate ranking, poor calibration, weak feature-only OOD detection, and 5.6% combined coverage. New independent sites, original settings, full common factorial, and factual project-team/venue metadata remain unresolved. |

## Real-world readiness gate

The separate staged workflow is in `REAL_WORLD_READINESS_WORKFLOW.md`, with
data-access candidates in `EXTERNAL_DATA_ACCESS_PATHWAYS.md`. The machine gate
`uv run python experiments/evaluate_readiness.py` reports `NO_GO`: **1 of 13
phases passed**. This is consistent with the matrix above; it does not mark
the research or clinical-readiness objective complete. The checker verifies
ledger structure, evidence-file existence, and SHA-256 capture, not the content
of clinical, statistical, ethics, security, or regulatory decisions.

## Current evidence summary

The authoritative 3 outer x 3 inner seed-42 results remain under
`results/final_completion_20261105/`. A fresh provenance-rich rerun is under
`results/master_directive_20261105_serial/`; all fold-mean candidate metrics
match the prior stage exactly, and the fresh manifest says
`external_validation: false`. Corrected OVEC ROC-AUC is 0.9295 on Heart5 and
0.9957 on Mendeley; stable OSEC is 0.9253 and 0.9942. The fresh run also
stores all outer predictions and split indices for 918 and 1,000 rows. These
are internal development/replication results and do not establish population
transport. The separate seed-sensitivity protocol ran seeds 43–47 under one
current source-bundle and lockfile hash. Every row was scored once per seed,
and all pooled metrics were recomputed within `1e-10`; seed 42 was excluded
from this aggregate because its source and lock hashes differ. The analysis is
exploratory and does not replace patient-level or external validation.

AURA-ML V2 is dataset-conditional: it did not exceed the strongest simple
baseline on Heart5, was higher than tested baselines on Mendeley, and has only a
frozen-baseline feasibility comparison on the 70K dataset. The results do not
justify universal superiority or a novelty claim.

## Required external inputs

The project owner has described the current work as research-based, with
possible future clinical use. The current scope is documented as offline
research in `INTENDED_USE_SCOPE.md`; any clinical use remains unspecified and
requires a clinical partner and formal review.

A newly published Mendeley 918-row heart dataset was retrieved and verified
against the repository's Heart5 file. Its API file hash matched, and all 918
rows matched Heart5 exactly across the complete labeled schema. The
row-level source audit also found a compatible record in the UCI cohorts for
every Heart5 row. These checks improve provenance evidence but confirm the new
Mendeley release is not a new external cohort; see `DATA_PROVENANCE.md` and
`EXTERNAL_DATA_ACCESS_PATHWAYS.md`.

1. A genuinely independent, endpoint-compatible cohort not previously
   examined, with provenance, licensing, overlap assessment, a semantic
   feature map, and a frozen one-way evaluation protocol. The official UCI
   Statlog release was audited and all 270 rows matched Cleveland; Duke ACATH
   uses >=75% versus source >50%; AngioCAD is endpoint-aligned but was already
   examined.
2. Correct author names/affiliations and factual ethics, funding, contribution,
   and data-use statements for the manuscript.
3. Upstream license confirmation for the composite Heart5 and Kaggle 70K data
   before redistribution.
4. A selected venue/template and project-team metadata for submission checks.
   A local Tectonic build produced and visually verified the current IEEE-style
   draft PDF; venue-specific proofing remains.

No item above is inferred from local files or fabricated.
