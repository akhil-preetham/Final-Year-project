# Reproducibility instructions

## Environment

The project declares Python 3.11–3.13 dependencies in `pyproject.toml` and
pins the resolved dependency graph in `uv.lock`.

Preferred setup:

```text
uv venv --python 3.11 .venv
uv sync
```

On the current host, the shell's first `uv` entry is a permission-blocked
package-manager wrapper, and Windows Application Control also blocks execution
of newly created virtual-environment `python.exe` files. The validated
workaround is to call the accessible uv executable explicitly and run the same
project dependencies through an ephemeral environment:

```text
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pytest --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python -m pytest -q
```

This is an environment restriction, not a project test failure. The equivalent
command passed all current tests (31 tests at the current audit).

## Checks

```text
uv run ruff check .
uv run python -m pytest -q
```

The first command passes in this workspace. The second command cannot spawn the
workspace virtual-environment interpreter because of the host policy; the
ephemeral-environment equivalent passes all current tests.

## Audit and smoke runs

```text
cardiodiag audit
cardiodiag smoke
python experiments/run_research.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_internal_seed42.json --seeds 42
```

The generated JSON is an internal smoke result only. It is not an external
validation result and must not be copied into a manuscript as final evidence
without repeated-seed analysis, confidence intervals, a frozen protocol, and a
provenance review.

Post-correction bounded nested reruns use separate artifact names and do not
overwrite earlier results:

```text
uv run python experiments/run_nested_validation.py --dataset heart5.csv --target HeartDisease --output results/generated/schema_corrected_heart5_nested_2x2.json --outer-splits 2 --inner-splits 2
uv run python experiments/run_nested_validation.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/schema_corrected_mendeley_nested_2x2.json --outer-splits 2 --inner-splits 2
```

The associated stability, uncertainty, linkage, and generated-table artifacts
are summarized in `docs/schema_corrected_evidence.md`.
