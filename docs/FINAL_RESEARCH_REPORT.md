# CARDIODIAG final research report and closeout

**Assessment date:** 2026-11-05
**Status:** The offline engineering prototype and its validity audit are
complete. Internal evidence, source-distinct transport stress tests, and one
endpoint-aligned external evaluation are reproducible. The positive scientific
claim of dependable unseen-site prediction is not established: the one-site
external result has poor calibration and weak feature-only OOD separation.
Untouched multi-site confirmation and publication metadata remain open.

## Project outcome

The project now has a traceable audit of the supplied CARDIODIAG paper and its
notebook variants, a separate leakage-controlled research implementation,
machine-readable internal validation predictions, updated provenance, nine
core publication figures, three source-distinct cohort evaluations, and a
compiled and visually reviewed manuscript PDF. The latest draft uses the
author names and shared affiliation supplied provisionally by the project
owner; its remaining factual declarations are explicitly pending. Its source,
supporting run manifests, figures, and output hash are recorded in the
publication manifest. Existing
notebooks, data, result artifacts, release snapshot, and the four original RAR
archives were preserved; the RAR files were restored from the checked-out
source commit. The active source tree remains uncommitted, and nothing was
committed or pushed to the upstream remote.

The defensible research contribution is a reproducibility and
stability-versus-reliability audit. It does not establish a novel universally
superior algorithm, clinical benefit, safety, fairness, or transportability.

## Original method and reproduction status

The paper describes a pipeline combining LoRAS resampling, XAIH-DRC feature
reduction, and optimized voting and stacking classifiers (OVEC/OSEC). The
article and notebook family do not provide one unambiguous, executable
specification: the paper reports a 75:25 split, five-fold development
validation, and repeated runs, while notebooks include different split ratios,
preprocessing orders, model blocks, and table-generation paths. Some notebooks
resample or fit preprocessing/PCA before splitting. The XAIH-DRC description
also combines correlation and LIME criteria with PCA conflict resolution, but
the available code does not freeze a single matching implementation and
runtime.

`docs/PROTOCOL_AUDIT.md`, `docs/ORIGINAL_ALGORITHM_WALKTHROUGH.md`,
`docs/PAPER_TO_CODE_MAP.md`, and `docs/baseline_reproduction_report.md` keep
the paper protocol, notebook variants, and representative historical path
separate. The historical path is an approximation, not a bit-for-bit or
metric-exact reproduction. LoRAS parameters, fold-local LIME behavior, exact
article table provenance, and patient-level linkage cannot be independently
reconstructed from the supplied material. Historical metrics therefore remain
forensic evidence and are not used as corrected estimates.

## Corrected nested-validation results

A fresh internal-only stage used three outer folds, three inner folds, seed 42,
and ROC-AUC model selection on each of the two development/replication
benchmarks. The stage evaluates five candidates per dataset and stores outer
fold indices, labels, probabilities, fold metrics, selected parameters, and
runtime/provenance information. Predictions cover all 918 Heart5 rows and all
1,000 Mendeley rows. Its manifest explicitly sets
`external_validation: false`.

| Dataset | Candidate | ROC-AUC | PR-AUC | Brier | ECE |
|---|---|---:|---:|---:|---:|
| Heart5 | Corrected logistic | 0.9277 | 0.9345 | 0.1072 | 0.1021 |
| Heart5 | Corrected OVEC | 0.9295 | 0.9331 | 0.1002 | 0.0859 |
| Heart5 | Corrected OSEC | 0.9259 | 0.9281 | 0.1116 | 0.1208 |
| Heart5 | Stable logistic | 0.9278 | 0.9349 | 0.1072 | 0.1094 |
| Heart5 | Stable OSEC | 0.9253 | 0.9295 | 0.1095 | 0.1132 |
| Mendeley | Corrected logistic | 0.9930 | 0.9944 | 0.0270 | 0.1517 |
| Mendeley | Corrected OVEC | 0.9957 | 0.9966 | 0.0248 | 0.1582 |
| Mendeley | Corrected OSEC | 0.9943 | 0.9954 | 0.0233 | 0.2000 |
| Mendeley | Stable logistic | 0.9930 | 0.9944 | 0.0270 | 0.1404 |
| Mendeley | Stable OSEC | 0.9942 | 0.9953 | 0.0234 | 0.2422 |

