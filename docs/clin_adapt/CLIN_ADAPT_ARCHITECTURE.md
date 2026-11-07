# CLIN-ADAPT architecture

**Version:** `clin-adapt-v0.1-provisional`  
**Scope:** structured clinical/tabular classification  
**Status:** implemented research infrastructure; CASL is provisional and not a
proven novel algorithm

## Boundary with CARDIODIAG

CLIN-ADAPT is a separate package under `src/clin_adapt/` with results under
`results/clin_adapt/`. Existing CARDIODIAG, AURA-ML code, frozen metrics and
cross-dataset feasibility artifacts were not overwritten. CLIN-ADAPT consumes
the frozen local baseline as a comparison reference only.

## Components

```text
clinical dataframe
    |
    +-- explicit schema and identifier handling
    +-- training-partition dataset profile
    +-- candidate registry and availability resolution
    +-- candidate-specific training-only preprocessing
    +-- parallel inner validation with failure isolation/checkpointing
    +-- provisional CASL coordination policy
    +-- optional validation-only calibration
    +-- outer-fold evaluation and serialized provenance
```

### Package modules

| Module | Responsibility |
|---|---|
| `registry.py` | Model metadata, optional dependency detection and deterministic factories |
| `profiling.py` | Leakage-safe clinical tabular meta-features |
| `preprocessing.py` | Explicit mixed-type, training-only pipelines |
| `parallel_engine.py` | Worker-limited execution, retries, failure records and checkpoints |
| `adaptive_learning.py` | Validation-only candidate rejection and coordination |
| `calibration.py` | Inner-prediction sigmoid/isotonic selection |
| `nested.py` | Inner candidate discovery and outer evaluation |
| `evaluation.py` | Classification and probability metrics |
| `cli.py` | Registry and profile commands |

## Information-flow rule

Every outer test partition is isolated from profile construction, preprocessing,
candidate selection, fusion, calibration and threshold decisions. Dataset-level
cross-dataset transfer remains disabled because the existing CARDIODIAG data do
not pass the approved semantic endpoint/map gates.

## Future modalities

The registry's modality field allows future EHR time-series, ECG, imaging and
text adapters, but no such adapter exists in v0.1. A tabular candidate is never
represented as support for those modalities.
