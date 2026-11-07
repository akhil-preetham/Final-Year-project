# CARDIODIAG quality assurance report

**Run date:** 2026-11-05
**Scope:** Local software, saved experiment artifacts, generated figures, and
the manuscript PDF. These checks do not establish clinical validity or
independent external generalization.

The table records the latest local check run. Historical addenda below retain
the test counts and manuscript builds that applied to those earlier stages.

## Current run

| Check | Command or evidence | Result |
|---|---|---|
| Unit and integration tests | `uv run --locked python -m pytest -q` | PASS — all 106 collected tests; includes AngioCAD compatibility and feature-ablation audits plus schema, data adapter, selective-set, support-gate, unknown-site, readiness-gate, seed-summary, source-lineage, Mendeley source/codebook, external-overlap, and validity-sensitivity checks |
| Test console wrapper | `uv run pytest -q` | ENVIRONMENT ISSUE — `uv` still fails before collection with “trampoline failed to canonicalize script path”; Python-module invocation above passes |
| Lint | `uv run --locked ruff check .` | PASS — full repository |
| Python compilation | `uv run --locked python -m compileall -q src experiments tests` | PASS |
| Dependency lock | `uv lock --check` | PASS — 54 packages resolved |
| Package imports and config | `import cardiodiag, clin_adapt`; parse `pyproject.toml` and local dataset manifest | PASS — 3 datasets |
| Domain-gate demos | `uv run python demo/run_domain_guard_demo.py` with both final model bundles | PASS — accepted registered case; uncertainty, out-of-support, and unknown-site abstentions; probabilities withheld on all abstentions |
| JSON parsing and finite numeric constants | Repository scan excluding environment and distribution folders | PASS — 261 JSON files, 0 parse failures or non-finite constants |
| Notebook structure | JSON parse and `cells`-list check | PASS — 39 notebooks |
| Dataset identity | SHA-256 recomputation against `data/manifests/local_datasets.json` | PASS — all 3 datasets matched |
| Fresh nested predictions | `results/master_directive_20261105_serial/internal_stage_manifest.json` and both dataset artifacts | PASS — complete 3x3, seed 42; five candidates per dataset; predictions cover all 918 and 1,000 rows |
| Five-seed sensitivity audit | `uv run python experiments/summarize_internal_seed_sensitivity.py` | PASS — seeds 43–47 audited on both datasets; common source and lock hashes, exactly-once outer-row coverage, and pooled metrics recomputed within `1e-10`; seed 42 excluded for provenance mismatch |
| Heart5-to-UCI lineage audit | `uv run python experiments/audit_heart5_uci_lineage.py` | PASS — all 918 Heart5 rows match observed UCI source fields and labels; 914 unique source-row matches, 4 ambiguous due to source missingness, 0 unmatched; source imputation history remains unresolved |
| 2021 Mendeley source/codebook audit | `uv run python experiments/audit_mendeley_2021_source.py --download` | PASS — official API CSV and codebook hashes match; 1,000 rows and target counts verified; codebook defines presence/absence but not the diagnostic reference standard or angiographic threshold |
| New Mendeley cohort screen | `uv run python experiments/audit_mendeley_heart_2026_overlap.py --download` | PASS — downloaded file hash matches Mendeley API; all 918 labeled rows exactly duplicate Heart5, so excluded from external validation |
| Release data and attribution audit | `uv run python experiments/audit_distribution_data.py` | PASS — six ZIPs scanned; no byte-identical Heart5 or Kaggle 70K raw file; every package containing the 1,000-row Mendeley CSV includes source, DOI, and CC BY 4.0 attribution. Derived 70K result files remain in four historical packages, and the scan does not settle their rights. |
| Result parity | Fresh stage compared with `results/final_completion_20261105/` | PASS — all candidate fold-mean metrics match; maximum absolute delta 0 |
| Figure generation | `paper/figures/master_directive_20261105_final/figure_manifest.json` | PASS — 18 PNG/PDF outputs and SHA-256 checks |
| Transfer artifact audit | `uv run python experiments/audit_domain_guard_artifacts.py` | PASS — all input/code/output hashes match; AUC, average precision, Brier, log loss, and ECE independently recomputed from both target CSVs; unknown-site deployment scores absent |
| Validity sensitivity audit | `uv run python experiments/audit_validity_sensitivities.py --angiocad-dir results\validity_audit_20261105\angiocad_without_fbs_final` | PASS — verifies shared Mendeley splits, labels, row coverage, source partitions, AngioCAD IDs/labels, and independently recomputes sensitivity metrics from saved predictions |
| Statlog overlap audit | `uv run python experiments/audit_statlog_overlap.py` | PASS — 270/270 records exactly match Cleveland after binary-target harmonization; excluded from independent testing |
| Real-world readiness gate | `uv run python experiments/evaluate_readiness.py` | PASS — 13-gate ledger valid; 53 evidence references across 42 files hashed with no missing or mismatched hashes; decision NO-GO because external, clinical, governance, and regulatory gates remain open |
| LaTeX build | Tectonic 0.17.0, manifest at `paper/build/research_draft_20261105_remediation/publication_manifest.json` | PASS — final 14-page research draft; manuscript, bibliography, included tables/figures, key audit manifests, compiler archive, page renders, contact sheet, and output hashes recorded |
| PDF structure and text | Poppler `pdfinfo`; `pypdf` extraction | PASS — 14/14 pages contain extractable text; includes new provenance and policy audits, explicit research NO-GO, provisional author names, and pending declarations |
| PDF render review | Poppler, 110 dpi; `paper/build/research_draft_20261105_remediation/render/contact_sheet.png` plus full-page images | PASS — all 14 pages reviewed in the contact sheet; pages 4, 5, 13, and 14 inspected full-page |
| LaTeX references and layout | Tectonic `.log` and BibTeX `.blg` | PASS — no unresolved citations/references, missing graphics, BibTeX errors, or overfull boxes; font fallback, underfull boxes, and missing default Fontconfig configuration remain |
| Manuscript publication facts | User-supplied metadata and manuscript declaration block | PASS with pending inputs — provisional names/shared affiliation are present; ethics, funding, Ch Hari Krishna and G Vennela contributions, competing interests, author order/individual affiliations, data-use facts, and journal remain explicitly unconfirmed |
| Follow-up public data search | `docs/REMAINING_WORK_REGISTER_20261105.md`; access pathway review | PASS — identified access leads, but no additional publicly downloadable endpoint-compatible tabular cohort; no external party was contacted or restricted data acquired |
| Git whitespace | `git diff --check` plus trailing-space scan of current QA/handoff/matrix/index files | PASS — no whitespace errors in the diff or scoped current-status files |

