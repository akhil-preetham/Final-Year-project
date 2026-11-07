# CARDIODIAG strict validation closeout

**Date:** 2026-11-05

**Scope:** Local code, frozen protocols, source and target data manifests, saved transfer results, demonstration, figures, and current manuscript build.

**Status:** Superseded by the validity-audit addendum below and the later
`MASTER_SCIENTIFIC_REMEDIATION_REPORT_20261105.md` closeout. The offline
engineering prototype and local validity checks are complete. Reliable
cross-site prediction is not established; clinical readiness is outside this
engineering project's completion scope, and paper submission inputs remain.

## What was verified and corrected

- The repository Ruff check initially found 40 style issues in the LODO runner and plotter. Both scripts were formatted, remaining findings were fixed, and the full Ruff command now passes.
- Added two automated AngioCAD checks for the matched-cohort schema, missingness, derived artery-label target, ordering, and class counts.
- Added hashes for every local Python runner/helper used by CD-XD-002, CD-XD-003, and CD-XD-004. Fresh run manifests verify those code hashes along with the frozen inputs and protocols.
- Reran all three transfer studies into separate validation folders, preserving the earlier primary and reproduction artifacts.
- Rebuilt the manuscript PDF from the current source, refreshed its publication manifest, rendered all pages, and reviewed the contact sheet plus pages 1, 6, and 11 at full size.

## Verification results

| Check | Result |
|---|---|
| Automated tests | 64 passed. Two new tests cover the AngioCAD adapter and endpoint derivation. |
| Ruff | `uv run ruff check src tests experiments` passed. |
| Python compilation | `uv run python -m compileall -q src experiments demo tests` passed. |
| Dependency lock | `uv lock --check` passed; 53 packages resolved. |
| Demo | `uv run python demo/run_demo.py` completed and returned an abstention-capable prediction and conformal set with a research-only warning. |
| Repository data structure | 212 JSON files parsed with finite numeric values; 39 notebooks parsed with `cells` lists; all three local dataset hashes matched their manifest. |
| Main figure set | All 18 PNG/PDF outputs matched the final figure manifest. |
| Manuscript PDF | Tectonic 0.17.0 built 11 pages; all 11 pages have extractable text. No unresolved citations/references, missing graphics, BibTeX warnings, or overfull boxes were found. The 30-source publication manifest includes source, protocol, result, figure, validation, and PDF hashes. |
| Visual review | No clipping, overlap, unreadable glyphs, or broken figures observed. Tectonic reports font fallback, underfull boxes, and a missing default Fontconfig configuration. |
| Whitespace | `git diff --check` passed. The checkout remains dirty and uncommitted. |

The two AngioCAD tests produce an openpyxl warning that it ignores conditional-formatting extensions while reading the workbooks. The workbooks are not written back, and the schema, matched records, missingness, and derived labels are checked.

The supported test invocation is `uv run python -m pytest -q` (64 passed). The optional console wrapper `uv run pytest -q` still fails in this host with `uv trampoline failed to canonicalize script path` before test collection.

## Transfer-study reproduction

- **CD-XD-002:** `results/transfer_20261105_lodo_validation_rerun/` has the same fold results and byte-identical prediction CSV as the primary run in `results/transfer_20261105_lodo_final/`. Its current runner, protocol, and archive hashes match disk.
- **CD-XD-003:** `results/transfer_20261105_zas_validation_rerun/` has byte-identical external and source-calibration prediction CSVs and matching study metrics. The fresh manifest's entrypoint and shared-helper hashes match disk.
- **CD-XD-004:** `results/transfer_20261105_angiocad_validation_rerun/` matches the primary and reproduction prediction CSVs byte-for-byte. Feature workbook, label workbook, source archive, target manifest, protocol, entrypoint, and helper hashes match disk. Independent recalculation of raw and calibrated ROC-AUC, average precision, Brier score, log loss, and ECE differs from the run manifest by at most `2.7755575615628914e-17`.

## What the research results establish

| Study | Result | Interpretation |
|---|---|---|
| CD-XD-002 | Four retrospective UCI cohort holds; macro ROC-AUC 0.760; OOD AUROC 0.758 with a 0.515–0.980 site range. | Pipeline feasibility evidence. The source cohorts are already represented in the historical Heart5 composite. |
| CD-XD-003 | 303-row source-distinct Z-Alizadeh Sani cohort; ROC-AUC 0.720 (95% interval 0.651–0.780); OOD AUROC 0.604 (0.552–0.652). | Transport stress test. Its `>=50%` target endpoint differs from the source `>50%` endpoint. |
| CD-XD-004 | 377 matched AngioCAD records; ROC-AUC 0.787 (95% interval 0.734–0.838); calibrated Brier 0.185, ECE 0.216, mean predicted risk 0.574 versus 0.790 observed prevalence; OOD AUROC 0.589 (0.541–0.635). | Endpoint-aligned evaluation at one distinct hospital. Calibration remains poor and the OOD warning is weak. |

