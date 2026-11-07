# CARDIODIAG final acceptance matrix

**Updated:** 2026-11-07. A `PASS` means the named technical check passed on this checkout; it does not mean the scientific generalization objective passed.

| Gate | Acceptance evidence | Result | Interpretation / remaining condition |
|---|---|---|---|
| Dataset identities and current lineage | Four audit documents reconciled into `FINAL_DATASET_ATTRIBUTION_REGISTER.md`; source IDs, DOI/version, access/license and overlap stated | PASS | Heart5 upstream exact record and standalone terms remain unresolved; explicitly blocked from release. |
| Compatibility and endpoint separation | Compatibility matrix and manuscript separate CAD, HF, MI, and ECG tasks | PASS | No candidate ECG/HF/MI data acquired or merged. |
| Patient/cohort independence claims | Overlap report; Statlog-Cleveland 270/270; Heart5-UCI mapping; Mendeley2026-Heart5 918/918; no unsupported independence claims in final narrative | PASS | No verified patient-independent external validation is established. |
| Dataset-specific attribution notices | Notices under `data/attribution/` for eligible acquired CC BY sources | PASS | Notices do not independently clear unresolved composites or Duke redistribution. |
| Raw and row-level release exclusion | Final manifest excludes unresolved/restricted data, record-level derivatives, and all legacy ZIPs | PASS as policy | The manifest is an allow-list, not a clean package or upload attestation. |
| Manuscript numeric tables | Existing frozen tables plus corrected-quantile tables generated from 10-seed source-side reruns; source/output hashes in `paper/tables/conformal_corrected_table_manifest_20261107.json` | PASS | New `experiments/rebuild_final_manuscript_tables.py` generates the stability, reliability, feature-ablation, and selective-policy tables; existing generators rebuild nested, validity, and transfer tables. |
| Conflicting OOD metrics | ZAS and AngioCAD manifests, validity-sensitivity audit, current manuscript tables | PASS | 0.604 is ZAS CD-XD-003; 0.589 is primary AngioCAD CD-XD-004; 0.5787/0.5801 are distinct later CD-XD-006 IF/kNN diagnostics. The final report and app preserve run/cohort distinctions. |
| Full pytest suite | `.venv\Scripts\python.exe -m pytest -q` on the finalization branch | PASS — 141 tests | Three known OpenPyXL conditional-formatting warnings while reading AngioCAD workbooks; no source workbook was written. | Three OpenPyXL warnings report ignored conditional-formatting extensions while reading AngioCAD workbooks; files are not written back. Includes demo schema/range/gate, artifact hash, LOF and selective-audit helper tests. |
| Clean installation | `uv sync --locked` in a new isolated environment | PASS | 54 packages resolved; project installed editable. The initial attempt used `--no-install-project` and predictably failed imports; corrected clean install and full suite passed. |
| Source-only LOF diagnostic | `controlled_shift_lab.py`; hashed run4 metrics and two tests | PASS as diagnostic | LOF novelty comparison is fitted on source training data; no real target label used for method choice. Does not improve the external OOD gate. |
| Descriptive selective risk–coverage audit | Saved target predictions; hashed CSV/JSON/PNG and three helper tests | PASS as audit | No fitting or threshold selection. AngioCAD/Duke labels are previously examined; confidence intervals condition on each cohort. |
| Ruff | `.venv\Scripts\ruff.exe check .` | PASS | All checks passed on the final source tree. |
| Python compilation | `.venv\Scripts\python.exe -m compileall -q src experiments tests demo` | PASS | Final source, experiment, test and demo scripts compiled. |
| Dependency lock | `uv lock --check` | PASS | 54 packages resolved with no lock change required; app adds no dependency. |
| Reproducibility audits | Distribution ZIP scan, Heart5-UCI lineage, Statlog overlap, AngioCAD compatibility, validity sensitivities, selective components, and domain-guard artifact recomputation | PASS | Exact results and fresh audit outputs are recorded under `results/final_consolidation_20261106/` and `results/DOMAIN_GUARD_FINAL_AUDIT.json`. |
| Historical LaTeX source build (2026-11-06) | Tectonic 0.17.0, prior build folder, bibliography and tables | PASS — 15 pages | Zero build errors, unresolved references/citations, or overfull boxes. Underfull-box and Fontconfig warnings remain. |
| PDF structure/text consistency | `pdfinfo`, `pypdf` extraction, page renders/contact sheet | PASS | 15/15 pages contain extractable text; all 15-page contact sheet reviewed. The PDF and inputs are hashed in `paper/build/final_consolidation_20261106/publication_manifest.json`. |
| Master inventory, gap analysis and roadmap | `MASTER_PROJECT_INVENTORY.md`, `MASTER_RESEARCH_GAP_ANALYSIS.md`, `MASTER_IMPLEMENTATION_ROADMAP.md` | PASS | Captures source-control state, evidence boundaries and external dependencies. |
| Original-method reconstruction | `ORIGINAL_CARDIODIAG_RECONSTRUCTION.md` plus historical method audits | PARTIAL | Deviations and source variants documented; exact reproduction blocked by inconsistent notebooks and missing parameters. |
| Research demonstration application | `demo/app.py`, `APPLICATION_GUIDE.md`, live Windows UI inspection | PASS for local research demo | Overview, synthetic input, saved evaluation evidence and explanation limits render; unknown-domain abstention withholds probability; registered synthetic example returned the frozen model result. Not clinical use. |
| Application helper tests | `tests/test_demo_app.py` | PASS | Schema/range/category validation, ordering, unknown-domain abstention and registered-model call covered. |
| Final project report | `FINAL_PROJECT_REPORT.md` | PASS as evidence summary | Numeric claims link to the existing artifacts; negative scientific conclusion and separate gates retained. |
| Research generalization objective | Verified untouched patient-independent endpoint-compatible validation | NO-GO | Not available in this repository; the observed site tests are exposed, endpoint-mismatched, or linkage-unverified. |
| Journal submission | Final coauthor and institutional declarations plus target journal requirements | BLOCKED | Ethics/funding/contributions/conflicts/author metadata/venue remain pending. |
| Public code package | Clean-room data-free archive, file-level scan, and confirmed code license/redistribution authorization | BLOCKED | No root `LICENSE` is present locally; the original GitHub root lists no license and its `LICENSE` URL returned 404 on 2026-11-06. Confirm authority; no clean archive exists. Existing ZIPs are prohibited from release. |
| Version-controlled completeness | All intended research source/docs/results have tracked history and a reviewed snapshot | BLOCKED | Current Git HEAD is the original snapshot; nearly all research-tree files are untracked. Preserve files, establish project-owner intent, then review/track changes before release. |

