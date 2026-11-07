# CD-XD-006: endpoint-aligned AngioCAD replay with fail-closed domain guard

## Purpose and status

This run integrates source-domain robust conformal uncertainty and the runtime
domain registry with the existing source-distinct AngioCAD transfer study.
AngioCAD was already examined in CD-XD-004, so CD-XD-006 is a reproducible
post-hoc policy evaluation, not a pristine final holdout or a new independent
validation claim. The endpoint is the closest available match: source UCI
`num > 0` and AngioCAD any artery stenosis bin above 50%. The AngioCAD 26-50%
negative bin does not identify exact-50% cases.

## Frozen cohort and predictors

Train on the four UCI Heart Disease cohorts (Cleveland, Hungary, Switzerland,
and VA Long Beach); evaluate on the 377 AngioCAD patients with both feature and
label records. Use age, sex, and fasting blood sugar >120 mg/dL only. Source
sex is mapped to male/female strings; AngioCAD FBS is thresholded at 120 using
the workbook's numeric values, with mg/dL retained as an explicit assumption.
All imputation and scaling are fit on source training rows.

## Source-only fit and calibration

Within each source cohort, use stratified seeded partitions: 70% model fit,
15% Platt probability calibration, and 15% conformal/OOD threshold
calibration. The latter two partitions are disjoint. Logistic regression is
domain weighted so each source cohort contributes equal total fit weight.
Platt calibration uses equal total calibration weight per source cohort. No
AngioCAD labels are used for fitting, calibration, or thresholds.

## Prediction reliability and operating boundary

For each source domain, compute a finite-sample 90% split-conformal quantile
from calibrated `1-p(y)` scores on the separate conformal partition. Compute
the source-domain 95% OOD thresholds from mean distance to the 10 nearest
source-fit examples. The inference bundle returns a classification only when
the caller provides a registered source-domain identifier, the class set is
singleton, and the feature-support score is within that domain's threshold.
For a new or missing domain, it abstains without exposing a probability. The
domain identifier must come from trusted provenance metadata. This is a
fail-closed operating rule; it does not establish clinical validity.

## Evaluation

Report raw and Platt-calibrated discrimination, calibration, confidence-ranked
risk/coverage, conformal set coverage and singleton coverage, OOD AUROC and
alert rates, and operational domain-gate coverage. Repeat source leave-one-
cohort-out validation with the same partitions to characterize source-domain
variability. Target labels are used for scoring only. Since this target has
been examined before, all target performance remains exploratory.

## Reproduction

```powershell
uv sync --locked
uv run python experiments/run_aligned_angiocad_gate.py
uv run python demo/run_domain_guard_demo.py --bundle results/transfer_20261105_angiocad_domain_guard/model_bundle.joblib
```

