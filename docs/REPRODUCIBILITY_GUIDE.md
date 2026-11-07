# CARDIODIAG reproducibility guide

## Environment

The project targets Python 3.11--3.13 and uses `pyproject.toml` plus the
committed `uv.lock`.

```text
uv venv --python 3.11 .venv
uv sync
```

On Windows, the repository-local executable can be invoked directly. In this
checkout, `uv run pytest` itself fails to canonicalize its generated script
path, so invoke pytest as a Python module:

```text
./.venv/Scripts/python.exe --version
uv run python -m pytest -q
./.venv/Scripts/ruff.exe check src tests experiments
```

## Data preparation

Keep raw datasets in their documented paths and do not alter them. Verify the
three local hashes using `data/manifests/local_datasets.json`. The external
template is intentionally `NOT_FROZEN` and must not be used for evaluation.

## Quick checks

```text
uv run python -m pytest -q
./.venv/Scripts/ruff.exe check src tests experiments
./.venv/Scripts/python.exe -m compileall -q src experiments demo tests
./.venv/Scripts/python.exe demo/run_demo.py
uv lock --check
```

Launch the interactive local research demonstration (synthetic inputs only):

```powershell
uv run python demo/app.py
```

Its default frozen bundle, no-network/no-input-persistence behavior, supported
schema, abstention policy and limitations are documented in
`APPLICATION_GUIDE.md`. Metrics are read from named saved CSV/JSON artifacts;
the app does not generate or tune evaluation results.

## Main experiments

```text
./.venv/Scripts/python.exe experiments/run_internal_stage.py
./.venv/Scripts/python.exe experiments/run_nested_validation.py --help
./.venv/Scripts/python.exe experiments/run_model_benchmark.py --help
./.venv/Scripts/python.exe experiments/run_stability_evidence.py --help
./.venv/Scripts/python.exe experiments/run_uncertainty_evidence.py --help
./.venv/Scripts/python.exe experiments/run_stability_reliability_linkage.py --help
```

The source-distinct CD-XD-003 transfer stress test can be reproduced with the
frozen UCI archives and protocol:

```powershell
.\.venv\Scripts\python.exe experiments\run_external_transfer.py
.\.venv\Scripts\python.exe experiments\analyze_external_transfer.py
.\.venv\Scripts\python.exe experiments\plot_external_transfer.py
```

The runner checks the source, target, workbook, and protocol hashes before
fitting. The study is not endpoint-identical external validation because the
target threshold is `>=50%` stenosis and the source threshold is `>50%`.

The endpoint-aligned AngioCAD study is `CD-XD-004`. Reproduce the primary
source-only fit, paired calibration analysis, figure, and byte-identical repeat
with:

```powershell
.\.venv\Scripts\python.exe experiments\run_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\analyze_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\plot_angiocad_transfer.py
.\.venv\Scripts\python.exe experiments\run_angiocad_transfer.py --output-dir results\transfer_20261105_angiocad_external_reproduction
```

The protocol, dataset manifest, result report, predictions, and independent
reproducibility audit are in `docs/TRANSFER_STUDY_PROTOCOL_20261105_ANGIOCAD.md`,
`data/manifests/angiocad_external.json`,
`docs/TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`, and
`results/transfer_20261105_angiocad_external/`. This study uses 377 matched
AngioCAD records; 36 of 413 label IDs have no feature row in the public files.

The default internal-stage run writes to a new UTC-named directory under
`results/`. It refuses to overwrite an existing result or manifest. For
repeatable artifact locations, provide a new, empty `--output-dir` each time;
do not reuse historical paths. Each completed outer fold records test-row
indices, true labels, predicted probabilities, selected inner parameters, and
runtime. Result provenance records dataset and lockfile hashes, source-bundle
hash, Git head/dirty state, software versions, platform, and CPU information.

The default internal stage can be expensive and is not required to reproduce
the already saved artifacts. The fresh 3x3 seed-42 stage in
`results/master_directive_20261105_serial/` includes saved outer predictions
and split indices and matches the prior authoritative fold means exactly. Use
the exact dataset, target, seed, fold counts, and output paths documented in
the registry before comparing results.

## Registry and publication tables

```text
./.venv/Scripts/python.exe experiments/build_authoritative_registry.py
./.venv/Scripts/python.exe experiments/summarize_nested.py --input results/generated/post_boundary_corrected_nested_heart5.json results/generated/post_boundary_corrected_nested_mendeley.json --csv results/tables/nested_summary.csv --markdown results/tables/nested_summary.md
./.venv/Scripts/python.exe experiments/generate_paper_assets.py --input results/tables/nested_summary.csv --output paper/tables/nested_summary.tex
```

The source-of-truth registry is `docs/AUTHORITATIVE_METRIC_REGISTRY.json`.
Generated summaries are under `results/tables/`; editable manuscript sources
are under `paper/`.

## External validation gate

Only after a human reviewer freezes a genuinely independent compatible dataset:

```text
./.venv/Scripts/python.exe experiments/check_external_manifest.py data/manifests/external_dataset.json
./.venv/Scripts/python.exe experiments/run_external_evaluation.py --help
```

The evaluator must never fit, calibrate, tune, select a threshold, or select a
model using external rows or labels.

## Manuscript build

From the `paper/` directory, compile with Tectonic into a temporary directory,
render every page with Poppler, inspect a contact sheet and selected full pages,
then place the reviewed PDF under the repository's `output/pdf/` folder:

```powershell
$buildName = "domain_shift_20261105_rerun"
New-Item -ItemType Directory -Force "tmp/pdfs/$buildName" | Out-Null
tectonic -k --keep-logs -o "tmp/pdfs/$buildName" manuscript.tex
New-Item -ItemType Directory -Force ..\output\pdf | Out-Null
Copy-Item "tmp/pdfs/$buildName/manuscript.pdf" "../output/pdf/$buildName.pdf"
```

The current manuscript PDF is
`output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`; its source-hash record is
under `paper/build/research_draft_20261105_remediation/`. Nine generated figures and
their input/output hashes are in
`paper/figures/master_directive_20261105_final/`. Render every page and inspect
the contact sheet and full pages after any manuscript changes. The current
PDF was visually checked; Tectonic reported font fallback and underfull boxes.
Do not call the manuscript submission-ready until author, affiliation,
ethics/data-use, funding, contribution, and target-journal requirements are
supplied and checked.