The AngioCAD workbook tests cause openpyxl to warn that it ignores
conditional-formatting extensions while reading the source workbooks. The
workbooks are never written back; matched rows, labels, and feature values are
checked against the frozen schema.

## Interpretation

The test, lint, compilation, data-hash, experiment-parity, figure, and PDF
checks support the integrity and repeatability of the local research package.
The nested results are internal development/replication evidence. They do not
resolve dataset source overlap, patient linkage, licensing, external transport,
prospective performance, calibration under shift, clinical utility, or
fairness.

The current manuscript draft is not submission-ready. Author names and a
shared affiliation are provisional; ethics and funding are not determined,
contributions from two coauthors and competing interests are pending, no
target journal has been selected, and data redistribution terms remain
dataset-specific. The updated register records the person or access input that
would resolve each open item.

The separate real-world readiness ledger reports `NO_GO`; that ledger concerns
future clinical/real-world use and is not a completion gate for the offline
engineering project. The project's `GO` is for a reproducible research
prototype and its demonstrations. It does not mean the predictive objective
of dependable unseen-site performance succeeded.

The CD-IV-001 five-seed results describe split sensitivity only. They are not
patient-level uncertainty intervals, and the repeated runs are exploratory
because seed-42 results had already been inspected. Mendeley discrimination is
high in these internal splits, but calibration varies across seeds; this does
not establish transportable calibration or clinical performance. The full
candidate-level table and row-level audit are in
`results/internal_seed_sensitivity_20261105/seed_repeat_summary.md` and
`seed_repeat_summary.json`.

The fresh run is a separate, namespaced artifact stage. It matches the prior
authoritative fold means while adding prediction vectors, split indices,
runtime details, source/lock hashes, platform, hardware, and package versions.
The earlier interrupted run in `results/master_directive_20261105/` remains
preserved and must not be interpreted as complete.

## Transfer pilot artifact audit (2026-11-05)

The `CD-XD-002` runner completed both prespecified zero-value policies across
four outer held-out cohorts. The run manifest's archive, protocol, and runner
hashes match the files on disk. ROC-AUC and calibrated Brier scores recomputed
from all eight sets of saved row predictions match the recorded fold metrics.
The initial execution emitted a warning for balanced accuracy on accepted
subsets containing only one outcome class; the corrected runner marks
class-dependent metrics undefined for such subsets. Its probabilities, OOD
scores, thresholds, and flags matched the initial execution exactly. This was
an implementation correction, not a model or threshold selection change.

After the runner cleanup, a fresh namespaced run reproduced the prior fold
metrics and prediction CSV byte-for-byte. The run manifest hashes the runner,
archive, and frozen protocol. The final 64-test suite, Ruff, and compilation
checks were rerun; the study remains retrospective because its UCI cohorts
overlap the historical Heart5 composite.

## Earlier PDF build notes (superseded)

