# CARDIODIAG dataset overlap and independence report

**Checked:** 2026-11-06. Independence is a claim about people, sites, collection periods, data lineage, and evaluation exposure—not a file name or a different download URL. “No overlap found” is not equivalent to “independent” when person identifiers are unavailable.

## Confirmed or documented overlap

| Pair / relationship | Evidence | Independence conclusion |
|---|---|---|
| Heart5 ↔ UCI Heart Disease components | Frozen row comparison mapped all 918 Heart5 rows to the UCI source records: 914 unique source matches, 4 ambiguous due to missing source fields, zero unmatched. Heart5 is a Five States composite of the same historic Cleveland/Hungary/Switzerland/VA sources. | Confirmed data lineage overlap; Heart5 cannot be held out as an independent test relative to those components. |
| Statlog Heart ↔ UCI Cleveland | Local `data/external/uci_statlog_heart/overlap_audit.json` reports all 270/270 rows match Cleveland on the 13 predictors and harmonized binary outcome. UCI itself describes Statlog as similar to the Heart Disease database. | Exact row duplicate after harmonization; Statlog adds no new independent patients for this pipeline. |
| Mendeley Heart Disease Clinical 2026 ↔ Heart5 | Local audit found exact 918/918 labeled-row multiset equality across all 12 columns; hashes and source record recorded in manifest. | Confirmed duplicate release; no independent validation. |
| PTB-XL+ ↔ PTB-XL | Official PTB-XL+ record explicitly states it supplements/derives from PTB-XL. It is ECG-derived features/algorithm outputs for the PTB-XL records. | Same source cohort by construction; must never be counted as independent external data relative to PTB-XL. |
| Chapman Challenge subset ↔ Chapman full PhysioNet record | Challenge 2021 lists 10,247 Chapman-Shaoxing records; original subset record/paper describes 10,646; the combined PhysioNet collection describes 45,152 ECGs including the Ningbo dataset. These are versions/subsets of related collection material, not independent datasets. | Do not use the Challenge subset as an external cohort against the larger Chapman collection. Distinguish records and source IDs explicitly. |

## Cross-dataset lineage screening already in CARDIODIAG

- UCI Heart Disease and Statlog rows already occur in historical project lineage and are excluded as external tests.
- Z-Alizadeh Sani was downloaded and evaluated in `CD-XD-003`. It is a source-distinct reported site but patient-level duplicate matching is impossible from the released workbook (no suitable IDs); the exact stenosis boundary differs (`>=50%` vs source `>50%`). This is a completed exploratory stress test, not a pristine final holdout.
- AngioCAD is from a separately reported hospital and no common person-level identifiers are released. The cohort is source-distinct by reported collection site, but participant overlap cannot be ruled out. The 377 matched rows were used in `CD-XD-004`; later runs are post-hoc.
- Duke ACATH is described as a Duke University Medical Center cohort. It is not expected to share historical UCI source patients based on institution/time lineage, but no common person identifiers exist to rule out record duplication. It was already examined in `CD-XD-005`, and its >=75% stenosis outcome differs from the source target.
- The Mendeley 1,000-row data was used by the base paper; its diagnostic reference standard and relation to other public heart disease data are not established. It is a replication dataset, not untouched external evidence.
- Kaggle Cardiovascular 70K has no verified person linkage or authoritative overlap declaration. Existing exact/coarse common-field comparisons cannot establish independence due to non-unique covariates and mismatched schema. Its license is also unknown.
- MultiD4CAD is only represented locally by a public record and unsigned access/DUA materials. Since no authorized data was downloaded or analyzed, no overlap test or independence assertion has been made.

## Candidate independence and compatible role

