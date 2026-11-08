# CARDIODIAG Research Extension

<!-- CURRENT_COMPLETION_STATUS_20261108 START -->
## Completion update (2026-11-08)

The frozen multi-dataset run remains preserved. A subsequent exact-row audit found Hungary rows 101/102 crossing development and outer-test in one frozen fold, plus one duplicate group in VA Long Beach. A duplicate-safe rerun completed 12 within-task model configurations and all 72 directed CAD transfers after removing exact duplicates before partitioning. Source-only Platt, isotonic, beta, and temperature comparisons now cover seven tasks and six models; a matched fixed-versus-tuned meta-estimator ablation also evaluates OSEC across all seven tasks. The latest eight-page manuscript is under `paper/multi_dataset_study_20261108_dedup_safe_ablation_calibration/` with PDF `output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe_Ablations_Calibration.pdf`. The previous six-page and seven-page versions remain preserved. The corrected Hungary and VA results supersede those two frozen within-task estimates; their rerun fold differences also include fold reshuffling. This is retrospective benchmark work and does not establish independent external validation or clinical use.
<!-- CURRENT_COMPLETION_STATUS_20261108 END -->

This repository preserves the original CARDIODIAG notebooks and datasets while
adding a separate, leakage-controlled research implementation. The research
implementation is not a clinical diagnostic device and must not be used for
patient care.

## Current status

### Completion branch update (2026-11-08)

The `research/cardiodiag-complete-project-finalization` branch extends the
multi-dataset study with verified training/validation diagnostics, 80/90/95%
conformal evaluation, cross-cohort OOD average precision and alert rates,
full confusion-derived metrics, a 17-source inventory, data-quality tables,
module inventory, and EDA/reliability figures. The frozen study evaluated seven
separate tasks with six models (42 task/model summaries and 114 outer/official
test folds) and 72 directed transfers among the four UCI angiographic cohorts.
All 114 selected-fit probability replays and all 72 cross-cohort OOD AUC checks
matched saved outputs; 1,362 aggregate metric checks matched row-level saved
predictions. The transfers remain retrospective because the UCI component
cohorts are represented in Heart5 and patient-level independence is unknown.

The focused completion reports and final acceptance matrix are linked from
`docs/CARDIODIAG_COMPLETE_TECHNICAL_RESEARCH_REPORT.md`. Machine-readable
completion outputs are under `results/final_research_20261108/`. The existing
six-page manuscript is preserved under `paper/multi_dataset_study_20261108/`;
its original build manifest and PDF hash verify. The seven-page duplicate-safe
version is also preserved. The current eight-page manuscript adds the calibration
and OSEC optimization comparisons, was compiled with Tectonic 0.17.0, and was
visually checked under
`paper/multi_dataset_study_20261108_dedup_safe_ablation_calibration/`; its PDF
is `output/pdf/CARDIODIAG_MultiDataset_Experimental_Evaluation_20261108_DedupSafe_Ablations_Calibration.pdf`.
Current verification and remaining
submission blockers are in `docs/FINAL_PROJECT_ACCEPTANCE_MATRIX.md`.

**Engineering demonstration: GO. Generalization research claim: NO-GO. Journal submission: NO-GO pending evidence and author metadata.**
The pipeline trains across four UCI cohorts and has a source-only evaluation
on a separately reported, nominally endpoint-aligned AngioCAD site cohort,
with calibration, uncertainty, OOD scoring, and a fail-closed unknown-site
gate. Cross-dataset patient independence is unverified, the cohort was exposed
before follow-up reliability analysis, and only 377 of 413 labeled IDs have
features. The workflow is implemented and demonstrated; it does not establish
dependable generalization or clinical readiness. The feature-only OOD AUROC was 0.589 on AngioCAD, and
the post-hoc combined abstention policy accepted 5.6% of that cohort. The
separate clinical/real-world readiness ledger remains `NO_GO` (1/13 gates
passed); it is not a completion gate for this engineering prototype. Current
rejection findings, evidence, and external blockers are consolidated in
`docs/MASTER_SCIENTIFIC_REMEDIATION_REPORT_20261105.md`,
`docs/SUBMISSION_READINESS_REPORT_20261105.md`, and
`docs/REMAINING_WORK_REGISTER_20261105.md`.