## Master mission acceptance gates

Statuses in this table use the directive's strict vocabulary. `PASS` means the stated engineering/research task is evidenced; it does not mean the performance hypothesis passed.

| Gate | Status | Evidence and interpretation |
|---|---|---|
| Original reconstruction | PASS | End-to-end deviations and conflicting source variants are recorded. Exact numerical replication remains unavailable; see `ORIGINAL_CARDIODIAG_RECONSTRUCTION.md`. |
| Dataset provenance | PASS | Source/version/license/attribution audit complete for identified data; unresolved composite/provider terms are excluded from release. |
| Dataset compatibility | PASS | CAD vs HF/MI/ECG endpoints are separated; external compatibility caveats are explicit. |
| Leakage control | PASS | Audited corrected pathways use training-fold fits and nested selection; historical unsafe results remain labeled historical. |
| Baseline evaluation | PASS | Internal corrected logistic, OVEC and OSEC artifacts and summaries are present. They are not external validation. |
| Improved framework | BLOCKED | Reliability components and alternative models were implemented/evaluated, but no confirmatory improvement on a new compatible cohort is established; no superiority claim is made. |
| Feature stability | PASS | Stability artifacts exist for named source datasets; stability is not interpreted as generalization. |
| Calibration | PASS | Internal and source-only transfer calibration was evaluated; transfer evidence is inadequate for a reliability GO. |
| Uncertainty | PASS | Conformal/ensemble/selective behavior is evaluated with assumptions and target-shift limits stated. |
| OOD detection | FAIL | Primary AngioCAD CD-XD-004 AUROC is 0.589; later post-hoc CD-XD-006 IF/kNN values are 0.5787/0.5801. The 0.604 result belongs to ZAS CD-XD-003. None establishes useful unseen-site recognition. |
| Selective prediction | FAIL | AngioCAD coverage is 5.6%; Duke coverage is 11.4% on an endpoint-mismatched target. Useful validated risk-coverage is not established. |
| Explainability | PASS | LIME/global stability/ablation analyses exist; no causal or clinically validated explanation claim is made. |
| Statistical validity | PASS | Study-specific uncertainty/sensitivity analyses are reported with conditional limitations; between-site variability is not estimable. |
| External validation | BLOCKED | No qualifying untouched, patient-independent, endpoint-compatible cohort is verified. Existing site studies are stress tests only. |
| Application | PASS | Offline UI, input checks, evidence views and abstention were tested; synthetic research demonstration only. |
| Reproducibility | PASS | 141 tests, Ruff, Python compilation, `uv lock --check` (54 packages), and `git diff --check` pass; key runs/tables/manuscript have provenance. Git tracking of current research tree remains a separate release blocker. |
| Manuscript | PASS | Draft text/tables match the supported evidence and limitations; built/inspected PDF exists. This is not submission readiness. |
| Code release | BLOCKED | Ownership/redistribution authority and clean data-free package scan are not established. |
| Publication readiness | BLOCKED | Author/institution declarations and publication venue remain pending. |

