# SAGE-Transfer cross-dataset feasibility report

**Date:** 2026-11-03  
**Protocol:** `CD-XD-001` in `docs/CROSS_DATASET_EVALUATION_PROTOCOL.md`  
**Baseline:** `LOCAL_MODEL_BASELINE_2026-11-03_V1`  
**Machine-readable report:** `results/cross_dataset_feasibility.json`

## Executive conclusion

The cross-dataset evaluation protocol is feasible as a study design, but the
empirical SAGE-Transfer question is **blocked with the current local data**.
The three available files do not currently provide a valid confirmatory
leave-dataset-out or independent external-validation benchmark:

- `heart5.csv` is a composite of public component datasets and is a historical
  replication/development benchmark;
- Mendeley was already used by the base study;
- the 70K Kaggle file has a different schema and target, unresolved source
  independence, and an unknown reported license.

The small datasets have plausible candidate feature correspondences, but no
approved semantic/endpoint map exists. The 70K file has only partial name-level
overlap and cannot be treated as the same prediction endpoint. Running direct
train-on-one/test-on-another experiments now would produce potentially numeric
outputs without a defensible estimand.

**Decision:** freeze the local baseline, do not implement another classifier,
and do not run cross-dataset prediction until a compatible target cohort and
mapping pass the registration gates.

## 1. Baseline freeze completed

The current local results are preserved by
`results/local_model_baseline_freeze.json`, including hashes for:

- heart5 compact candidate pool;
- Mendeley compact candidate pool;
- 70K broad screening benchmark;
- 70K tuned-priority benchmark;
- AURA V2 70K feasibility artifact;
- the derived local-model inventory and report;
- all three local dataset files and the local manifest.

The frozen reference values are:

| Dataset | Reference model | ROC-AUC | PR-AUC | Brier | ECE | Interpretation |
|---|---|---:|---:|---:|---:|---|
| heart5 | soft voting | 0.929033 | 0.931312 | 0.099458 | 0.038747 | best frozen compact-pool reference |
| Mendeley | CatBoost | 0.997828 | 0.998345 | 0.014838 | 0.122701 | best frozen compact-pool reference |
| 70K | tuned CatBoost | 0.800432 | 0.785413 | 0.180825 | 0.008961 | fairer tuned local reference |
| 70K | AURA V2 | 0.802842 | 0.786891 | 0.179746 | 0.006031 | feasibility only; baselines were frozen |

These are not cross-dataset scores and must not be averaged into a universal
performance claim.

## 2. Feasibility gates

| Gate | Result | Evidence |
|---|---|---|
| Protocol specified before a new run | PASS | `CD-XD-001` |
| Existing local results frozen | PASS | baseline freeze manifest and hashes |
| Dataset manifests and hashes available | PASS | `data/manifests/local_datasets.json` |
| Approved common feature map | FAIL | only candidate name-level correspondences exist |
| Approved common endpoint | FAIL | target definitions have not been reconciled |
| Independent locked target cohort | FAIL | no eligible external manifest is frozen |
| Existing universal methods executable locally | FAIL | TabPFN/TabICL/TabDPT/HyperFast/CARTE/FLAT packages absent |
| Predictive cross-dataset run authorized | FAIL | protocol stop rule applies |

## 3. Pairwise data audit

### 3.1 heart5 and Mendeley

There are plausible correspondences for eleven concepts: age, sex/gender, chest
pain, resting blood pressure, cholesterol, fasting blood sugar, resting ECG,
maximum heart rate, exercise angina, oldpeak and slope. However:

- heart5 uses mixed textual categorical fields while Mendeley uses integer
  codes;
- Mendeley includes `patientid` and `noofmajorvessels`, which have no direct
  heart5 counterpart;
- codebooks and unit conventions must be verified rather than inferred;
- endpoint definitions and ascertainment are not demonstrated equivalent;
- the datasets are not independent validation evidence for this project.

They can support a **semantic mapping workshop** or a pre-registered stress
test, not a confirmatory transport claim.

