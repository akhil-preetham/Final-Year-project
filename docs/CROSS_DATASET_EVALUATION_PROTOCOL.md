# CARDIODIAG cross-dataset evaluation protocol

**Protocol version:** `CD-XD-001`  
**Date:** 2026-11-03  
**Status:** design and feasibility stage; no cross-dataset predictive run is
authorized by this document  
**Baseline:** `LOCAL_MODEL_BASELINE_2026-11-03_V1`

**Historical status update (2026-11-05):** The user subsequently requested
execution of an exploratory leave-one-source-out pilot. That work was run under
the separate frozen protocol `CD-XD-002` in
`docs/TRANSFER_STUDY_PROTOCOL_20261105.md`. This earlier protocol remains the
design record for its proposed tracks; the newer pilot does not establish an
independent external-validation claim.

## 1. Purpose

This protocol is designed to determine whether SAGE-Transfer addresses a real,
measurable research gap, or whether an existing method already provides the
required cross-dataset behavior. It is deliberately not an accuracy-optimization
plan and does not authorize implementation of a new classifier.

The protocol separates four questions that are often incorrectly combined:

1. **Semantic feasibility:** Can the source and target cohorts be mapped to a
   common, clinically defensible feature and endpoint definition?
2. **Cross-dataset transport:** Can a model trained without target labels rank or
   calibrate target cases on a previously held-out cohort?
3. **Adaptation value:** Does a declared use of unlabeled or few-shot target data
   improve transport without leaking target evaluation information?
4. **Novelty:** Does SAGE-Transfer add a measurable capability beyond existing
   cross-dataset, foundation-model, AutoML, retrieval or domain-adaptation
   methods under the same information and compute budget?

Failure at question 1 or lack of an eligible target cohort is a feasibility
failure, not evidence that a new algorithm is needed.

## 2. Non-goals and prohibitions

- Do not optimize for a fixed accuracy or ROC-AUC target.
- Do not tune feature maps, thresholds, calibration, model choice or refusal
  rules on a held-out target cohort.
- Do not call heart5, Mendeley or the 70K file independent external validation
  under the current provenance record.
- Do not pool row-level predictions from incompatible endpoints into one score.
- Do not compare a target-trained model with a source-only model as if they had
  the same information budget.
- Do not implement SAGE-Transfer until the feasibility gate below is passed.
- Do not overwrite the frozen local-model baseline or reuse its paths for new
  cross-dataset outputs.

## 3. Frozen baseline reference

The current local results are frozen in
`results/local_model_baseline_freeze.json` and described in
`docs/LOCAL_MODEL_BASELINE_FREEZE.md`. They remain within-dataset references.

| Frozen reference | Role in this protocol |
|---|---|
| Logistic Regression, Random Forest, XGBoost, CatBoost and existing ensembles | Source-only and target-trained local comparator families, when a common feature map is approved |
| OVEC/OSEC | Existing CARDIODIAG representation/ensemble comparator, not assumed cross-dataset capable |
| AURA V1/V2 | Historical local adaptive baseline; not a new method and not a universal-transfer baseline |
| TabPFN, TabICL, TabDPT, HyperFast, CARTE, FLAT and related methods | Required literature comparators when executable, licensed and compatible; no local execution is claimed at present |

The frozen headline values are not used as cross-dataset metrics. Their purpose
is to prevent later protocol changes from making the local baseline appear
weaker or stronger by selective reruns.

## 4. Dataset roles and eligibility

Each dataset must receive one of these roles before any model result is viewed:

| Role | Meaning | Permitted use |
|---|---|---|
| `SOURCE_DEVELOPMENT` | Labels may be used for fitting and source-side selection | Training, source-only validation and meta-training |
| `TARGET_META_TEST` | Entire dataset is held out at the dataset level during development | Final cross-dataset evaluation for a pilot/benchmark |
| `EXTERNAL_LOCKED` | Independent compatible cohort frozen before final method decisions | One-way external validation only |
| `STRESS_ONLY` | Related data with unresolved endpoint/schema compatibility | Mapping/robustness audit; no transfer claim |
| `INELIGIBLE` | Provenance, endpoint, licensing or feature requirements fail | No model evaluation |

Eligibility is conjunctive. A target cohort must have:

1. documented provenance, access date/version and licensing status;
2. a target definition shown to be compatible with the declared estimand;
3. a feature map with units, codebooks, missingness semantics and directionality;
4. no unresolved patient or source overlap with development cohorts;
5. a declared target population and sampling frame;
6. enough positive and negative cases for the predeclared metrics;
7. a frozen hash and immutable manifest before target labels influence any
   decision.

“Similar column names” or a high within-dataset score is not sufficient.

## 5. Current-data feasibility audit

| Dataset | Rows | Target | Current role | Cross-dataset status |
|---|---:|---|---|---|
| `heart5.csv` | 918 | `HeartDisease` | Historical replication/development | `STRESS_ONLY`; composite of public component sources and not independent |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 | `target` | Historical replication/development | `STRESS_ONLY`; already used by the base study, and its codebook does not specify a diagnostic reference standard or angiographic threshold |
| `data/kaggle_cardiovascular_70k/cardio_train.csv` | 70,000 | `cardio` | Separate benchmark/development | `STRESS_ONLY`; different schema/target and unresolved independent provenance |

