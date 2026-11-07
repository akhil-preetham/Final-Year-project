# Dependency audit

## Declared environment

The project is configured for Python 3.11 through 3.13 in `pyproject.toml`.
Runtime dependencies cover imbalanced learning, scientific Python, explainable
AI, gradient-boosting libraries, and plotting. Development dependencies are
pytest, pytest-cov, and Ruff. `uv.lock` is present.

## Verification

- Ruff: passed for `src experiments tests demo`.
- `uv run pytest`: failed before tests started because the local `uv` trampoline
  could not canonicalize its script path after the editable package rebuild.
  This is an environment/tooling failure, not a test assertion failure.
- No dependency manifest was changed.

## Recommendations

Keep the declared dependencies unchanged. Historical notebook requirements are
not separately declared, so they should be documented rather than removed from
the modern research environment. Re-run tests with the repository virtual
environment's Python executable before considering dependency changes.