Values are fold means. The pooled outer-fold curve scores in the figures are
computed on concatenated predictions and are not numerically interchangeable
with these fold means. A full fresh run under
`results/master_directive_20261105_serial/` reproduced the fold-mean metrics
of every candidate from `results/final_completion_20261105/` exactly (maximum
absolute difference 0). It took 581.5 seconds. The earlier interrupted attempt
under `results/master_directive_20261105/` is retained and is not a complete
result stage.

Corrected OVEC is the strongest listed discriminator on both benchmarks, but
the differences are small and do not demonstrate a universal ensemble
advantage. Stable OSEC is below corrected OSEC on Heart5 and nearly tied on
Mendeley. The Mendeley results have appreciable fold-mean ECE despite very high
ROC-AUC; discrimination does not establish calibrated probabilities.

### Five-seed split sensitivity

Protocol `CD-IV-001` ran the same five candidates and 3×3 nested design under
seeds 43–47. Every row was scored exactly once per seed, and recomputing pooled
metrics from the saved labels and probabilities matched the recorded metrics
within `1e-10`. The runs share one dataset hash, source-bundle hash, and
dependency-lock hash. Seed 42 is excluded from this aggregate because its
source and lock hashes differ from the repeat set.

For example, corrected OVEC had mean ROC-AUC `0.926 ± 0.003` and Brier
`0.099 ± 0.002` on Heart5; on Mendeley it had ROC-AUC `0.995 ± 0.001` and
Brier `0.026 ± 0.001`. The five-seed summary reports all candidates and also
shows that calibration error varies by dataset and candidate. These are
descriptive statistics across randomized splits, not patient-level confidence
intervals or hypothesis tests. They do not establish external transport.
Detailed values are in
`results/internal_seed_sensitivity_20261105/seed_repeat_summary.md` and the
machine-readable audit is in `seed_repeat_summary.json`.

## Stability, reliability, and proposed extensions

The repeated stability and stability-reliability linkage analyses do not show
that a more stable selected feature set reliably improves predictive or
selective behavior. Their intervals are descriptive and use only three
repeat-level paired differences or ten seeds; they are not independent-patient
confidence intervals. Feature-set stability is distinct from explanation
stability, causal importance, and clinical interpretability. No authoritative
fold-local LIME explanation-stability result is available.

AURA-ML V2 is dataset-conditional. Its seed-aggregated ROC-AUC was 0.9244
versus 0.9257 for corrected OVEC on Heart5, and 0.9977 versus 0.9955 on
Mendeley. Its separate 70K feasibility result was 0.802842 versus 0.800253
for a frozen CatBoost comparator, but those baselines were not inner-retuned.
The 70K outcome and schema differ from the CARDIODIAG tasks. Neither result
supports a new universal-algorithm or external-validation claim.

The 70K study remains a separate exploratory benchmark. The full custom
five-candidate CARDIODIAG nested protocol and complete matched factorial
ablation set were not completed there. Synthetic missingness/noise analyses
are evaluation stress tests only. Distribution diagnostics across local data
are label-free covariate comparisons; endpoint/schema incompatibility prevents
treating them as direct predictive transfer. A source-distinct Z-Alizadeh Sani
cohort is now evaluated in `CD-XD-003` using three harmonized features.
ROC-AUC was 0.720 (95% CI 0.651–0.780); source-only calibration changes were
modest and paired intervals included no improvement; OOD AUROC was 0.604. The
target threshold is `>=50%` versus `>50%` in source, so the result is a
transport stress test, not endpoint-identical external validation.
Label/concept shift, prospective utility, broad demographic fairness, and
patient-level safety remain unestablished.