### 5.1 Candidate semantic overlap

The two small files contain plausible *candidate* correspondences for age,
sex/gender, chest pain, resting blood pressure, cholesterol, fasting blood
sugar, resting ECG, maximum heart rate, exercise angina, oldpeak and slope.
This is not an approved map: categorical codes, units, missingness conventions,
endpoint construction and source provenance still require human review.

The 70K file has plausible partial correspondences for age, gender and
cholesterol, but its blood-pressure fields, measurements, codes and `cardio`
endpoint are not established as equivalent to either small-dataset target. Its
additional height, weight, glucose, smoking, alcohol and activity fields do not
solve that endpoint problem.

### 5.2 Current decision

The local files are sufficient for a **mapping and protocol pilot**, but not for
a confirmatory cross-dataset performance claim. No current pair is approved as
`TARGET_META_TEST` or `EXTERNAL_LOCKED`. A direct train-on-one-file/test-on-
another run would create a number, but not a valid SAGE-Transfer evaluation.

## 6. Required evaluation tracks

Every eligible source/target pair must be evaluated in separate tracks. Results
from different tracks must not be merged.

### Track A — Frozen zero-shot transfer

- Fit the predictor and all preprocessing on source development data only.
- Apply the pre-registered feature/endpoint map to the target.
- Use no target rows, target labels or target prevalence for decisions.
- Thresholds, if needed, are fixed from source validation; ranking metrics are
  primary.

This is the strictest test of an unseen-dataset predictor.

### Track B — Unlabeled target adaptation

- Permit only operations listed before the target is opened, such as unsupervised
  scaling, covariate-shift weighting or representation normalization.
- Fit those operations on target features without target labels.
- Keep target labels sealed until final scoring.
- Report the cost and failure rate of adaptation separately from prediction.

This is not external validation if target data were used to select the method;
it is a declared unsupervised adaptation experiment.

### Track C — Few-shot labeled adaptation

- Use prespecified target-label budgets, for example 1%, 5% and 10%.
- Draw adaptation/calibration rows using a fixed seed and keep an untouched
  target test partition.
- Repeat the sampling only if the repetition count is fixed before evaluation.
- Never tune the label budget after seeing results.

This measures few-shot adaptation, not zero-shot generalization or independent
external validation.

### Track D — Target-trained local upper bound

- Train the frozen local baselines on target training rows with nested
  target-only preprocessing and selection.
- Keep this comparator separate from Tracks A–C.
- Interpret it as a target-data upper/reference condition, not transfer.

### Track E — Locked external validation

- Freeze the external manifest, feature map, endpoint definition, code version,
  model weights and output schema before reading evaluation labels.
- Run exactly once per locked external cohort.
- No recalibration, threshold selection, feature deletion or model comparison is
  allowed after the external labels are inspected.

## 7. Dataset-level split design

### 7.1 Leave-one-dataset-out meta-test

For datasets `D1 ... Dk`, define each outer task as:

```text
development = D1 ... D(k-1), excluding target Dj
target_meta_test = Dj
```

The target dataset is held out as a whole. No row from `Dj` may be used for
feature-map choice, model selection, calibration, threshold selection,
hyperparameter tuning, router training or stopping decisions.

For a confirmatory study, source cohorts must be grouped by provenance so that
near-duplicate component datasets cannot appear in both development and target
roles. A pilot with fewer than three independent target cohorts is labelled
`INCONCLUSIVE`; a confirmatory study should pre-register at least five
independent target cohorts or clearly report that it remains a low-power pilot.
These counts are design safeguards, not claims of a universal statistical
threshold.

### 7.2 Source-side nested selection

Within each outer task:

1. Fit preprocessing and candidate models on source-training rows only.
2. Use source-validation rows and source-task holdouts for model selection.
3. If a meta-router is used, train it on source tasks and validate it on a
   source task not used for router fitting.
4. Freeze the resulting policy before touching target labels.
5. Evaluate once on the complete untouched target test partition.

Row-level cross-validation is allowed for fitting a source cohort, but it cannot
replace the dataset-level holdout. Repeated target peeking invalidates the
outer-task result.

## 8. Feature, endpoint and leakage controls

The protocol requires a versioned mapping file containing, for every transferred
field:

- source and target names;
- clinical meaning and unit;
- allowed value range and codebook;
- directionality and transformations;
- missingness meaning and imputation policy;
- whether it is available at prediction time;
- reviewer and approval status.

The following are mandatory:

- remove identifiers and source-specific row keys before fitting;
- reject post-outcome or label-derived variables;
- fit imputation, scaling, encoding, feature selection and weighting on source
  training data only;
- never infer categorical semantics from integer values alone;
- preserve impossible values for a declared sensitivity track rather than
  silently repairing them;
