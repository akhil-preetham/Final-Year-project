# Feature selection and ablation report

The corrected multi-dataset run compared the six existing model configurations and did not add a feature selector to those pipelines. Earlier evidence is summarized from the frozen feature-stability and ablation reports.

On the Kaggle 70K benchmark, mean Nogueira stability was 0.8432 for StableXAIHDRC and 0.8429 for the one-shot selector; the difference was 0.00036 with descriptive interval [0, 0.00109], and the existing positive-evidence flag was false. In a reduced nested pair, stable logistic ROC-AUC was 0.78862 versus 0.78930 for corrected logistic. The matched Heart5/Mendeley 2x2 comparisons show small, dataset-specific shifts in ROC-AUC, Brier and ECE. The AURA results are exploratory, and some switches were inactive when the same tree model was selected repeatedly.

The historical A–L ablation labels were not prespecified; the complete factorial and original LoRAS/LIME settings are unavailable. The evidence therefore does not establish a causal contribution for each named component or a universal benefit from stable feature selection.

Machine-readable tables: `results/final_research_20261108/metrics/feature_selection_metrics.csv` and `ablation_metrics.csv`. Provenance is given per row. Primary source reports: `docs/final_feature_stability_report.md`, `docs/ABLATION_REPORT.md`, and `docs/ABLATION_A_L_MATRIX_20261105.md`.

## Matched selector and class-weight ablation extension

A supplemental nested comparison was run after the duplicate-safe completion. It evaluated Logistic Regression with six configurations on all seven current tasks: no feature selection, one-shot relevance selection, or StableXAIHDRC; each was tested with balanced and unweighted downstream Logistic Regression. The one-shot selector uses the existing relevance function once; StableXAIHDRC uses its six-resample configuration. All candidates shared the same outer partitions and the same three-fold inner search over `C = {0.1, 1, 10}`. Preprocessing and selection remained inside each fitted pipeline. The target was not used for fitting transforms, selecting features, or choosing `C`.

Frozen partitions were reused for Cleveland, Switzerland, heart failure and MI. Hungary and VA were deduplicated before regenerating seeded folds. SPECTF used the existing 80/187 official split, with the development/calibration separation retained and the official test set evaluated once. The class-weight contrast changes only the downstream Logistic Regression estimator; the selectors' internal relevance estimator remains balanced by design. This is therefore a controlled Logistic Regression component study, not a class-weight conclusion for every model.

| Task | No-selection, balanced AUC | No-weight Δ AUC | One-shot, balanced Δ AUC | Stable, balanced Δ AUC |
|---|---:|---:|---:|---:|
| Cleveland | 0.915 | −0.001 | +0.001 | +0.001 |
| Hungary, deduplicated | 0.897 | +0.001 | −0.003 | −0.003 |
| Switzerland | 0.830 | −0.020 | −0.015 | −0.015 |
| VA Long Beach, deduplicated | 0.650 | +0.009 | +0.017 | +0.012 |
| Heart failure | 0.735 | −0.002 | −0.013 | −0.021 |
| MI complications | 0.854 | −0.001 | −0.002 | −0.005 |
| SPECTF Heart | 0.758 | +0.000 | +0.007 | −0.011 |

Each Δ is the mean of matched outer-fold ROC-AUC differences against the no-selection, balanced Logistic Regression candidate. The unweighted baseline averaged −0.002 AUC difference across tasks (range −0.020 to +0.009). One-shot selection with balanced Logistic Regression averaged −0.001 (range −0.015 to +0.017); StableXAIHDRC averaged −0.006 (range −0.021 to +0.012). Their unweighted counterparts also showed no consistent gain. The outcome is task-dependent; these three-fold or single-official-split contrasts are descriptive and do not support statistical-significance or universal-benefit claims.

The run produced 114 candidate-fold records, 42 task/configuration summaries and 18,624 row-level predictions. All 114 fold metric records were independently recomputed from those predictions across 15 metrics, and the manifest, data, source-code and output hashes validated. Predictions and resumable checkpoints are git-ignored; aggregate fold metrics, summaries, paired fold differences and figures are committed. Reproduce with `python experiments/run_final_ablation_extension.py` in the project environment.

Machine-readable outputs and figures are under `results/final_research_20261108/ablation_extension/`; the row-level file is local at `results/final_research_20261108/predictions/ablation_extension/out_of_fold_predictions.csv`.

## Remaining ablation limits

The full historical A–L factorial, original target-aware preprocessing, and exact LoRAS/LIME/XAIH-DRC branches remain unreconstructable from available specifications. Recreating leakage-prone original preprocessing as a modern holdout comparator would not be a valid evaluation. The new study does not isolate every interaction across all six classifiers, and it does not tune a new OVEC weight scheme because that would change the preserved canonical voting definition. Those items remain partial rather than being reported as completed.

## OSEC meta-estimator optimization ablation

A second matched component study compared the existing OSEC stack with its final Logistic Regression `C` fixed at the default 1.0 against the existing inner three-fold ROC-AUC search over `{0.1, 1, 10}`. Only this hyperparameter-selection step changed; base estimators, internal five-fold stacking, preprocessing, outer partitions and test scoring stayed fixed. Hungary and VA were deduplicated before their matched folds were formed. Tuned predictions were read from the preserved primary or duplicate-safe run; fixed-`C` OSEC was fitted on development rows only.

| Task | Fixed-C AUC | Tuned-C AUC | Δ AUC, fixed − tuned | Δ Brier, fixed − tuned |
|---|---:|---:|---:|---:|
| Cleveland | 0.900 | 0.903 | −0.003 | +0.003 |
| Hungary, deduplicated | 0.900 | 0.896 | +0.004 | +0.002 |
| Switzerland | 0.724 | 0.751 | −0.027 | +0.036 |
| VA Long Beach, deduplicated | 0.624 | 0.620 | +0.004 | +0.000 |
| Heart failure | 0.737 | 0.736 | +0.001 | −0.004 |
| MI complications | 0.861 | 0.868 | −0.006 | +0.007 |
| SPECTF Heart | 0.797 | 0.797 | +0.000 | +0.000 |

Across the seven task-level matched comparisons, mean fixed-minus-tuned changes were −0.004 AUC, +0.006 Brier and +0.016 log loss. The tuned condition modestly improved the average scores, but directions varied by task; tuning was not consistently beneficial. SPECTF selected `C=1` on its one official split, so both conditions matched there. Switzerland retained the warning that the stack’s fixed internal five-fold split exceeds the minority count in some OSEC fits; this was not changed to avoid modifying the canonical OSEC definition.

The run contains 38 condition/fold rows, 14 task/condition summaries and 42 paired metric differences. Aggregate outputs and the reproducible fit script are in `results/final_research_20261108/osec_optimization_ablation/` and `experiments/run_osec_optimization_ablation.py`. Row-level predictions remain local. This ablation narrows, but does not close, the historical A–L or original-preprocessing gaps.

<!-- DATA_REPRESENTATION_AUDIT START -->
## Additional leakage and data-quality checks

The target field is excluded from each recorded predictor matrix, and preprocessing/model selection remain partition-local. However, files alone cannot verify predictor timing for the death-event or MI-complication tasks. Numerical feature distribution summaries, categorical value counts, and pairwise Spearman correlations with |rho| >= 0.8 are machine-readable. Pairwise correlations are descriptive and are not variance-inflation factors or evidence of causal redundancy. `leakage_audit.csv` records these limits and the exact duplicate boundary evidence.
<!-- DATA_REPRESENTATION_AUDIT END -->