| Candidate | Existing-lineage screen | Independence evidence / limits | Fit conclusion |
|---|---|---|---|
| UCI Heart Disease | Already in project; components map into Heart5. | Known direct overlap. | Internal retrospective LOSO only. |
| Statlog Heart | Already screened; exact Cleveland row match. | Known direct overlap. | Exclude as external. |
| Z-Alizadeh Sani | Already used in CD-XD-003. | Distinct named site; no person IDs; cannot exclude accidental overlap. | Previously used stress test only. |
| UCI Heart Failure Clinical Records | Acquired 2026-11-07; UCI ID 519; see source manifest. | Different HF cohort of 299 records; no cross-source IDs to link. Exact independence from CARDIODIAG populations is not proven. | Separate binary death-event task; no common horizon; not CAD validation. |
| UCI Myocardial Infarction Complications | Acquired 2026-11-07; UCI ID 579; see source manifest. | UCI says record IDs cannot be related to participants. Therefore de-duplication cannot be performed against the CARDIODIAG cohorts. | Separate admission-time lethal-outcome task; not CAD validation. |
| PTB-XL | Not found in current manifests/files. | German PTB source cohort, 18,869 patients in v1.0.3 page. Different setting/source, but no cross-dataset person linkage to prove zero overlap. | Separate ECG-label study. |
| PTB-XL+ | Not found in current manifests/files. | Deterministically derived from PTB-XL; fully dependent on same patients/records. | Use only with PTB-XL, not as a second independent cohort. |
| Chapman-Shaoxing-Ningbo | Not found in current manifests/files. | Separate reported Chinese hospital sources; no cross-dataset person linkage against CARDIODIAG. Its Challenge data packages can bundle multiple databases; source subfolders must be isolated and checked. | Separate ECG task; not tabular CAD validation. |
| EPHNOGRAM | Not found in current manifests/files. | 24 healthy adult volunteers; distinct published acquisition, but public IDs cannot be linked to CARDIODIAG patient files. No disease endpoint. | Signal-processing/quality task only. |

## What the evidence does and does not establish

**Established:** direct row matches, derived-data relationships, repository source lineage, recorded cohort sites, and local prior project use where noted.

**Not established:** universal unique patient identities across unrelated releases, zero cross-site patient overlap, absence of copies in downstream compilations, or legal rights implied by a download URL. Several source files intentionally lack cross-study patient identifiers; a failed match on common clinical values is weak evidence because such values are not unique identifiers.

## Procedure before calling any future dataset “independent external validation”

1. Freeze the candidate dataset/version and the CARDIODIAG model/protocol before inspecting candidate labels or performance.
2. Preserve a source manifest: official record, dataset DOI/version, license/DUA, access date, exact file hashes, patient/record IDs and acquisition sites where legally allowed.
3. Search lineage papers, acknowledgements, challenge bundles, and derivative datasets for shared source cohorts; do not combine source components with aggregated releases.
4. Compare legitimate stable de-identified patient IDs when available. Otherwise state that overlap could not be ruled out; do not claim verified independence.
5. Define patient-level split and prevent repeated ECGs/visits from a person crossing partitions. For derived records, follow upstream subject identifiers.
6. Record target definition, prediction time, source population, endpoint threshold, and missingness before performance analysis. Use a different endpoint only as a separately named stress test.
7. Keep external data labels from model selection, threshold selection, recalibration, or feature-map iteration. Once inspected, treat that cohort as exposed/post-hoc.

## Local evidence files

- `results/data_provenance_audits/heart5_uci_row_map.csv`
- `results/data_provenance_audits/heart5_uci_lineage.json`
- `data/external/uci_statlog_heart/overlap_audit.json`
- `results/external_candidate_screen_20261105/mendeley_heart_disease_2026_overlap.json`
- `docs/DATA_PROVENANCE.md`
- `docs/DATASET_COMPATIBILITY.md`
- `data/manifests/angiocad_external.json`, `data/manifests/uci_z_alizadeh_sani_external.json`, `data/manifests/duke_acath_external.json`

## Primary source records

- [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease) and [Statlog Heart](https://archive.ics.uci.edu/dataset/145/statlog%2Bheart).
- [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/) and [PTB-XL+](https://physionet.org/content/ptb-xl-plus/1.0.1/).
- [Chapman-Shaoxing-Ningbo / large scale ECG arrhythmia dataset](https://physionet.org/content/ecg-arrhythmia/1.0.0/).
- [EPHNOGRAM](https://physionet.org/content/ephnogram/1.0.0/).
