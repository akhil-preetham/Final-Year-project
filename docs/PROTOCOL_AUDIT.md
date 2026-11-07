# Original protocol audit

## Published-paper claims checked against the supplied article

The local copy `../peerj-cs-4059-BASE_PAPER.pdf` is the published PeerJ article
(DOI `10.7717/peerj-cs.4059`). It describes a 75:25 train/test split, five-fold
cross-validation within the training portion, training-only preprocessing, and
an untouched 25% final test set (article pp. 18--19). It also says results are
averaged over 10 independent runs with a fixed random seed of 42 (pp. 23--24).
OVEC is described as random-search tuning of LR, RF, KNN, and SVM; OSEC as grid
search over base learners with an XGBoost meta-learner trained on out-of-fold
probabilities (pp. 19--21).

The paper's stated protocol and its execution lineage are not interchangeable.
The audited original repository snapshot is commit
`e63b02c8a2aba6344a48025f657696fd99ac3a5f` (2026-01-31), which predates the
article's publication. It contains datasets and four RAR notebook archives,
without a portable package, locked environment, or one unambiguous executable
protocol. The expanded notebooks demonstrate materially different paths:

- `Daza_Paper_Exact_Accuracy.ipynb` applies SMOTE to all rows, then uses an
  80:20 split with seed 42 and five-fold grid searches.
- The Five States full-methodology notebook applies LoRAS before its later
  75:25 splits. Correlation and PCA operations are also performed on a full
  resampled table in some cells; other cells split before LIME or tuning.
- The article's claims of a single 75:25 protocol and ten independent runs
  therefore cannot be mapped to one consistent notebook execution. Reusing
  seed 42 does not by itself establish ten independent data partitions.
- The article describes cross-dataset harmonization/generalization, but its
  evaluation is presented as separate within-dataset 75:25 holdouts. No
  train-on-Five-States/test-on-Mendeley or leave-one-dataset-out result is
  specified. This does not establish predictive transport between datasets.
- The paper describes a patient-level split, but the distributed feature tables
  do not provide a common patient-linkage key that allows this claim to be
  independently audited. Duplicate-row removal is not equivalent to patient
  linkage.

These observations establish code-level risks and protocol ambiguity; they do
not determine which notebook outputs generated each article table. The exact
article metrics have not been bit-for-bit reproduced.

## Reconstructed versus corrected execution

`cardiodiag.historical.run_historical_native` is an explicitly labelled
forensic approximation of the 80:20-after-SMOTE notebook ordering. It fixes
SMOTE's random state for repeatability, whereas the source cell calls
`SMOTE()` without a `random_state`, and it does not reproduce every notebook
model-tuning/calibration step. It is not described as a faithful reproduction
of the published 75:25/ten-run article method. The
corrected runner instead uses nested outer/inner splits; preprocessing,
selection, and tuning are fitted inside training partitions. The outer test
rows are scored once and are not used for model choice. Calibration and
conformal runners use distinct training, calibration, and evaluation partitions.

The current 3x3 seed-42 stage is an internal corrected comparison, not the
article's holdout protocol. The corrected comparison and historical metrics
must remain separate evidence families.

## Leakage assessment

| Risk | Historical evidence | Corrected status |
|---|---|---|
| Resampling before evaluation split | Directly present in the Daza reproduction and LoRAS notebook | No resampling in the primary nested comparison; sampler, when configured, must be inside the training pipeline |
| Global imputation/outlier bounds | Present in notebook variants | Fold-local pipeline fitting |
| Target-aware imputation | Present in a full-methodology path | Removed from the prediction-time pipeline |
| Global PCA/feature selection | Present in LoRAS/XAIH-DRC notebook variants | Fold-local stable-selector approximation; not a faithful LIME/PCA reconstruction |
| Test-driven model selection | Possible across repeated notebook analyses; exact table lineage unclear | Inner-search rule; outer metrics are reported for all candidates |
| Calibration on evaluation rows | Variant-dependent | Separate calibration partition in reliability/conformal workflows |
| External fitting | Not applicable to historical benchmark runs | Fail-closed external gate |

## Fidelity limits and evidence status

The historical runner captures only one representative notebook path. A
bit-for-bit reproduction remains unverifiable because the archived workflows
conflict on split size, resampling order, model definitions, hyperparameter
spaces, package versions, and saved outputs; the LoRAS dependency and parameters
are not frozen; and the paper does not identify which notebook generated every
table. Do not interpret the 80:20 forensic score as reproduction of the
published score.

The corrected experiments support comparisons on the supplied development
benchmarks only. They do not establish clinical utility, fairness,
transportability, or independent external validity. See
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md` for requirement-level disposition.
