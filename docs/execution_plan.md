# CARDIODIAG minimal-intervention execution plan

**Objective:** complete the project in small, automatically checked stages while
keeping the original notebooks untouched and preventing premature scientific
claims.

## Operating rules

1. Every stage writes machine-readable artifacts under `results/generated/`.
2. Every artifact includes dataset hash, target, seed, split protocol, code
   variant, and sample counts.
3. No stage may read labels from an external dataset unless the external
   manifest is frozen and the command is explicitly an evaluation command.
4. A failed gate stops later stages; it does not get bypassed by editing a
   result file or changing a test.
5. The manuscript is generated only from result files. It will contain
   `[RESULT PENDING]` placeholders until the evidence gates pass.
6. Historical notebooks remain archival evidence. New code lives under
   `src/`, `experiments/`, `tests/`, `docs/`, and `results/`.

## Automated stages

### Stage 0 — Environment and source freeze

**Command:** `uv lock --check`, Ruff, tests, dataset audit.  
**Artifact:** environment lock, dataset manifest, test report.  
**Gate:** all checks pass and the local data hashes match the manifest.

### Stage 1 — Historical reproduction

**Command:** protocol-comparison runner.  
**Artifact:** `results/generated/heart5_protocol_comparison.json`.  
**Gate:** historical behavior and deviations are recorded; historical metrics
are not mixed with corrected metrics.

### Stage 2 — Nested internal validation

**Command:** nested/repeated validation runner.  
**Artifact:** one JSON file per dataset plus a summary CSV/Markdown table.  
**Gate:** all transformations are inside the fitted pipeline, hyperparameters
are selected only in inner folds, and no candidate is declared superior from a
single split.

### Stage 3 — Ablations and reliability

**Command:** ablation runner using the same outer splits.  
**Artifact:** ablation table, bootstrap intervals, calibration summaries,
feature-selection stability summaries, and conformal risk/coverage results.  
**Gate:** the proposed method must show a prespecified benefit in at least one
reliability/generalization dimension without unacceptable deterioration in the
others. Otherwise revise the claim to a negative or inconclusive result.

### Stage 4 — External dataset freeze

**Human gate:** choose a compatible, genuinely independent dataset and verify
provenance, overlap, license, target definition, and feature mapping.  
**Artifact:** completed `data/manifests/external_dataset.json`.  
**Status:** completed for the one-site AngioCAD primary evaluation. A fresh
follow-up search found CARDIIGAN data are unavailable and a new five-site
APPROACH/Ottawa/UHN protocol is access-restricted. No untouched multi-site
cohort is available to freeze. The approved manifest is at
`data/manifests/angiocad_external.json`; AngioCAD labels have since been
examined, so it cannot serve as a fresh confirmatory target.

### Stage 5 — One-way external evaluation

**Command:** external evaluation runner in read-only model mode.  
**Artifact:** external-validation report with all metrics, uncertainty,
missing-feature decisions, and negative results.  
**Status:** completed for CD-XD-004 AngioCAD with a frozen source-only model,
saved predictions, exact rerun, and independent scoring. The same target's
CD-XD-006 policy replay is explicitly post hoc; it does not restore
confirmation. Further runs require a newly accessible compatible cohort.

### Stage 6 — Manuscript and demonstration

**Command:** result-to-table/figure generator and LaTeX build.  
**Artifact:** IEEE-editable manuscript, BibTeX, figures, tables, and a
non-clinical demonstration.  
**Status:** complete as a checked engineering research draft. The 14-page PDF
build, source hashes, tables, figures, and demo are present. Provisional author
metadata is now inserted; factual ethics/data-use, funding, coauthor
contributions, conflicts, venue choice, and venue-specific format review remain.

## Minimal human intervention points

Only these decisions should require user input:

1. Confirm author order and each author's affiliation and contributions.
2. Obtain an institutional ethics/data-use determination and confirm funding
   and competing-interest declarations.
3. Select a target journal and review its current author instructions.
4. Obtain a new compatible multi-site dataset through an authorized investigator
   or data-sharing agreement if confirmatory generalization evidence is required.

Everything else should be repeatable from the repository commands.

## Current state

- Stages 0–3: complete for the supplied development datasets, including
  reliability and conformal/selective analysis.
- Stages 4–6: completed to the extent allowed by currently accessible data;
  AngioCAD provides a one-site evaluation, while new multi-site confirmation
  and factual publication inputs remain external dependencies.
