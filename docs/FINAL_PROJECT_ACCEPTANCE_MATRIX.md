# CARDIODIAG final project acceptance matrix

**Branch:** `research/cardiodiag-complete-project-finalization`
**Evidence run:** `20261107T202404Z`, with a duplicate-safe sensitivity replay generated 2026-11-08.
**Scope:** machine-learning research software and retrospective benchmark evaluation. This matrix does not assess or claim clinical readiness.

| Category | Status | Evidence and remaining qualification |
|---|---|---|
| Repository audit and preservation | COMPLETED | Existing implementation, results, tests, demo, original manuscript, and frozen experiment outputs are preserved. Changes are recorded in `docs/PROJECT_COMPLETION_CHANGELOG_20261108.md`. |
| Dataset inventory and provenance | PARTIALLY COMPLETED | The 17-source inventory and 136-pair compatibility matrix are complete. Seven distinct tasks were evaluated. Candidate sources still have unresolved access, license, endpoint, or feature-timing questions; source checks do not prove participant independence. |
| Data quality and preprocessing | COMPLETED | Missingness, class counts, exact duplicate rows, feature distributions, high Spearman pairs, and leakage limitations are recorded. Imputation, encoding, scaling, selection, and model selection remain within training partitions. |
| Individual classifiers | COMPLETED | Logistic Regression, KNN, SVM, and Random Forest were evaluated under the recorded protocol across seven tasks. |
| OVEC | COMPLETED | Existing OVEC configuration evaluated across all seven tasks and in all 72 directed CAD transfers. |
| OSEC | COMPLETED | Existing OSEC configuration evaluated across all seven tasks and in all 72 directed CAD transfers. |
| Model comparison | COMPLETED | Six configurations, 42 model rows, 114 fold/test rows, confusion-derived metrics, pooled metrics, fold metrics, and duplicate-safe Hungary/VA sensitivities are available. Rankings are descriptive. |
| Overfitting and generalization diagnostics | PARTIALLY COMPLETED | Train/test AUC and accuracy gaps are available for all 42 model/task configurations, with duplicate-safe folds for Hungary and VA. Training precision, recall, and F1 were not regenerated for the 12 duplicate-safe sensitivity configurations. Patient linkage, near-duplicate detection, and independent-site generalization remain unproven. |
| Feature selection | PARTIALLY COMPLETED | Existing feature-stability comparisons are preserved and reported. Original XAIH-DRC/LoRAS/LIME settings are not reconstructable from available records. |
| Ablation studies | PARTIALLY COMPLETED | Historical matched and reduced comparisons are reported. The original A–L design is not a prespecified complete factorial, so component-specific causal benefit is not established. |
| Calibration | PARTIALLY COMPLETED | Brier score, ECE, reliability plots, and existing calibrated outputs are evaluated. A full controlled comparison of Platt scaling and all requested calibration alternatives was not completed. |
| Conformal prediction | COMPLETED | 80%, 90%, and 95% empirical coverage and set-size diagnostics are saved; Hungary/VA have duplicate-safe recalculations. These are finite-sample empirical results, not transport guarantees. |
| OOD detection | COMPLETED | Within-task error detection and all 72 source/target feature-support diagnostics are recorded. Target outcomes did not tune cross-cohort OOD thresholds. |
| Selective prediction | COMPLETED | Coverage, accepted-subset errors, and risk/coverage diagnostics are saved. No universally reliable operating point is demonstrated. |
| Cross-dataset evaluation | COMPLETED | All 72 directed CAD transfers were rerun after exact-row deduplication on both source and target. These are retrospective cohort stress tests, not independent external validation. |
| Computational performance | PARTIALLY COMPLETED | Refit time, inference latency, and serialized size were measured. Peak memory was not instrumented, and the full custom nested search for the 70K benchmark was not completed. |
| Software quality | COMPLETED | Full pytest suite: 143 passed, 0 failed, 0 skipped; three nonfatal OpenPyXL conditional-formatting warnings. Ruff, compileall, `uv lock --check`, and `git diff --check` passed. |
| Offline demonstration | COMPLETED | Synthetic offline guard check passed for in-domain classification, uncertainty abstention, outside-support abstention, and unknown-domain abstention. |
| Technical documentation | COMPLETED | Focused reports, technical research report, architecture/demo documentation, machine-readable inventories, and this matrix are present. |
| LaTeX manuscript | PARTIALLY COMPLETED | A seven-page revised manuscript compiled with Tectonic 0.17.0; citations, references, figures, and page layout were checked. Author order, affiliations, institutional ethics determination, declarations, and venue remain for the project team to confirm. |
| Reproducibility package | PARTIALLY COMPLETED | The 114 within-task selected-fit replays, 114 primary AUC checks, 72 OOD checks, and 1,362 metric/prediction checks passed. Raw data and row-level predictions remain local; reproduction requires access to those locally held UCI source files. |
| Submission package | PARTIALLY COMPLETED | The source, aggregate artifacts, and revised PDF are prepared. Project-team declarations and a repository code license remain unresolved; restricted and locally held data are excluded. |
| Clinical deployment or device validation | NOT APPLICABLE | The project scope is computer-science and machine-learning research; no clinical-use claim is made. |

## Material finding

The frozen Hungary run placed identical predictor rows 101 and 102 across development/outer-test in fold 3 and calibration/outer-test in fold 2. The duplicate-safe rerun removes that row before partitioning and is the more defensible Hungary sensitivity estimate. VA Long Beach also contained a repeated predictor row; its pair did not cross development and outer test in the frozen folds. Frozen results are preserved. Fold changes after deduplication also reflect fold reshuffling, so score differences are descriptive, not paired causal effects.

## Submission gate

The project software and research artifacts are substantially complete. The revised manuscript remains a working draft until authorship, affiliation, ethics determination, funding/conflict/contribution statements, data-use wording, and target venue are confirmed. No independent contemporary cohort was available, so independent external validation remains unproven.
