# Method reproduction audit

## Original method sources

The original authors' Git snapshot e63b02c contains data and four notebook archives, not a package with a single executable method. The paper specification is separately recorded in PROTOCOL_AUDIT.md and ORIGINAL_ALGORITHM_WALKTHROUGH.md. Archived notebooks include Daza_Paper_Exact_Accuracy.ipynb, Reviewer1_XAIH_DRC.ipynb, Reviewer1_Five_States_Full_Methodology.ipynb, and Mendeley variants.

## Reproduction matrix

| Component | Original evidence | Current implementation | Assessment |
|---|---|---|---|
| Data loading and target | Notebook paths/manual dataset setup | Validated loader and dataset-specific adapters | Corrected implementation; historical schemas retained |
| Imputation/outlier treatment | dropna, global percentiles, class-aware medians; paper also describes mean imputation | TrainingOnlyCleaner with training-fold statistics, no target use | Method changed to fix leakage; not exact reproduction |
| Balancing | Paper LoRAS; notebook LoRAS/SMOTE, sometimes before split | No resampling in corrected primary pipeline; historical SMOTE path retained | Exact LoRAS cannot be reproduced from frozen parameters/environment |
| XAIH-DRC | Correlation + LIME + agreement/conflict + conditional PCA | StableXAIHDRC correlation/permutation/stability approximation | Explicit approximation; not original XAIH-DRC |
| OVEC | KNN/RF/LR/SVM vote, search and weights vary | Deterministic soft vote with fixed defaults | Family preserved; search/weights differ |
| OSEC | Paper NB/Ada/tree/LR with XGBoost meta; notebooks vary | Five-fold OOF stacking; LR default meta; optional XGBoost meta | Partial structural reproduction; no unique original configuration |
| Calibration | Sigmoid calibration appears in notebooks | Source-only calibration separated from external evaluation | New leakage-controlled protocol |
| Evaluation | Paper 75:25, 5-fold, ten-run claim; notebooks include divergent 80:20/75:25 sequences | 3x3 nested internal study and separate source-to-target studies | Corrected but not protocol-equivalent |

**Conclusion:** Exact, metric-level reproduction is PARTIAL/BLOCKED by divergent notebooks, missing LoRAS configuration, changing LIME/PCA choices, environment gaps, and absent article-table lineage. Corrected outcomes are new experiments and must not be labelled original reproduction.
