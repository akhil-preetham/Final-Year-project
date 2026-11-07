# Statistical Consistency and Frozen-Result Recalculation

**Date:** 2026-11-05  
**Scope:** saved CD-XD-005/006 target predictions, OOD scores, post-hoc
AngioCAD feature ablation, and source-alert reconciliation.

## Independent recalculation

`experiments/audit_selective_policy_components.py` reads frozen source and
target prediction CSVs with pandas round-trip float parsing and recalculates
the source-versus-target detector AUROC and strict threshold counts. It raises
if recalculated counts or AUROC disagree with the frozen study metrics. The
result and source/output hashes are in
`results/validity_audit_20261105/selective_policy_components/`.

The initial apparent one-unit-in-the-last-place threshold mismatch was caused
by pandas' default fast CSV parser. Round-trip parsing reproduces the saved
false-alert counts and AUROCs exactly. No detector tie or threshold change was
found. The detector score is an anomaly score, not a calibrated probability;
the reported AUPRC baseline depends on the source/target row ratio.

| Cohort | Detector | AUROC | Target alert rate at frozen threshold | Source false alerts |
|---|---|---:|---:|---:|
| AngioCAD, n=377 | kNN support | 0.580 | 25/377 (6.6%) | 0/140 |
| AngioCAD, n=377 | Isolation Forest | 0.579 | 1/377 (0.3%) | 0/140 |
| Duke ACATH, n=3,504 | kNN support | 0.556 | 155/3,504 (4.4%) | 1/140 |
| Duke ACATH, n=3,504 | Isolation Forest | 0.598 | 95/3,504 (2.7%) | 0/140 |

Source leave-one-domain-out AUROCs vary materially. AngioCAD-study source
folds range 0.537--0.756 for kNN and 0.532--0.755 for Isolation Forest; Duke
source folds range 0.355--0.682 for kNN and 0.470--0.879 for Isolation
Forest. These four UCI source cohorts overlap the historical Heart5 composite
and do not act as independent hospitals for this project.

## Selective-policy recalculation

Every policy row is calculated from frozen target probabilities, conformal
sets, detector flags, and domain actions. Target labels are used for
evaluation only. AngioCAD had already been examined, so all rows are
post-hoc. Duke has a different >=75% endpoint and is only a transport stress
test.

| Cohort | Policy | Coverage | Accepted errors |
|---|---|---:|---:|
| AngioCAD | Fixed 0.5 probability, no abstention | 100.0% | 96/377 (25.5%) |
| AngioCAD | Conformal singleton only | 8.8% | 0/33; all accepted rows are positive |
| AngioCAD | kNN alert only | 93.4% | 93/352 (26.4%) |
| AngioCAD | Isolation Forest alert only | 99.7% | 96/376 (25.5%) |
| AngioCAD | Registered conformal + kNN combination | 5.6% | 0/21; all accepted rows are positive |
| AngioCAD | Unknown-domain registry gate | 0.0% | No target score emitted |
| Duke | Fixed 0.5 probability, no abstention | 100.0% | 1,358/3,504 (38.8%) |
| Duke | Conformal singleton only | 13.9% | 61/487 (12.5%) |
| Duke | kNN alert only | 95.6% | 1,305/3,349 (39.0%) |
| Duke | Isolation Forest alert only | 97.3% | 1,330/3,409 (39.0%) |
| Duke | Registered conformal + kNN combination | 11.4% | 41/401 (10.2%) |
| Duke | Unknown-domain registry gate | 0.0% | No target score emitted |

Zero observed errors among 21 AngioCAD positives is not a useful risk estimate;
the selected subset contains no negative class and covers only 5.6%. The
unknown-site gate is an operational fail-closed policy, not successful
predictive validation.

## Feature ablation consistency

The seven post-hoc age/sex/FBS subsets use frozen UCI source fit and calibration
partitions. Target labels are withheld from every fitting/calibration
function and scored after all prediction vectors are generated. Intervals are
class-stratified bootstrap intervals conditional on this previously examined
AngioCAD cohort and have no multiplicity correction.

| Features | Source-Platt AUC (95% conditional CI) | Brier | 10-bin ECE | Unit status |
|---|---:|---:|---:|---|
| Age | 0.639 (0.579--0.702) | 0.190 | 0.174 | Unit-safe fields |
| Sex | 0.690 (0.628--0.747) | 0.194 | 0.211 | Unit-safe fields |
| Age + sex | 0.788 (0.734--0.842) | 0.176 | 0.196 | FBS excluded; age-as-years still assumed |
| FBS | 0.354 (0.306--0.401) | 0.205 | 0.195 | mg/dL assumption only |
| Age + FBS | 0.632 (0.570--0.694) | 0.199 | 0.192 | mg/dL assumption only |
| Sex + FBS | 0.771 (0.717--0.823) | 0.202 | 0.233 | mg/dL assumption only |
| Age + sex + FBS | 0.787 (0.733--0.840) | 0.185 | 0.216 | mg/dL assumption only |

Age+sex and age+sex+FBS have nearly identical target ranking in this
post-hoc cohort. This does not validate the FBS unit and is not fresh
confirmation. The locked historical CD-XD-004 model and results are preserved;
the FBS-excluded subset is not fully unit-verified and is not relabeled as the
original primary protocol. AngioCAD's numeric age unit also remains
undocumented in the workbook; the years mapping is provisional.

## Statistical limitations

- Predictive bootstrap intervals condition on observed target class counts and
  do not quantify between-site variation.
- AngioCAD results are one-site and post-hoc; multiple comparison claims are
  unadjusted.
- Duke's endpoint threshold differs from source, so performance changes
  confound population, measurement, endpoint, and time.
- Four UCI domains are few and related to historical Heart5 rows; their LODO
  folds are stress checks, not independent external sites.
- No target-derived metric can restore a pristine holdout after outcomes have
  already been inspected.
