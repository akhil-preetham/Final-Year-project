# CARDIODIAG reproducibility report

**Audit date:** 2026-11-06  
**Git branch:** `codex/research-completion-2026-11-06`  
**Base commit:** `e63b02c8a2aba6344a48025f657696fd99ac3a5f`.

## Baseline and changes in this iteration

Before this iteration's code change, the baseline full test suite passed **122 tests**, with three OpenPyXL warnings on AngioCAD workbook reading. The source tree was already largely untracked relative to the upstream Git baseline; the new branch preserves the commit anchor but does not itself add those existing files to version control.

This iteration adds a source-only LOF novelty diagnostic to `experiments/controlled_shift_lab.py`, two tests for its score direction/input checks, a saved-target risk–coverage audit runner, and three helper tests for Wilson intervals, risk curves, and accepted/rejected partitions. Final LOF results are under `results/controlled_shift_lab_20261106_run5/`; target risk–coverage artifacts are under `results/selective_audit_20261106_run3/`.

## Reproduction commands

From repository root, with Python 3.11 and `uv` available:

```powershell
uv sync --locked
uv run python -m pytest -q
uv run ruff check .
uv run python -m compileall -q src experiments tests demo
uv lock --check
uv run python experiments/controlled_shift_lab.py --output-dir results/controlled_shift_lab_20261106_rerun1
uv run python experiments/audit_target_risk_coverage_descriptive.py --output-dir results/selective_audit_20261106_rerun1
```

Both audit runners write to versioned output directories with `exist_ok=False`; they preserve prior attempts rather than overwrite. All target-label-derived selective metrics are descriptive; the risk curve runner does not fit or tune.

## Verification status

The original 122-test baseline passed before modifications. Targeted tests for new functionality passed: 2 LOF tests and 3 selective-audit helper tests. The two experiment runners completed successfully and wrote JSON/CSV artifacts; the selective audit also generated a PNG. Exact repeat runs (run4→run5 for LOF and run2→run3 for selective analysis) reproduced all metric, curve and policy-summary CSV rows. The final suite passed **127 tests** in both the existing environment and a fresh `uv sync --locked` environment, with three known OpenPyXL workbook-reader warnings. Ruff, compilation and `uv lock --check` passed in the clean environment.

The previous manuscript and table artifacts retain their original hashes and were not rebuilt from these diagnostic-only additions. No existing experiment directory was overwritten. The model bundle and demonstration code were not changed. The full existing dataset/manuscript reproducibility claims are indexed in `EXPERIMENTAL_PROTOCOL.md`, `REPRODUCIBILITY_GUIDE.md`, `EXPERIMENT_PROVENANCE_AUDIT.md`, and `paper/tables/final_numeric_table_manifest.json`.

## Environment and reproducible limitations

The lock resolves 54 packages. `uv sync --locked` successfully created a clean isolated environment and installed the local project. The first attempt explicitly included `--no-install-project` and failed test collection because the package was absent; the corrected command installed the project and passed the full suite. Three known OpenPyXL warnings concern ignored conditional-formatting extensions while reading workbook inputs; the workbooks are not saved back. A `pip-licenses` inventory found license metadata for all 45 third-party installed packages; the local project is `UNKNOWN`, confirming no software license is declared. Full row-level data, model bundles, output archives and local environments are excluded from any public allow-list pending the release audit.

**Reproducibility gate:** clean locked installation, code/artifact checks, and tests are reproducible locally. Public clean-room reproducibility remains blocked until the intended source tree is tracked, a data-free package is rights-cleared, and a clean installation can be repeated from that reviewed package.
