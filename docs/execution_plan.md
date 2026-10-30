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
**Gate:** manifest is frozen before external labels are used for tuning,
calibration, threshold selection, or model choice.

### Stage 5 — One-way external evaluation

**Command:** external evaluation runner in read-only model mode.  
**Artifact:** external-validation report with all metrics, uncertainty,
missing-feature decisions, and negative results.  
**Gate:** the command cannot call `.fit` on the external data.

### Stage 6 — Manuscript and demonstration

**Command:** result-to-table/figure generator and LaTeX build.  
**Artifact:** IEEE-editable manuscript, BibTeX, figures, tables, and a
non-clinical demonstration.  
**Gate:** every reported number resolves to a stored result artifact; no
unsupported novelty, safety, fairness, or clinical-readiness claim remains.

## Minimal human intervention points

Only these decisions should require user input:

1. Approve or reject the final research claim after Stage 3.
2. Supply/approve an independent external dataset and its access conditions.
3. Select the target IEEE journal after the evidence is complete.
4. Supply author metadata and any required institutional/ethics statements.

Everything else should be repeatable from the repository commands.

## Current state

- Stages 0–3: complete for the supplied development datasets, including
  reliability and conformal/selective analysis.
- Stage 4: blocked until an independent compatible dataset is frozen.
- Stages 5–6: pending the external-data decision and final evidence review.