The remediation pass is complete for the evidence and tools available in this
checkout. The paper now includes the AngioCAD ID/unit audit, Mendeley
predictor-timing audit, seven-subset sensitivity, selective-policy component
results, and an explicit research `NO-GO` conclusion. The latest 15-page PDF is
`output/pdf/CARDIODIAG_Final_Consolidated_20261106.pdf`; its source, numeric-table,
result, compiler, and output hashes are in
`paper/build/final_consolidation_20261106/publication_manifest.json`. Numeric
tables are regenerated from frozen artifacts and hashed in
`paper/tables/final_numeric_table_manifest.json`. The full 127-test suite
passed; Ruff, Python compilation, and lockfile checks passed. New untouched,
endpoint-compatible external data and project-team declarations remain unavailable,
so the generalization claim and journal submission remain `NO-GO`.

The 2026-11-06 completion pass adds a source-only LOF comparison and a
post-hoc risk–coverage audit without changing the frozen model or manuscript
estimates. See `docs/OOD_IMPROVEMENT_REPORT.md`,
`docs/SELECTIVE_PREDICTION_REPORT.md`,
`docs/FINAL_RESEARCH_COMPLETION_REPORT.md`, and
`docs/FINAL_ACCEPTANCE_MATRIX.md` for current gates.
No public code archive is approved: the repository has no root code license,
and clean data-free packaging remains outstanding.

The initial audit is documented in `docs/initial_audit.md`. Earlier work
examined training-only feature stability and selective reliability within the
two development benchmarks. The active research direction is now
**generalization-aware and uncertainty-calibrated cardiovascular prediction
under dataset shift**. A four-cohort leave-one-source-out pilot, with source-only
calibration and OOD detection, is recorded in
`docs/TRANSFER_STUDY_RESULTS_20261105.md`. A second frozen study trained on all
four sources and evaluated once on the separately reported Z-Alizadeh Sani
hospital cohort; its endpoint uses `>=50%` while the source endpoint uses
`>50%`. Patient-level independence is unverified; the result is a transport
stress test, not verified external validation.
The results are in `docs/TRANSFER_STUDY_RESULTS_20261105_ZAS.md`. A third,
endpoint-aligned site evaluation (`CD-XD-004`) uses the separately reported
AngioCAD hospital cohort in Isfahan; patient-level independence is unverified,
the cohort is post-hoc, and its full results and limitations are in
`docs/TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.

The reliability/abstention extension adds a post-hoc replay of AngioCAD
(`CD-XD-006`) and a fresh Duke ACATH transport stress test (`CD-XD-005`). The
AngioCAD replay had 5.6% automatic coverage; Duke's endpoint is >=75% rather
than the source >50%. Feature-only OOD separation was weak, and the trusted
domain registry withheld every unseen-site score. A direct screen showed all
270 UCI Statlog records duplicate Cleveland. A newly published 2026 Mendeley
918-row dataset was also screened: all 918 labeled rows exactly match Heart5,
so it is not a new cohort. A separate source audit finds all Heart5 rows
compatible with the UCI components (914 unique source-row matches and four
ambiguous matches due to source missingness). No untouched, endpoint-compatible
public cohort was verified. Cross-source patient independence cannot be
confirmed for the site-separated records because common patient identifiers
are unavailable; UCI components and Statlog overlap development lineage. The
2021 Mendeley codebook was hash-checked against
its official API: its target means absence/presence, but the diagnostic
reference standard is unspecified, so it is not pooled with angiographic
labels. The field-level timing audit found no documented measurement time for
any Mendeley field. The AngioCAD audit preserved all 36 unmatched label IDs and
found that neither age nor FBS units are stated in its feature workbook; the
historical mappings remain assumptions. See
`docs/MENDELEY_PREDICTOR_PROVENANCE_AUDIT_20261105.md` and
`docs/ANGIOCAD_FEATURE_HARMONIZATION_AUDIT_20261105.md`.

The post-correction audit additionally declares coded categorical predictors in
`data/manifests/local_datasets.json` and evaluates selector relevance on an
inner training partition. Bounded rerun artifacts use the
`results/generated/schema_corrected_*` prefix and are summarized in
`docs/schema_corrected_evidence.md`.

## Latest verified closeout (2026-11-05)

A fresh 3 outer x 3 inner seed-42 internal run completed for Heart5 and
Mendeley with all fold predictions and split indices saved under
`results/master_directive_20261105_serial/`. Its fold-mean metrics match the
prior authoritative stage exactly. Corrected OVEC ROC-AUC is 0.9295 on Heart5
and 0.9957 on Mendeley; stable OSEC scores 0.9253 and 0.9942. These remain
internal development/replication results and do not establish external
generalization.

The paper package has nine generated, hashed core figures and an IEEE-style
research draft with provisional author metadata and explicit pending
declarations. The latest PDF is
`output/pdf/CARDIODIAG_Research_Draft_20261105_Remediation.pdf`; its source,
result, protocol, figure, rendered-page, extractable-text, and PDF hashes are
recorded in
`paper/build/research_draft_20261105_remediation/publication_manifest.json`.
It has been rebuilt and visually reviewed, but not venue-proofed. Author
order/affiliations, ethics, funding, coauthor contributions, competing
interests, and data-use declarations still need confirmation. The report and
completion matrix are
`docs/FINAL_RESEARCH_REPORT.md` and
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md`. Current checks are summarized in
`docs/QA_REPORT.md`.

