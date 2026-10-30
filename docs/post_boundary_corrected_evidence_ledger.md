# Post-boundary-corrected evidence ledger

**Purpose:** Consolidated record of the corrected CARDIODIAG experiment
artifacts, protocols, metric definitions, claims, and limitations.

**Scope:** This ledger covers the generated `post_boundary_corrected_*`
artifacts. It does not replace the historical or pre-correction artifacts.
No independent external validation is represented here.

## 1. Corrected artifact inventory

| Experiment family | Five States / `heart5.csv` | Mendeley |
|---|---|---|
| Stability | [`post_boundary_corrected_stability_heart5.json`](../results/generated/post_boundary_corrected_stability_heart5.json) | [`post_boundary_corrected_stability_mendeley.json`](../results/generated/post_boundary_corrected_stability_mendeley.json) |
| Nested validation | [`post_boundary_corrected_nested_heart5.json`](../results/generated/post_boundary_corrected_nested_heart5.json) | [`post_boundary_corrected_nested_mendeley.json`](../results/generated/post_boundary_corrected_nested_mendeley.json) |
| Stability--reliability linkage | [`post_boundary_corrected_linkage_heart5.json`](../results/generated/post_boundary_corrected_linkage_heart5.json) | [`post_boundary_corrected_linkage_mendeley.json`](../results/generated/post_boundary_corrected_linkage_mendeley.json) |

The earlier `heart5_*`, `mendeley_*`, and `schema_corrected_*` artifacts remain
historical or pre-final-correction evidence where they used the old selector
procedure. They are not silently replaced by this ledger.

## 2. Dataset identity

| Dataset | Rows | Target | SHA-256 | Role |
|---|---:|---|---|---|
| `heart5.csv` | 918 | `HeartDisease` | `e4068802a044e8a1e3ae9fa81deae7025711bf4f13e3057f96e4f1cf3b0180c2` | Development/replication benchmark |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 | `target` | `9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e` | Development/replication benchmark |

The Mendeley dataset was used by the base study and is not new independent
external evidence. The Five States file is related to public component sources
and is also not treated as independent external validation.

## 3. Protocol ledger

### Stability evidence

- Runner: `experiments/run_stability_evidence.py`
- Repeated stratified folds: 5 folds × 3 repeats.
- Selector relevance resamples: 8.
- Seed: 42.
- Stability threshold: 0.75.
- Relevance threshold: 0.02.
- Comparator: corrected resampling-based selector versus one-shot
  correlation/permutation selector.
- Feature universe: union of training-fold transformed feature names.
- Outer test labels: not used for selector fitting or stability selection.
- Selector protocol: `post_boundary_correction_v1`.

Results:

| Dataset | Stable mean repeat Nogueira | One-shot mean repeat Nogueira | Difference | Bootstrap interval | Prespecified positive flag |
|---|---:|---:|---:|---:|---|
| `heart5.csv` | 0.1117 | 0.0144 | 0.0974 | [-0.0272, 0.1978] | False |
| Mendeley | 0.2836 | 0.2149 | 0.0687 | [0.0000, 0.1671] | False |

The Mendeley interval touches zero; it is not treated as excluding zero.

### Nested validation

- Runner: `experiments/run_nested_validation.py`
- Outer validation: 3 stratified folds, 1 repeat.
- Inner selection: 3-fold `GridSearchCV`.
- Seed: 42.
- Primary inner/outer selection score: ROC-AUC.
- Candidates:
  - corrected logistic;
  - corrected OVEC;
  - corrected OSEC;
  - stable logistic;
  - stable OSEC.
- Stable candidates use the corrected selector inside the training pipeline.
- Stable selector threshold is tuned inside inner folds over `[0.5, 0.75, 1.0]`.
- Outer predictions are generated only on held-out outer folds.

Fold-mean ROC-AUC:

| Dataset | Corrected logistic | Corrected OVEC | Corrected OSEC | Stable logistic | Stable OSEC |
|---|---:|---:|---:|---:|---:|
| `heart5.csv` | 0.927704 | 0.929533 | 0.925858 | 0.927834 | 0.925268 |
| Mendeley | 0.992989 | 0.995749 | 0.994258 | 0.993013 | 0.994172 |

Fold-mean Brier score:

| Dataset | Corrected logistic | Corrected OVEC | Corrected OSEC | Stable logistic | Stable OSEC |
|---|---:|---:|---:|---:|---:|
| `heart5.csv` | 0.107239 | 0.100233 | 0.111602 | 0.107162 | 0.109453 |
| Mendeley | 0.027036 | 0.024828 | 0.023329 | 0.026970 | 0.023405 |

These are internal nested estimates, not external-validation estimates.

### Stability--reliability linkage

