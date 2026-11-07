# CARDIODIAG final research and release audit

**Audit date:** 2026-11-06  
**Scope:** dataset lineage/licensing integration, manuscript/results consistency, reproducibility checks, and proposed public release. This is a research-software audit, not a legal or clinical determination.

## Dataset and manuscript reconciliation

The controlling dataset source of truth is [`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md), reconciled with the four source audit documents. The manuscript now distinguishes historical replication, retrospective UCI source-domain stress testing, and separately reported site-level evaluation. It does not treat Heart5 and its UCI components, Statlog and Cleveland, or Mendeley 2026 and Heart5 as independent cohorts. It explicitly says that no verified patient-independent, untouched, endpoint-identical external validation has been demonstrated.

The manuscript distinguishes endpoint compatibility from cohort independence: AngioCAD's source threshold is nominally aligned, but patient linkage is absent, only 377 of 413 labeled IDs have features, measurement units are not fully documented, and its target was examined before subsequent analyses. Z-Alizadeh Sani differs at the 50% boundary and has no linkage identifiers. Duke's >=75% endpoint differs from UCI's >50%, and its redistribution terms are unclear. ECG, HF, and MI candidate tasks remain separate.

## Numerical provenance

- `results/tables/nested_summary.csv`, its Markdown view, and `paper/tables/nested_summary.tex` are regenerated from the two seed-42 nested result JSON files by `experiments/summarize_nested.py` and `experiments/generate_paper_assets.py`.
- The nested stage manifest identifies `external_validation: false`, hashes input data and result JSON, and records the 3x3 protocol at seed 42.
- `paper/tables/domain_guard_transfer.tex` is regenerated from AngioCAD and Duke saved `study_metrics.json` files by `experiments/build_domain_guard_table.py`; its companion manifest hashes both inputs, generator, and table.
- The LaTeX manuscript contains other historical/study-specific numbers. Those remain tied to the named run manifests and frozen prediction artifacts; this audit does not overwrite or merge experimental stages.
- Current headline findings include corrected OVEC internal mean ROC-AUC 0.930 (SD 0.007) on Heart5 and 0.996 (SD 0.001) on Mendeley; AngioCAD domain-guard combined automatic coverage 5.6%; Duke combined automatic coverage 11.4% with 41/401 accepted errors; both unknown sites receive 0% coverage from the registry gate.

## Release decisions

The proposed code release is data-free. Attribution and audit notices may be included; raw dataset bytes, row-level predictions, record-linked splits, trained model bundles, restricted DUA material, untraced archives, and existing `dist/*.zip` snapshots are excluded. Heart5/Five States and Kaggle 70K remain unresolved for redistribution. Duke's provider use permission does not explicitly clear redistribution. MultiD4CAD was not downloaded; its DUA is restrictive. CC BY 4.0 sources retain attribution/license/change obligations, and EPHNOGRAM remains ODC-By.

`FINAL_DATA_RELEASE_MANIFEST.md` specifies an allow-list but is not evidence that a clean release archive has already been constructed. No public upload is authorized or claimed.

## Verification record

Fresh verification results are recorded in [`FINAL_ACCEPTANCE_MATRIX.md`](FINAL_ACCEPTANCE_MATRIX.md). The requested suite comprises pytest, Ruff, Python compilation, lockfile validation, dataset/artifact audit scripts, and a new LaTeX build with reference and PDF-text checks. Historical QA reports are not substituted for current rerun results.

## Decision

| Area | Decision | Reason |
|---|---|---|
| Engineering prototype | GO, research-only | Code, frozen protocols, saved results, and fail-closed unknown-site demonstration exist; current verification listed in acceptance matrix. |
| Generalization-aware prediction claim | NO-GO | No verified independent, untouched, endpoint-identical patient cohort; OOD and selective operating results are weak/low-coverage. |
| Clinical or real-world deployment | NO-GO / out of scope | No prospective clinical validation, workflow/utility study, governance determination, or safety case. |
| Code release | BLOCKED | No root code `LICENSE` is present locally; the original GitHub root does not list a license file and its `LICENSE` URL returned 404 on 2026-11-06. Redistribution authority must be confirmed. A clean data-free archive and package scan are also outstanding. Legacy ZIPs are excluded. |
| Raw-data release | NO-GO as a combined project package | Heart5/Kaggle rights unresolved; Duke redistribution unclear; separate CC BY sources remain omitted by data-free policy. |
| Journal submission | NOT READY | The rebuilt 15-page draft has been compiled and visually checked, but the scientific claim is negative/limited as above; author, ethics, funding, competing-interest and venue details remain pending. |

## Remaining blockers that cannot be resolved from this checkout

1. Locate the exact upstream 1,190-row Heart5/Five States Kaggle artifact and its applicable terms and transformation history, or keep the data and derivatives out of release.
2. Obtain written Duke/Vanderbilt clarification before redistributing raw ACATH or row-level derivatives.
3. Obtain external patient-linkage evidence or an appropriate documented independence basis; otherwise do not claim patient independence.
4. Acquire an untouched, endpoint-compatible cohort under a frozen protocol, subject to lawful access and data-use approval.
5. Obtain project-team confirmation of author order/affiliations, contributions, ethics determination, funding, competing interests, and venue.
6. Confirm code ownership and redistribution authority for the original repository and the local research extension before publishing source; neither local nor inspected upstream root has a code license file.

None of these blockers is repaired by relabeling, additional candidate downloads, or a larger internal split count.
