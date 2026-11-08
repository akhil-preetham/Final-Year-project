# Feature selection and ablation report

The corrected multi-dataset run compared the six existing model configurations and did not add a feature selector to those pipelines. Earlier evidence is summarized from the frozen feature-stability and ablation reports.

On the Kaggle 70K benchmark, mean Nogueira stability was 0.8432 for StableXAIHDRC and 0.8429 for the one-shot selector; the difference was 0.00036 with descriptive interval [0, 0.00109], and the existing positive-evidence flag was false. In a reduced nested pair, stable logistic ROC-AUC was 0.78862 versus 0.78930 for corrected logistic. The matched Heart5/Mendeley 2x2 comparisons show small, dataset-specific shifts in ROC-AUC, Brier and ECE. The AURA results are exploratory, and some switches were inactive when the same tree model was selected repeatedly.

The historical A–L ablation labels were not prespecified; the complete factorial and original LoRAS/LIME settings are unavailable. The evidence therefore does not establish a causal contribution for each named component or a universal benefit from stable feature selection.

Machine-readable tables: `results/final_research_20261108/metrics/feature_selection_metrics.csv` and `ablation_metrics.csv`. Provenance is given per row. Primary source reports: `docs/final_feature_stability_report.md`, `docs/ABLATION_REPORT.md`, and `docs/ABLATION_A_L_MATRIX_20261105.md`.

<!-- DATA_REPRESENTATION_AUDIT START -->
## Additional leakage and data-quality checks

The target field is excluded from each recorded predictor matrix, and preprocessing/model selection remain partition-local. However, files alone cannot verify predictor timing for the death-event or MI-complication tasks. Numerical feature distribution summaries, categorical value counts, and pairwise Spearman correlations with |rho| >= 0.8 are machine-readable. Pairwise correlations are descriptive and are not variance-inflation factors or evidence of causal redundancy. `leakage_audit.csv` records these limits and the exact duplicate boundary evidence.
<!-- DATA_REPRESENTATION_AUDIT END -->