- Runner: `experiments/run_stability_reliability_linkage.py`
- Seeds: 42 through 51 inclusive.
- Fit fraction: 0.5625.
- Calibration fraction: 0.1875.
- Evaluation fraction: 0.25.
- Candidate pair: corrected OSEC versus stable OSEC.
- Calibration: dedicated calibration partition for split conformal prediction.
- Reliability metrics are calculated on the held-out evaluation partition.
- External labels: not used.
- The question is associational and falsifiable; no positive relationship is
  assumed.

Differences are **stable OSEC minus corrected OSEC**. Positive differences are
worse for AURC, full-coverage risk, and ECE.

| Dataset | Metric | Mean difference | Descriptive bootstrap interval |
|---|---|---:|---:|
| `heart5.csv` | ROC-AUC | -0.000864 | [-0.002683, 0.000719] |
| `heart5.csv` | Confidence-error AUC | -0.001529 | [-0.015049, 0.011360] |
| `heart5.csv` | AURC | 0.001128 | [-0.001037, 0.003589] |
| `heart5.csv` | Full-coverage risk | -0.000435 | [-0.004348, 0.003478] |
| `heart5.csv` | Conformal coverage | 0.001304 | [-0.003478, 0.005652] |
| `heart5.csv` | ECE | -0.000113 | [-0.015190, 0.018461] |
| Mendeley | ROC-AUC | -0.000236 | [-0.000433, -0.000053] |
| Mendeley | Confidence-error AUC | -0.000074 | [-0.002993, 0.004298] |
| Mendeley | AURC | 0.000162 | [0.000033, 0.000314] |
| Mendeley | Full-coverage risk | 0.000800 | [0.000000, 0.002000] |
| Mendeley | Conformal coverage | -0.000800 | [-0.002800, 0.000800] |
| Mendeley | ECE | -0.004453 | [-0.026256, 0.014645] |

Cross-seed selected-set Nogueira stability was 0.2007 for `heart5.csv` and
0.1780 for Mendeley. Spearman correlations between internal selector stability
and reliability metrics were not consistently positive:

- ROC-AUC: `rho=-0.431`, `p=0.214` for `heart5.csv`; `rho=-0.097`,
  `p=0.790` for Mendeley.
- Confidence-error AUC: `rho=-0.369`, `p=0.294` for `heart5.csv`;
  `rho=-0.446`, `p=0.196` for Mendeley.

## 4. Metric definitions as implemented

### Nogueira stability

For a binary selection matrix, the implementation computes the mean feature
selection rate, the per-feature sample variance of selection indicators, and
returns:

```text
1 - mean(per-feature sample variance) /
    (mean_selection_rate * (1 - mean_selection_rate))
```

The result is clipped to `[-1, 1]`. If the denominator is zero, it returns
`1.0`. It compares selected sets on a common feature universe; it is not a
future-sample guarantee.

### Brier score

The Brier score is the mean squared error between binary outcomes and predicted
positive-class probabilities:

```text
mean((y_true - probability) ** 2)
```

Lower is better.

### ECE

`ece_uniform` uses ten uniform probability bins. For each non-empty bin, it
computes the absolute difference between the observed positive fraction and the
mean predicted probability, then averages those absolute differences equally
across non-empty bins. Empty bins are omitted. Lower is better. The result is
bin-sensitive and is not a universal calibration guarantee.

### Confidence-error AUC

Confidence is `max(probability, 1 - probability)`. Predictions use a 0.5
threshold. The metric is ROC-AUC for distinguishing correct predictions from
errors using confidence as the score. Values above 0.5 indicate better-than-
chance ranking in the evaluated sample. This is not semantic uncertainty.

### AURC

Observations are sorted by descending confidence. The implementation computes
cumulative error risk after retaining the first 1, 2, ..., n observations and
returns the arithmetic mean of those cumulative risks. Lower is better.

**Unresolved naming ambiguity:** this implementation calls the value AURC, but
it is a discrete mean of cumulative risks rather than an explicitly integrated
trapezoidal area. The manuscript should define the implemented statistic
precisely before submission.

### Full-coverage risk

The error rate among all evaluated observations at 100% coverage:

```text
mean(predicted_label != y_true)
```

Lower is better.

### Conformal coverage

Split conformal calibration fits the estimator on the fit partition, computes
nonconformity scores `1 - p(true class)` on the calibration partition, and
forms prediction sets on evaluation rows. Coverage is the proportion of
evaluation labels contained in their prediction sets. The nominal finite-sample
interpretation relies on exchangeability and is not assumed under dataset
shift.

## 5. Interval interpretation

The intervals in these artifacts are descriptive percentile bootstrap intervals:

