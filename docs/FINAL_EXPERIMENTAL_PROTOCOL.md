# Final experimental protocol

## Experiment families

| Family | Data boundary | Permitted conclusion |
|---|---|---|
| Historical reconstruction | Archived notebook ordering; leakage risks retained where part of historical recreation | Forensic comparison only |
| Corrected internal evaluation | Stratified outer/inner folds; each learned transformation is refit inside training partitions | Internal development evidence; not independent-site validation |
| UCI leave-one-cohort-out | One source cohort held out per fold | Retrospective domain stress test; source records overlap Heart5 |
| CD-XD-003/004/005 | Source model/calibration/thresholds frozen before target scoring | External stress test; only AngioCAD is endpoint-aligned, and it has already been examined |
| Calibration comparison | Maps fit on 185 source calibration rows with equal source-domain weighting | Post-hoc comparison on existing AngioCAD predictions; not confirmatory model selection |
| Controlled shift lab | Held-out Heart5 rows versus synthetic covariate transformations | Detector diagnostics only; not external clinical evidence |
| Selective components | Frozen saved target predictions and post-hoc labels | Descriptive component audit; cannot select a deployment policy |

## Locked boundaries

- No target label fits a model, calibrator or threshold.
- The current source-only calibration comparison retains one-way target labels only for evaluation and bootstrap uncertainty.
- Synthetic shifts retain source labels and explicitly preserve synthetic status.
- Historical/unsafe and corrected results remain in different evidence families.
- A study after target labels have been inspected is exploratory even when a new split is created.

## Reproducibility artifacts

Each current study records configuration/protocol, data hashes, predictions, metrics, seeds and output manifests. The authoritative indexes are AUTHORITATIVE_METRIC_REGISTRY.md, EXPERIMENT_PROVENANCE_AUDIT.md and the per-study protocol/result files.

## Limitations

Current internal folds are row-level where patient IDs are absent. External studies do not establish multiple-hospital variance. The exact original paper run is not recoverable. The synthetic shift lab does not model all natural clinical shifts or concept-shift uncertainty. No further target cohort is available for a confirmatory one-way study.
