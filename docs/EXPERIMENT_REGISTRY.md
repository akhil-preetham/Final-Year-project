# Experiment registry

The machine-readable registry is generated from stored artifacts by:

```text
./.venv/Scripts/python.exe experiments/build_authoritative_registry.py
```

Canonical files:

- `docs/AUTHORITATIVE_METRIC_REGISTRY.json`
- `docs/AUTHORITATIVE_METRIC_REGISTRY.md`

## Protocol separation

| Family | Role | Can support the primary claim? |
|---|---|---|
| `post_boundary_corrected_*` | Corrected internal CARDIODIAG evidence | Yes, with internal-only scope |
| `schema_corrected_*` | Bounded sensitivity evidence after schema correction | Sensitivity only; do not pool silently |
| `kaggle70k_*` | Separate target/schema model benchmark | No external-validation claim |
| `*_protocol_comparison.json` | Historical approximation | Historical only |
| `*_smoke_*` and stress artifacts | Engineering or perturbation checks | Exploratory only |

Every registry entry records dataset identity/hash, method, preprocessing,
validation protocol, folds/repeats/seeds, selection metric, aggregation rule,
source artifact, source script, and an explicit status. The registry generator
fails if an allow-listed artifact is missing, invalid JSON, contains non-finite
numbers, has a mismatched local dataset hash, or references a missing source
script.

No registry entry is evidence of clinical utility, fairness, safety, or
deployment readiness.
