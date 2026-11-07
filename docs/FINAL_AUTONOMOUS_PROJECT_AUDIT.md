# Final autonomous CARDIODIAG project audit

**Audit date:** 2026-11-06. This is the mandatory first-stage synthesis of the current local repository and the prior audits, with the second-stage calibration and synthetic-shift artifacts included.

## Architecture and methodology

The project is a compact Python research package under src/cardiodiag, with experiment entrypoints under experiments, manifests and result artifacts, archived notebooks/releases, and a LaTeX manuscript at paper/manuscript.tex. The corrected internal path validates CSV/target schema, drops identifiers, then fits preprocessing, optional feature selection, and model selection inside stratified nested folds. Historical notebook reconstructions remain separate. External-transfer runners harmonize a restricted common feature set, fit the predictor/calibrator/thresholds on source cohorts, freeze them, then score a target cohort. Conformal sets and a domain/support guard are downstream research components, not proven safety mechanisms.

The primary research question is whether multi-source cardiovascular models can retain discrimination and reliable probability/uncertainty behavior on unseen, endpoint-compatible sites. The current evidence answers “not established”: one source-distinct, endpoint-aligned AngioCAD study exists, but only one hospital is available and calibration/OOD/coverage are weak.

## Experimental evidence verified

- Original source and notebooks: audited in SOURCE_PROVENANCE.md, PROTOCOL_AUDIT.md, METHOD_REPRODUCTION_AUDIT.md; exact reproduction is not possible from the available conflicting notebook lineage.
- Internal nested model study: saved fold predictions and indices; fresh run matched prior fold means.
- Transfer studies: UCI LODO (overlapping Heart5 provenance), Z-Alizadeh Sani (endpoint boundary mismatch), AngioCAD (377 matched, 36 unmatched; unit caveats), and Duke (endpoint mismatch).
- Source-only calibration extension: Platt, isotonic, beta, and temperature fitted to source calibration predictions with equal source-domain weights; target cohort only used for fixed evaluation and stratified bootstrap intervals. Source-temperature improved one examined target retrospectively; no confirmation on an untouched site.
- Controlled shift lab: six detectors evaluated across five synthetic transformations on a stratified Heart5 split. Unit scaling was readily detected; correlation disruption and variance shift were weakly detected. This is a synthetic diagnostic, not external validation.
- Selective prediction: existing component audit gives 8.8% singleton-conformal coverage, 93.4% KNN-only coverage, and 5.6% combined coverage on AngioCAD; all 21 combined accepted cases were positive.
- Tests, Ruff and compilation passed in the latest recorded execution. Repeated workbook warnings concern unsupported conditional-formatting extensions during read-only tests.

## Contradictions and defects found

| Issue | Severity | Root cause and status | Evidence needed to close |
|---|---|---|---|
| Reliable unseen-site claim absent | CRITICAL | One endpoint-aligned site only; moderate ranking, poor calibration, weak OOD, no independent site variance estimate. BLOCKED externally. | Frozen model on a second independent endpoint-compatible hospital with documented patient independence, units, endpoint and sufficient events |
| Exact historical algorithm unclear | HIGH | Original notebook variants conflict; LoRAS/LIME/PCA settings and paper table lineage absent. Irrecoverable from current files. | Original authors' exact supplement, code/environment, seeds/splits and table lineage |
| Calibration candidate selected post hoc risk | HIGH | Temperature performs better on already examined AngioCAD; could be target-specific coincidence. PARTIAL. | Predeclared validation of source-temperature on untouched compatible cohort |
| OOD methods do not establish individual error detection | HIGH | Existing real target results measure source/target separation; synthetic tests measure designed perturbations. PARTIAL. | Error-label association on new independent cohorts and broader predeclared detector evaluation |
| Selective coverage very low | HIGH | Singleton conformal plus KNN conjunction rejects most target rows; useful point not established. PARTIAL. | Source-only operating policy then confirmation on untouched site with adequate positive and negative accepted events |
| Cross-dataset patient overlap unresolved | HIGH | Common linkage keys absent for releases. BLOCKED. | Lawful linkage or authoritative source-level overlap assessment |
| Endpoint/units/timing uncertain | HIGH | Mendeley reference standard/timing and AngioCAD FBS units not documented. BLOCKED. | Source codebooks/author confirmation or exclude uncertain predictors/claims |
| Clean public release absent | HIGH | Local tree is uncommitted on original-source HEAD; tracked README modified, large untracked project tree. FAIL for release handoff. | Reviewed project-owned snapshot, license scan and independent clean clone test; no push to original upstream |
| Full common factorial and prospective clinical utility absent | MEDIUM/HIGH | Original A–L key unavailable; heterogeneous study protocols; no clinical partner. PARTIAL/BLOCKED. | Prespecified shared-fold factorial where justified; clinical utility requires separate clinical endpoint/study |
| Publication declarations incomplete | HIGH | Ethics, consent, coauthor facts, funding, conflicts and venue require humans/institution. BLOCKED. | Completed PUBLICATION_FACTS_REGISTER.md by authors/institution |

## Previous work retained and verified

Six first-stage audits, second-stage root-cause/issue records, a source-calibration comparison, a synthetic covariate-shift runner, transfer metrics, selective components, manuscript builds and software QA are present. Existing evidence was reused rather than rerunning expensive historical/transfer studies without a scientific reason. New calibration and synthetic-shift runs are versioned separately and do not overwrite CD-XD source artifacts.

## Optimal resolution path and status

Locally solvable work (source-only calibrator comparison, synthetic shift diagnostics, issue classification, architecture boundaries, provenance and software checks) has been executed. External data acquisition, patient linkage, ethics and coauthor declarations cannot be completed by local code. No additional cohort was fabricated or acquired without authorization.

**Overall:** technical research prototype is operational. Research objective remains NO-GO for reliable unseen-site prediction. Submission readiness remains BLOCKED by both scientific evidence and factual declarations. See UPDATED_FINAL_ACCEPTANCE_MATRIX.md and USER_INPUT_AND_RESOURCE_REQUIREMENTS.md.
