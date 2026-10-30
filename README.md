# CARDIODIAG

CARDIODIAG is a research implementation for generalization-aware and
uncertainty-calibrated cardiovascular disease prediction under dataset shift.
It preserves the corrected StableXAIHDRC selector, leakage-safe preprocessing,
nested validation, stability, calibration, reliability, uncertainty, and
model-comparison workflows.

This repository is for reproducible research and education. It is not a
clinical diagnostic device and does not establish external validation,
clinical utility, or deployment readiness.

## Quick start

```bash
python -m venv .venv
python -m pip install -e .
python -m pytest
python -m ruff check src tests experiments
```

See [`kaggle/README.md`](kaggle/README.md) for Kaggle notebook execution and
dataset attachment instructions.

The bundled Mendeley dataset is CC BY 4.0. Its source, hash, and the status of
the optional heart5 and Kaggle 70k datasets are documented in
[`LICENSE_AND_ATTRIBUTION.md`](LICENSE_AND_ATTRIBUTION.md) and
[`data/manifests/local_datasets.json`](data/manifests/local_datasets.json).
