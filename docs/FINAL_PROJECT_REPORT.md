# CARDIODIAG final project report

**Report date:** 2026-11-07  
**Scope:** local research/engineering implementation and evidence in this checkout. This is not a clinical validation report, regulatory assessment, legal opinion or journal submission.

## Executive summary

CARDIODIAG now has a reproducible research implementation, a substantial test suite, dataset lineage and license audits, frozen internal and transfer artifacts, a rebuilt manuscript draft and an offline demonstration app. The engineering/research implementation is usable for a final-year research demonstration. The primary scientific objective—reliable performance on genuinely independent unseen cohorts—**was not achieved**. Keep generalization and reliability at NO-GO. Code release is blocked by ownership/redistribution and package-scan requirements. Journal submission is not ready because author/institution declarations and target venue remain pending.

| Acceptance gate | Status |
|---|---|
| Engineering | **GO** (local research prototype) |
| Research implementation | **GO** (historical/corrected/evaluation paths present; original exact reproduction partial) |
| Model reliability | **NO-GO** (external calibration/OOD/coverage evidence inadequate) |
| Independent generalization | **NO-GO** |
| Demonstration application | **GO** for local synthetic research demonstration; not clinical use |
| Reproducibility | **GO** for documented artifacts and checks on this checkout; staged snapshot is preserved on an isolated branch, with a tree savepoint pending Git author identity for a commit |
| Public code release | **BLOCKED** |
| Journal submission | **NOT READY** |

## 1. Original objective and final research question

The original objective was a cardiovascular classification framework using percentile-based outlier handling, LoRAS, XAIH-DRC/LIME, OVEC/OSEC ensembles and hyperparameter tuning. The current question is whether such a framework retains discrimination, calibration, uncertainty and useful abstention on truly independent cardiovascular populations under dataset shift. Original-method and corrected-method results must remain separate.

## 2. Original reconstruction and changes

The original local Git snapshot contains data and RAR notebook/result archives, not one immutable executable pipeline. The paper and notebooks disagree on preprocessing order, split proportions, LoRAS settings, XAIH-DRC/PCA details, estimator choices, tuning, and calibration. `ORIGINAL_CARDIODIAG_RECONSTRUCTION.md`, `ORIGINAL_ALGORITHM_WALKTHROUGH.md`, `METHOD_REPRODUCTION_AUDIT.md`, and `ORIGINAL_REPRODUCTION_MATRIX_20261105.md` map these differences.

The corrected implementation preserves the OVEC/OSEC families but uses fold-local preprocessing and nested model selection, explicit source-only calibration, stability-aware feature selection, saved prediction/provenance artifacts, and separate uncertainty/OOD/selective evaluation. The selector is an approximation, not original XAIH-DRC. Exact original metric reproduction remains partial/blocked; no new algorithm claim is made.

## 3. Datasets, provenance and compatibility

Detailed records: `FINAL_DATASET_ATTRIBUTION_REGISTER.md`, `FINAL_DATASET_COMPATIBILITY_MATRIX.md`, `FINAL_DATASET_PROVENANCE_AUDIT.md`, `COHORT_INDEPENDENCE_AUDIT.md`, and `OPEN_DATASET_LICENSE_AUDIT.md`.

- Heart5/UCI records overlap; Statlog is a 270/270 Cleveland match; Mendeley 2026 has a 918/918 Heart5 multiset match. These cannot establish independent validation.
- Z-Alizadeh Sani uses >=50% vs source >50% stenosis and lacks patient linkage.
- AngioCAD is nominally endpoint-aligned but only 377 of 413 labels have feature rows, patient linkage is unavailable, some feature units are undocumented, and target labels were previously examined.
- Duke ACATH uses >=75% vs source >50%, and redistribution terms are unclear.
- UCI heart-failure mortality and post-MI complications were acquired and analyzed as separate exploratory tasks; ECG datasets remain unacquired. None were merged with the CAD task.
- Heart5 composite and Cardiovascular 70K licensing/source lineage remain unresolved for redistribution. Public accessibility is not treated as permission.

The UCI HF and MI public source files were downloaded for the separate analyses described in Section 15. No raw data were redistributed or staged in the Git snapshot.

## 4. Baseline and improved framework results

The corrected nested study artifacts are `results/generated/post_boundary_corrected_nested_heart5.json` and `results/generated/post_boundary_corrected_nested_mendeley.json`; summary table: `results/tables/nested_summary.csv`. At seed 42 with 3 outer and 3 inner folds, corrected OVEC mean ROC-AUC is **0.9295 (SD 0.00735)** on Heart5 and **0.9957 (SD 0.00127)** on the separate 1,000-row 2021 Mendeley dataset. Corrected OSEC is **0.9259 (SD 0.01097)** and **0.9943 (SD 0.00370)**, respectively. These are internal development results, not independent external validation. The very high 2021 Mendeley result is constrained by its undefined target reference standard and predictor timing. A distinct 2026 918-row Mendeley release exactly matches Heart5, but was only screened for provenance and is not the 1,000-row benchmark.

