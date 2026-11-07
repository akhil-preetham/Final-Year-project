# CARDIODIAG final research completion report

**Report date:** 2026-11-06  
**Scope:** highest defensible state of the existing local project and current evidence. This report does not assert clinical validity, legal permission, paper acceptance or independent generalization.

## Decision summary

The local CARDIODIAG research prototype is operational and reproducible on this checkout. Its central research claim—reliable prediction and uncertainty under independent unseen-site dataset shift—is **not established**. Local engineering tasks added in this iteration are complete and tested. Work that depends on a new independent cohort, rights-holder approval, or author/institution facts remains externally blocked and is stated as such.

| Acceptance area | Status | What the evidence means |
|---|---|---|
| Engineering prototype and offline demo | GO | Existing pipeline and synthetic-only desktop demonstration work locally; not a clinical system. |
| Reproducibility | GO for local checkout | Full suite passed in current and fresh locked environments; new detector and selective-audit helpers are tested, and experiment artifacts are hashed. Current source tree is not fully tracked. |
| Original CARDIODIAG reproduction | PARTIAL | OVEC/OSEC families are retained; corrected fold-local/nested methodology is documented. Conflicting source notebooks and missing parameter details prevent exact original reproduction. |
| Dataset provenance | PASS as audit; dataset-specific limits remain | Sources, licenses, overlap, endpoints and access constraints are documented. Heart5/Kaggle/Duke restrictions remain. |
| External validation | NO-GO | No untouched, verified patient-independent and endpoint-compatible target cohort is established. |
| OOD reliability | NO-GO | Real-site detector results are weak. LOF now has a reproducible synthetic source-only comparison but does not dominate. |
| Selective prediction usefulness | NO-GO | AngioCAD coverage is 5.6%; Duke is endpoint-mismatched and coverage 11.4%. Risk bounds are too wide for reliability claims. |
| Public code release | BLOCKED | Code ownership/license authorization, tracked snapshot, complete package scan and exact archive clean-install are not established. |
| Journal submission | NOT READY | Author, contribution, ethics, funding, competing-interest and venue declarations remain unresolved. |

## What was done in this iteration

1. Inspected the final report, acceptance matrix, key dataset/provenance records, experimental protocol, OOD method audit, selective policy audit, and source runner. Ran the full baseline suite: **122 tests passed** with three known workbook-reader warnings.
2. Created branch `codex/research-completion-2026-11-06` at base commit `e63b02c8a2aba6344a48025f657696fd99ac3a5f`; no prior archive, dataset, experiment, or manuscript artifact was reset or overwritten.
3. Added a source-only LOF novelty detector to the controlled synthetic-shift laboratory and tests. For five generated shifts, LOF AUROC was 0.591 (age), 0.629 (variance), 0.524 (correlation disruption), 1.000 (extreme unit shift), and 0.684 (missingness). An exact repeat matched all 35 metric rows. This is shift-specific synthetic evidence only; no real-site threshold was tuned.
4. Added a descriptive saved-target risk–coverage audit that reports coverage/risk Wilson intervals and compares accepted with rejected rows. An exact repeat matched all 40 curve rows and 10 policy-summary rows. It changes no estimator, calibrator, threshold or policy.
5. Added OOD, selective-prediction, provenance/license, reproducibility, GitHub-release, journal-readiness and completion reports. Corrected stale local-path and outdated test/environment instructions in active documentation.
6. Investigated official candidate dataset records. Publicly licensed UCI and PhysioNet candidates are incompatible, overlapping, or previously examined for the current task; MIMIC-IV is credentialed and requires training and a DUA, and does not supply the same frozen endpoint by default. No dataset was downloaded.

## Why no external-validation GO is possible now

Heart5/UCI/Statlog/Mendeley releases overlap. Z-Alizadeh Sani uses a different ≥50% stenosis boundary and was examined. AngioCAD is a one-site, retrospective stress test with missing feature rows, undocumented feature units and no patient linkage; its outcomes were already reviewed. Duke uses a ≥75% threshold and has unclear redistribution terms. HF, MI-complication and ECG datasets predict different outcomes/modalities. MIMIC-IV is restricted and does not equal the current >50% angiographic endpoint without separately designed cohort extraction and adjudication. None meets all frozen-cohort, endpoint, feature, independence, rights and untouched-label requirements.

