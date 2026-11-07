# Feature-Shift Method Selection Audit

## Implemented methods and evidence

The frozen source-only studies implement two feature-support scores chosen for
small mixed-type tabular inputs: mean k-nearest-neighbor distance after
source-fit preprocessing, and Isolation Forest anomaly score. Thresholds are
source-only and were not selected from external labels. Both produce
uncalibrated anomaly scores; their AUROC/AUPRC describe domain discrimination,
not probability calibration or clinical danger.

| Method | Implemented | Source-only threshold | AngioCAD domain AUROC | Duke domain AUROC | Current conclusion |
|---|---|---|---:|---:|---|
| kNN source-support distance | Yes | Per-source calibration q95 / domain-robust maximum | 0.580 | 0.556 | Weak external domain separation |
| Isolation Forest | Yes | Source calibration q95 | 0.579 | 0.598 | Weak external domain separation |
| Mahalanobis / shrinkage covariance | No | Not evaluated | -- | -- | Not compared; mixed one-hot support, small effective feature set, and few related source domains require a prespecified LODO implementation before claiming utility |
| Local outlier factor | No | Not evaluated | -- | -- | Not compared; novelty-mode and neighborhood settings would require source-held-out stability evidence |
| MMD / kernel two-sample score | No | Not evaluated | -- | -- | Not a patient-level acceptance score without an additional calibration design; no bandwidth or group-level threshold was frozen |
| Domain classifier / density ratio | No | Not evaluated | -- | -- | Would estimate source-vs-domain membership under a study design, not guarantee reliability for an unseen cohort; no target-adaptation policy was frozen |
| Missingness / range monitor | No | Not evaluated | -- | -- | Deterministic monitor is feasible, but source range definitions and age units need source confirmation; no measured performance is claimed |

## Stability and failure boundary

The current kNN/Isolation Forest score AUROCs vary across source leave-one-
cohort-out folds: AngioCAD-study source folds span 0.537--0.756 for kNN and
0.532--0.755 for Isolation Forest; Duke-study source folds span 0.355--0.682
and 0.470--0.879, respectively. The four UCI cohorts overlap the historical
Heart5 composite and are not independent external institutions. Source alert
counts at the frozen threshold and target alert counts are independently
recalculated in
`results/validity_audit_20261105/selective_policy_components/`.

The main rejection is not simply that too few detectors were tried. The
available target features overlap with source support and the outcome
relationship may have shifted. A detector operating on unlabeled age/sex/FBS
cannot be assumed to recognize concept shift, a changed reference standard, or
clinical unreliability. The FBS unit is unverified and AngioCAD age-as-years is
provisional, limiting even the feature space that can be interpreted.

## Why more detector runs are not a repair to these target results

AngioCAD labels have already been inspected. Choosing among extra methods or
thresholds from their target performance would produce post-hoc selection, not
confirmatory evidence. The current results therefore preserve kNN and
Isolation Forest as diagnostics, mark the policy evaluation post hoc, and
leave additional method development for source-held-out data and future
confirmation on a newly acquired cohort. No method listed above as “No” should
be described as evaluated in the manuscript.
