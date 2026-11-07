# Original CARDIODIAG reconstruction

**Purpose:** distinguish the paper's method, archived code/notebook variants, and the corrected research implementation. This is not a claim of exact metric reproduction.

## Source evidence and reproducibility boundary

The local Git snapshot at commit `e63b02c8a2aba6344a48025f657696fd99ac3a5f` contains datasets and four RAR snapshots rather than one packaged executable implementation. The local audits `ORIGINAL_ALGORITHM_WALKTHROUGH.md`, `METHOD_REPRODUCTION_AUDIT.md`, `PROTOCOL_AUDIT.md`, `ORIGINAL_REPRODUCTION_MATRIX_20261105.md`, and `ORIGINAL_TO_CURRENT_PIPELINE_TRACE_20261105.md` record paper and notebook evidence. Notebook variants disagree on split order, preprocessing, ensembles and tuning. The reconstruction below preserves those differences; exact reproduction is therefore not claimed.

## End-to-end method comparison

| Pipeline stage | Published-method description / observed original variants | Current corrected research implementation | Classification and rationale |
|---|---|---|---|
| Dataset loading | Manual notebook paths for Five States/Heart5 and Mendeley; schemas/targets vary by notebook | Validated dataset adapters and provenance manifests | Modified/corrected: explicit schemas, target separation and hashes improve traceability. |
| Preprocessing | Percentile outlier bounds (commonly 1st/99th in notebooks), imputation and category encoding; some global preprocessing occurs before split | Training-only preprocessing inside estimator pipelines/folds | Corrected: fit boundaries prevent evaluation-fold information from influencing transforms. Not bitwise historical reproduction. |
| Class balance | Paper describes LoRAS; notebooks call LoRAS/SMOTE, sometimes before later split | Corrected primary pipeline does not oversample; historical/resampling analyses are separate | Modified: resampling before split leaks synthetic information; exact LoRAS configuration is not fixed in sources. |
| Feature reduction | XAIH-DRC combines target correlation, global LIME, agreement/conflict and conditional PCA; paper/notebooks disagree on PCA scope/components | StableXAIHDRC-style correlation/permutation/stability approximation; fold-aware | Replaced/approximated: preserves feature-selection intent but is not original XAIH-DRC and does not claim identical selection. |
| Explanation | LIME perturbation explanations and global aggregation in source descriptions | LIME/global analyses and stability/ablation evidence exist in separate workstreams | Modified: explanations are model-behavior evidence, not causal or clinical explanations. Current app does not invent per-instance contributions. |
| Base models | OVEC variants use KNN, RF, logistic regression and SVM; OSEC paper lists NB/AdaBoost/tree/logistic with XGBoost meta-learner; notebooks differ | Explicit `build_ovec`, `build_osec`, and paper-like XGBoost-meta variant | Preserved at ensemble-family level; member/search differences are documented. |
| Voting (OVEC) | Soft-vote family, with reported weights and variants not uniquely pinned down | Deterministic soft-vote research baseline and explicit candidate search | Modified: fixed/configured implementation is reproducible, but not same fitted model as original. |
| Stacking (OSEC) | Paper-like OOF stacking; notebook variants use different estimators/meta learners | `StackingClassifier`/OOF estimators with logistic-regression default and separate XGBoost-meta variant | Partially preserved/corrected: base predictions for meta-learning are generated out of fold; configurable variants remain distinct. |
| Hyperparameter search | Paper reports 5-fold search and ten runs; notebooks vary between 75:25 and 80:20 and inspect test results in some flows | Nested inner/outer model selection with saved seeds/configuration | Corrected: model selection isolated from outer test data. Exact search-space/result equivalence is unavailable. |
| Calibration and uncertainty | Calibration/bootstraps are inconsistent across archived notebooks | Source-only calibration, conformal sets, OOD scores, selective rules are separately evaluated | Added/corrected: leakage boundaries and transfer assumptions are explicit. |
| Final prediction | Historical notebook outputs are not one immutable estimator and may include post-test selection | Guarded predictor scores only registered domains and in-support singleton cases; otherwise abstains | Added: explicit fail-closed research policy. It is not a clinical authorization system. |

## Reproduction experiment families

Existing artifacts include historical notebook reconstructions, corrected nested internal studies on Heart5 and Mendeley, source-cohort leave-out stress tests, source-only AngioCAD/Duke transfer studies, stability/ablation and reliability audits. These are not merged into one estimate. The historical runs document the original-style pipeline; corrected runs are a methodological reconstruction; reliability and transfer results are later exploratory extensions. See `docs/AUTHORITATIVE_METRIC_REGISTRY.md`, `docs/FINAL_EXPERIMENTAL_PROTOCOL.md`, and `docs/EXPERIMENT_PROVENANCE_AUDIT.md` for run IDs and paths.

## Reproduction verdict

**Faithful reconstruction:** partial, with deviations and unavailable specifications clearly recorded.  
**Corrected leakage-controlled implementation:** implemented and tested for the documented pipelines.  
**Novel improved algorithm:** not established. Existing components are established methods; the contribution is an integrated reproducibility/reliability assessment and its negative findings.  
**Exact original metric reproduction:** blocked by conflicting notebook variants, incomplete LoRAS/XAIH-DRC parameters, absent immutable environment and uncertain paper-table lineage.

The primary method record is `ORIGINAL_ALGORITHM_WALKTHROUGH.md`; this document consolidates it with the implementation audit and end-to-end trace.
