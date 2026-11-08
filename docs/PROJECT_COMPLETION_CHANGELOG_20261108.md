# Project completion changelog — 2026-11-08

## Added on `research/cardiodiag-complete-project-finalization`

- `experiments/run_project_completion_diagnostics.py`: exact-order replay of saved selected fits, training/resubstitution diagnostics, 80/90/95 conformal coverage, OOD-score replay, latency and serialized size.
- `experiments/build_final_completion_deliverables.py`: deterministic builder for aggregate metric/data-quality tables, figures, manifests and focused reports.
- `results/final_research_20261108/`: aggregate metrics, inventory/compatibility tables, EDA and reliability figures, module inventory, manifests; row-level scores/checkpoints are ignored locally.
- Focused technical audit, data compatibility, model comparison, overfitting, ablation, calibration, OOD/selective, transfer, performance, architecture, demo, technical research, manuscript-finalization, acceptance and changelog reports.
- Root README current-status note for this completion branch.

## Preservation and exclusions

The original and corrected implementations, OVEC/OSEC definitions, prior experiment results, existing tests, demo, historical reports, and versioned manuscript were preserved. Raw datasets, `data/access_requests/`, local row-level predictions/checkpoints, credentials, and prior untracked audit artifacts are not staged. The exact-SPECT partition-name adjustment only aligns replay with the frozen assignment manifest; it does not change the primary run.

<!-- DEDUP_SAFE_IMPLEMENTATION START -->
The exact-duplicate sensitivity found two groups in Hungary and VA Long Beach. The Hungary frozen split placed one duplicate across development/test and calibration/test boundaries. A fresh deduplicated evaluation completed 12 within-task model runs and all 72 directed transfers. Aggregate comparisons, data-quality tables, updated manuscript tables/figure, and a versioned LaTeX source bundle were added. The primary frozen outputs were retained.
<!-- DEDUP_SAFE_IMPLEMENTATION END -->