OVEC/OSEC do not show an established universal advantage over simpler baselines. Additional model/stability/ablation outputs are indexed in `AUTHORITATIVE_METRIC_REGISTRY.md`, `ABLATION_REPORT.md`, and frozen run manifests. New or exploratory model studies are not pooled into the primary estimates.

## 5. Calibration, uncertainty, OOD and selective prediction

Source-only calibration, conformal, uncertainty and feature-support methods are in their named manifests and transfer study metrics. The primary AngioCAD CD-XD-004 feature-only Isolation Forest source-vs-target AUROC is **0.589** (conditional bootstrap 95% interval 0.541–0.635); age/sex-only sensitivity is **0.544** (0.496–0.592). Later post-hoc CD-XD-006 domain-robust diagnostics are **0.5787** for Isolation Forest and **0.5801** for kNN distance (conditional interval 0.5269–0.6345 for kNN); they use different score/policy protocols and do not overwrite the primary estimate. The often-cited **0.604** is the separate Z-Alizadeh Sani CD-XD-003 result. Source-calibrated AngioCAD ECE is 0.216 in `VALIDITY_AUDIT_20261105.md`. None of these weak cohort-discrimination values establishes reliable individual uncertainty detection.

The combined selective policy accepted **5.6% (21/377)** of AngioCAD rows; the accepted set had one outcome class, so zero observed errors are not evidence of useful risk control. Duke accepted **11.4% (401/3,504)** with 41 accepted errors, but its threshold differs. The trusted registry gate abstains on unknown sites (0% target coverage); this is metadata-based fail-closed behavior, not learned OOD success. Conformal empirical target coverage is descriptive; exchangeability assumptions do not ensure arbitrary-shift coverage.

## 6. External validation and statistical analysis

There is no verified, untouched, patient-independent, endpoint-identical external validation cohort. Existing studies are internal, overlapping, endpoint-mismatched, linkage-unverified or previously examined. Statistical/bootstrap intervals condition on observed cohorts and do not estimate between-hospital variability. Repeated CV folds are not independent populations. Small post-hoc comparisons are not confirmatory; the project does not claim universal superiority, clinical utility or causal explanation.

## 7. Explainability

The repository contains LIME-based historical/analysis material, feature ranking/stability and ablation outputs. The current stable selector is not the original XAIH-DRC, and global feature behavior is not a local explanation or causal effect. The desktop demo deliberately states that the loaded bundle lacks a validated local SHAP/LIME explanation artifact and does not fabricate one.

## 8. Demonstration application architecture and testing

`demo/app.py` is a local Tk desktop UI over `DomainAwareSelectivePredictor` and frozen `model_bundle.joblib` artifacts. It verifies the bundle hash against the adjacent demo manifest before loading. It has project status, exact-schema synthetic input, source-domain/unregistered choice, fail-closed result display, aggregate evaluation tables/plots, and explicit explanation limits. It makes no network requests and does not persist input rows. Invalid schema/categories/ranges are rejected; unknown or unsupported domains retain abstention and withhold probability. Visual desktop inspection confirmed overview, input, metrics/plots, and unknown-domain abstention; a registered synthetic example returned the frozen bundle's class/probability. This is a software demonstration only; synthetic input and its source-domain selector do not validate patient data or source identity.

Application logic tests are in `tests/test_demo_app.py`. Final suite/tool results are recorded in `FINAL_ACCEPTANCE_MATRIX.md` after post-change checks.

## 9. Reproducibility and software quality

Environment: Python 3.11--3.13, `pyproject.toml` and `uv.lock`. Reproduction commands and experiment directories are in `REPRODUCIBILITY_GUIDE.md`, `REPRODUCIBILITY_REPORT.md`, and `EXPERIMENTAL_PROTOCOL.md`. Final post-change checks passed: **127 tests**, Ruff, Python compilation, a fresh locked environment install, and `uv lock --check` (54 packages). Three known OpenPyXL warnings appeared while reading AngioCAD workbooks; files were not written back. The local research tree is mostly untracked at Git HEAD `e63b02c`; a clean version-controlled snapshot is still required before release.

## 10. Publication and release status

The consolidated LaTeX draft is `paper/manuscript.tex`; the previously built 15-page PDF is `output/pdf/CARDIODIAG_Final_Consolidated_20261106.pdf`, with hashes in `paper/build/final_consolidation_20261106/publication_manifest.json`. App changes do not change the manuscript's numeric inputs. Before submission, confirm author order/affiliations, contributions, ethics determination, funding, competing interests and journal requirements. Current declarations remain pending.