- Nested validation: resampling pooled outer-fold prediction rows.
- Stability: resampling three repeat-level stability summaries.
- Linkage: resampling ten seed-level paired differences or stability values.

These units are dependent because folds partition the same dataset and repeated
seeds reuse the same observations. They are not independent-patient confidence
intervals, and they should not be used as if they were population-level
uncertainty guarantees. No multiplicity-adjusted confirmatory inference is
claimed.

## 6. Fixed threshold versus nested threshold tuning

The stability evidence uses a fixed stability threshold of `0.75` and a fixed
relevance threshold of `0.02` across repeated training perturbations.

Nested validation tunes the stable selector's stability threshold inside each
inner fold over `[0.5, 0.75, 1.0]`. Therefore, the nested stable-candidate
results are not a direct replication of the fixed-threshold stability
comparison. Their purposes differ:

- fixed-threshold stability: compare feature-set repeatability under a
  prespecified selector;
- nested validation: estimate candidate performance while allowing the
  threshold to be selected inside training data.

The linkage pipeline uses the pipeline default stability threshold of `0.75`
and six selector resamples, whereas the standalone stability runner uses eight
resamples. This protocol difference is unresolved for direct cross-family
numeric comparison and must remain explicit.

## 7. Supported and unsupported claims

### Supported claims

1. The corrected pipeline enforces training-only preprocessing and selector
   fitting boundaries in the evaluated workflows.
2. The two supplied datasets support internal development/replication evidence,
   not independent external validation.
3. Feature-set stability and predictive/selective reliability are distinct
   empirical dimensions in these corrected analyses.
4. The stable selector does not show a consistent predictive, calibration, or
   selective-risk advantage over corrected baselines.
5. The corrected linkage analysis does not show a consistent positive
   stability--reliability association.
6. Results are dataset-conditional and should not be generalized to new
   populations from these artifacts alone.

### Unsupported claims

The artifacts do not support claims of:

- independent external generalization;
- clinical utility, safety, patient benefit, or deployment readiness;
- a novel feature-selection algorithm;
- universal or consistent superiority of the stable selector;
- guaranteed calibration or conformal coverage under shift;
- semantic understanding of uncertainty;
- independent-patient inferential certainty from the reported intervals.

## 8. Remaining risks and unresolved review items

1. **Mendeley score interpretation:** Very high Mendeley discrimination must be
   interpreted as benchmark-specific performance. It does not establish
   clinical generalization or transportability.
2. **No independent external validation:** Mendeley was used by the base study,
   and `heart5.csv` is related to public component sources.
3. **Small effective replication counts:** Three stability repeat summaries and
   ten linkage seeds are limited repeated estimates, not independent cohorts.
4. **Multiple comparisons:** Multiple candidates and reliability metrics are
   reported without multiplicity adjustment; secondary findings are exploratory.
5. **Dependence-aware uncertainty:** Current intervals do not model fold/seed
   dependence hierarchically.
6. **Protocol mismatch:** Standalone stability uses eight selector resamples;
   nested/linkage pipelines use six. Fixed threshold and tuned threshold
   analyses answer different questions.
7. **Software provenance:** Newly generated outputs from the updated runners
   record Python/package versions, Git HEAD, and dirty-worktree status. Existing
   corrected JSON artifacts were generated before nested/linkage provenance was
   added and remain unchanged; their dataset hashes and protocol fields are
   still available.
8. **AURC terminology:** The exact discrete implementation should be named or
   defined explicitly before manuscript finalization.
9. **License and source overlap:** Upstream licensing and possible overlap
   constrain redistribution and independence claims.

## 9. Claim-to-artifact traceability

| Proposed conclusion | Primary artifact(s) | Evidence field(s) | Scope and limitation |
|---|---|---|---|
| Corrected selector stability comparison is inconclusive on `heart5.csv` | Stability `heart5` JSON | `paired_stability_difference` | Three repeat summaries; descriptive interval |
| Stability advantage is not established on Mendeley | Stability Mendeley JSON | `paired_stability_difference` | Interval touches zero; benchmark-specific |
| Corrected OVEC has the highest listed fold-mean ROC-AUC on both datasets | Both nested JSON files | `candidates[*].fold_mean.roc_auc` | Only 3 outer folds; ROC-AUC-selected protocol |
| Stable selector has no consistent nested predictive advantage | Both nested JSON files | Stable versus corrected candidate fold means | Internal evidence; not external validation |
| Stability does not consistently improve reliability | Both linkage JSON files | `paired_reliability_differences` | Ten repeated seeds; descriptive intervals |
| No consistent stability--reliability association is observed | Both linkage JSON files | `stability_reliability_rank_correlations` | Correlation is exploratory and seed-dependent |
| Conformal coverage is measured, not assumed under shift | Linkage JSON files and [uncertainty.py](../src/cardiodiag/uncertainty.py) | `conformal_coverage`, `external_labels_used` | No independent shifted cohort was evaluated |
| No external validation claim is permitted | All six corrected artifacts; [dataset_provenance.md](./dataset_provenance.md) | Dataset roles, hashes, protocol fields | Both datasets are development/replication evidence |

