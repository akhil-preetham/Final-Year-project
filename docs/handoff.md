# CARDIODIAG handoff

**Checkpoint:** 2026-11-05

**Status:** `GO` for the offline final-year research prototype and demonstration. Clinical/real-world readiness remains `NO_GO`; the measured transfer and OOD results do not establish dependable generalization.

This is the current handoff. The active research focus is generalization-aware cardiovascular prediction under dataset shift, with source-only calibration and out-of-distribution (OOD) warnings. The work is a research prototype, not a clinically validated diagnostic system.

## Current intended use and readiness

The project owner described the final-year project as research-based, with
possible future clinical use. The current intended-use boundary is offline
research only; future clinical use remains unspecified and unapproved. The
machine-readable readiness decision is `NO_GO` (1 of 13 phases passed; G1 is
partial). See `docs/INTENDED_USE_SCOPE.md` and
`docs/REAL_WORLD_READINESS_WORKFLOW.md`.

## Evidence by study

- **CD-XD-002 — retrospective leave-one-source-out pilot.** Each of four UCI cohorts was held out while the other three were used for fitting. Macro ROC-AUC was 0.760; OOD AUROC averaged 0.758 but ranged from 0.515 to 0.980. These cohorts already appear in the project's historical Heart5 composite, so this is not independent project-level external validation.
- **CD-XD-003 — Z-Alizadeh Sani transport stress test.** The 303-row source-distinct cohort uses a `>=50%` endpoint while the source uses `>50%`. ROC-AUC was 0.720 and OOD AUROC was 0.604. Calibration changes were inconclusive; this is not endpoint-identical validation.
- **CD-XD-004 — endpoint-aligned AngioCAD evaluation.** The study used 377 matched records from a distinct hospital. ROC-AUC was 0.787 (95% class-stratified bootstrap interval 0.734–0.838); calibration remained poor and OOD AUROC was 0.589. The result supports the evaluation workflow, not dependable shift detection or broad transportability.
- **CD-XD-005 — Duke ACATH transport stress test.** A new public 3,504-row cohort was sourced and hashed. Its endpoint is >=75% stenosis rather than the UCI source's >50%. With age, sex, and cholesterol, ROC-AUC was 0.661; source Platt calibration worsened Brier from 0.216 to 0.241. Feature OOD AUROC was 0.556 for kNN and 0.598 for Isolation Forest. The inference boundary abstained on all records because Duke is unregistered.
- **CD-XD-006 — endpoint-aligned AngioCAD policy replay.** The source-only pipeline was rebuilt with separate 70% fit, 15% Platt, and 15% conformal/OOD partitions, then scored on the previously examined AngioCAD target. ROC-AUC was 0.790; Brier changed 0.189 to 0.174 and ECE 0.211 to 0.192. Empirical set coverage was 100%, but only 8.8% had singleton sets; the combined rule accepted 21/377 (5.6%) with zero observed errors. The unknown-site gate returned no probability for all 377. This is exploratory and not a fresh final holdout.

The UCI Statlog (Heart) release was also screened as a possible additional cohort. An exact comparison found that all 270 records duplicate Cleveland after harmonizing the binary outcome, so it contributes no unseen patients and is excluded. The reproducible comparison and archive hash are in `data/external/uci_statlog_heart/overlap_audit.json`.

A 2026 Mendeley release advertised as a 918-patient clinical heart dataset was
downloaded under its CC BY 4.0 record and verified against the repository's
Heart5 table. The Mendeley API SHA-256 matched, and all 918 rows matched the
full 12-column Heart5 multiset exactly. It is excluded as a duplicate, not
counted as external evidence. The UCI source-lineage audit separately maps all
918 Heart5 rows to UCI records (914 unique, four ambiguous due to source
missingness). Reports and row maps are indexed in `results/RESULT_INDEX.md`.

The original 2021 Mendeley dataset is licensed CC BY 4.0, and its CSV and
official codebook hashes now match the public API. The codebook defines the
target as absence/presence of heart disease but omits the diagnostic reference
standard, so this dataset remains a development benchmark and is not pooled
with the angiographic endpoint. The six current ZIPs contain no byte-identical
Heart5 or Kaggle 70K raw CSV; four historical packages do contain 70K-derived
result files, whose rights are not established.

The feature-only OOD detectors remain weak, and abstention utility is low. The working method therefore fails closed using trusted source-domain metadata and exposes probabilities only for registered domains when the conformal set is singleton and the support score is within threshold. This is an operational boundary, not evidence of dependable feature-based site detection.

## Current verification

The latest CD-XD-003 reproduction under
`results/transfer_20261105_zas_completion_check/` produced byte-identical
external and source-calibration predictions against the prior validation
rerun. Data, protocol, and code hashes match, as do the metric, bootstrap, and
OOD summaries.

