# CARDIODIAG experimental protocol index

The frozen experiment-family table and leakage boundaries are in [`FINAL_EXPERIMENTAL_PROTOCOL.md`](FINAL_EXPERIMENTAL_PROTOCOL.md). This index identifies the executable protocol and how to interpret its result families.

## Protocol families and allowed conclusions

| Family | Artifact / runner | Evaluation boundary | Claim ceiling |
|---|---|---|---|
| Historical reconstruction | `results/generated/heart5_protocol_comparison.json`, original notebooks/audits | Reconstructs archived ordering, including unsafe practices where they are part of history | Forensic only; not unbiased validation. |
| Corrected internal | `experiments/run_nested_validation.py`; `results/generated/post_boundary_corrected_nested_*.json` | Outer test rows excluded from fit, tuning, selection, calibration and threshold selection | Internal development evidence only. |
| Feature stability | `experiments/run_stability_evidence.py`; `results/generated/post_boundary_corrected_stability_*.json` | Fold/resample scoped selector fits | Selection stability on the named source data; not transportability. |
| Reliability/uncertainty | `experiments/run_uncertainty_evidence.py` and linkage runs | Fit/calibration/evaluation partitions separated within source | Internal behavior and assumptions only. |
| UCI cohort transfer | `experiments/run_external_transfer.py`, LODO protocols | Holds out named UCI source cohort; source rows overlap the Heart5 lineage | Retrospective source-domain stress test, not independent validation. |
| Site transfer | CD-XD-003/004/005 runners and protocol files | Source fit/calibration frozen before target scoring; target was later revisited | Exploratory transfer stress test; cannot serve as confirmatory evidence. |
| Synthetic covariate perturbations | `results/generated/dataset_shift.json` and shift scripts | Perturbation labels are synthetic; not a clinical target population | Detector diagnostic only. |
| Final table regeneration | `experiments/rebuild_final_manuscript_tables.py` and generator-specific inputs | Table values generated from frozen artifacts; hashes in `paper/tables/final_numeric_table_manifest.json` | Presentation/provenance only; does not alter evidence class. |

## Required controls for new work

1. Freeze the dataset identity/version/hash, endpoint, feature map, exclusion rules, and data license before execution.
2. Split by patient where identifiers permit; otherwise label the row-level independence limitation.
3. Put every learned transformation, resampling method, feature selector, hyperparameter search, calibration fit, threshold and policy choice strictly inside development/inner folds.
4. Keep a final external cohort untouched until the model and analysis plan are frozen. Do not tune on already inspected AngioCAD, ZAS or Duke labels and call a replay confirmatory.
5. Record experiment ID, date, source commit/dirty state, environment, seeds, model configuration, input hashes, split indices, predictions, metrics, confidence intervals and output hashes.
6. Report discrimination, calibration, class-specific outcomes, uncertainty, OOD detection and risk/coverage separately. Do not infer reliable predictions from cohort discrimination or an OOD score alone.

The current 3x3 internal nested studies use seed 42 and are descriptive due limited cohort diversity. Exact run records are indexed in `AUTHORITATIVE_METRIC_REGISTRY.md` and `EXPERIMENT_PROVENANCE_AUDIT.md`. A confirmatory external protocol cannot be run until new untouched data and required permissions exist.