## Gate interpretation

Technical `PASS` rows establish repository-level traceability and implementation checks only. They do not establish that the model generalizes. A technically complete negative result can be reported honestly; it cannot be converted to a positive generalization claim without new independent evidence.

## Iteration closure

Repository-controlled work for this consolidation is closed: the source, audit trail, manuscript tables, reproducibility checks, and rendered draft are complete and verified as recorded above. No remaining local edit can supply the missing cohort-independence evidence, dataset redistribution rights, project code ownership authorization, or author/institution declarations. Those are external evidence and authority requirements, not unfinished coding tasks.

This is the last iteration of the current evidence set because further local iterations would only reformat or restate the same result. Reopen the project only when at least one blocking input changes: a qualifying independent endpoint-compatible cohort is obtained under a frozen protocol; written dataset/code redistribution authority is established; or the project team/institution confirms the pending submission declarations. Until then, keep the project at research-prototype GO, generalization-claim NO-GO, code-release BLOCKED, and journal-submission NOT READY.

## Completion follow-up (2026-11-06)

| Requirement | Result | Evidence / interpretation |
|---|---|---|
| Branch and baseline preservation | PASS | Work is on `codex/cardiodiag-finalization-2026-11-07`, based on the existing completion branch at original `e63b02c`; no research results were overwritten. The checkout contains numerous untracked research files and remains blocked for a clean release snapshot. |
| External cohort search | NO-GO for qualification | `EXTERNAL_COHORT_SEARCH.md` records official candidate sources and rejection evidence. No qualifying untouched cohort is demonstrated. |
| Dataset rights registry and checker | PASS as guardrail | `data/registry/datasets.json`, `experiments/check_dataset_release.py`, and `tests/test_dataset_release.py` fail closed unless a dataset has explicit `approved_for_redistribution` status. Not a package scan or legal opinion. |
| Ownership and release documents | BLOCKED | File-family ownership matrix and permission templates are prepared; actual rights-holder permission is missing. `PUBLIC_RELEASE_MANIFEST.md` is not an approved release. |
| Author and ethics documents | BLOCKED pending humans | Fillable author/CRediT/funding/conflict forms and ethics determination request exist. No approvals or statements were invented. |
| Publication venue | PROVISIONAL | `JOURNAL_SHORTLIST.md` recommends BMJ Health & Care Informatics subject to author agreement and current submission checks. No venue is selected by the authors. |
| Accidental Windows `nul` file | PASS | Exact content was read through extended-length path; it contained only an earlier failed-command message, was untracked and unreferenced, then was removed. |
| Historical verification (2026-11-06) | PASS — 133 tests | Full suite: 133 passed with 3 known OpenPyXL read warnings. Ruff and Python compileall passed. `uv lock --check` resolved 54 packages using a project-local cache. New validator/release-gate tests passed; the unresolved Heart5 registry entry was refused. Demo application tests passed; prior visual review covered unchanged offline UI code. |