## Engineering validity audit (2026-11-05)

The corrected pipeline's target, identifier, and fold-local preprocessing
boundaries were reviewed. A nested Mendeley sensitivity excluding the
fluoroscopy-derived major-vessel field left all five AUCs between 0.993 and
0.996, so that one potentially post-diagnostic feature does not explain the
high score. The Mendeley reference standard and feature timing remain
undocumented. An AngioCAD age/sex-only sensitivity removed the undocumented FBS
unit assumption; AUC remained 0.788, while feature-only OOD AUROC was 0.544
(95% interval 0.496-0.592). This is post hoc and not a fresh external
confirmation. See the validity audit for what these results do and do not
support.

## Real-world readiness workflow

The agreed final-year project scope is a completed offline research prototype
and retrospective evaluation. The results do not establish reliable
cross-dataset generalization or clinical performance. Possible future clinical
use is not specified or approved. See `docs/INTENDED_USE_SCOPE.md`.

## Desktop research demonstration

The local-only Tk interface uses a frozen domain-aware model bundle and the
project's saved aggregate results. Run it with:

```powershell
uv run python demo/app.py
```

It includes project status, a synthetic input form, evaluation evidence and
explanation limitations. It defaults to an unregistered domain and abstains;
registered-domain selection is for synthetic policy demonstration only. Do
not enter patient data. The demo is not clinically validated and must not be
used for care decisions. Setup and limitations are in `docs/APPLICATION_GUIDE.md`.

The final project inventory and gate-by-gate conclusion are in
`docs/MASTER_PROJECT_INVENTORY.md` and `docs/FINAL_PROJECT_REPORT.md`. The
scientific generalization gate remains NO-GO; the app does not change that
conclusion.

The current build is **not ready for clinical or real-world use**. The staged
gates, measurable exit targets, blockers, and evidence paths are in
`docs/REAL_WORLD_READINESS_WORKFLOW.md`. The executable ledger is
`docs/real_world_readiness_gates.json`; check its current decision with:

```powershell
uv run python experiments/evaluate_readiness.py
```

The checker currently reports `NO_GO`; it verifies recorded evidence paths and
hashes plus gate states, not the underlying clinical or regulatory judgments.
It writes `results/REAL_WORLD_READINESS_REPORT.json`. Data-access options
screened for the next external evaluation are in
`docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md`.

## Dataset-shift pilot (2026-11-05)

