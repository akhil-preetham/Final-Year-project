# A--L Experiment Completion Matrix

## Audit note

The checked-in project has an experiment registry and many named protocols,
but no authoritative source file that binds letters A--L to one frozen set of
conditions, splits, seeds, and metrics. The matrix below is therefore a
reviewer-facing crosswalk of the 12 major workstreams used in the supplied
remediation brief and current project records. It is **not evidence that the
original authors prespecified these exact A--L labels**. A claim that the
original A--L factorial is complete would be rejected unless its original key
is recovered.

| Label | Condition family | Evidence / implementation | Status | Why it is not a complete factorial cell |
|---|---|---|---|---|
| A | Original paper / historical notebook baseline | `archive/`, `src/cardiodiag/historical.py`, `docs/baseline_reproduction_report.md` | Partial historical approximation | Source notebooks conflict; leakage-prone paths and settings are not a unique protocol |
| B | Faithful reconstruction | `docs/ORIGINAL_REPRODUCTION_MATRIX_20261105.md`, `docs/PAPER_TO_CODE_MAP.md` | Incomplete | LoRAS/LIME/PCA settings and article-table lineage are unavailable |
| C | Leakage-controlled baseline | `results/final_completion_20261105/`, `results/master_directive_20261105_serial/` | Completed for internal benchmarks | Not external validation; only matched internal protocol scope |
| D | Original XAIH-DRC / LIME reduction | Archived notebooks and historical analyses | Partial | No exact fold-local reconstruction of original thresholds, conflicts, and PCA rule |
| E | Stability-aware selector | `src/cardiodiag/feature_selection.py`, `docs/ABLATION_REPORT.md`, stability results | Completed as a separate candidate analysis | Stability did not show a consistent predictive/reliability advantage |
| F | OVEC candidate | `src/cardiodiag/models.py`, nested metrics registry | Completed within stated internal comparisons | Candidate results are dataset-dependent and do not support universal superiority |
| G | OSEC candidate | `src/cardiodiag/models.py`, nested metrics registry | Completed within stated internal comparisons | Current model variants do not match one exact original OSEC specification |
| H | Calibration-enabled models | Internal and CD-XD transfer artifacts | Implemented and evaluated | Source calibration transfers poorly or inconsistently to external cohorts |
| I | Uncertainty / conformal output | CD-XD-005/006, inference bundle, tests | Implemented; validity conditional | Source exchangeability assumptions do not guarantee coverage after dataset shift |
| J | Selective prediction | `results/validity_audit_20261105/selective_policy_components/` | Audited; low useful coverage | AngioCAD integrated coverage 5.6%; Duke 11.4%; unregistered-site gate 0% |
| K | AURA-ML / adaptive model selection | `docs/AURA_ML_DESIGN.md`, `docs/AURA_ML_BASELINE_AUDIT.md`, results | Research prototype completed for local benchmarks | No independent external confirmation or algorithmic novelty claim |
| L | Integrated CARDIODIAG transport workflow | CD-XD-002--006, demo and domain guard | Engineering prototype demonstrated | Weak feature-only OOD, poor calibration under shift, one aligned site, and fail-closed 0% registered-site coverage on targets |

## Matched comparisons versus missing evidence

The five-candidate internal nested study has shared folds and is a valid
matched comparison for those candidates. Other selector, calibration,
reliability, AURA-ML, and transfer studies are separate experiments with
different partitions and targets. Results from these separate runs cannot be
combined into a single full factorial. The unavailable original LoRAS/LIME
branches cannot be manufactured by substituting corrected analogues.

The implementable next comparison is a new shared-fold internal experiment
for a narrowly stated method question. It cannot establish transportability.
The confirmatory external cell remains blocked by an untouched,
endpoint-compatible dataset and verified feature definitions.
