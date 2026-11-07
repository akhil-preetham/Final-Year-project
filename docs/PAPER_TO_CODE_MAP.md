# Paper-to-code and protocol map

## Traceability

| Paper/research element | Historical implementation | Current implementation | Status |
|---|---|---|---|
| Five States benchmark | Archived Five States notebooks and `heart5.csv` | `data.py`, manifests, nested runners | Reconstructed with explicit schema |
| Mendeley benchmark | Archived Mendeley notebooks and CSV | `data.py`, manifests, nested runners | Reconstructed for development validation |
| 75:25 split claim | Paper claim; notebook variants include 80:20 and 75:25 cells | Nested outer folds | Not protocol-equivalent; reported separately |
| Five-fold tuning | `GridSearchCV(cv=5)` in notebooks | Inner `GridSearchCV` | Preserved as a nested inner operation |
| Ten independent runs | Appears in the requested paper protocol and analysis outputs | Repeated runners and stored seed manifests | Must not be inferred from a single fixed-seed run |
| Percentile outlier handling | Notebook preprocessing cells | `TrainingOnlyCleaner` | Corrected to training-only fitting |
| Imputation | `dropna` and target-aware class medians in variants | sklearn pipeline and training-only cleaner | Corrected; historical behavior retained only in archive |
| Categorical encoding | Manual maps and `LabelEncoder` | Explicit mixed-type preprocessing and one-hot encoding | Corrected nominal geometry |
| LoRAS/SMOTE | Notebook-only resampling | Fold-local pipeline support where configured | Historical and corrected metrics remain separate |
| XAIH-DRC | LIME/correlation/PCA notebook analyses | `StableXAIHDRC` approximation | Explicitly labelled approximation |
| OVEC/OSEC | Notebook voting and stacking workflows | `build_ovec`, `build_osec`, optional XGBoost analogue | Candidate families retained |
| Reliability/uncertainty | Historical calibration and analysis notebooks | reliability, uncertainty, external gate, and selective runners | Corrected internal evidence available |

## Article-level implementation differences

The local PeerJ article (Methods, pp. 15--22) specifies an OVEC soft vote over
KNN, RF, logistic regression, and SVM. Its OSEC description uses NB, AdaBoost,
decision tree, and logistic regression as base learners, an XGBoost meta-learner
trained on five-fold out-of-fold probabilities, and sigmoid calibration. The
corrected package's default `build_osec` uses logistic regression as the
meta-learner; `build_osec_xgboost` provides an optional XGBoost analogue. The
older `historical.py` path approximates a different notebook variant (RF,
tree, gradient boosting, NB, logistic meta-learner) and its 80:20 split after
SMOTE.
These three configurations must be named separately in any comparison.

The article describes Pearson/LIME thresholds of 0.072/0.05 and five-fold
model search, whereas archived notebooks include multiple feature/PCA paths,
global LoRAS or PCA before splitting, different voting weights, and different
test fractions. The corrected `StableXAIHDRC` is training-only and stable by
resampling, but is **not** a reproduction of Pearson + LIME + conflict-driven
PCA. No authoritative result in the current registry is labeled as a faithful
paper reproduction.

The article reports 75:25 train/test, five-fold CV, ten runs, and a fixed seed
of 42. The audited source notebooks do not implement these items as one
consistent end-to-end procedure. The corrected 3x3 nested runs use a distinct
protocol and are internal replication evidence, not direct numerical
reproduction of the paper's reported holdout values.

## Protocol conclusion

The original source and paper description are not a single executable protocol:
the repository contains multiple notebook variants and hard-coded environments.
Therefore the reconstruction reports three evidence classes separately:

1. historical notebook outputs;
2. corrected nested internal validation; and
3. evaluation-only stress or external-validation attempts.

No historical metric is silently relabelled as corrected evidence, and no
external generalization claim is made without a frozen independent manifest.