The earlier manuscript build included CD-XD-003 through CD-XD-006, the Statlog
duplicate-data finding, and the abstention behavior. It was 12 pages. It is
superseded by the 13-page validity-audit build and then by the latest 14-page
remediation build documented in the current-run table above.

The previous PDF is `output/pdf/CARDIODIAG_Validity_Audit_20261105.pdf`; its
manifest is `paper/build/validity_audit_20261105/publication_manifest.json`.
It is preserved as a historical build and superseded by
`output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`. The current
draft uses provisional author names and affiliation; factual ethics, funding,
contribution, data-use, and venue statements still require project-team review.

## Source-tree state

The canonical checkout began with a large dirty/untracked source and result
tree. The original notebooks, datasets, generated result artifacts, and four
original RAR archives were preserved; the archives were restored from the
checked-out source commit. No commit or push was made. Review the full
`git status --short --untracked-files=all` before staging or publishing any
allow-listed files. The configured remote is the original source project, not
a publication destination.

## Research addendum: CD-XD-003

The source-distinct transfer runner was rerun into a separate validation
folder after adding hashes for both the entrypoint and its shared helper. The
303-row external prediction CSV and 185-row source calibration CSV match the
prior run byte-for-byte; run inputs, protocol, and both local code hashes match
the current files. Independent scoring in the saved audit matches ROC-AUC,
average precision, Brier score, log loss, and ECE. The paired calibration
analysis and transfer figure were generated from saved predictions, and the
figure was visually inspected. The current manuscript PDF includes this
stress test.

## Research addendum: CD-XD-004

The endpoint-aligned AngioCAD runner completed in the primary, reproduction,
and fresh validation folders after the final protocol and data-manifest hashes
were frozen. Both prediction CSVs match byte-for-byte across the three runs;
input, protocol, entrypoint, and shared-helper hashes match current files.
Independent recalculation of the raw and calibrated AUC, average precision,
Brier score, log loss, and ECE matches to below `1e-12` maximum absolute
difference. Two tests now cover the matched cohort schema and derived target.
The full 64-test suite and repository Ruff check pass, the transfer figure was
visually inspected, and the updated 11-page manuscript PDF was rebuilt and
reviewed. These checks do not establish robust calibration, reliable OOD
rejection, multi-hospital validity, or clinical use.

See `TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md` for study interpretation,
metrics, and limitations. These reproducibility checks verify the stored
research outputs; they do not establish clinical validity or between-site
transportability.

## Final hardening addendum (2026-11-05)

- Updated the serialized domain guard so every abstention withholds its
  probability, and out-of-support inputs also withhold the conformal set.
  Added a test for non-singleton conformal abstention and assertions for
  out-of-support suppression.
- Re-ran CD-XD-005 and CD-XD-006 after the code change. Their target prediction
  CSVs are byte-identical to the preserved pre-hardening runs, and the saved
  metric JSON objects are equal; current manifests hash the updated code.
- The independent transfer audit passes all recorded input, code, and output
  SHA-256 checks and recomputes AUC, average precision, Brier, log loss, and
  10-bin ECE from both target prediction CSVs to within `1e-12`.
- The independent Statlog audit confirms 270/270 exact row matches to
  Cleveland and excludes the duplicate file from external testing.
- Both model bundles passed the expanded synthetic demonstration: an accepted
  in-domain record, an in-domain uncertain record, an out-of-support record,
  and an unknown site. Abstentions expose no probability.
- At this checkpoint, the suite passed 82 collected cases, including six readiness-gate
  tests. Ruff, compilation, dependency-lock, artifact audits, demos, and the
  final PDF checks pass.
- The new 13-phase readiness ledger currently passes G0 only. The evaluator
  reports NO-GO; it checks recorded paths and statuses, not the underlying
  clinical, statistical, ethics, security, or regulatory judgments.

These checks verify the local prototype and its evidence trail only. The
AngioCAD replay remains post-hoc, Duke has a different endpoint, feature-only
OOD separation is weak, and no untouched endpoint-compatible external cohort
was verified.

The project owner described the final-year project as research-based, with
possible future clinical use. The current scope is therefore recorded as
offline research only; no patient-care use is authorized. G1 is partial because
the future clinical population, workflow, decision, jurisdiction, and clinical
owner remain unspecified. See `INTENDED_USE_SCOPE.md`.

## CD-XD-003 reproduction check (2026-11-05)

The canonical UCI archive was re-evaluated into
`results/transfer_20261105_zas_completion_check/`. Its external and source
calibration prediction CSVs are byte-identical to the prior validation rerun.
Source/target archive, protocol, and code hashes match, and raw/calibrated
metrics, bootstrap intervals, and OOD summaries reproduce exactly. This
confirms analysis reproducibility for CD-XD-003; it does not resolve the
`>=50%` versus `>50%` label boundary or prove person-level non-overlap.
