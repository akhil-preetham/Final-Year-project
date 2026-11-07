# CARDIODIAG execution status

**Historical checkpoint:** 2026-11-04
**Status:** Superseded by the 2026-11-05 closeout. This file preserves the
prior execution notes; use `docs/FINAL_RESEARCH_REPORT.md`,
`docs/QA_REPORT.md`, and `docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md` for the
latest results and completion status.

The earlier 2026-11-05 closeout completed the fresh provenance-rich 3x3 stage,
verified CD-XD-002–004, recorded 64 passing tests, and rebuilt an 11-page
manuscript. The later closeout added CD-XD-005/006, Statlog duplicate screening,
policy hardening, 76 passing tests, and the 12-page manuscript at
`output/pdf/CARDIODIAG_Domain_Shift_Manuscript_20261105.pdf`. See
`docs/handoff.md`, `docs/QA_REPORT.md`, and
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md` for current status. The prior
state and commands below are retained as dated history. The subsequent
real-world readiness workflow added a machine-checked 13-phase gate. This
historical note's 92-test count is superseded by the 106-test current run in
`docs/QA_REPORT.md`; the readiness gate remains `NO_GO` (1/13 phases passed).

## Completed and verified in this session

- Inspected the current branch, working tree, remote, recent commits, source,
  experiment runners, tests, manifests, results, notebooks, and manuscript.
- Confirmed the pre-existing expanded archives and archive deletions are user
  work and were not removed or reverted.
- Ran the local test suite after AURA-ML implementation: **50 passed**.
- Ran Ruff on `src`, `tests`, and `experiments`: **passed**.
- Ran `git diff --check`: **passed**.
- Ran Python bytecode compilation for source, experiments, demo, and tests:
  **passed**.
- Parsed 39 notebooks and verified their JSON/cell structure: **0 failures**.
- Ran the installed `cardiodiag smoke` command: **passed**.
- Verified 11 manuscript citation keys and all LaTeX table inputs: **passed**.
- Parsed the repository JSON artifacts: **122 checked, 0 invalid**.
- Recomputed the three local dataset summaries and confirmed manifest hashes,
  row counts, targets, class counts, and explicit feature schemas.
- Generated the authoritative registry from 26 explicitly selected result
  artifacts: `docs/AUTHORITATIVE_METRIC_REGISTRY.json` and `.md`.
- Regenerated `results/tables/nested_summary.*` and
  `paper/tables/nested_summary.tex` from the post-boundary corrected nested
  artifacts, removing a protocol/source ambiguity in the manuscript package.
- Corrected the CLI smoke path so its preprocessing uses the explicit dataset
  schema rather than dtype inference for coded categorical predictors.

## Latest 70K live run

The requested resource-aware 2x2 nested validation completed in 193.4 seconds
and wrote `results/generated/live_70k_nested_2x2.json`. It evaluated Logistic
Regression, Random Forest, XGBoost, CatBoost, HistGradientBoosting as the
ensemble component, and the fixed XGBoost + HistGradientBoosting + Logistic
ensemble. The artifact stores fold-level test indices, labels, probabilities,
selected inner parameters, and all requested metrics. The companion comparison
is `results/final_publication/LIVE_70K_NESTED_2X2_REPORT.md`.

## AURA-ML research prototype

Implemented and tested the provisional AURA-ML framework under
`src/cardiodiag/aura/`. The design and mathematical formulation are in
`docs/AURA_ML_DESIGN.md`; the baseline/data audit is in
`docs/AURA_ML_BASELINE_AUDIT.md`; and the exploratory results are in
`results/aura_ml/AURA_ML_2X2_REPORT.md`. Primary artifacts are
`results/aura_ml/aura_nested_2x2_heart5.json`,
`results/aura_ml/aura_nested_2x2_mendeley.json`, and
`results/aura_ml/aura_nested_2x2_70k.json`.

The AURA runs completed with paired same-fold baselines. Pooled ROC-AUC was
0.924990 vs 0.924376 on heart5, 0.995854 vs 0.994561 on Mendeley, and 0.801851
vs 0.800072 on 70K. The small-dataset bootstrap intervals include zero; the
70K interval is positive under the stored row-level bootstrap but remains
exploratory. AURA exceeded 93% accuracy only on Mendeley. The full ablation
grid was completed on heart5 and Mendeley; the 70K ablation grid remains
unrun because of repeated fitting cost.

## AURA-ML V2 confirmatory strengthening

V2 audits the immutable V1 artifacts in `results/aura_ml_v2/V1_AUDIT.json`,
adds isotonic calibration and training-side threshold analysis, removes feature
selection from the frozen default after the V1 ablation evidence, and evaluates
strong baselines under identical 3x3 folds. Six small-dataset artifacts were
completed for seeds 42--44. The V2 registry is
`results/aura_ml_v2/V2_REGISTRY.json` and the report is
`results/aura_ml_v2/AURA_ML_V2_REPORT.md`.

The V2 seed-aggregated ROC-AUC was 0.924449 vs 0.925725 for corrected OVEC on
heart5, and 0.997661 vs 0.995546 on Mendeley. Thus V2 was dataset-conditional,
not uniformly superior. The requested 70K 3x3 run exceeded 35 minutes without
writing an artifact; it is recorded as incomplete, and the previous 70K 2x2
result remains exploratory only. The solver diagnostic completed for liblinear,
 lbfgs, and saga without warnings on the fixed 19-feature representation.

A separate checkpointed 70K feasibility run then completed in 518.0 seconds
under `results/aura_ml_v2/70k_feasibility_3x3.json`. AURA completed inner 3-fold
selection and selected CatBoost in all three outer folds; comparison models were
frozen single-threaded defaults on identical outer folds. AURA ROC-AUC was
0.802842 versus 0.800253 for frozen CatBoost and 0.799116 for the frozen
existing ensemble. This is feasibility evidence, not definitive superiority,
because the comparison baselines were not inner-retuned.

## Adaptive-learning literature investigation

Completed a source-traceable prior-art investigation without running experiments
or modifying CARDIODIAG/AURA source code. The registry contains 34 records across
AutoML, dataset-conditioned learning, tabular foundation models, domain/shift
adaptation, ordinary tabular architectures, benchmarks, and the local AURA
prototype. MOSAIC and SageNet were confirmed as ambiguous names with multiple
unrelated publications. CrossAdapt was resolved to a 2026 online
cross-architecture recommendation-transfer preprint, not a general-purpose
cardiovascular tabular model. AutoIRAD could not be verified, and ModernNCA was
only found as a secondary benchmark mention.

Deliverables:

- `docs/EXISTING_MODELS_REGISTRY.json`
- `docs/EXISTING_ADAPTIVE_MODELS_COMPARISON.md`
- `docs/MOSAIC_SAGENET_CROSSADAPT_VERIFICATION.md`
- `docs/ADAPTIVE_ML_LITERATURE_REVIEW.md`
- `docs/TABULAR_FOUNDATION_MODELS_REVIEW.md`
- `docs/CROSS_DATASET_GENERALIZATION_REVIEW.md`
- `docs/AUTOML_AND_META_LEARNING_REVIEW.md`
- `docs/BENCHMARK_FRAMEWORK_COMPARISON.md`
- `docs/CARDIODIAG_RESEARCH_GAP.md`
- `docs/PROPOSED_NEW_ALGORITHM_DIRECTIONS.md`
- `docs/FINAL_ALGORITHM_RECOMMENDATION.md`

The evidence does not support starting another generic adaptive ensemble. The
recommended direction is a guarded, semantic schema/unit/endpoint alignment and
cross-dataset reliability framework, preceded by leave-dataset-out meta-risk
router benchmarking. No new algorithm was implemented in this phase.

## Local model exhaustion

The compatible local portfolio was exhausted through verified existing artifacts:
scikit-learn classical/neural models, RBF-SVM, KNN, XGBoost, LightGBM, CatBoost,
OVEC/OSEC, soft voting, stacking, and AURA V1/V2. TabPFN, TabICL, TabDPT,
HyperFast, AutoGluon, PyTorch, TensorFlow, Transformers and related frameworks
are not installed in the active environment and were not falsely reported as
executed. The consolidated report is
`docs/LOCAL_MODEL_EXHAUSTIVE_EVALUATION.md`; machine-readable inventory is
`results/local_model_inventory.json`.

Best verified local results are compact-pool soft voting ROC-AUC 0.929033 on
heart5, CatBoost ROC-AUC 0.997828 on Mendeley, tuned CatBoost ROC-AUC 0.800432
on 70K, and AURA V2 feasibility ROC-AUC 0.802842 on 70K. Because the latter
used frozen comparison baselines, no new algorithm is justified solely by that
difference. The correct next step is fair execution of unavailable foundation
models or compatible external validation, not another unvalidated model.

## Local baseline freeze and cross-dataset feasibility

The current local-model results are frozen as
`LOCAL_MODEL_BASELINE_2026-11-03_V1` in
`results/local_model_baseline_freeze.json`, with a human-readable reference at
`docs/LOCAL_MODEL_BASELINE_FREEZE.md`. The freeze records dataset and artifact
SHA-256 hashes and preserves the caveat that the AURA 70K feasibility comparison
used frozen rather than fully retuned baselines.

The cross-dataset protocol is `docs/CROSS_DATASET_EVALUATION_PROTOCOL.md` and
the feasibility report is `docs/SAGE_TRANSFER_FEASIBILITY_REPORT.md`, with
machine-readable status in `results/cross_dataset_feasibility.json`. The
protocol is feasible as a design, but empirical transfer is currently blocked:
no local pair has an approved common endpoint and semantic feature map, no
independent compatible target cohort is frozen, and the major existing
cross-dataset methods are not installed in the active environment. No direct
cross-dataset predictive run was performed and no classifier was implemented.

Current conclusion: SAGE-Transfer novelty is not identifiable from the local
datasets. The next action is provenance, endpoint and mapping approval, followed
by a new namespaced evaluation against existing methods under the registered
information budgets—not accuracy optimization.

## CLIN-ADAPT development cycle

CLIN-ADAPT was added as a separate package under `src/clin_adapt/` with separate
artifacts under `results/clin_adapt/` and documentation under
`docs/clin_adapt/`. The registry resolved 20 executable local candidates and 15
explicitly unavailable neural, foundation-model and AutoML families. The
parallel engine completed 60/60 candidate jobs on Heart5, 60/60 on Mendeley,
and 12/12 on the resource-bounded 70K priority run.

The provisional CASL coordinator selected single candidates when fusion did not
pass its fixed validation-improvement/diversity gate. Full 3x2 pooled ROC-AUC
was 0.926700 on Heart5 and 0.997701 on Mendeley; the 2x2 70K priority run was
0.802481. These are separate within-dataset development artifacts, not
cross-dataset or external-validation results. The Heart5 ablation improved its
bounded no-fusion control, while Mendeley showed no fusion benefit; therefore no
universal-superiority or novelty claim is made.

Required CLIN-ADAPT documents are in `docs/clin_adapt/`, including architecture,
registry, mathematical design, novelty analysis, parallel execution,
experimental protocol, ablations, cross-dataset status, reliability and final
research assessment. The cross-dataset run remains blocked under `CD-XD-001`.

Final CLIN-ADAPT QA on 2026-11-04 passed: **57 tests**, Ruff, compilation,
JSON validation, CLI registry serialization, frozen-baseline hash verification,
and `git diff --check`. The runtime snapshot is
`results/clin_adapt/runtime_resources.json`: 12 logical CPUs detected, no GPU
backend detected, and no memory probe available in the active environment.

## Latest live execution

Fresh bounded nested-validation runs completed during the current session. They
are intentionally exploratory and are not merged into the authoritative
registry without a review of the protocol decision.

| Dataset | Best fold-mean ROC-AUC | Candidate | Artifact |
|---|---:|---|---|
| `heart5.csv` | 0.9276 | corrected OVEC | `results/generated/live_heart5_nested_2x2.json` |
| Mendeley | 0.9946 | corrected OVEC | `results/generated/live_mendeley_nested_2x2.json` |

The smoke command also completed with ROC-AUC `0.9348`, PR-AUC `0.9317`,
accuracy `0.8913`, Brier `0.0878`, and ECE `0.0772` on its fixed internal split.

## Completed before this session and retained

- Training-only preprocessing and selector relevance evaluation.
- Corrected nested internal validation on `heart5.csv` and Mendeley.
- Stability, calibration, selective-risk, conformal, robustness, and linkage
  analyses with machine-readable outputs.
- Separate exploratory 70K model benchmarks and bounded tuning.
- External-manifest fail-closed gate and one-way external evaluator.
- Editable manuscript and archived historical notebook evidence.

## Blocked or incomplete

- No frozen, genuinely independent, schema-compatible external dataset is
  available; external validation therefore remains **BLOCKED**.
- The full five-candidate custom CARDIODIAG nested workflow on 70K was not
  completed within the available runtime; the reduced logistic pair and generic
  benchmark are retained as separate evidence.
- Author names, affiliations, ethics/data-use statement, funding, contributions,
  and target journal are not supplied.
- No LaTeX compiler (`pdflatex`, `xelatex`, or `tectonic`) is available on the
  host, so PDF compilation remains unverified.
- Primary nested JSON artifacts store fold-level and pooled metrics, not all raw
  outer-fold prediction vectors; independent metric recomputation is therefore
  limited to the stored summaries.

## Exact commands executed

```text
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/ruff.exe check src tests experiments
./.venv/Scripts/python.exe -m compileall -q src experiments demo tests
./.venv/Scripts/cardiodiag.exe smoke
git diff --check
./.venv/Scripts/python.exe experiments/run_nested_validation.py --dataset heart5.csv --target HeartDisease --output results/generated/live_heart5_nested_2x2.json --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/run_nested_validation.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/generated/live_mendeley_nested_2x2.json --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/build_authoritative_registry.py
./.venv/Scripts/python.exe experiments/summarize_nested.py --input results/generated/post_boundary_corrected_nested_heart5.json results/generated/post_boundary_corrected_nested_mendeley.json --csv results/tables/nested_summary.csv --markdown results/tables/nested_summary.md
./.venv/Scripts/python.exe experiments/generate_paper_assets.py --input results/tables/nested_summary.csv --output paper/tables/nested_summary.tex
./.venv/Scripts/python.exe experiments/run_aura_nested.py --dataset heart5.csv --target HeartDisease --output results/aura_ml/aura_nested_2x2_heart5.json --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/run_aura_nested.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/aura_ml/aura_nested_2x2_mendeley.json --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/run_aura_nested.py --dataset data/kaggle_cardiovascular_70k/cardio_train.csv --target cardio --output results/aura_ml/aura_nested_2x2_70k.json --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/run_aura_ablations.py --dataset heart5.csv --target HeartDisease --output results/aura_ml/ablations/heart5 --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/run_aura_ablations.py --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target --output results/aura_ml/ablations/mendeley --outer-splits 2 --inner-splits 2 --seed 42
./.venv/Scripts/python.exe experiments/build_aura_registry.py
./.venv/Scripts/python.exe experiments/run_aura_v2_70k_feasibility.py --dataset data/kaggle_cardiovascular_70k/cardio_train.csv --target cardio --output results/aura_ml_v2/70k_feasibility_3x3.json --outer-splits 3 --inner-splits 3 --seed 42
```

## Next recoverable action

Run the full final QA commands listed in `docs/REPRODUCIBILITY_GUIDE.md`, then
review the generated registry and completion report. Do not run external
evaluation unless `data/manifests/external_dataset.json` is frozen and passes
the external gate.
