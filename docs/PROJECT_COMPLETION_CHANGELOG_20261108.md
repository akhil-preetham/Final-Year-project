# Project completion changelog — 2026-11-08

## Added on `research/cardiodiag-complete-project-finalization`

- `experiments/run_project_completion_diagnostics.py`: exact-order replay of saved selected fits, training/resubstitution diagnostics, 80/90/95 conformal coverage, OOD-score replay, latency and serialized size.
- `experiments/build_final_completion_deliverables.py`: deterministic builder for aggregate metric/data-quality tables, figures, manifests and focused reports.
- `results/final_research_20261108/`: aggregate metrics, inventory/compatibility tables, EDA and reliability figures, module inventory, manifests; row-level scores/checkpoints are ignored locally.
- Focused technical audit, data compatibility, model comparison, overfitting, ablation, calibration, OOD/selective, transfer, performance, architecture, demo, technical research, manuscript-finalization, acceptance and changelog reports.
- Root README current-status note for this completion branch.

## Supplemental ablation extension

- Added `experiments/run_final_ablation_extension.py`, a matched nested comparison of no feature selection, one-shot relevance selection and StableXAIHDRC, each with balanced or unweighted Logistic Regression, across all seven benchmark tasks.
- Reused the frozen outer assignments where valid and removed exact duplicates before regenerating Hungary/VA folds. Preserved local row-level predictions/checkpoints; committed aggregate fold metrics, summaries, paired fold deltas, and figures.
- Added unit coverage for the one-shot selector wrapper, confusion-derived metrics, and class-weight configuration. All 114 candidate-fold records were independently recalculated from predictions across 15 metrics.
- Updated the focused ablation report, technical research report, acceptance matrix, and the versioned manuscript with the supplemental evidence. Historical A–L and original preprocessing cells remain incomplete because their exact specifications are unavailable.

## Preservation and exclusions

The original and corrected implementations, OVEC/OSEC definitions, prior experiment results, existing tests, demo, historical reports, and versioned manuscript were preserved. Raw datasets, `data/access_requests/`, local row-level predictions/checkpoints, credentials, and prior untracked audit artifacts are not staged. The exact-SPECT partition-name adjustment only aligns replay with the frozen assignment manifest; it does not change the primary run.

## Calibration and OSEC tuning extensions

- Added `experiments/run_calibration_extension.py` and source-only comparisons of raw, Platt, isotonic, beta, and temperature probability maps across seven tasks and six models. Hungary/VA calibration probabilities were reconstructed after exact-row deduplication; held-out probabilities matched the saved duplicate-safe outputs to `1.11e-16` maximum absolute error. Added fold metrics, summaries, paired deltas, fitted parameters, seven task-wise reliability figures, a per-task Brier-change heatmap, and a manifest. Row-level predictions remain ignored locally.
- Added `experiments/run_osec_optimization_ablation.py` and compared unchanged OSEC with fixed meta-estimator `C=1` against the existing inner search over `{0.1,1,10}` across all seven tasks. Added 38 condition/fold records, task summaries, paired metric differences, a figure, and manifest. Switzerland's existing five-fold internal stacking warnings were retained.
- Added focused tests for calibration mapping and fixed OSEC configuration, plus a deterministic paper-asset builder.
- Updated the calibration, ablation, complete technical research, acceptance, and manuscript reports. Preserved the previous six-page and seven-page manuscript versions; added an eight-page compiled version with verified citations, references, figures, tables, and visual review.

<!-- DEDUP_SAFE_IMPLEMENTATION START -->
The exact-duplicate sensitivity found two groups in Hungary and VA Long Beach. The Hungary frozen split placed one duplicate across development/test and calibration/test boundaries. A fresh deduplicated evaluation completed 12 within-task model runs and all 72 directed transfers. Aggregate comparisons, data-quality tables, updated manuscript tables/figure, and a versioned LaTeX source bundle were added. The primary frozen outputs were retained.
<!-- DEDUP_SAFE_IMPLEMENTATION END -->