Public code release is blocked: code ownership/license authority is not established and no clean, data-free archive has been constructed/scanned. Raw data and legacy ZIPs are not approved for redistribution. No public push/upload was made.

## 11. Remaining blockers and recommendations

1. Keep the generalization claim NO-GO until a new untouched compatible cohort is accessed lawfully, patient/cohort independence is documented, and the protocol is frozen before outcomes are viewed.
2. Obtain written project-code ownership and redistribution authorization; then build and inspect a data-free release package.
3. Resolve dataset license/version/attribution questions for any proposed redistribution; otherwise continue excluding the files and derivatives.
4. Obtain written coauthor/institution confirmations for all manuscript declarations and select a venue.
5. Keep HF/MI/ECG as separate future tasks; define their own endpoints, protocols and release rights.
6. If future confirmatory data arrive, evaluate calibration/OOD/selective behavior prospectively under a preregistered protocol with enough independent sites and accepted cases.

See `USER_DECISIONS_REQUIRED.md` for the exact external confirmations needed. The current evidence set is closed; reopening requires new data, rights, or author/institution facts, not more formatting passes.

## 12. Completion-pass addendum (2026-11-06)

The follow-up completion pass preserved the upstream commit on branch
`codex/research-completion-2026-11-06`, added a source-only LOF novelty
comparison to the controlled synthetic-shift runner, and added a frozen-target
risk–coverage audit with accepted/rejected summaries and conditional Wilson
intervals. These results do not change the manuscript estimates and are not
confirmatory. See `OOD_IMPROVEMENT_REPORT.md`,
`SELECTIVE_PREDICTION_REPORT.md`, `DATASET_PROVENANCE_AND_LICENSE_REPORT.md`,
`REPRODUCIBILITY_REPORT.md`, `GITHUB_RELEASE_READINESS.md`,
`JOURNAL_SUBMISSION_READINESS.md`, and `FINAL_RESEARCH_COMPLETION_REPORT.md`.

No suitable independent validation cohort or release rights were found.
Engineering additions are tested locally; external generalization remains
NO-GO, code publication BLOCKED, and journal submission NOT READY.

## 13. Final blocker-resolution pass (2026-11-06)

The required explicit deliverable files have been added: `EXTERNAL_COHORT_SEARCH.md`, `CODE_OWNERSHIP_AUDIT.md`, `DATASET_RIGHTS_AUDIT.md`, `PUBLIC_RELEASE_MANIFEST.md`, `AUTHOR_DECLARATIONS.md`, `ETHICS_DETERMINATION_REQUEST.md`, `JOURNAL_SHORTLIST.md`, and the journal readiness record. Dataset access and upstream permission request templates are also included. The new cohort search preserves the NO-GO conclusion because every currently known candidate is overlapping, already examined, endpoint/schema incompatible, not accessible under current approvals, or lacks independence evidence.

A machine-readable dataset registry at `data/registry/datasets.json` and fail-closed `experiments/check_dataset_release.py` now block unknown, unresolved, restricted, or non-allow-listed dataset IDs. The checker does not certify a whole package or establish legal rights. Tests cover blocked, unknown and explicitly approved registry entries.

The root `nul` artifact was verified as an 82-byte failed-command error message, was not tracked, and was not referenced by project scripts. It has been removed using its Windows extended-length path. Final verification status is recorded in `FINAL_ACCEPTANCE_MATRIX.md` after execution.

Venue recommendation is provisional: BMJ Health & Care Informatics is the closest applied informatics fit for the supported, carefully limited negative evaluation. Submission remains blocked on the actual authors' approvals, institutional determination, declarations, code/data access statements, and venue approval.

The external manifest validator now fails closed unless the frozen record includes population/recruitment, endpoint compatibility, per-feature unit and timing mappings, legal evaluation access, patient independence, unseen target labels, and explicit qualification flags. It rejects prior target-label exposure. The updated tests exercise qualified records and rejection when independence, label exposure, or feature metadata fail. A separate generic BMJ HCI review-layout copy is available at `paper/manuscript_bmjhci.tex`; the original IEEE draft is preserved. Venue and all author/institution declarations remain provisional.

A conservative file-by-file ownership inventory is now available at `CODE_OWNERSHIP_FILE_MATRIX.csv` (generated by `experiments/build_code_ownership_matrix.py`). All untracked files remain unknown ownership unless independently confirmed; tracked status is not treated as copyright evidence. The inventory makes the release exclusions reviewable without claiming unresolved authorship.