Replaying target data, lowering abstention thresholds after seeing labels, or selecting an alternative OOD detector from these cohorts cannot produce a confirmatory test. The resolution requires a new cohort from an authoritative source, documented use permission, patient/cohort independence support, compatible prediction-time features and target definition, and a preregistered frozen evaluation plan.

## Why release and submission remain blocked

The current branch preserves the upstream commit but most of the local research tree was untracked before this iteration. `LICENSE_AND_ATTRIBUTION.md` covers source/data attribution; it does not grant a software license. Heart5 and Kaggle 70K terms remain unresolved, Duke redistribution is unclear, and legacy ZIPs are not release-cleared. No public upload occurred.

The manuscript draft and 15-page PDF exist, but authors/order/contributions, ethics status, funding, competing interests and target venue are pending. Do not invent these declarations or add a root license/Citation file with guessed author metadata.

## Verification record

Baseline: 122 tests passed, with three OpenPyXL warnings. New targeted tests: 5 passed (LOF and selective-audit helpers). Final full suite: **127 passed** in both the existing environment and a fresh `uv sync --locked` environment. Ruff, Python compilation, and `uv lock --check` passed; 54 packages resolved. The desktop demo code was unchanged in this iteration; its synthetic-only screens and abstention behavior were visually verified in the preceding project audit. `pip-licenses` reported metadata for 45 third-party packages and the local project as `UNKNOWN` because no root software license exists. The scoped text-pattern scan found no active-document local Windows paths or credential-pattern matches; it is not a substitute for full file/archive secret scanning. Three known OpenPyXL warnings occurred while reading AngioCAD workbook data; the workbooks were not modified.

## Closure criterion

Local implementation, audit and reproducibility work for the current evidence set is closed. The scientific external-validation claim cannot be marked complete. Reopen the research gate only when a qualifying cohort or rights/author/institution facts change. Current outcome: **research-engineering prototype GO; independent generalization NO-GO; reliability NO-GO; public code release BLOCKED; journal submission NOT READY.**

## Additional completion pass (2026-11-06)

Added the named cohort-search, ownership, dataset-rights, release-manifest, author-declaration, ethics-request and journal-shortlist documents, plus institutional data-access and upstream code-permission templates. Added `data/registry/datasets.json` and a fail-closed dataset redistribution checker with tests. The root accidental `nul` error file was content-checked, confirmed untracked and unreferenced, then removed using an extended-length Windows path. Scientific conclusions are unchanged: independent generalization and useful real-site OOD/selective behavior remain NO-GO; release and submission remain blocked on external evidence and approvals.

The external dataset manifest validator has been hardened to require explicit, supported qualification evidence for population, endpoint, per-feature schema/units/timing, independence, access, and label-blinding state; it rejects previous target-label exposure. Tests cover both acceptance and fail-closed cases. A separate BMJ HCI-oriented generic LaTeX review copy is prepared at `paper/manuscript_bmjhci.tex`; it is not an official publisher class or final submission file, and the original IEEE manuscript remains intact.

Added a generated file-by-file ownership inventory (`docs/CODE_OWNERSHIP_FILE_MATRIX.csv`) and reproducible builder. It classifies unknown untracked files conservatively and does not infer legal title from Git history. This improves auditability but leaves actual contributor and upstream permission gates blocked.

Final post-change engineering verification passed: 136 tests, Ruff, Python compilation, and the locked dependency check (54 packages). Three known OpenPyXL warnings occurred on read-only AngioCAD workbook loads. The newly created BMJ HCI-oriented generic LaTeX review copy has not been separately compiled; no LaTeX compiler was available on PATH. The previously built and visually checked IEEE-format PDF remains the existing compiled manuscript artifact.


## 2026-11-07 follow-up

A finite-sample split-conformal quantile error was corrected. The existing Heart5 and Mendeley source-side uncertainty/linkage experiments were rerun using seeds 42–51, preserving prior artifacts. Reliability output now distinguishes legacy macro-bin ECE from sample-weighted ECE. Detailed results and claim boundaries: `CONFORMAL_AND_CALIBRATION_CORRECTION_20261107.md`. Corrected manuscript table sources and hashes are recorded in `paper/tables/conformal_corrected_table_manifest_20261107.json`; the existing PDF predates this change. Final verification passed: 141 tests, Ruff, compileall, `uv lock --check` (54 packages), and `git diff --check`; three known OpenPyXL warnings occurred during read-only AngioCAD workbook tests. No TeX compiler is available, so the existing PDF was preserved and remains older than the corrected manuscript source.