- record a `MAP_FAIL` or `MAP_UNCERTAIN` outcome instead of forcing a transfer;
- treat no safe map as a valid abstention/failure result.

Target endpoint compatibility must be approved from cohort documentation and
clinical definitions, not inferred from binary column names.

## 9. Comparator set

The minimum executable comparator set is:

1. source-only Logistic Regression;
2. source-only CatBoost;
3. source-only XGBoost;
4. source-only Random Forest or corrected OVEC/OSEC where the map supports it;
5. the strongest fixed source ensemble from the frozen baseline;
6. a target-trained CatBoost and Logistic Regression upper/reference condition;
7. an explicit `NO_TRANSFER`/`MAP_FAIL` policy.

The literature comparator set should add TabPFN, TabICL, TabDPT, HyperFast,
CARTE, FLAT and Drift-Resilient TabPFN when each is executable, licensed,
version-pinned and evaluated under the same track. Their absence from the
current environment is a feasibility limitation, not permission to omit them
from a universal-method claim.

SAGE-Transfer is not a comparator until its mechanism is implemented after this
protocol gate. The protocol must first establish that the task is valid and that
existing methods do not already meet the requirement.

## 10. Predeclared outcomes

### Primary outcomes

- AUROC for discrimination;
- Brier score and log loss for probabilistic reliability;
- valid-target coverage and failure-to-map rate for guarded transfer.

PR-AUC is reported when prevalence differs materially; it must not replace
AUROC silently. Accuracy is secondary and is never the optimization target.

### Secondary outcomes

- calibration slope and intercept;
- ECE with its binning rule fixed in advance;
- sensitivity, specificity and balanced accuracy at a source-frozen threshold;
- selective risk versus coverage and abstention rate;
- subgroup or site performance when identifiers are ethically and legally
  available;
- training/inference time, peak memory, model size and adaptation time;
- mapping labor, number of manually reviewed fields and `MAP_UNCERTAIN` rate.

### Aggregation

Report every target dataset separately. The summary is a macro-average across
target datasets, not a pooled row-level metric. Use paired dataset-level
differences against each comparator. Confidence intervals are obtained by
resampling target datasets only when there are enough independent targets; row
bootstrap intervals are secondary and must not be presented as evidence of
cross-cohort generalization.

## 11. Statistical comparison and decision rule

For metric `m` and target dataset `j`, define the paired difference:

```text
Delta[j, method] = m[j, method] - m[j, comparator]
```

Reverse the sign for loss metrics so that positive is always better. Freeze the
comparator, direction, non-inferiority margin and multiplicity plan before
opening target labels.

SAGE-Transfer can be considered to address a measurable gap only if all of the
following hold:

1. the mapping and endpoint gates pass for the declared target cohorts;
2. the method is evaluated on at least the predeclared pilot/confirmatory number
   of independent target datasets;
3. it is compared with the strongest executable existing method under identical
   information, adaptation and compute budgets;
4. it shows a predeclared improvement in at least one reliability, coverage or
   safe-transfer outcome without unacceptable discrimination degradation;
5. the result is not driven by one target cohort or by post-hoc mapping changes;
6. it has a reproducible advantage in failure handling, semantic compatibility,
   calibration under shift or compute—not merely a new name for model routing.

If an existing method meets the same criteria, the proposed SAGE gap is closed
for that setting. If all methods fail because the schemas or endpoints cannot be
aligned, the result is `INFEASIBLE`, not evidence of algorithmic novelty. If the
sample of target cohorts is too small, the result is `INCONCLUSIVE`.

## 12. Required artifacts for every run

Each run must write a new namespaced artifact containing:

- protocol version and git/source hash;
- dataset manifest hashes and role assignments;
- mapping version and approval status;
- exact source/target split assignments;
- target-label access mode (`none`, `unlabeled`, `few_shot`, `evaluation_only`);
- model versions, hyperparameters and random seeds;
- preprocessing fitted-data provenance;
- row-level target predictions, labels and abstention flags where permitted;
- per-target and macro metrics with metric definitions;
- calibration, selective-risk and runtime summaries;
- failures, map uncertainty and reasons for exclusion;
- artifact SHA-256 and a human-readable interpretation.

No artifact may claim external validation unless its role is
`EXTERNAL_LOCKED` and the one-way gate passed.

## 13. Stop rules

Stop before model fitting if:

- target endpoint compatibility is unresolved;
- source/target overlap cannot be assessed to the predeclared standard;
- the feature map requires target labels or post-outcome information;
- licensing or access status is unresolved;
- the target cohort is too small for the declared estimands;
- the implementation would require changing the frozen baseline or protocol.

The correct output in each case is a feasibility report with the blocker and
the required data or review action.

## 14. Current authorization

As of 2026-11-03, this protocol authorizes documentation and data/provenance
feasibility work only. It does **not** authorize a direct heart5-to-Mendeley,
heart5-to-70K or Mendeley-to-70K predictive transfer run. A new run becomes
authorized only after a compatible target manifest and approved mapping pass the
gates above.
