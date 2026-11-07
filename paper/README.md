# Manuscript package

`manuscript.tex` is an editable IEEE-style research draft based on the
verified local evidence. It distinguishes the historical notebook path from
the corrected nested evaluation and includes the Z-Alizadeh Sani stress test
(`CD-XD-003`), AngioCAD evaluation and post-hoc reliability replay
(`CD-XD-004`/`CD-XD-006`), and the Duke ACATH endpoint-mismatched stress test
(`CD-XD-005`). It reports the low automatic coverage, weak feature-only OOD
separation, and limits of the fail-closed metadata gate.

## Build and visual verification

The current research draft was rebuilt with Tectonic 0.17.0 after adding the
provisionally supplied author names and explicit pending publication
declarations. Its PDF is
`../output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`. Source,
audit-input, table/figure, compiler, page-render, text-extraction, and PDF
hashes are recorded in
`build/research_draft_20261105_remediation/publication_manifest.json`. Page
extraction, reference checks, and visual inspection are recorded in
`../docs/QA_REPORT.md`.
This is a reviewed draft, not venue-specific proofing; the selected journal's
current instructions must be applied after the project team chooses it.

To make a new build from this directory, use a new output directory so the
saved build remains intact:

```powershell
$buildName = "domain_shift_20261105_rerun"
New-Item -ItemType Directory -Force "tmp/pdfs/$buildName" | Out-Null
tectonic -k --keep-logs -o "tmp/pdfs/$buildName" manuscript.tex
New-Item -ItemType Directory -Force ..\output\pdf | Out-Null
Copy-Item "tmp/pdfs/$buildName/manuscript.pdf" "../output/pdf/$buildName.pdf"
```

After compiling, render the PDF pages and inspect the full-page output as well
as a contact sheet. The IEEE-style template still needs review against the
selected journal or conference's official author instructions.

## Current manuscript status

The current PDF includes CD-XD-003 through CD-XD-006 and the 2026-11-05
validity sensitivity analyses. The 270-row UCI Statlog release was excluded
after all its records matched Cleveland exactly. The endpoint-aligned AngioCAD
replay is post-hoc; Duke uses a different endpoint. A follow-up public-data
search found no additional accessible endpoint-compatible tabular cohort;
CARDIIGAN reports no shareable patient-level data, and the 2026 APPROACH
multi-site protocol keeps records in secure institutional environments.
Author names and a shared affiliation are provisionally supplied. Author
order/individual affiliations, coauthor contributions, ethics/data-use,
funding, competing interests, license review, and venue-specific proofing
remain pending.

## Figures and tables

The manuscript uses nine generated figures in
`figures/master_directive_20261105_final/`. That directory contains PNG preview
files and vector PDF files; `figure_manifest.json` records input and output
SHA-256 hashes and the internal-only interpretation boundaries. The earlier
`master_directive_20261105/` and `_v2/` directories are retained figure-layout
iterations; the manuscript references only the `_final/` directory.
Machine-readable tables are in `tables/` and are sourced from the stored
result artifacts:

- `tables/nested_summary.tex` — five candidate summaries from 3x3 internal
  validation.
- `tables/stability_evidence.tex` — repeated feature-selection stability.
- `tables/uncertainty_evidence.tex` — repeated selective-reliability summary.
- `tables/stability_reliability_linkage.tex` — paired stability/reliability
  analysis.
- `tables/domain_guard_transfer.tex` — source-only AngioCAD and Duke transfer,
  calibration, conformal, abstention, and OOD summary.
- `tables/validity_sensitivity_mendeley.tex` and
  `tables/validity_sensitivity_angiocad.tex` — predictor-timing and FBS-unit
  sensitivities, with their limits stated in the manuscript.

The primary nested table reports fold means. The ROC and precision-recall
figure legend scores use pooled outer-fold predictions and are not the same
aggregation. Distribution-shift plots are label-free covariate diagnostics,
not predictive transfer. AURA-ML ablations and synthetic perturbation tests
are exploratory.

## Remaining project-team work

Confirm author order and individual affiliations with all authors; finalize
ethics/data-use, funding, competing-interest, and contribution statements;
review redistribution rights for the composite and 70K datasets; and select a
target venue for venue-specific reporting and format checks. Do not add claims
of clinical utility, fairness, novelty, external validation, or deployment
readiness without new supporting evidence.

- `tables/uncertainty_evidence_conformal_corrected.tex` and `tables/stability_reliability_linkage_conformal_corrected.tex` — versioned reliability tables rebuilt from the corrected conformal-quantile ten-seed reruns; weighted ECE is shown alongside the legacy macro-bin ECE. See `tables/conformal_corrected_table_manifest_20261107.json`.


## 2026-11-07 finalization deliverables

The corrected manuscript source builds to `../output/pdf/CARDIODIAG_Final_Consolidated_20261107.pdf`. The 16-page build was rendered and inspected; provenance and QA are in `build/finalization_20261107/publication_manifest.json`. The complete refreshed nine-figure pack and four new diagnostic figures are under `figures/finalization_20261107/`. Corrected source-side and transfer runs are under `../results/finalization_20261107/`; the manuscript tables include corrected conformal coverage and both macro-bin and sample-weighted ECE.
