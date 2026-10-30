# CARDIODIAG final repository and evidence audit

**Audit date:** 2026-10-27  
**Scope:** current working tree, source package, experiment runners, tests,
checked-in data, generated artifacts, archived notebooks, and manuscript files.

## Executive finding

The checkout contains a substantial, separately added research package around
the original notebook archive. The package is runnable through the accessible
explicit `uv.exe` executable and currently passes its lock check, Ruff check,
27-test suite, dataset-hash check, and demonstration smoke run. The standard
`python` launcher is unavailable on this host, and the shell-resolved `uv`
wrapper is permission-blocked; the validated commands therefore use
`C:/Users/akhil/.local/bin/uv.exe` with an ephemeral environment.

The evidence supports an internal, leakage-controlled comparison and a mixed
stability/reliability finding. It does not support independent external
validation, clinical utility, deployment readiness, or a new classifier claim.

## Working-tree and Git audit

- Branch: `main`, tracking `origin/main`.
- HEAD at audit: `e63b02c` (`Datasets`), also tagged `v1.0.0` and `1.0.0`.
- Existing tracked changes: the four original archive `.rar` entries are
  deleted; `README.md` is modified.
- Existing untracked work: expanded notebook/archive directories, data and
  manifests, `src/cardiodiag`, experiment scripts, tests, results, docs, demo,
  `pyproject.toml`, `uv.lock`, and manuscript files.
- No tracked or untracked file was deleted or overwritten during this audit.
- The archive deletions and expanded directories are treated as pre-existing
  user work and are preserved.

## Verified inventory

### Source and experiment code

| Area | Verified contents | Assessment |
|---|---|---|
| `src/cardiodiag/` | data validation, training-only cleaning, mixed-type preprocessing, logistic/OVEC/OSEC models, stable selector, evaluation metrics, nested validation, reliability, conformal prediction, historical approximation, external gate | Modular and importable; scientific caveats below remain material. |
| `experiments/` | historical comparison, nested validation, internal stage, repeated reliability/stability runners, external evaluator, table generation, demo support | Machine-readable outputs are generated; some protocols still need stronger prespecification. |
| `tests/` | 13 test modules covering data, preprocessing, models/experiments, historical protocol, metrics, nested validation, stability, reliability, uncertainty, robustness, and external gate | 31 tests collected; scientific-invariant coverage is useful but incomplete. |
| original notebook directories | Daza reproduction, Five States analyses, Mendeley analyses, LIME/XAI reports | Preserved as archival evidence; not a portable bit-for-bit reproduction. |

### Data and provenance

- `heart5.csv`: 918 rows, 12 columns including `HeartDisease`; target counts
  410/508; no exact duplicate rows in the checked-in file.
- `MendeleyCardiovascular_Disease_Dataset.csv`: 1,000 rows, 14 columns
  including `target` and `patientid`; target counts 420/580; no exact duplicate
  rows; `patientid` is unique and is dropped before modeling.
- Both SHA-256 hashes and roles match `data/manifests/local_datasets.json`.
- Both files are development/replication benchmarks, not new independent
  external evidence. Mendeley was used by the base study; `heart5.csv` is a
  composite related to public component datasets.
- The external manifest remains a `NOT_FROZEN` template. No independent
  external evaluation is verified.

### Results and manuscript artifacts

- Nested results exist for both local datasets under `results/generated/`.
- Repeated stability, uncertainty, and stability/reliability linkage JSON files
  exist for both datasets.
- Summary CSV/Markdown tables exist under `results/tables/`; the LaTeX nested
  table exists under `paper/tables/`.
- `paper/manuscript.tex` and `paper/references.bib` are editable and explicitly
  state that external validation is unavailable.
- PDF compilation is not verified because `pdflatex` was not reported as
  installed in the handoff.

## Commands actually executed

Passed:

```text
"C:/Users/akhil/.local/bin/uv.exe" lock --check
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with ruff --with-editable . ruff check .
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pytest --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python -m pytest -q
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with-editable . python demo/run_demo.py
```

The first test invocation exceeded 120 seconds before completion; the same
command completed with 27 passing tests using a 360-second limit. The manifest
script verified both local hashes and row counts. The plain `python` launcher
was unavailable, so an initial literal `python --version`/`uv` chain did not
execute project checks.