The frozen `CD-XD-002` protocol trained on three UCI cohorts and tested on the
fourth, rotating through all four cohorts. Macro ROC-AUC was 0.760 and mean
Brier score improved from 0.202 to 0.170 after source-only Platt calibration.
The OOD score averaged 0.758 AUROC, but its held-out alert rate ranged from
2.4% to 86.8% across cohorts. This is a retrospective pilot because the source
cohorts are represented in the historical Heart5 composite; it is not
independent external validation. See the full site-level metrics, confidence
intervals, sensitivity analysis, and limitations in
`docs/TRANSFER_STUDY_RESULTS_20261105.md`.

## Separate-site transport stress test (2026-11-05)

The frozen `CD-XD-003` study trained on Cleveland, Hungary, Switzerland, and VA
Long Beach, then scored the distinct 303-patient Z-Alizadeh Sani cohort from
Shahid Rajaei Center in Tehran once. It used only age, sex, and fasting glucose
with documented compatible definitions. ROC-AUC was 0.720 (95% bootstrap CI
0.651–0.780); source-only calibration modestly reduced Brier score from 0.200
to 0.193, with a paired interval that includes no difference. The source-only
OOD detector had AUROC 0.604 and flagged 14.9% of target rows at a 5.3% source
false-alert rate. The `>=50%` target label boundary differs from the `>50%`
source definition, so this is a source-distinct transport stress test, not
endpoint-identical external validation. See
`docs/TRANSFER_STUDY_RESULTS_20261105_ZAS.md` and the frozen protocol.

## Endpoint-aligned external-site evaluation (2026-11-05)

The locked `CD-XD-004` pipeline used the same four source cohorts and three
harmonized predictors, then scored AngioCAD's separately reported Isfahan site
cohort once. Its stenosis
bins align with the source `>50%` endpoint. Although AngioCAD reports 413
labeled patients, only 377 had matching clinical predictors; those cases had
79.0% positive labels. ROC-AUC was 0.787 (95% bootstrap CI 0.734–0.838).
Source-only Platt calibration modestly improved Brier/log loss by point
estimate, but paired intervals included no change and ECE worsened slightly.
The OOD detector separated source from target weakly (AUROC 0.589) and flagged
11.7% of target rows. The workbook omits FBS units; its values are interpreted
as mg/dL based on their range, and this assumption is documented. This is one
endpoint-aligned external-site evaluation, but participant-level independence
cannot be confirmed because cross-dataset identifiers are unavailable. The
cohort was inspected before subsequent reliability analyses, and the prototype
does not provide dependable calibration or useful shift rejection.
The primary and byte-identical repeat run are in
`results/transfer_20261105_angiocad_external/` and
`results/transfer_20261105_angiocad_external_reproduction/`.

## Working source-domain abstention prototype (2026-11-05)

The project now has a runnable inference boundary in
`src/cardiodiag/domain_guard.py`. A trained model bundle exposes a probability
only when the caller supplies a registered source-domain ID, the source-only
90% conformal set is a singleton, and a 10-neighbor feature-support score is
inside that domain's 95% threshold. Unknown or missing domain IDs abstain
without returning a probability. Any other abstention also withholds the
probability; out-of-support rows do not expose a conformal set. The ID must
come from trusted provenance metadata; the feature-only OOD scores were weak
and are not presented as a reliable site detector.

`CD-XD-006` replays the endpoint-aligned AngioCAD transfer with disjoint
probability and conformal calibration partitions. Its exploratory target
ROC-AUC is 0.790. Platt calibration changed Brier score from 0.189 to 0.174
and ECE from 0.211 to 0.192. The 90% conformal set covered all 377 target rows,
but only 8.8% received a singleton set; after the feature-support rule, 5.6%
(21 rows) were auto-classified with no observed errors. The domain registry
correctly abstained on all 377 AngioCAD records because that site is not a
registered source domain. AngioCAD had already been examined in CD-XD-004, so
this is an exploratory policy replay, not fresh confirmation. Full outputs are
in `results/transfer_20261105_angiocad_domain_guard/`.

`CD-XD-005` stress-tested the same abstention method on the newly sourced Duke
ACATH cohort. The source endpoint is >50% stenosis while Duke's is >=75%, so
that result is not endpoint-identical. ROC-AUC was 0.661; Platt calibration
worsened Brier score from 0.216 to 0.241. Feature-only OOD AUROC was 0.556 for
kNN and 0.598 for Isolation Forest. The trusted-domain gate abstained on all
3,504 Duke rows. Results and a hashed model bundle are in
`results/transfer_20261105_duke_acath_final/`.