The CD-IV-001 internal sensitivity analysis completed seeds 43–47 across both
development datasets. All five manifests share the same source-bundle and
dependency-lock hashes; every outer row is covered once, and the summary
recomputes pooled metrics within `1e-10`. The full summary is at
`results/internal_seed_sensitivity_20261105/seed_repeat_summary.md`.

- The complete automated suite passes, including direct AngioCAD schema/label checks, finite-sample conformal quantiles, disjoint calibration partitions, and known/unknown domain-gate behavior.
- Ruff, Python compilation, dependency-lock, JSON/notebook, local dataset-hash, and demo checks pass.
- `uv run python experiments/audit_domain_guard_artifacts.py` independently recomputes AUC, average precision, Brier, log loss, and 10-bin ECE for both target cohorts; it verifies all recorded input, code, and output hashes and checks that unknown-site rows receive no deployment probability.
- The non-clinical demos exercise an accepted registered synthetic case, an in-domain uncertain case, an out-of-support case, and an unknown site. Every abstention withholds the probability; out-of-support cases also hide the conformal set. Each demo saves results plus a hash manifest beside its model bundle.
- The current manuscript PDF is `output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`, with page count, text extraction, visual review, and source/compiler/output hashes recorded in `docs/QA_REPORT.md` and `paper/build/research_draft_20261105_remediation/publication_manifest.json`. It includes the predictor-timing, AngioCAD matching/unit, feature-ablation, and selective-policy audits and explicitly marks unresolved publication declarations.
- The Tectonic build reports font fallback, underfull boxes, and a missing default Fontconfig configuration. No clipping, overlap, unresolved reference, missing figure, or overfull box was found. The PDF is a verified draft, not venue-specific proofing.
- See `docs/QA_REPORT.md` for commands and check details. Run the test suite with `uv run python -m pytest -q`.

## Limits and remaining work

- AngioCAD's public feature workbook has rows for 377 of 413 labeled IDs. The workbook omits age and fasting-blood-sugar units; the conservative post-hoc subset excludes FBS but retains an unverified age-as-years assumption. Public identifiers do not support cross-dataset patient-level duplicate checks.
- The validity audit confirms that excluding Mendeley's fluoroscopy-derived major-vessel field does not explain its high internal AUC, but its label reference standard and other predictor timing remain undocumented. An age/sex-only AngioCAD sensitivity gives a similar AUC, but is post hoc and cannot resolve the FBS unit.
- The AngioCAD result is from one angiography-referred site with a high positive fraction. It does not establish performance across hospitals, care settings, or population screening.
- The AngioCAD replay uses a target already examined in CD-XD-004; the fresh Duke cohort has a different disease threshold. Statlog duplicates Cleveland. No untouched, endpoint-compatible target remains available in the screened public datasets.
- Source-only calibration and feature-only OOD detection are inconsistent under shift. The domain registry blocks unseen cohorts by metadata; an unflagged feature-space score must not be treated as proof of reliability.
- Prospective validation, clinical utility, fairness, safety, and treatment impact are not established.
- Exact original-paper reproduction and the full matched factorial ablation remain incomplete. The upstream licensing of the composite Heart5 and 70K data remains unresolved.
- The manuscript includes provisionally supplied author names and one shared affiliation. Confirm author order and individual affiliations; obtain factual ethics/data-use, funding, competing-interest, and all coauthor contribution statements; select a venue and apply its formatting requirements.
- The project is complete as a bounded engineering demonstration; it does not establish dependable unseen-site prediction. The exact limits, evidence, and best resolution paths are in `docs/VALIDITY_AUDIT_20261105.md`.
- The checkout remains dirty and uncommitted. Review `git status --short --untracked-files=all` before staging or publishing.

## Key artifacts

- Primary study reports: `docs/TRANSFER_STUDY_RESULTS_20261105.md`, `docs/TRANSFER_STUDY_RESULTS_20261105_ZAS.md`, and `docs/TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.
- Protocols and data manifests: `docs/TRANSFER_STUDY_PROTOCOL_20261105*.md` and `data/manifests/`.
- Fresh validation outputs: `results/transfer_20261105_lodo_validation_rerun/`, `results/transfer_20261105_zas_validation_rerun/`, and `results/transfer_20261105_angiocad_validation_rerun/`.
- New source-domain bundles and outputs: `results/transfer_20261105_angiocad_domain_guard/` and `results/transfer_20261105_duke_acath_final/`.
- Runtime gate: `src/cardiodiag/domain_guard.py`; experiments: `experiments/run_aligned_angiocad_gate.py` and `experiments/run_duke_transfer.py`.
- Current manuscript: `paper/manuscript.tex`; checked research draft: `output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`; publication manifest: `paper/build/research_draft_20261105_remediation/publication_manifest.json`.
- Full status matrix and validation record: `docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md` and `docs/VALIDATION_CLOSEOUT_20261105.md`.
