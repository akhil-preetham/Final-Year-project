# CARDIODIAG handoff

## Goal

Deliver a reproducible, leakage-controlled research extension of CARDIODIAG,
with honest internal validation, reliability analysis, an editable IEEE-style
manuscript, and no unsupported clinical or novelty claims.

## State

Completed locally:

- Historical and corrected protocol audit.
- Nested validation on `heart5.csv` and the Mendeley benchmark.
- Stability-aware selector, calibration, selective-risk, and conformal analyses.
- Repeated feature-stability comparison and repeated uncertainty-evidence runs.
- Paired stability--reliability linkage analysis using the same repeated splits.
- External-manifest freeze gate.
- Manuscript package and non-clinical demonstration.
- 31 automated tests and Ruff checks.

Incomplete/blocking:

- No genuinely independent compatible external dataset is frozen.
- The manuscript therefore reports no independent external validation.
- Final literature novelty review and target-journal selection remain open.
- IEEE PDF compilation was not run because `pdflatex` is not installed on the
  host.

## Important files

- `docs/final_status.md`: final evidence status and remaining gates.
- `docs/execution_plan.md`: automated workflow and human intervention points.
- `docs/baseline_reproduction_report.md`: historical/corrected audit.
- `docs/literature_and_dataset_review.md`: targeted novelty and dataset review.
- `src/cardiodiag/nested_validation.py`: nested validation.
- `src/cardiodiag/reliability.py`: calibration and selective-risk metrics.
- `src/cardiodiag/external_gate.py`: external dataset freeze gate.
- `experiments/run_external_evaluation.py`: one-way external evaluator that
  refuses incomplete manifests and never fits on external rows.
- `results/generated/`: machine-readable experiment outputs.
- `results/tables/nested_summary.csv`: generated summary table.
- `paper/manuscript.tex`: editable IEEE-style manuscript.
- `demo/run_demo.py`: non-clinical prediction-set demonstration.

## Decisions

- The stability-aware method is not claimed superior because nested results do
  not show a uniform advantage.
- The Mendeley dataset is not treated as independent external validation because
  the base paper already used it.
- Overlapping UCI component datasets are not treated as independent evidence.
- The final manuscript explicitly reports the absence of independent external
  validation rather than inventing or forcing a dataset choice.
- The stability claim is dataset-conditional: positive on Mendeley, inconclusive
  on `heart5.csv`.
- The uncertainty claim is empirical selective reliability only; it is not a
  claim that the model semantically understands uncertainty.
- The current contribution framing is a stability--reliability decoupling audit:
  feature-set stability did not translate into a consistent reliability gain.

## Checks

Passed using the accessible uv executable:

```text
"C:/Users/akhil/.local/bin/uv.exe" lock --check
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with ruff --with-editable . ruff check .
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pytest --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python -m pytest -q
```

Observed results: lock check passed, Ruff passed, and the current suite passed
31 tests after adding schema-boundary and robustness invariants.

Required literal commands were attempted but blocked before project execution
because the shell resolves `uv` to a permission-blocked wrapper:

```text
uv run ruff check .
uv run python -m pytest -q
```

The failure is host-level (`Permission denied`), not a project test failure.

Manual smoke check passed:

```text
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python demo/run_demo.py
```

The demonstration printed a probability, a conformal prediction set, and an
abstention-capable prediction while displaying the non-clinical warning.

Additional evidence commands passed:

```text
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_stability_evidence.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_stability_evidence.json --n-splits 5 --n-repeats 10 --n-resamples 8 --seed 42
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_stability_evidence.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/mendeley_stability_evidence.json --n-splits 5 --n-repeats 10 --n-resamples 8 --seed 42
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_uncertainty_evidence.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_uncertainty_evidence.json --seeds 42 43 44 45 46 47 48 49 50 51
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_uncertainty_evidence.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/mendeley_uncertainty_evidence.json --seeds 42 43 44 45 46 47 48 49 50 51
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_stability_reliability_linkage.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_stability_reliability_linkage.json --seeds 42 43 44 45 46 47 48 49 50 51
"C:/Users/akhil/.local/bin/uv.exe" run --no-project --with pandas --with numpy --with scipy --with scikit-learn --with imbalanced-learn --with xgboost --with lime --with-editable . python experiments/run_stability_reliability_linkage.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/mendeley_stability_reliability_linkage.json --seeds 42 43 44 45 46 47 48 49 50 51
```

Observed: stability evidence was positive on Mendeley (`0.078`, 95% CI
`[0.035, 0.119]`) and inconclusive on `heart5.csv` (`0.098`, 95% CI
`[-0.111, 0.254]`). Internal confidence-error AUC was above 0.5 for both
datasets, but no external-shift evidence exists. The paired linkage run found
near-zero ROC-AUC differences and no consistent reliability improvement from
the stable selector.

## Post-correction bounded evidence

Post-correction sensitivity artifacts are kept separately under the
`schema_corrected_*` prefix. They use explicit coded-category schemas and
held-out relevance scoring inside selector resamples. The 2x2 nested runs,
5-fold/3-repeat stability runs, four-seed uncertainty runs, and four-seed
linkage runs completed for both datasets. The default 3x3 two-dataset internal
stage exceeded the available ten-minute execution limit before writing output;
it is not reported as passed. See `docs/schema_corrected_evidence.md`.

## Next action

If stronger external evidence is required, provide or approve one independent
compatible dataset and complete `data/manifests/external_dataset.json`; then
run `experiments/check_external_manifest.py` before adding any external labels
to model selection or calibration.
