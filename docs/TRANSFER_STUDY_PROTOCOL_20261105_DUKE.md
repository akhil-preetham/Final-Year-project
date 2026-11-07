# CD-XD-005: Duke ACATH transport and abstention protocol

## Research question

Can a source-only cardiovascular predictor trained across the four UCI Heart
Disease cohorts provide useful risk ranking on a separately collected Duke
catheterization cohort, while exposing uncertain predictions and flagging
inputs outside the source support?

## Cohort and endpoint

The source is UCI Heart Disease (Cleveland, Hungary, Switzerland, and VA Long
Beach), with the original binary endpoint `num > 0` (>50% stenosis). The target
is the Duke ACATH cohort (3,504 records), with `sigdz=1` defined as at least
75% diameter narrowing in a major coronary artery. This threshold mismatch is
prespecified and makes the target a transport stress test, not an
endpoint-identical external validation set. The dataset was sourced from the
Vanderbilt Department of Biostatistics public data repository; provenance and
attribution are in `data/manifests/duke_acath_external.json`.

## Frozen predictors and mappings

Use age, sex, and total cholesterol only. Map Duke sex (0 male, 1 female) to
the UCI convention (1 male, 0 female). Map Duke `choleste` (mg/dL) to UCI
`chol`. Treat UCI zero cholesterol values as missing. Impute numeric values
from source-fit medians only, with missingness indicators. Exclude `cad.dur`,
all target fields, and any post-test or diagnosis-related field.

## Development, calibration, and target isolation

For each of the four UCI cohorts, reserve 15% for probability calibration and
a separate 15% for conformal/OOD threshold calibration, with locked seeds and
stratification by source outcome. Fit preprocessing and a domain-balanced
logistic regression to the remaining 70% of source rows. Fit a Platt
calibrator only on the probability-calibration partition with equal total
weight per source cohort. Estimate conformal and OOD thresholds only on the
disjoint conformal/OOD partition. Do not refit any component on Duke data.

For cross-source validation, repeat this pipeline four times, holding one UCI
cohort out for scoring and using the other three for fitting/calibration. These
folds are source-domain stress tests, not independent external evidence, as
the UCI records overlap the historical Heart5 project composite.

## Reliability and abstention methods

Compare the locked baseline (Platt-calibrated point probability plus
Isolation Forest source-fit support score) with:

1. **Domain-robust split conformal set:** compute nonconformity
   `1 - p(y)` on source calibration rows. Compute the finite-sample 90%
   quantile separately within each calibration source, then use the maximum
   source quantile. Include class `c` for a new record when `1-p(c)` is no
   greater than that threshold. A singleton set yields a classification; a
   two-class set abstains. The worst-source threshold is intended to avoid
   pooling away source-domain calibration failures. Its coverage guarantee
   requires calibration and future observations to be exchangeable within a
   source domain; it does not guarantee coverage on unseen shifted cohorts.
2. **K-nearest-neighbor support score:** fit a source-only Euclidean neighbor
   reference on the preprocessed source-fit rows; anomaly score is the mean
   distance to the 10 nearest source-fit rows. Select the alert threshold as
   the maximum source-specific 95th percentile among the calibration domains.
   A target record above this frozen threshold is flagged as outside source
   support.
3. **Combined action:** auto-classify only when the conformal set is a
   singleton and the support score is below threshold. Otherwise abstain and
   display the calibrated probability, prediction set, and OOD reason.

Also report the existing Isolation Forest detector under the same
source-calibration false-alert budget. Detector selection will be assessed on
the four leave-one-source-out folds; no Duke labels may affect thresholds.

## Runtime domain guard

The runnable model bundle also enforces a fail-closed source-domain registry.
It exposes a score only when the caller supplies a registered development
domain ID; a new or missing domain receives an abstention with no risk score.
For a registered domain, the guard uses that domain's conformal and OOD
thresholds. The ID must come from trusted provenance metadata; this gate does
not infer site identity from measurements. It is designed to prevent
unvalidated cohorts from receiving automatic classifications, not to claim
that an enrolled source domain is clinically validated.

## Outcomes and comparisons

Report ROC-AUC, average precision, Brier score, log loss, ECE, calibration
intercept/slope, sensitivity, specificity, balanced accuracy, confusion
matrix, bootstrap 95% intervals, conformal empirical coverage, prediction-set
size, singleton coverage, selective risk, combined accepted coverage, accepted
error rate, OOD AUROC, target alert fraction, and source calibration false
alert rate. Compare calibration and OOD components to the current CD-XD-004
method where feature support allows. Record target and source metrics without
using target outcomes to select a model, threshold, feature, or method.

## Interpretation limits

The threshold difference (source >50%, Duke >=75%) changes label semantics.
The Duke cohort is an older, referred-for-chest-pain population, and cholesterol
is missing for 1,246/3,504 records. Therefore performance/calibration changes
cannot be attributed to covariate shift alone; endpoint, population,
measurement, and historical-era differences are confounded. OOD detection is
not a clinical danger detector. This is a research prototype, not a clinical
diagnostic system.

## Reproduction

From the project root, run:

```powershell
uv sync --locked
uv run python experiments/run_duke_transfer.py
uv run python demo/run_domain_guard_demo.py
uv run python -m pytest -q tests/test_duke_transfer.py tests/test_uncertainty.py
```

The run writes a manifest, row-level predictions, an inference bundle, JSON
metrics, and plots to the result directory.