## Verified internal evidence

The saved nested artifacts use the same outer 3-fold stratified partitions for
all candidates and 3-fold inner model selection. Their stored fold means are:

| Dataset | Best observed corrected/stable candidate by ROC-AUC mean | ROC-AUC | Interpretation |
|---|---|---:|---|
| `heart5.csv` | corrected OVEC | 0.9298 | Stable logistic is similar; stable OSEC is lower. |
| Mendeley | corrected OVEC | 0.9956 | Stable OSEC is similar; no meaningful uniform advantage is shown. |

The saved repeated analyses report higher comparative feature-selection
stability for the stable selector on Mendeley (paired difference 0.078, 95%
bootstrap interval [0.035, 0.119]) and an inconclusive difference on `heart5.csv`
(0.098, [-0.111, 0.254]). Linkage artifacts report near-zero paired ROC-AUC
differences and no consistent calibration, confidence-ranking, or conformal
coverage advantage. These are internal benchmark results, and the intervals are
resampling summaries rather than independent-patient uncertainty guarantees.

## Methodological defects requiring correction or explicit limitation

1. **Coded categorical variables are not schema-controlled.** The Mendeley
   integer codes are currently discovered as numeric and therefore receive
   continuous scaling/outlier treatment and continuous model geometry. This is
   scientifically inappropriate for nominal variables and must be fixed with
   an explicit feature-type manifest.
2. **Stable relevance uses in-sample permutation importance.** Each selector
   resample fits logistic regression and evaluates permutation importance on
   the same rows. Although still training-only relative to an outer fold, this
   can inflate and destabilize relevance. Relevance should be evaluated on an
   inner validation partition or out-of-bag rows.
3. **The nested primary score is discrimination-only.** Inner selection uses
   ROC-AUC, while calibration and selective reliability are post hoc. This is
   acceptable for a discrimination endpoint but cannot support a calibration-
   aware selection claim.
4. **Outer-fold aggregation is not a complete uncertainty analysis.** The
   pooled bootstrap treats rows as exchangeable and the repeated-fold/seed
   summaries are not a hierarchical model. Results must be labeled as
   descriptive paired resampling intervals, with dependence acknowledged.
5. **Stability comparisons are benchmark-specific.** The two datasets are
   related public benchmarks and neither supplies an independent transport
   evaluation. Stability evidence cannot be generalized to new populations.
6. **The historical implementation is an approximation.** Notebook paths,
   dependencies, preprocessing order, search spaces, and saved sample totals
   conflict; exact bitwise reproduction is not possible from the archive.
7. **Threshold, calibration, and conformal policy are not clinical decisions.**
   The current artifacts measure empirical behavior only; they do not establish
   clinical utility, safety, fairness, or semantic uncertainty.

## Claims supported and unsupported

### Supported by the current artifacts

- The original notebook archive contains leakage-prone or underspecified paths
  involving preprocessing/resampling before splitting.
- A separate implementation can fit the documented cleaner, encoder, selector,
  and model inside training folds.
- Corrected OVEC is competitive with the listed corrected candidates on these
  local benchmarks under the saved protocol.
- Feature-set stability and predictive/selective reliability are distinct
  empirical outcomes in the saved internal analyses.
- Confidence ranking and split-conformal coverage can be measured on a held-out
  internal evaluation split when calibration is separated.

### Not supported

- A universally superior stability-aware classifier.
- Independent external validation or transportability.
- Clinical benefit, safety, readiness, or fairness across unmeasured groups.
- A causal interpretation of selected features or explanations.
- A novel algorithm claim without a completed, source-verifiable literature
  comparison.

## Priority order

1. Freeze explicit feature typing and rerun corrected baselines/ablations.
2. Replace in-sample relevance scoring with inner validation-only relevance and
   add tests for this boundary.
3. Generate result tables from the rerun artifacts and compare paired candidates
   on identical outer folds.
4. Complete the literature/novelty matrix and hostile reviewer audit.
5. Keep external evaluation blocked unless a genuinely independent compatible
   dataset is supplied and frozen before labels are used.
