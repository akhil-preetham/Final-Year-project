# Reproducibility instructions

## Environment

The project declares Python 3.11–3.13 dependencies in `pyproject.toml` and
pins the resolved graph in `uv.lock`. From the repository root:

```powershell
uv sync --locked
uv run python -m pytest -q
uv run ruff check .
uv run python -m compileall -q src experiments tests demo
uv lock --check
```

The current Windows checkout successfully runs the virtual-environment Python
interpreter. Earlier notes about a blocked interpreter and a 31-test suite are
historical and have been superseded by the current validation record in
`REPRODUCIBILITY_REPORT.md` and `FINAL_ACCEPTANCE_MATRIX.md`.

## Audit and smoke runs

```powershell
uv run cardiodiag audit
uv run cardiodiag smoke
uv run python experiments/run_research.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_internal_seed42.json --seeds 42
```

The smoke JSON is internal only; it is not external validation. Do not use it
as final paper evidence without repeated-seed analysis, confidence intervals,
a frozen protocol, and a provenance review.

Post-correction nested reruns use distinct output names and preserve earlier
artifacts:

```powershell
uv run python experiments/run_nested_validation.py --dataset heart5.csv --target HeartDisease --output results/generated/schema_corrected_heart5_nested_2x2.json --outer-splits 2 --inner-splits 2
uv run python experiments/run_nested_validation.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/schema_corrected_mendeley_nested_2x2.json --outer-splits 2 --inner-splits 2
```

The new synthetic LOF diagnostic and saved-target selective audit commands are
recorded in `REPRODUCIBILITY_REPORT.md`. The latter is post-hoc, does not tune,
and cannot establish confirmatory external validation.
