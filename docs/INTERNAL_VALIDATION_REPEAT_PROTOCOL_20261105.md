# Internal nested-validation seed-sensitivity protocol

**Protocol ID:** `CD-IV-001`  
**Frozen:** 2026-11-05  
**Scope:** retrospective, within-dataset split sensitivity; not external or
confirmatory clinical validation.

## Rationale and limitation

The existing final nested run used seed 42. This protocol fixes a repeat set
before launching any additional fits to describe how results vary under the
same randomized nested design. Because seed-42 results and model comparisons
have already been examined, this is an exploratory robustness check, not a
preregistered confirmatory study. No candidate, feature, or claim will be
selected based on these repeats.

## Frozen design

- **Datasets:** the existing Heart5 composite (`heart5.csv`, target
  `HeartDisease`) and Mendeley cardiovascular dataset
  (`MendeleyCardiovascular_Disease_Dataset.csv`, target `target`). Their
  licenses, patient linkage, and representativeness limitations remain.
- **Design:** same nested stratified evaluation as the seed-42 final stage,
  with 3 outer folds, 3 inner folds, one outer repeat, and the repeated seed
  list `[43, 44, 45, 46, 47]`.
- **Execution:** seed 42 is an earlier completed stage, but its source-bundle
  and dependency-lock hashes differ from the current checkout. It is excluded
  from the repeated-seed aggregate. Execute seeds 43–47 with
  `experiments/run_internal_stage.py`, each in a distinct output directory.
- **Candidates and selection:** retain the existing five candidates and the
  existing nested selection rule. Do not alter features, estimators,
  preprocessing, candidate pool, or selection based on repeat results.
- **Primary summary:** compute ROC-AUC for each candidate and dataset per seed;
  also report PR-AUC, Brier score, uniform-bin ECE, and balanced accuracy.
  Recompute each pooled out-of-fold metric from saved labels and probabilities
  and fail if it differs from the stored result.
- **Aggregation:** report mean, sample standard deviation, minimum, and maximum
  across the five seed-level pooled out-of-fold metrics. Do not treat seeds as
  independent patients or report a confidence interval or significance test
  across seeds.
- **Integrity:** record the dataset SHA-256, source-bundle hash, lockfile hash,
  split indices, predictions, runner parameters, and per-seed run manifest.

## Acceptance targets and stop rules

1. All five seed stages must complete for both datasets with 3x3 nested splits.
2. Each seed must score every row exactly once in its outer test folds; no row
   may appear in two outer test folds within the same seed.
3. Recomputed pooled metrics must match the stored metrics to absolute
   tolerance `1e-10`.
4. Every seed uses the same dataset hash, candidate set, target, and split
   configuration. Any mismatch invalidates the seed-sensitivity summary.
5. These runs do not close patient-level uncertainty or external-validation
   gates. Available files do not provide a verified patient-linkage key across
   all records, and repeated random splits cannot establish independent
   patients or transportability.

## Reproduction commands

```powershell
uv run python experiments/run_internal_stage.py --seed 43 --output-dir results/internal_seed_sensitivity_20261105/seed_43
uv run python experiments/run_internal_stage.py --seed 44 --output-dir results/internal_seed_sensitivity_20261105/seed_44
uv run python experiments/run_internal_stage.py --seed 45 --output-dir results/internal_seed_sensitivity_20261105/seed_45
uv run python experiments/run_internal_stage.py --seed 46 --output-dir results/internal_seed_sensitivity_20261105/seed_46
uv run python experiments/run_internal_stage.py --seed 47 --output-dir results/internal_seed_sensitivity_20261105/seed_47
```

After completion, run `experiments/summarize_internal_seed_sensitivity.py` to
recompute and aggregate the recorded predictions.

## Provenance amendment

After seed 43 completed and seed 44 started, a manifest-only comparison found
that seed 42 used a different source-bundle hash and `uv.lock` hash. Before
reading any seed-43 or seed-44 outcome metrics, the repeated set was amended to
43–47 so all five repetitions can be required to share one code and dependency
snapshot. Seed 42 remains a separately reported historical result and is not
included in the five-seed summary. This correction is based on provenance,
not observed performance.
