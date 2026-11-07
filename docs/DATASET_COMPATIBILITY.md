# Dataset compatibility

| Dataset | Rows | Target | Compatible role | Main blockers |
|---|---:|---|---|---|
| Heart5 | 918 | `HeartDisease` | Development/replication | Composite of public sources; not independent |
| Mendeley Heart Disease Clinical (2026) | 918 | `HeartDisease` | Duplicate-source provenance screen | All 918 labeled rows exactly match Heart5; not an independent cohort |
| Mendeley | 1,000 | `target` (0=absence, 1=presence) | Development/replication only | Official codebook does not identify the diagnostic reference standard or angiographic threshold; used by base study |
| Cardiovascular 70K | 70,000 | `cardio` | Separate benchmark/stress test | Different case definition, measurements, and unresolved license |
| UCI Heart Disease components | 920 across Cleveland, Hungary, Switzerland, and VA Long Beach | `num=0` vs `num=1..4` | Retrospective leave-one-source-out pilot | Components occur in historical Heart5; legacy cohorts; uneven missingness and case mix |
| UCI Statlog (Heart) | 270 | `class=1` vs `class=2` | Screened and excluded from external testing | All 270 rows exactly match Cleveland after binary-target harmonization; no new patients |
| UCI Z-Alizadeh Sani | 303 at Shahid Rajaei Center, Tehran | `Cath=Normal` vs `Cath=Cad` | Source-distinct transport stress test (`CD-XD-003`) using age, sex, and FBS | Target threshold `>=50%` vs source `>50%`; no patient IDs for linkage; one site only |
| AngioCAD | 377 matched cases from Shahid Chamran Heart Center, Isfahan (413 IDs in labels) | Any artery segment >50% vs all segments <=50% | Endpoint-aligned source-distinct evaluation (`CD-XD-004`); subsequent analyses are post-hoc | 36 labeled IDs lack predictor rows and reason is unknown; age and FBS units are not stated in the workbook; exact 50% is not separable within the 26-50 stenosis bin; no cross-dataset person identifiers |
| Duke ACATH | 3,504 at Duke University Medical Center | `sigdz`: at least 75% stenosis | Fresh source-distinct stress test (`CD-XD-005`) using age, sex, and cholesterol | Endpoint differs from source `>50%`; cholesterol missing for 1,246 records; no patient linkage |
| MultiD4CAD | 118 single-site CCTA patients (reported 78 CAD, 40 no CAD) | `CAD` vs `no CAD` | Restricted candidate for a separate CCTA-domain stress test | Signed DUA and authenticated access required; label is not established as the source invasive-angiography `>50%` endpoint; small cohort; not acquired |
| APPROACH registry | Registry profile reports >240,000 participants | Obstructive CAD and longitudinal outcomes | Potential partner-based external evaluation | No direct public download; study-team contact, access approval, and endpoint mapping required; not acquired |

Heart5 and the 2021 Mendeley dataset have semantic overlap across predictors,
but their endpoint definitions are not verified as equivalent. The Mendeley
codebook defines only binary disease absence/presence and supplies no diagnostic
reference standard or stenosis threshold. They are not pooled for the
angiographic transfer study.
The Mendeley feature `noofmajorvessels` is mapped in the source article to the
number of major vessels seen by fluoroscopy. The dataset does not record when
this was measured relative to the target. Treat it as a potentially
post-diagnostic predictor: the all-feature score is a retrospective replication
benchmark, not evidence for early detection. A nested sensitivity result without
this field is recorded in `docs/VALIDITY_AUDIT_20261105.md`. The full field-level
assessment is in `docs/MENDELEY_PREDICTOR_PROVENANCE_AUDIT_20261105.md`.
The 70K dataset shares only narrow candidate fields; age units and blood
pressure definitions differ, and cholesterol coding is not equivalent to a
continuous cholesterol measurement.

`CD-XD-002` is a retrospective leave-one-source-out pilot: those UCI component
records were already represented in the Heart5 composite. The separately
screened Statlog file added no new patients: all 270 rows exactly matched
Cleveland on the 13 predictors and binary outcome. `CD-XD-003` is a
source-distinct transport stress test whose target boundary differs at exactly
50%. `CD-XD-004` evaluated one endpoint-aligned external site (377 matched
patients), but its outcomes were examined before the reliability replay
`CD-XD-006`; neither is a pristine final test. `CD-XD-005` adds a newly sourced
Duke cohort, but the >=75% target threshold is not endpoint-identical to the
source >50% definition. Across the available public files, no untouched,
endpoint-compatible cohort with harmonizable predictors was verified. These
limitations prevent a confirmatory claim of generalization to unseen sites.
See the transfer study protocols and results in `docs/` and the exact Statlog
overlap audit at `data/external/uci_statlog_heart/overlap_audit.json`.

The AngioCAD ID-compatibility audit lists all 36 label IDs without features and
verifies the one-to-one ID join. The workbooks do not document age or FBS units;
the old age-as-years and FBS-as-mg/dL mapping remains conditional. The
post-hoc FBS-excluded map records age-as-years as provisional and is not a
confirmatory protocol. See
`docs/ANGIOCAD_FEATURE_HARMONIZATION_AUDIT_20261105.md` and
`data/manifests/angiocad_fbs_excluded_mapping_v1.json`.

A later access screen identified MultiD4CAD as a restricted 118-patient CCTA
candidate, not an acquired or confirmed endpoint-compatible cohort. Its DUA
requires an investigator to sign, take data-controller responsibilities, and
request access; no request was submitted. APPROACH and ACC NCDR require
study-team or institutional access. See `docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md`.

The UCI Heart Disease repository documents four cohorts, a shared 13-predictor
subset, and binary presence derived from `num=0` versus `num=1..4`; the release
is licensed CC BY 4.0. [Dataset documentation](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease)

# Current interpretation

This older compatibility ledger is retained as experiment history. The
controlling, source-audited table is
[`DATASET_COMPATIBILITY_MATRIX.md`](DATASET_COMPATIBILITY_MATRIX.md), with
overlap conclusions in
[`DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`](DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md).
“Source-distinct” in historical records means a separately reported source or
site only; it does not demonstrate patient-level independence. Do not count
Heart5's UCI components or Statlog/Cleveland as external cohorts.

