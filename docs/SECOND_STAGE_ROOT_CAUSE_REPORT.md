# Second-stage root-cause report

**Assessment date:** 2026-11-06. This report verifies the previously reported findings against current outputs and records the new source-only calibration comparison.

| No-go cause | Verified current finding | Root cause assessment | What can resolve it |
|---|---|---|---|
| External calibration | CD-XD-004 raw Brier/ECE 0.1898/0.2108; source Platt 0.1851/0.2160. The new source-only temperature candidate gives 0.1605/0.1473 on this already examined site. | Case mix/prevalence and predictor/endpoint differences are confounded with calibration error. Source calibration contains 185 rows; external prevalence is 79%. The target has already been examined, so its apparent temperature improvement is exploratory. | Freeze the source-temperature map before evaluation at another independent endpoint-compatible site. Do not select on current AngioCAD. |
| Weak OOD detector | AngioCAD IF source-vs-target AUROC 0.589; KNN diagnostic AUROC about 0.580. | The detector scores cohort membership in a low-dimensional age/sex/FBS representation. This is not individual anomaly detection, error detection, or concept-shift detection. | Broader source-only detector study and controlled synthetic shifts can diagnose behavior; only new labelled independent sites can establish external utility. |
| Low selective coverage | AngioCAD conformal-singleton 8.8%; KNN-only support accepts 93.4%; combined policy 5.6% (21/377), all accepted records positive. | The conjunction of singleton conformal set and KNN support rule causes the drop; the metadata gate is a separate rule that rejects every unregistered site. The component audit shows conformal filtering is the larger coverage reduction. | Thresholds may be explored on source-only held-out domains, but useful external risk-coverage needs a new untouched cohort. Do not relax thresholds based on current target labels. |
| Generalization | One endpoint-aligned AngioCAD site has AUC 0.787; calibration and shift detection are weak. Z-Alizadeh Sani and Duke have endpoint mismatches. | One site cannot identify between-site variance; endpoint/units and person-level linkage are incomplete. | Obtain a second untouched compatible site with signed data access, codebook, units, event counts and overlap audit. |
| Original algorithm fidelity | Historical notebook variants conflict on resampling order, splits, models, LIME/PCA and calibration. | The source archive does not uniquely identify article-table lineage or exact LoRAS environment/parameters. | Only original authors' run manifests, environment and exact supplement can close this evidence gap. |

## Disambiguation of four shift concepts

- **Dataset discrimination:** distinguish AngioCAD from source records. Existing AUROC answers only this.
- **Individual anomaly:** flag unusual feature vectors; source/target AUROC does not prove this.
- **Prediction-error detection:** associate a score with whether a prediction is wrong; requires labelled evaluation and is not established by domain discrimination.
- **Concept shift:** changes in predictor-outcome relation; cannot be diagnosed from unlabeled covariates alone.

**Conclusion:** The source-only temperature result is a promising hypothesis, not a NO-GO resolution. Reliable unseen-site operation remains NO-GO. The exact cohort, metadata and historic-source gaps are blocked by external evidence rather than fixable code.
