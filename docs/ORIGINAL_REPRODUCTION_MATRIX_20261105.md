# Original CARDIODIAG Reproduction Matrix

This matrix distinguishes the article, archived notebook behavior, current
reconstruction, and leakage-controlled pipeline. “Partial” means an analogous
component exists; it does not mean the published procedure or numbers were
faithfully reproduced.

| Original component | Article / repository evidence | Current implementation | Difference or invalidating issue | Status |
|---|---|---|---|---|
| Percentile Method | Percentile outlier replacement and imputation are described; notebooks vary in quantiles and order | `TrainingOnlyCleaner` fits bounds and imputers within training folds | Exact paper quantile rule and one canonical original code path are not established; historical notebooks include global preprocessing | Partial; corrected method is separate |
| LoRAS class balancing | Paper describes Localized Random Affine Shadow Sampling; notebook calls exist | Historical path retained; optional resampling support in corrected pipelines | Package version, parameters, generated counts, and fold-local use are not frozen; some notebooks resample before split | Not faithfully reproducible |
| XAIH-DRC relevance | Paper describes correlation and LIME-based relevance with relevance thresholds | `StableXAIHDRC` uses training-only repeated relevance/importance selection | It does not reproduce the paper's LIME settings, groups, conflict statistic, or exact PCA rule | Approximation only |
| Correlation-based feature reduction | Pearson relevance and feature grouping appear in article/workflow | Correlation/relevance baselines exist in current selector experiments | Fold-local input and exact relationship to LIME/PCA conflict logic differ | Partial |
| LIME | Article reports kernel width 3, quartile discretization, 1,500 perturbations, 30 instances, and five seeds | LIME code and archived analyses exist | No authoritative fold-local LIME run linked to every reported experiment; no single fixed notebook lineage | Historical analysis only |
| Conditional PCA | Article describes PCA depending on agreement/conflict analysis | Current pipeline contains fold-local PCA/selector analogues in selected paths | Original feature subset and component-retention rule conflict across descriptions/notebooks | Not exact |
| OVEC | Soft voting over KNN, RF, logistic regression, and SVM, with search/tuning | `build_ovec` and corrected nested evaluation | Voting weights, tuned parameters, and notebook variants are not one recoverable protocol | Candidate-family reconstruction |
| OSEC | Article describes NB, AdaBoost, decision tree, logistic base learners, five-fold OOF predictions, XGBoost meta-learner, sigmoid calibration | `build_osec`; optional `build_osec_xgboost`; separate historical runner | Default corrected model uses logistic meta learner; historical notebooks use different learners/meta models | Partial analogue, not faithful |
| Hyperparameter optimization | Article describes random/grid searches with five-fold CV | Nested inner-fold search for corrected baselines | Search spaces, objective details, package versions, and selected settings do not all match original claims | Corrected protocol only |
| Train/test split and repetitions | Article reports 75:25, five-fold CV, ten runs, seed 42 | Historical reproduction plus 3x3 nested and other seed sensitivity protocols | Archived notebooks include 80:20 and other splits; one fixed seed is not ten independent repetitions | No exact common protocol |
| Calibration | Sigmoid calibration appears in original workflow | Source-only and fold-local calibration implemented in current studies | Original calibration's exact split and relation to each table are not recoverable | Corrected calibration evidence only |
| Metrics/table lineage | Published accuracy/AUC/Brier tables | Historical outputs and authoritative local registry | No deterministic mapping from every published table cell to a frozen source run | Exact numeric reproduction unverified |

## Reproduction decision

The supplied paper and repository do not define a single, executable,
metric-exact protocol. The closest faithful reconstruction is blocked by
conflicting notebook versions, missing LoRAS environment/parameters, changing
LIME/PCA logic, model/search differences, and unknown table-to-run lineage.
The existing historical runner is an approximation and the leakage-controlled
nested implementation is a distinct corrected method. They must not be merged
or reported as though the corrected pipeline reproduced the original paper.

## What would resolve the open items

The exact article supplement/notebook versions, LoRAS package and parameters,
fold-local XAIH-DRC and PCA rules, full model search spaces, run seeds/split
indices, environment lock, and per-table result provenance would be needed for
exact reproduction. Without those items, the proper scientific disposition is
to report both the historical reconstruction and corrected results separately.
