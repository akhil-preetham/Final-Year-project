# CARDIODIAG complete project technical audit

**Assessment date:** 2026-11-08
**Branch:** `research/cardiodiag-complete-project-finalization`
**Evidence base:** frozen multi-dataset run `20261107T202404Z`, its prediction/index manifests, the existing implementation and prior audit records.

## Scope and implementation history

The repository preserves historical notebooks and student implementations alongside the corrected `src/cardiodiag` research package. The corrected package is the source for the current experiment. Earlier Heart5, Mendeley, Kaggle and transfer results remain historical evidence with their own protocols; they are not pooled with this run. Original LoRAS/LIME/XAIH-DRC behavior is not reproduced bit for bit because the exact original resampling and explainer settings are unavailable. The stable selector is a training-fold approximation and is reported as such.

## Execution path

1. Dataset-specific loaders keep the CAD, heart-failure death, MI complication and SPECT imaging outcomes separate.
2. `build_corrected_pipeline` applies training-only cleaning, median/mode imputation, categorical encoding and numeric scaling; `build_ovec` and `build_osec` preserve established ensemble definitions.
3. Six candidates are compared with nested 3x3 stratified CV where supported. SPECTF retains its official 80/187 train/test split; only its 80 training rows are subdivided for development and calibration.
4. Saved predictions are used to derive classification metrics. Source-only calibration supports conformal and feature-support diagnostics; target outcomes do not enter transfer OOD scores.
5. Machine-readable outputs and plots are written under `results/final_research_20261108/`; the manuscript source and compiled artifact remain versioned under `paper/multi_dataset_study_20261108/` and `output/pdf/`.

## Main implementation components

See [SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md](SOFTWARE_ARCHITECTURE_AND_ENGINEERING_REPORT.md), the generated module inventory at `results/final_research_20261108/module_inventory.csv`, and dependency edges at `results/final_research_20261108/module_dependency_edges.csv`. The package separates loading, preprocessing, feature selection, model construction, nested validation, evaluation, calibration/uncertainty, experiment orchestration, demo and tests.

## Verified experiment state

- 7 task datasets; 6 models; 42 within-task model summaries and 114 fold/test records.
- 72 directed model-transfer comparisons among the four UCI CAD cohorts.
- Refits reproduce saved within-task probabilities to floating-point precision; cross-OOD values are checked against the frozen run in the completion manifest.
- Six Switzerland learning-curve configurations are recorded as failed because small training subsets do not contain both classes for the requested split.
- The frozen run verification manifest records source/prepared checksums and recomputation checks. See `results/final_research_20261108/manifests/verification_manifest.json` for the consolidated validation.

## Material limitations

The four CAD cohorts are known components of Heart5; exact-row overlap checks do not establish person-level independence. Switzerland contains only eight negative cases. Heart failure, MI and SPECTF are distinct endpoints. The public benchmarks are small, old and retrospective. No prospective or independent contemporary external validation was conducted. No clinical performance or deployment conclusion is supported.

## Preserved work and additions

Frozen experiment outputs, prior audit reports, test suite, offline demo and manuscript source were preserved. This branch adds replay diagnostics, enriched aggregate metrics, data-quality tables/figures, focused reports, a completion matrix and manuscript checks. The accompanying changelog records each new artifact and excludes local raw data, row-level diagnostics and credentials.

<!-- DUPLICATE_SAFE_AUDIT START -->
## Exact-duplicate audit and sensitivity

The frozen split audit found two within-cohort exact predictor duplicate groups: Hungary rows 101/102 (label 0) and VA Long Beach rows 139/187 (label 1). In Hungary, the duplicate crossed calibration/test in fold 2 and development/outer-test in fold 3, so the frozen outer-test estimate is directly exposed in one fold. In VA, the pair did not cross development/outer-test, although repeated records remained. The sensitivity removes one row per group before any partition, re-runs six models on both affected cohorts, and re-runs all 72 directed transfers with both source and target deduplicated.

The duplicate-safe within-task winners are UCI Hungary: logistic (0.897); UCI VA Long Beach: random_forest (0.694). Across the 72 duplicate-safe transfer pairs, target ROC-AUC ranges 0.236–0.903; direction-level six-model means range 0.539–0.885 (minimum UCI Switzerland→UCI VA Long Beach, maximum UCI Cleveland→UCI Hungary). Feature-support domain OOD AUROC ranges 0.357–0.951, while target alert rate ranges 0.008–0.719. Target labels are used only for the predictive metrics, never to tune transfer models or OOD thresholds.

Frozen-versus-deduplicated score differences are not paired effects: deduplication changes the row count and the newly seeded stratified folds. These results establish sensitivity to a corrected record set, not the causal contribution of two records. The frozen data and scores remain preserved. See `results/final_research_20261108/duplicate_audit.csv`, `duplicate_partition_audit.csv`, `duplicate_safe_manifest.json`, and `metrics/duplicate_safe_*.csv`.

No exact cross-cohort feature-row matches were found, but the cohorts are part of Heart5 lineage and have no persistent participant key. Exact matching cannot rule out near-duplicates or transformed copies.
<!-- DUPLICATE_SAFE_AUDIT END -->