### 3.2 The 70K file and the small datasets

The 70K file has `age`, `gender` and `cholesterol` fields that look partially
similar to the small datasets. This is insufficient for transfer:

- age is stored in days rather than years;
- blood pressure is represented as `ap_hi`/`ap_lo`, not a demonstrated equivalent
  to resting blood pressure;
- the target is `cardio`, with no approved equivalence to `HeartDisease` or
  Mendeley's `target`;
- the dataset has documented implausible blood-pressure records and unresolved
  licensing/source-linkage limitations;
- no patient-level identifiers or source linkage can establish independence.

It remains a separate benchmark and possible data-quality stress resource.

## 4. Does an existing method already solve the problem?

The literature audit shows that SAGE-Transfer cannot claim novelty merely from
dataset adaptation, model routing or heterogeneous-schema handling. Existing
methods already cover substantial portions of the desired capability:

| Capability | Existing prior art | Status in this environment |
|---|---|---|
| Dataset-level model/pipeline selection | AutoML, Mosaic-MCTS, TabRepo | Local classical portfolio available; no new transfer evidence |
| Unseen tabular task prediction | TabPFN, TabICL, TabDPT, APT, Mitra | Reviewed, not executable locally |
| Dataset-conditioned predictor generation | HyperFast | Reviewed, not executable locally |
| Heterogeneous feature-space transfer | CARTE, FLAT | Reviewed, not executable locally |
| Shift-aware tabular prediction | Drift-Resilient TabPFN and domain-adaptation literature | Reviewed, not executable locally |
| Reliability/calibration and abstention | Established methods, but no universal guarantee | Must be tested under the protocol |

Therefore the current evidence supports neither conclusion “SAGE-Transfer is
needed” nor “an existing method wins.” The comparison is **not identifiable**
until a compatible target dataset and executable comparator set are available.

## 5. What would make the gap measurable?

The minimum next evidence package is:

1. a provenance and licensing manifest for at least one compatible new cohort;
2. a human-approved feature/unit/codebook map;
3. a clinically reviewed endpoint definition and prevalence description;
4. an overlap assessment against the three local sources;
5. a frozen target role and target-label access policy;
6. executable, version-pinned existing comparators or an explicit reason for
   excluding each one;
7. a new namespace for predictions, metrics and provenance.

For a meaningful pilot, use at least three independent target cohorts; for a
confirmatory claim, pre-register a larger set (the protocol recommends five or
more). If only one compatible cohort can be obtained, report a one-way external
validation or feasibility study, not a general cross-dataset law.

## 6. Planned analysis after the gate passes

The first authorized run will use:

- Track A frozen zero-shot transfer;
- Track B unlabeled target adaptation;
- Track C fixed few-shot label budgets, if ethically and scientifically allowed;
- Track D target-trained local upper bounds;
- Track E one-way locked external validation when an independent cohort exists.

It will report per-cohort AUROC, PR-AUC where appropriate, Brier, log loss,
calibration slope/intercept, ECE, selective risk/coverage, mapping failures,
runtime and memory. Macro-averages will be across target cohorts, not rows.

SAGE-Transfer will only be considered a research contribution if it adds a
predeclared capability—such as safer semantic refusal, calibration under shift
or lower failure-to-map rate—against the strongest existing method under the
same information budget. A higher score on one local file is not sufficient.

## 7. Final feasibility classification

| Question | Current answer |
|---|---|
| Is a rigorous protocol available? | Yes |
| Is the local baseline frozen? | Yes |
| Can current local data support a valid cross-dataset pilot immediately? | No; mapping and endpoint gates fail |
| Can current data establish SAGE-Transfer novelty? | No; the estimand is not currently identifiable |
| Should another classifier be implemented now? | No |
| Is there a real research opportunity? | Potentially, in guarded semantic transfer and reliability, but it requires compatible cohorts and direct comparison with existing methods |

The correct next action is data/provenance acquisition and mapping review, not
accuracy optimization.
