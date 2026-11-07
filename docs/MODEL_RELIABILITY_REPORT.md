# CARDIODIAG model reliability report

**Evidence status:** source-internal reliability is characterized on limited public benchmark datasets; reliable transfer to unseen sites is not established.

## Internal discrimination and calibration

The seed-42 3-outer by 3-inner corrected nested study reports Heart5 OVEC mean ROC-AUC **0.9295** (SD 0.00735) and OSEC **0.9259** (SD 0.01097); Mendeley OVEC is **0.9957** (SD 0.00127) and OSEC **0.9943** (SD 0.00370). These values are in `results/tables/nested_summary.csv` and the two named JSON artifacts in `results/generated/`. They are internal descriptive estimates, not external performance. Mendeley/Heart5 overlap and target/feature-timing limitations materially constrain interpretation. Brier/ECE are in the same table; high ranking does not imply calibrated probabilities.

## Calibration and uncertainty

Source-only calibrators and internal uncertainty methods are saved in the reliability experiment artifacts listed in `AUTHORITATIVE_METRIC_REGISTRY.md`. External calibration is reported separately. The AngioCAD primary source-calibrated ECE is reported as 0.216 in `VALIDITY_AUDIT_20261105.md`; the study is post hoc and one site. Conformal outputs report empirical target coverage, set size and selective risk, but standard exchangeability-based coverage is not a promise under arbitrary dataset shift. No target label is used to fit the frozen source calibrator or policy in the documented study; post-hoc target summaries remain exploratory because labels were already examined.

## Shift detection and selective behavior

- AngioCAD feature-only Isolation Forest source-vs-target AUROC: **0.589** (conditional bootstrap 95% interval 0.541–0.635 in the validity audit). Age/sex-only sensitivity: 0.544 (0.496–0.592). These are weak distribution classifiers and do not establish detection of unreliable individual predictions.
- The later, post-hoc CD-XD-006 domain-robust diagnostics are different scores on the already examined AngioCAD cohort: Isolation Forest AUROC **0.5787** and kNN-distance AUROC **0.5801** (kNN conditional 95% interval 0.5269–0.6345). These do not replace the primary CD-XD-004 result of 0.589; they use a different source-domain-robust scoring/threshold protocol. The 0.544 age/sex-only sensitivity is also a separate post-hoc run.
- The often-repeated **0.604** OOD AUROC is from CD-XD-003 on the Z-Alizadeh Sani cohort, not AngioCAD. It has a different cohort and endpoint (>=50% vs source >50%). Thus 0.604, 0.589, 0.5787, 0.5801 and 0.544 are not interchangeable estimates of the same run.
- AngioCAD combined selective coverage: **5.6%** (21/377 accepted in the audited run); the accepted set had only one outcome class, so zero observed errors is not evidence of useful balanced performance.
- Duke combined selective coverage: **11.4%** (401/3,504 accepted) and 41 accepted errors; endpoint threshold is >=75% vs source >50%, so it is an endpoint-mismatched stress test.
- The trusted-domain registry gate abstains on all rows from unregistered AngioCAD/Duke sites (0% coverage). This is metadata-based fail-closed logic, not learned OOD detection.

## Reliability verdict

**Reliability GO: not met.** Current artifacts support an honest negative/limited reliability result: source calibration, OOD signals and abstention do not demonstrate useful unseen-site prediction. Keep uncertainty scores, conformal sets, feature support and registry decisions distinct; none independently establishes clinical safety or correctness. New untouched compatible sites are needed for a confirmatory assessment.
