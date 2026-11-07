# External and cross-dataset evaluation report

## Acceptance decision

**Independent generalization: NO-GO.** The current project does not establish a genuinely independent, untouched, endpoint-identical patient cohort. Existing evaluations are classified as internal, retrospective source-domain stress tests, endpoint-mismatched transfer, or exploratory site transfer.

## Studies and permitted interpretation

| Study | Evidence / result source | Interpretation |
|---|---|---|
| UCI leave-one-cohort-out | `results/transfer_20261105_lodo_final/` and `docs/TRANSFER_STUDY_RESULTS_20261105.md` | Retrospective UCI source-cohort stress test; UCI component records overlap the Heart5 lineage. |
| Z-Alizadeh Sani | `results/transfer_20261105_zas_external_reproduction/`, `docs/TRANSFER_STUDY_RESULTS_20261105_ZAS.md` | Exploratory site transfer with threshold >=50% vs source >50%; patient linkage unavailable. |
| AngioCAD | `results/transfer_20261105_angiocad_domain_guard/`, `study_metrics.json`, `docs/TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md` | 377 matched rows of 413 label IDs; 36 labels lack features. Nominally compatible >50% threshold but age/FBS units and patient linkage remain uncertain; labels were previously examined. Exploratory only. |
| Duke ACATH | `results/transfer_20261105_duke_acath_final/`, `study_metrics.json` | 3,504 records, target >=75% vs source >50%; target labels previously examined and redistribution terms unclear. Stress test only. |
| Synthetic distribution changes | `results/generated/dataset_shift.json` | Controlled perturbation diagnostic; not external clinical evidence. |

No study above should be called confirmatory independent external validation. The domain registry rejects unknown sites; its 0% coverage is an explicit limitation and a fail-closed behavior, not successful predictive generalization.

## OOD AUROC reconciliation

The OOD AUROC **0.604 (0.552–0.652)** belongs to CD-XD-003 (Z-Alizadeh Sani). The primary AngioCAD CD-XD-004 Isolation Forest result is **0.589 (0.541–0.635)**; the age/sex-only sensitivity is **0.544 (0.496–0.592)**. The later, already post-hoc CD-XD-006 domain-robust diagnostics on AngioCAD report Isolation Forest **0.5787** and kNN distance **0.5801** (kNN conditional interval 0.5269–0.6345). These use distinct detector scores and operating policies; they are not corrections to one another. The final manuscript retains 0.604 in the ZAS section and 0.589 in the AngioCAD section.

## Reopening the gate

Require a new eligible cohort with authoritative provenance, access/use terms, clinically coherent target, compatible measured features/units, patient/cohort independence basis, and no prior outcome use. Freeze the development model, preprocessing, calibration, uncertainty, thresholds and statistical plan before target labels are accessible. Report conditional confidence intervals and avoid claiming broad hospital generalization from a single site.

## Additional official-source screening in the completion pass

The official UCI and PhysioNet candidate records listed in
`DATASET_PROVENANCE_AND_LICENSE_REPORT.md` were rechecked. CC BY 4.0 access to
UCI Heart Disease and PhysioNet PTB-XL/Chapman records does not make them
independent or endpoint-compatible: UCI Heart Disease is already in the source
lineage, while ECG records require a different input/task pipeline. UCI Heart
Failure predicts death after an HF diagnosis; UCI Myocardial Infarction
Complications predicts time-indexed complications. Those remain separate
research tasks.

MIMIC-IV v3.1 is an additional possible source for a future separately defined
hospital-record study, but its [official PhysioNet access page](https://physionet.org/content/mimiciv/3.1/)
requires credentialing, CITI training and a signed data-use agreement. It is
not a public-download substitute for an endpoint-matched angiography cohort;
ICD-based diagnosis extraction would define a different, retrospective task
unless a separate clinical definition and adjudication protocol were supplied.
No MIMIC or other candidate data were downloaded. Therefore the acceptance
decision remains **NO-GO** for independent external validation.

## Current cohort search addendum (2026-11-06)

The authoritative candidate screen and rejection rationale are consolidated in `EXTERNAL_COHORT_SEARCH.md`. No additional independent compatible cohort qualified. A machine-readable cohort-rights registry is in `data/registry/datasets.json`; the current external manifest gate remains fail-closed. No target data were downloaded or used for model selection in this pass.

The 2026 targeted screen also found a Mendeley extension of Z-Alizadeh Sani (v1, DOI 10.17632/bgf5czvpg2.1). The official record describes it as an extension of that dataset with artery fields, so it is not treated as a new independent cohort; patient-row linkage has not been audited. See the complete search log in `EXTERNAL_COHORT_SEARCH.md`.
