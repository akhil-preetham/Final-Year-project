# CARDIODIAG session handoff

> Historical checkpoint. The current state is in `docs/handoff.md`,
> `docs/QA_REPORT.md`, and `docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md`.

## Resume point

The working directory is the canonical repository root on branch `main`. The
checkout is intentionally dirty with pre-existing and untracked source,
datasets, results, documentation, and release artifacts. Four original RAR
archives were restored from the checked-out source commit. Do not reset, clean,
or delete the existing research tree.

The current checkpoint is `docs/handoff.md`, with detailed analysis in
`docs/FINAL_RESEARCH_REPORT.md`, directive status in
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md`, and checks in `docs/QA_REPORT.md`.
The fresh provenance-rich 3x3 results are in
`results/master_directive_20261105_serial/`; they exactly match the earlier
authoritative fold means and store all outer predictions and split indices. A
The historical 12-page manuscript is preserved at
`output/pdf/CARDIODIAG_Domain_Shift_Manuscript_20261105.pdf`. The latest
remediation draft is at
`output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`; its build and
verification status are in `docs/QA_REPORT.md`. CD-XD-005 and CD-XD-006
outputs are in their final transfer folders.

The authoritative result registry is still
`docs/AUTHORITATIVE_METRIC_REGISTRY.json`; its Markdown view is
`docs/AUTHORITATIVE_METRIC_REGISTRY.md`. The older execution notes in
`docs/EXECUTION_STATUS.md` are historical.

## Important decisions

1. `post_boundary_corrected_*` is the primary corrected internal evidence
   family. `schema_corrected_*` is bounded sensitivity evidence.
2. The Mendeley and Five States/`heart5.csv` files are development or
   replication benchmarks, not independent external validation.
3. The Kaggle 70K file has a different target and predictor schema and is a
   separate exploratory benchmark, not external validation of CARDIODIAG.
4. The defensible contribution is an auditable evaluation of stability,
   reliability, and multi-source transfer under shift, not a new predictor or
   clinical diagnostic claim.
5. Author names and a common affiliation are now provisionally supplied in the
   manuscript. Confirm order and individual affiliations; keep ethics/data-use,
   funding, two coauthor contribution statements, competing interests, and
   venue pending until authors and institution provide the facts.

## Files changed in the 2026-11-04 checkpoint (historical)

- `experiments/build_authoritative_registry.py`
- `src/cardiodiag/cli.py`
- `results/tables/nested_summary.csv`
- `results/tables/nested_summary.md`
- `paper/tables/nested_summary.tex`
- `docs/EXECUTION_STATUS.md`
- `docs/SESSION_HANDOFF.md`
- `docs/AUTHORITATIVE_METRIC_REGISTRY.json`
- `docs/AUTHORITATIVE_METRIC_REGISTRY.md`

## Verified commands

The current test command works through the Python module entry point:

```text
uv run python -m pytest -q
./.venv/Scripts/ruff.exe check src tests experiments
git diff --check
```

`uv run pytest -q` fails before tests start because the trampoline cannot
canonicalize its generated script path in this checkout. The equivalent
Python-module command above completed the latest 85-test suite. Ruff, compilation,
`uv lock --check`, data hashes, figure hashes, demo, and PDF verification are
summarized in `docs/QA_REPORT.md`.

The current real-world readiness gate is `NO_GO` (1/13 phases passed). The
workflow, measurable targets, current blockers, and external data-access paths
are in `docs/REAL_WORLD_READINESS_WORKFLOW.md` and
`docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md`; run
`uv run python experiments/evaluate_readiness.py` to recompute the gate.

## Remaining work

- AURA-ML is implemented as a provisional research prototype. Do not call it a
  genuinely novel or universally superior algorithm until a broader literature
  review and confirmatory repeated nested experiments support that claim.
- AURA primary artifacts, registry, design, audit, comparison table, and small
  dataset ablations are under `results/aura_ml/`, `docs/AURA_ML_DESIGN.md`, and
  `docs/AURA_ML_BASELINE_AUDIT.md`.
- The full 70K AURA ablation grid was intentionally not run; preserve this
  limitation and do not infer 70K component contributions from the primary run.
- AURA V2 completed three 3x3 seeds on heart5 and Mendeley. The 70K V2 3x3
  attempt timed out after 35 minutes without a valid artifact; do not report it
  as completed or replace it silently with V1's 2x2 run.
- V2 report, design, registry, and solver diagnostic are under
  `results/aura_ml_v2/` and `docs/AURA_ML_V2_DESIGN.md`.
- The checkpointed 70K feasibility artifact completed at
  `results/aura_ml_v2/70k_feasibility_3x3.json`. It is exploratory because
  baselines were frozen rather than inner-retuned; retain that caveat.
- The literature investigation is complete and literature-only. The 34-record
  registry and ten requested documents are under `docs/`; no new algorithm was
  implemented and no existing experiment/result was overwritten.
- The current recommendation is SAGE-Transfer: guarded semantic schema/unit/
  endpoint alignment plus reliability-aware cross-dataset transfer, preceded by
  a MetaRisk Router leave-dataset-out benchmark. Do not implement it until
  compatible multi-cohort data and a frozen transfer protocol are available.
- The local model portfolio has been exhausted through existing verified
  artifacts. See `docs/LOCAL_MODEL_EXHAUSTIVE_EVALUATION.md` and
  `results/local_model_inventory.json`. Do not claim TabPFN/TabICL/TabDPT or
  other unavailable models were run; their packages are absent.
- The local-model baseline is frozen as
  `LOCAL_MODEL_BASELINE_2026-11-03_V1` in
  `results/local_model_baseline_freeze.json`; do not overwrite its listed
  artifacts or compare across their different protocols as if they were one
  benchmark.
- The cross-dataset protocol is
  `docs/CROSS_DATASET_EVALUATION_PROTOCOL.md`; its feasibility report is
  `docs/SAGE_TRANSFER_FEASIBILITY_REPORT.md` and machine-readable status is
  `results/cross_dataset_feasibility.json`. Current status is
  `PROTOCOL_FEASIBLE_EMPIRICAL_RUN_BLOCKED`: no approved common endpoint/map or
  independent compatible target cohort exists. Do not run direct cross-dataset
  prediction or implement SAGE-Transfer until those gates pass.
- CLIN-ADAPT v0.1 is a separate provisional framework under `src/clin_adapt/`,
  with artifacts in `results/clin_adapt/` and ten required documents in
  `docs/clin_adapt/`. It has 20 executable local candidates and 15 unavailable
  records. Heart5 and Mendeley full portfolios completed 3x2 nested runs; 70K
  completed a six-model resource-bounded priority run. CASL is an engineering
  validation coordinator, not an established novel algorithm.
- CLIN-ADAPT did not run cross-dataset prediction. Existing local semantic and
  endpoint gates remain binding; do not interpret its within-dataset metrics as
  SAGE-Transfer or external-validation evidence.
- The 2026-11-04 CLIN-ADAPT QA snapshot reported 57 tests; the current complete
  suite reports 62. Runtime resources are recorded in
  `results/clin_adapt/runtime_resources.json`.
- Review the canonical audit, provenance, leakage, novelty, QA, and completion
  documents added in this finalization pass.
- If publication packaging continues, confirm provisional author metadata and
  remaining ethics, funding, contribution, competing-interest, and data-use
  statements; choose a venue and perform venue-specific formatting/proofing.
  The latest draft and manifest are at
  `output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf` and
  `paper/build/research_draft_20261105_remediation/`.
- Obtain and freeze an independent compatible cohort only if a responsible
  human reviewer approves its provenance, licensing, feature mapping, endpoint,
  and overlap status.
- Do not stage or push until the intentional-file list has been reviewed.