Additional deliverable: `CODE_OWNERSHIP_FILE_MATRIX.csv` contains 1,366 conservative path-level rows. It classifies unknown/untracked files conservatively and records whether each path was present in the base tree; it is an inventory aid, not a legal conclusion.

## Finalization correction (2026-11-07)

| Requirement | Result | Evidence / interpretation |
|---|---|---|
| Finite-sample conformal quantile | PASS | Correct order statistic is selected; invalid calibration labels and malformed probabilities are rejected. Focused tests and the full 141-test suite passed, including the new validation cases. |
| Corrected source-side evidence | PASS | Heart5 and Mendeley uncertainty and linkage studies rerun over seeds 42–51. Artifacts are in `results/finalization_20261107/conformal_corrected/`; old results were preserved. |
| Calibration error reporting | PASS | Legacy macro-bin ECE is retained and explicitly named; sample-weighted equal-width-bin ECE is added to metric output and corrected manuscript tables. |
| Corrected manuscript tables | PASS | Versioned TeX tables and SHA-256 provenance manifest generated by `experiments/build_corrected_reliability_tables.py`. Manuscript source consumes the new tables. |
| Final code verification | PASS | 141 tests passed; Ruff, compileall, lock check (54 packages), and diff whitespace check passed. Three known OpenPyXL warnings occurred during read-only AngioCAD workbook tests. |
| Updated PDF | PASS — 16 pages | Tectonic 0.17.0 local binary, build in `paper/build/finalization_20261107/`, copied to `output/pdf/CARDIODIAG_Final_Consolidated_20261107.pdf`; all pages rendered and visually reviewed. Underfull-box and Fontconfig warnings remain; no undefined references/citations or overfull boxes. |
| Scientific generalization | NO-GO | Repeated splits on existing development data cannot establish independent external or real-site clinical generalization. |

| Corrected transfer protocol reruns | PASS | CD-XD-003 through CD-XD-006 rerun from current code into `results/finalization_20261107/corrected_quantile_transfer/`; the earlier artifacts remain intact. AngioCAD/Duke probabilities and conformal/selective flags match the prior runs exactly. Target scoring remains post hoc. |
| OOD and selective diagnostic figures | PASS | Source-only OOD AUROC summary and frozen AngioCAD/Duke risk-coverage curves with conditional Wilson intervals generated as PNG and PDF; inputs/output hashes in `paper/figures/finalization_20261107/finalization_diagnostics_manifest.json`. |
| Final publication figure pack | PASS | Nine core figures and four supplemental figures regenerated in `paper/figures/finalization_20261107/`; generator and input provenance recorded in the two figure manifests. |
| Final manuscript QA | PASS | 16-page PDF text extraction succeeded on all pages; rendered contact sheet and new diagnostic pages visually reviewed; build manifest hashes the inputs and outputs. |