These runs show that the code can fail closed on unseen sites, while useful
automatic coverage and dependable feature-level shift detection remain
unproven. Run the studies and see the synthetic known/unknown-domain behavior:

```powershell
uv sync --locked
uv run python experiments/run_aligned_angiocad_gate.py
uv run python experiments/run_duke_transfer.py
uv run python demo/run_domain_guard_demo.py
uv run python demo/run_domain_guard_demo.py --bundle results/transfer_20261105_angiocad_domain_guard/model_bundle.joblib
uv run python experiments/audit_domain_guard_artifacts.py
uv run python experiments/audit_statlog_overlap.py
```

The saved-artifact audit independently recomputes target metrics, verifies
every recorded input/code/output SHA-256, and confirms that the unknown-site
gate abstains without exposing probabilities. A separate screen found all 270
UCI Statlog records exactly matched Cleveland, so Statlog was excluded rather
than counted as another external site. The overlap is documented at
`data/external/uci_statlog_heart/overlap_audit.json`.

## Setup

```text
uv venv --python 3.11 .venv
uv sync --locked
```

## Checks

```text
uv run python -m pytest
uv run ruff check src tests experiments demo
```

See `docs/roadmap.md` for the experimental gates and `docs/dataset_provenance.md`
for provenance and external-validation rules.

The AngioCAD site study uses `experiments/run_angiocad_transfer.py` and
fits/calibrates only on the four source cohorts. Its target construction is
nominally aligned to the source `>50%` endpoint, but person-level independence
is unverified, 36 of 413 labels lack feature rows, and the target was examined
before follow-up reliability analyses. The Z-Alizadeh Sani result remains a
separate transport stress test because its threshold differs at 50% and
patient overlap cannot be ruled out. Keep the
generic gated runner in `experiments/run_external_evaluation.py` for additional
frozen external cohorts.

## One-command internal stage

After setup, run the development-only nested validation stage with:

```text
uv run python experiments/run_internal_stage.py
```

This evaluates only the two existing benchmark datasets, writes JSON results
and a stage manifest to a new UTC-named directory under `results/`, and does
not perform or claim external validation. The runner refuses to overwrite
existing result files; use a new `--output-dir` for every run. Review
`docs/execution_plan.md` before freezing any external dataset or research
conclusion.

## What CARDIODIAG does

CARDIODIAG preserves the original cardiovascular prediction notebooks while
providing a separate Python research implementation. The corrected pipeline
uses explicit feature schemas, training-only preprocessing, nested model
selection, stability-aware feature selection, calibration, selective-risk, and
reliability analyses. It is research software, not a clinical diagnostic tool.

The current research focus is generalization-aware and uncertainty-calibrated
cardiovascular prediction under dataset shift. The engineering workflow trains
on multiple source cohorts, evaluates separately reported site cohorts with
independence caveats, reports calibration and feature-only shift diagnostics, and fails closed for
unregistered sites. The evidence is mixed: AngioCAD AUC was 0.787, calibrated
ECE was 0.216, and feature-only OOD AUROC was 0.589. Dependable unseen-site
prediction is therefore not established. A complementary stability--
reliability analysis found no consistent benefit from the stable selector; no
new prediction algorithm is claimed.

## AURA-ML research prototype

`src/cardiodiag/aura/` contains AURA-ML, a provisional adaptive representation
and reliability-aware selection framework. It profiles training folds, chooses
bounded original/multiview representations, applies optional stable and
redundancy-aware selection, evaluates candidate models with a fixed inner-only
utility, and retains reliability-gated fusion only when it beats the best single
candidate by a prespecified margin. The outer test fold is never used for these
choices.

Run the exploratory nested evaluation with:

```text
./.venv/Scripts/python.exe experiments/run_aura_nested.py --dataset heart5.csv --target HeartDisease --output results/aura_ml/aura_nested_2x2_heart5.json --outer-splits 2 --inner-splits 2 --seed 42
```