Historical verification at that time: **136 tests passed** in the locked clean environment (three known OpenPyXL warnings while reading existing AngioCAD workbooks); Ruff passed; Python compilation passed; `uv lock --check` resolved all 54 packages. Dataset registry JSON parses, and the dataset release checker refuses Heart5 while its redistribution status is unresolved. The existing offline demo logic tests passed; its code was unchanged and prior visual review remains the UI evidence. The newly prepared BMJ HCI-oriented LaTeX copy was not independently compiled in this pass because no LaTeX compiler is available on PATH; the previously rendered IEEE manuscript remains the compiled artifact.

## 2026-11-07 finalization correction

The conformal finite-sample quantile was corrected and tested, and both legacy macro-bin ECE and sample-weighted ECE are now reported. Final verification passed: 141 tests, Ruff, Python compileall, `uv lock --check` (54 packages), and `git diff --check`; three known OpenPyXL warnings occurred while reading AngioCAD workbooks. Heart5 and Mendeley source-side uncertainty and linkage studies were rerun over seeds 42–51. New outputs, comparisons, and limits are documented in [CONFORMAL_AND_CALIBRATION_CORRECTION_20261107.md](CONFORMAL_AND_CALIBRATION_CORRECTION_20261107.md). Corrected manuscript table inputs are versioned and hashed. The previously compiled PDF predates these table changes.


## 14. Final model, diagnostics, figures and manuscript (2026-11-07)

The finite-sample conformal correction was applied to the model evaluation layer and rerun on the two internal development datasets and all four saved transfer protocols. The Heart5/Five States and Mendeley uncertainty and stability-linkage reruns use seeds 42–51. Corrected outputs are preserved under `results/finalization_20261107/conformal_corrected/` and `results/finalization_20261107/corrected_quantile_transfer/`. The rerun target predictions for AngioCAD and Duke reproduce the former probability, conformal-singleton, and combined-policy flags exactly; target labels were used only for scoring. ZAS and AngioCAD source-only discrimination/OOD point estimates are unchanged because the quantile fix affects conformal sets, not the fitted probability model or feature OOD scores.

The current evidence remains mixed and negative for transferability. Repeated internal source-side conformal coverage is 0.908/0.909 on Five States and 0.906/0.908 on Mendeley for corrected/stable OSEC. Macro-bin and sample-weighted ECE are both shown. Feature-only domain separation remains weak: source-vs-target AUROC 0.604 for ZAS, 0.589 for the primary AngioCAD run, and 0.580 for AngioCAD kNN support. The unknown-site registry gate returns zero automatic coverage. Post-hoc selective risk-coverage plots use frozen AngioCAD (n=377) and Duke (n=3,504) predictions with conditional Wilson intervals; Duke is endpoint-mismatched. None of these results establishes independent clinical generalization or useful safety performance.

The complete nine-figure publication set was regenerated from stored artifacts, with four supplemental figures for corrected reliability, OOD separation, and target selective-risk diagnostics. Inputs and hashes are recorded in `paper/figures/finalization_20261107/figure_manifest.json` and `finalization_diagnostics_manifest.json`. The final 16-page IEEE-style manuscript was compiled, rendered, text-checked, and visually reviewed. Build and file hashes are in `paper/build/finalization_20261107/publication_manifest.json`; the deliverable is `output/pdf/CARDIODIAG_Final_Consolidated_20261107.pdf`. TeX emitted underfull-box and Fontconfig warnings; there were no undefined-reference/citation or overfull-box warnings, and visual review found no clipping or overlap in the inspected figure/table pages.

Final software verification is recorded in `FINAL_ACCEPTANCE_MATRIX.md`. The offline demo source was not changed in this iteration. Dataset redistribution authority, project-code ownership, author/institution declarations, and a prospectively untouched compatible cohort remain outside repository control and unresolved.

## 15. Separate public clinical dataset experiments (2026-11-07)

UCI Heart Failure Clinical Records (ID 519) and UCI Myocardial Infarction Complications (ID 579) were downloaded from official CC BY 4.0 records and evaluated independently using five-fold outer / three-fold shuffled inner nested validation. HF follow-up duration was excluded; the MI run used admission-time fields and removed later observations, outcome fields, identifiers, and two concurrent outcome proxies. Mean outer-fold ROC-AUC ranged from 0.711 to 0.728 on HF death-event classification and 0.867 to 0.884 on MI any-lethal-outcome classification. Calibration was imperfect, and neither dataset has a common outcome horizon for these binary labels. The MI record identifier cannot be linked to a participant, so patient-level split independence is unverified.

The complete protocol, per-model metrics, source attribution and limitations are in [`NEW_DATASET_EXPERIMENTS_20261107.md`](NEW_DATASET_EXPERIMENTS_20261107.md). These tasks do not validate the CARDIODIAG angiographic CAD model and remain outside the six-page CAD manuscript. Raw and prepared person-level files stay excluded; only explicitly audited fold-level aggregates and figures are included in the project snapshot.