The subsequent `CD-XD-004` study evaluated a source-distinct AngioCAD cohort
with an endpoint aligned at `>50%` stenosis. Only 377 of 413 labeled IDs had
clinical predictors. The source-only model achieved ROC-AUC 0.787 (95%
bootstrap interval 0.734–0.838). Platt calibration produced modest, inconclusive
Brier/log-loss changes and slightly worsened ECE. OOD AUROC was 0.589 (95%
interval 0.541–0.635), so the warning remains weak. Repeated runs yielded
byte-identical predictions and independent metrics matched to floating-point
precision. This closes the endpoint-aligned one-cohort evaluation gate but
does not support reliable calibration, rejection, or broad transport. Full
results are in `TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.

The reliability layer adds a post-hoc AngioCAD replay (`CD-XD-006`) and a
fresh Duke ACATH stress test (`CD-XD-005`). AngioCAD ROC-AUC was 0.790 (95%
bootstrap interval 0.733–0.837), but the combined selective rule automatically
covered only 21/377 records (5.6%). Duke ROC-AUC was 0.661; its >=75% stenosis
endpoint differs from the source >50% threshold, and 41 of 401 automatically
classified records were incorrect (10.2%). Feature-only OOD AUROCs were weak;
the trusted site gate withheld all unknown-site deployment scores. The exact
Statlog release was screened and all 270 rows matched Cleveland, so it was
excluded as duplicate data. Current protocols and outputs are indexed in
`docs/handoff.md`, `docs/DATASET_COMPATIBILITY.md`, and `docs/QA_REPORT.md`.

## Reproducibility and software changes

The internal runner now selects a unique UTC-named result directory, refuses
file collisions, records progress and failure state, hashes source files and
the dependency lock, and records platform, hardware, package versions, dataset
hashes, and result hashes. Nested artifacts retain outer splits, labels,
probabilities, and fit/tune/score timing. Voting and stacking are serial within
the experiment process to avoid nested joblib over-parallelism on Windows; a
seed-42 metric-parity check against the prior artifacts had zero metric delta.

The final result stage is
`results/master_directive_20261105_serial/internal_stage_manifest.json`. The
publication-figure manifest is
`paper/figures/master_directive_20261105_final/figure_manifest.json`; it
records input and output SHA-256 hashes for 18 PNG/PDF files. The editable
manuscript is `paper/manuscript.tex`; the latest compiled PDF is
`output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`, with its manifest in
`paper/build/research_draft_20261105/`. The PDF includes the validity
sensitivities and provisional author information, was rendered with Poppler,
and was visually inspected. The build completed without unresolved
references, unresolved citations, missing graphics, or overfull boxes.
Tectonic reported font fallback and underfull boxes, so this is a verified
research draft rather than final venue proofing.

## Quality assurance

The completed local QA run is recorded in `docs/QA_REPORT.md`: all 106 collected tests pass;
Ruff, bytecode compilation, lockfile checks, demos, JSON and notebook parsing,
dataset and experiment hashes, independent target-metric recalculation,
validity-sensitivity and Statlog overlap audits, figure hashes, and PDF
page/text extraction checks pass. The
console entry point `uv run pytest -q` fails to canonicalize its script path
in this checkout, but the equivalent `uv run python -m pytest -q` completes
successfully. No external-validity or clinical claim can be established by
these software checks.

## Real-world readiness decision

The staged workflow is in `docs/REAL_WORLD_READINESS_WORKFLOW.md`; its
machine-readable gate record is `docs/real_world_readiness_gates.json`. The
evaluator reports **NO-GO**, with 1 of 13 phases passed. The largest blockers
are an approved intended use, a fresh compatible external cohort, and
prospective/clinical and regulatory evidence. Screened data-access paths and
the unsigned MultiD4CAD DUA are recorded in
`docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md`. The DUA has not been signed and no
request was sent. This work does not authorize real-world or clinical use.

## Remaining requirements

1. Obtain an independent cohort with an endpoint exactly aligned to the source
   and sufficient negative cases; define its semantic feature mapping and
   overlap assessment; freeze it before a one-way predictive evaluation.
2. Confirm redistribution rights for the Five States composite and Kaggle 70K
   data, and complete the ethics/data-use review with the responsible team.
3. Confirm the provisional author order and individual affiliations. Obtain
   Ch Hari Krishna's and G Vennela's contribution statements and final factual
   ethics/data-use, funding, and competing-interest declarations. The current
   draft marks these items pending and claims no ethics approval or exemption.
4. Select a target venue and check its exact template, formatting, reference,
   and reporting requirements. The current PDF is an IEEE-style draft and is
   not submission-ready.
5. If a full original-method reproduction is required, first resolve the
   notebook protocol conflicts and obtain the original LoRAS/LIME parameters,
   executable environment, and source table provenance. Do not substitute a
   simpler protocol and describe it as exact reproduction.

The canonical source checkout remains dirty and uncommitted. The preserved
upstream remote belongs to the original project source; this work was not
pushed there. The completion matrix is in
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md`.