The design, equations, limitations, and results are in
`docs/AURA_ML_DESIGN.md`, `docs/AURA_ML_BASELINE_AUDIT.md`, and
`results/aura_ml/AURA_ML_2X2_REPORT.md`. The current evidence is exploratory;
it does not establish algorithmic novelty, universal superiority, external
validation, or clinical utility.

## Repository map

- `src/cardiodiag/` — reusable data, preprocessing, models, validation,
  reliability, provenance, conformal uncertainty, and domain-gating code.
- `experiments/` — reproducible experiment and artifact-generation runners.
- `data/manifests/` — dataset identity, schema, hash, provenance, and external
  validation gate metadata.
- `results/generated/` — machine-readable experiment artifacts.
- `results/tables/` — derived CSV/Markdown result tables.
- `paper/` — editable LaTeX manuscript, bibliography, and generated tables.
- `docs/` — audit, novelty, leakage, QA, registry, and handoff documents.
- `demo/` — non-clinical prediction-set, uncertainty, and domain-gate demonstrations.
- `archive/` — preserved historical notebooks and expanded release snapshots.
- `dist/` — retained ZIP distribution artifacts.

The original-source forensic record is in `docs/SOURCE_PROVENANCE.md`,
`docs/ORIGINAL_ALGORITHM_WALKTHROUGH.md`, and
`docs/PAPER_TO_CODE_MAP.md`. The protocol and leakage assessment is in
`docs/PROTOCOL_AUDIT.md` and `docs/LEAKAGE_AND_VALIDATION_AUDIT.md`.
Phase-2 metric reconciliation, integration decisions, ablations, compatibility,
shift analysis, and unresolved limitations are indexed in
`docs/FINAL_RESEARCH_REPORT.md`.

## Reproducibility and QA

The `pyproject.toml` and `uv.lock` define the environment. After
installation, run:

```text
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/ruff.exe check src tests experiments
./.venv/Scripts/python.exe demo/run_demo.py
```

The authoritative experiment index is generated from stored artifacts:

```text
./.venv/Scripts/python.exe experiments/build_authoritative_registry.py
```

Read `docs/AUTHORITATIVE_METRIC_REGISTRY.md` before comparing results. It
separates corrected internal validation, schema sensitivity, historical
evidence, exploratory 70K work, and incomplete attempts.

## Datasets and limitations

The local files are `heart5.csv`,
`MendeleyCardiovascular_Disease_Dataset.csv`, and the separate Kaggle 70K
`cardio` benchmark. Their hashes, schemas, roles, and licensing caveats are in
`docs/DATA_PROVENANCE.md`, `data/manifests/`, and
`docs/FINAL_DATASET_ATTRIBUTION_REGISTER.md`. The exact upstream record and
standalone license for Five States/Heart5 are unresolved; Kaggle 70K lists its
license as `Unknown`. Both are excluded from a public data release. UCI
components overlap Heart5; Statlog duplicates Cleveland; the Mendeley 2026
release duplicates Heart5. AngioCAD supplies one endpoint-aligned external-site
evaluation, but cross-source patient independence is unverified, 36 labeled
cases lack features, the FBS unit is undocumented, and OOD/calibration results
remain weak. Existing ZIPs in `dist/` are legacy and not approved for upload;
see `docs/FINAL_DATA_RELEASE_MANIFEST.md` and the individual notices in
`data/attribution/`.

Do not use this software for patient care. The project does not establish
clinical utility, safety, fairness, causal explanations, prospective validity,
or deployment readiness. The full status and blockers are in
`results/final_publication/FINAL_PROJECT_COMPLETION_REPORT.md`.

## Publication package

The editable manuscript is `paper/manuscript.tex`. Build instructions and
unresolved author/venue requirements are in `paper/README.md` and
`docs/REPRODUCIBILITY_GUIDE.md`. A draft PDF was compiled and visually checked;
author, ethics, funding, licensing, and target-venue review are still open.

## Licensing and attribution

See `LICENSE_AND_ATTRIBUTION.md`. Historical files and datasets retain their
upstream obligations; do not redistribute raw data unless the applicable
license and access conditions have been verified.
