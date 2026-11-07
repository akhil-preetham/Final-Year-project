# CARDIODIAG research architecture

## Scope

The repository contains a corrected tabular research implementation beside
preserved historical notebooks. It is designed for reproducible comparisons
on the supplied cardiovascular benchmarks. It is not a deployed diagnostic
system and does not claim clinical or external validity.

## Runtime flow

```text
dataset CSV + schema/provenance manifest
                 |
                 v
      validation and identifier removal
                 |
                 v
 outer training fold ---------------------- outer test fold
       |                                           ^
       v                                           |
 fold-local cleaning / encoding / selection       |
       |                                           |
       v                                           |
 inner model search + OOF stacking fit ------------+
       |
       v
 optional calibration / conformal calibration split
       |
       v
 saved metrics, fold predictions, provenance, reports
```

The primary nested runner keeps transformation and model selection inside the
outer training partition. Its outer test labels are used only for scoring.
The separate reliability runner reserves development, calibration, and
evaluation partitions. The split conformal module fits the estimator on the
development rows, forms its score quantile from calibration rows, and measures
coverage on evaluation rows. Its guarantee depends on exchangeability.

## Source modules

| Responsibility | Implementation |
|---|---|
| CSV loading, schema declaration, identifier removal, dataset summaries | `src/cardiodiag/data.py` |
| Training-only outlier handling, imputation, categorical encoding, scaling | `src/cardiodiag/preprocessing.py` |
| Corrected logistic, OVEC, OSEC, and optional XGBoost-meta stacking factories | `src/cardiodiag/models.py` |
| Stability-aware XAIH-DRC approximation | `src/cardiodiag/feature_selection.py` |
| Repeated outer/inner validation and fold predictions | `src/cardiodiag/nested_validation.py` |
| Discrimination, classification, calibration, and bootstrap metrics | `src/cardiodiag/evaluation.py`, `src/cardiodiag/reliability.py` |
| Split conformal prediction sets and abstention | `src/cardiodiag/uncertainty.py` |
| Dataset distribution-shift diagnostics | `experiments/run_dataset_shift.py` |
| Fail-closed external dataset manifest validation | `src/cardiodiag/external_gate.py` |
| Experiment provenance: data/code hashes, environment and hardware | `src/cardiodiag/provenance.py` |
| Adaptive research prototype | `src/cardiodiag/aura/` |
| Separate candidate discovery/selection prototype | `src/clin_adapt/` |

`experiments/` contains executable study entry points. `results/` stores
machine-readable artifacts and derived tables. `docs/AUTHORITATIVE_METRIC_REGISTRY.*`
indexes eligible evidence without pooling incompatible protocols. `paper/`
contains the editable manuscript and tables. `archive/` preserves source
notebooks and release snapshots.

## Validation boundaries

- The default internal stage includes Heart5 and Mendeley only; the 70K file
  has a different endpoint and is a separate benchmark.
- Nested validation records each outer test row index, label, probability,
  fold runtime, selected inner parameters, dataset hash, source bundle hash,
  Git state, lockfile hash, Python/packages, platform, and CPU count.
- The internal-stage runner writes to a unique UTC-named directory by default
  and refuses to overwrite existing result paths.
- Cross-dataset prediction remains disabled until an independent compatible
  cohort has a frozen endpoint, semantic feature map, license, and overlap
  assessment.
- AURA-ML and CLIN-ADAPT remain separate exploratory evidence families; neither
  is an established universally superior algorithm.

## Fidelity limits

The package does not provide a bit-for-bit implementation of the article's
LoRAS and LIME-based XAIH-DRC method. The historical runner reproduces one
notebook-like SMOTE-before-split path for forensic comparison. The corrected
stable selector is a training-fold approximation. See
`ORIGINAL_ALGORITHM_WALKTHROUGH.md`, `baseline_reproduction_report.md`, and
`PROTOCOL_AUDIT.md` for the evidence and differences.