CD-XD-004 flagged 44 of 377 cases (11.7%) and accepted 333 (88.3%). The calibrated Brier-score change and log-loss change versus raw predictions have bootstrap intervals containing no change; ECE worsened slightly by its point estimate. The study does not demonstrate dependable uncertainty calibration or recognition of inputs outside validated conditions.

The defensible novelty is the auditable, source-only evaluation of multi-source transfer, calibration, and OOD warning on a separate endpoint-aligned hospital cohort, including a clear negative reliability result. Logistic regression, Platt scaling, and Isolation Forest are established methods; no new prediction algorithm is established here.

## Limits requiring new evidence or project-team input

- One hospital and 377 matched records cannot estimate between-site variation. Thirty-six labeled AngioCAD IDs have no feature rows, public IDs do not establish cross-dataset person-level de-duplication, and the FBS unit is assumed from its range.
- The source-calibrated model remains miscalibrated on AngioCAD. The Isolation Forest OOD AUROC is close to chance. No reliable rejection behavior or clinical safety claim is established.
- No prospective or multi-hospital study, clinical-utility analysis, fairness evaluation, or treatment-impact study is present.
- A targeted screen for a second public cohort found candidate angiography resources that do not meet the frozen tabular cohort requirements. ADSD is an image-series dataset of 100 patients with confirmed one-vessel disease and a mixed anatomical/functional inclusion definition; ARCADE provides angiographic images and image-level task annotations. Neither supplies the matched case-control clinical fields and endpoint needed for another locked evaluation ([ADSD](https://doi.org/10.17632/ydrm75xywg.1), [ARCADE](https://zenodo.org/records/10390295)).
- Exact original-paper reproduction and the full matched factorial ablation remain incomplete. Licensing for redistribution of the Heart5 composite and 70K data remains unresolved.
- The manuscript's author/affiliation placeholder is visible. Factual ethics, funding, contribution, and data-use statements, author approval, and venue-specific formatting require the project team.

## Closeout decision

The local implementation, saved artifacts, reruns, and manuscript build now meet the documented software and reproducibility checks. The proposed research workflow is demonstrated. The results do not support a claim that the current model reliably calibrates cardiovascular risk or detects dataset shift. The full master directive remains incomplete, as recorded in `MASTER_DIRECTIVE_COMPLETION_MATRIX.md`; the project is not ready for clinical use or submission without the open evidence and metadata above.

## Final hardening addendum (2026-11-05)

This addendum supersedes the earlier test and manuscript counts in this dated
closeout.

- The inference gate now withholds the probability on every abstention and also
  withholds the conformal set for out-of-support rows. Tests cover registered
  in-support classification, non-singleton uncertainty, OOD abstention, and an
  unknown site.
- Both final transfer runs were repeated after the gate change. Their target
  prediction CSVs and study metrics match the preserved pre-hardening runs
  byte-for-byte / value-for-value; current run manifests include the updated
  code hash.
- `experiments/audit_domain_guard_artifacts.py` independently recalculates AUC,
  average precision, Brier score, log loss, and 10-bin ECE from both target CSVs
  and verifies every recorded input, code, and output hash. The unknown-site
  gate returns no deployment probability for any target row.
- `experiments/audit_statlog_overlap.py` confirms all 270 UCI Statlog records
  exactly match Cleveland after target harmonization. Statlog is excluded as
  duplicate patient data.
- The final suite passes 76 tests. Ruff, compilation, `uv lock --check`, both
  model-bundle demos, the saved-artifact audit, and the Statlog overlap audit
  pass. Demos show an accepted registered synthetic case, an uncertain case,
  an out-of-support case, and an unknown site; no abstention exposes a
  probability.
- The final manuscript is a 12-page PDF at
  `output/pdf/CARDIODIAG_Domain_Shift_Manuscript_20261105.pdf`, with its build
  record at `paper/build/domain_shift_20261105_final/publication_manifest.json`.
  All pages were rendered and reviewed; all have extractable text. There are
  no unresolved citations or references, missing graphics, BibTeX warnings, or
  overfull boxes. Font fallback, underfull boxes, and the missing default
  Fontconfig configuration remain non-blocking build warnings.

The research endpoint remains incomplete: AngioCAD was previously examined,
Duke uses a different stenosis threshold, Statlog is duplicate data, and no
untouched endpoint-compatible public cohort was verified. The prototype's
feature-only OOD detection is weak and automatic target coverage is low. This
closeout certifies local implementation and artifact integrity only, not
clinical validation or broad generalization.

See [`QA_REPORT.md`](QA_REPORT.md), the three transfer-study reports, and the current manuscript manifest for the command-level evidence.

## Validity-audit closeout (2026-11-05)

This is the latest state and supersedes the earlier test counts and PDF paths
above.

- The corrected evaluation path was inspected for target, identifier, and
  fold leakage. No direct leakage was found: target/ID columns are excluded and
  data transformations and selection stay within training folds.
- The new Mendeley nested sensitivity removed `noofmajorvessels` on the same
  saved splits. All five AUCs remained between 0.993 and 0.996. The field is
  potentially post-diagnostic, but it does not explain the high score. The
  dataset's diagnostic reference standard and timing of the other fields are
  still unknown.
- The AngioCAD age/sex-only sensitivity removed the undocumented FBS unit
  assumption. AUC remained similar (0.7868 with FBS, 0.7877 without), but
  calibration and OOD performance remain weak. Since AngioCAD
  labels were examined earlier, the sensitivity is explicitly post hoc.
- The endpoint-aligned external evaluation contains one site and 377 matched
  records. ROC-AUC is 0.787 (95% conditional interval 0.734–0.838), calibrated
  Brier is 0.185, ECE is 0.216, and feature-only OOD AUROC is 0.589. These
  results do not support dependable calibration or feature-only shift
  detection.
- The latest full suite passes 95 tests; Ruff, compilation, lockfile, and the
  independent validity-sensitivity audit pass. The current 13-page paper at
  `output/pdf/CARDIODIAG_Validity_Audit_20261105.pdf` has a SHA-256-checked
  publication manifest and was visually inspected.
- The strongest supported project outcome is a completed, reproducible
  engineering prototype demonstrating source-only transfer, uncertainty
  handling, and fail-closed rejection of unregistered sites. The empirical
  objective of dependable unseen-site prediction is not proven. The remaining
  resolution is new multi-site endpoint-compatible data, original source
  documentation or author confirmation for Mendeley/FBS details, and
  privacy-preserving overlap assessment. Retuning on the already inspected
  AngioCAD labels cannot replace those independent inputs.

Detailed threat evidence and resolution paths are in
[`VALIDITY_AUDIT_20261105.md`](VALIDITY_AUDIT_20261105.md); command-level checks
and the output manifest are linked from [`QA_REPORT.md`](QA_REPORT.md) and
`paper/build/validity_audit_20261105/publication_manifest.json`.

## Provisional metadata and follow-up access review (2026-11-05)

- The project owner supplied provisional author names and a shared
  institutional affiliation. The manuscript now lists Akhil Preetham E,
  Ch Hari Krishna, and G Vennela and marks order/individual affiliations as
  provisional. It records ethics as not determined, funding and competing
  interests as pending, Akhil's supplied contribution categories, and the two
  coauthors' contributions as pending. No approval, exemption, or funding
  statement has been invented.
- Rebuilt the IEEE-style draft with Tectonic 0.17.0 to
  `output/pdf/CARDIODIAG_Research_Draft_20261105.pdf` (13 pages). All pages
  have extractable text; the 110-dpi contact sheet was reviewed, and pages 1,
  12, and 13 were inspected full-page. No unresolved citation/reference,
  missing graphic, or overfull-box warning was found. Font fallback,
  underfull boxes, and the missing default Fontconfig configuration remain.
  Build inputs, output PDF, compiler, and contact sheet are hashed in
  `paper/build/research_draft_20261105/publication_manifest.json`.
- A fresh `pytest --collect-only` inventory found 94 tests, not the 95 stated
  in the earlier QA snapshot; the current full run passed all 94. The current
  QA table and limitation matrix correct the count. Ruff, compilation, and
  `uv lock --check` pass. Independent transfer, validity-sensitivity, and
  Statlog duplicate audits pass. The readiness evaluator remains `NO_GO` at
  1/13 phases; that clinical workflow is outside final-year prototype scope.
- The public-data/access search is recorded in
  `REMAINING_WORK_REGISTER_20261105.md`. It found no additional downloadable
  endpoint-compatible tabular cohort. CARDIIGAN does not share patient-level
  data; APPROACH/Ottawa/UHN data remain in secure institutional environments;
  CathAI is an image/video dataset with incompatible fields. No restricted data
  were acquired and no data owner was contacted.
- The current manuscript is a reviewed research draft, not submission-ready.
  Author confirmations, coauthor contributions, institutional ethics/data-use
  determination, funding and competing-interest facts, licensing review, and
  target-journal proofing remain open.
