# CARDIODIAG selective-prediction report

**Updated:** 2026-11-06  
**Decision:** useful validated selective operation is not established.

## Why integrated coverage is low

The saved registered rule accepts a row only if its conformal prediction set is a singleton **and** the source-calibrated kNN support rule raises no alert. In the post-hoc component audit, AngioCAD conformal-singleton coverage is 33/377 = **8.75%**; requiring the kNN rule reduces this to 21/377 = **5.57%**. Thus conformal set ambiguity is the larger bottleneck and the additional kNN gate removes 12 of the 33 singleton rows. KNN alone accepts 93.37% and Isolation Forest alone accepts 99.73%, but their accepted error rates are 26.42% and 25.53%; their high coverage does not make them useful risk controls.

For Duke ACATH, conformal alone accepts 487/3,504 = **13.90%**; the registered conformal-plus-kNN rule accepts 401/3,504 = **11.44%**. Its target endpoint is ≥75% stenosis, unlike the >50% source task, so this is only a stress test.

## Saved-target policy comparison

The new descriptive runner uses frozen predictions and flags only: `experiments/audit_target_risk_coverage_descriptive.py`. It performs no model fitting, recalibration, threshold selection, or policy selection. The final rerun is under `results/selective_audit_20261106_run3/`; it exactly reproduces all curve and policy-summary rows from the initial run2 output:

- `risk_coverage_descriptive.png` and `risk_coverage_curves.csv` show confidence-ranked risk–coverage curves plus fixed conformal and registered-policy points.
- `accepted_rejected_policy_summary.csv` compares accepted and rejected class/error counts and includes conditional Wilson 95% intervals for coverage and error rates.
- `risk_coverage_audit.json` records hashes, source files and limitations.

| Cohort / fixed policy | Accepted / total | Coverage (Wilson 95% CI) | Accepted errors / accepted | Accepted risk (Wilson 95% CI) | Rejected errors / rejected | Rejected risk (Wilson 95% CI) |
|---|---:|---:|---:|---:|---:|---:|
| AngioCAD, conformal singleton | 33/377 | 8.75% (6.30–12.04%) | 0/33 | 0% (0–10.43%) | 96/344 | 27.91% (23.43–32.87%) |
| AngioCAD, conformal + kNN | 21/377 | 5.57% (3.67–8.37%) | 0/21 | 0% (0–15.46%) | 96/356 | 26.97% (22.62–31.80%) |
| Duke, conformal singleton | 487/3,504 | 13.90% (12.79–15.08%) | 61/487 | 12.53% (9.88–15.76%) | 1,297/3,017 | 42.99% (41.23–44.76%) |
| Duke, conformal + kNN | 401/3,504 | 11.44% (10.43–12.54%) | 41/401 | 10.22% (7.63–13.58%) | 1,317/3,103 | 42.44% (40.71–44.19%) |

The AngioCAD accepted cases are 21/21 positive under the registered combination; its observed zero errors therefore does not establish balanced performance, and the upper conditional risk interval is wide. The rejected-case errors are reported to show what abstention excludes. Confidence-ranked error risk is about 2.6% at 20% coverage and 20.2% at 80% coverage on AngioCAD; on Duke it is 15.8% at 20% and 36.1% at 80%. These are descriptive curves on previously examined labels, not prospective operating characteristics.

The historical component audit and this report use fixed probability cutoff 0.5 for point predictions. Calibrators were source-fit, but conformal and OOD flags are distinct evidence channels. The unknown-domain registry gate correctly abstains on unregistered target sites, giving 0% target coverage; it is metadata-based fail-closed behavior, not learned selective success.

## Calibration and alternatives

Source-only Platt calibration, isotonic comparison, split conformal prediction, and confidence-ranked uncertainty are already implemented and evaluated internally. No target cohort was used to tune a new probability calibrator or threshold in this iteration. Conformal coverage depends on exchangeability and is not guaranteed under arbitrary dataset shift. ECE depends on binning; calibration does not by itself validate ranking, external transport, or a risk cutoff. No new threshold method is promoted.

## Prospective research acceptance criteria

No minimum useful coverage or maximum risk was preregistered before the current target labels were examined. To make the next confirmatory engineering study falsifiable, the project proposes a **provisional, non-clinical research gate**: at least **80% coverage** and an upper conditional 95% confidence bound for selective error risk no greater than **10%**, assessed on a newly acquired untouched endpoint-compatible cohort. These numbers are project screening criteria only, not clinical standards or safety claims; the project team must ratify them and freeze the policy before target labels are opened. Report overall and class-specific sensitivity/specificity, accepted/rejected counts, coverage and risk intervals, and calibration. A cohort with too few examples to bound risk fails the evidence gate regardless of point estimate.

The existing 5.57% AngioCAD and 11.44% Duke operating points fail the proposed coverage gate; Duke also fails the proposed risk-bound gate. Since both were examined and Duke is endpoint-mismatched, these failures are descriptive and do not constitute a confirmatory hypothesis test.

**Selective prediction: NO-GO.** Conformal, calibration, and abstention components are technically implemented and tested; useful externally validated risk–coverage has not been shown.