## 10. Decision after audit

The corrected stability, nested, and linkage stages jointly provide enough
evidence for the main methodological conclusion. More broad experiments are not
required before a journal-readiness review. Higher-value next work is
provenance/claim reconciliation, exact metric wording, dependence-aware
statistical review, and manuscript consistency checking. Any new experiment
should be justified by a specific unresolved reviewer question and assigned a
new artifact prefix.

## 11. Kaggle 70,000-record benchmark

The additional benchmark is registered at
[`data/manifests/local_datasets.json`](../data/manifests/local_datasets.json)
and stored at
[`data/kaggle_cardiovascular_70k/cardio_train.csv`](../data/kaggle_cardiovascular_70k/cardio_train.csv).
It was downloaded on 2026-10-29 from the public Kaggle dataset page:
<https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset>.
The archive SHA-256 is
`b78ff607480810c3e27de3e11d52c4962a3a81dbb3d69365e1cf3394a67c2b23`; the
extracted semicolon-delimited CSV SHA-256 is
`21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c`.
Kaggle metadata reports the license as **Unknown**, so redistribution and
publication rights remain unresolved. The metadata attributes the dataset to
Svetlana Ulianova and describes age in days, height in centimetres, weight in
kilograms, coded cardiovascular examination variables, and binary target
`cardio`.

The file contains 70,000 rows, 11 predictors plus `id`, and target counts
35,021/34,979 for classes 0/1. There are no missing values, no exact duplicate
rows, and all 70,000 IDs are unique. The identifier is excluded before model
fitting. Categorical predictors are `gender`, `cholesterol`, `gluc`, `smoke`,
`alco`, and `active`; numeric predictors are `age`, `height`, `weight`, `ap_hi`,
and `ap_lo`. The source contains 40 records with `abs(ap_hi) > 250`, 953 with
`abs(ap_lo) > 200`, 1,234 with `ap_hi < ap_lo`, 7 with `ap_hi <= 0`, and 22
with `ap_lo <= 0`. These values were not deleted, relabelled, or manually
corrected; the existing training-only cleaner handles numeric extremes within
each fitting partition.

Exact cross-dataset duplicate analysis is limited by incompatible schemas and
the absence of shared patient identifiers. After converting age from days to
rounded years and comparing feasible common fields, no Kaggle row matched a
Mendeley row on the full tuple of age, gender, blood pressure, and cholesterol.
Partial matches are expected from non-unique clinical values and do not
establish independence. No valid full semantic tuple was available for
`heart5.csv` because its categorical and measurement schema differs.

### Kaggle completed artifacts

| Workflow | Artifact | Status |
|---|---|---|
| Reduced stability smoke | `results/generated/post_boundary_corrected_kaggle70k_smoke_stability.json` | Completed; repeated identically |
| Reduced linkage smoke | `results/generated/post_boundary_corrected_kaggle70k_smoke_linkage.json` | Completed; repeated identically |
| Full stability | `results/generated/post_boundary_corrected_kaggle70k_stability.json` | Completed: 5 folds × 3 repeats × 8 resamples |
| Full linkage | `results/generated/post_boundary_corrected_kaggle70k_linkage.json` | Completed: seeds 42–51 |
| Full nested validation | No artifact | Not completed; reduced 2×2 smoke exceeded six minutes and was stopped |

The completed stability analysis produced stable and one-shot mean repeat
Nogueira values of 0.8432 and 0.8429, respectively. The paired difference was
0.00036 with descriptive interval [0.00000, 0.00109], and the artifact's
positive-evidence flag was false. The completed linkage analysis produced
cross-seed selected-set Nogueira stability of 0.2392. Stable-minus-corrected
ROC-AUC was -0.00074 [−0.00100, −0.00049], AURC was +0.00029
[+0.00012, +0.00048], full-coverage risk was +0.00074
[+0.00038, +0.00114], ECE was +0.00025 [−0.00089, +0.00138], and conformal
coverage was −0.00018 [−0.00051, +0.00015]. The linkage selector's internal
stability was constant across seeds, so rank correlations were undefined.

These are internal results for a separate binary outcome (`cardio`), not
cross-dataset external validation of either existing target. They do not
support clinical utility, universal selector superiority, or generalization
to a new population. The incomplete nested workflow must not be described as
completed evidence.
