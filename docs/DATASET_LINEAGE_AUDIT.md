# Dataset lineage audit

**Assessment date:** 2026-11-05. Dataset files were hashed and checked using the existing audit scripts and QA artifacts. No raw data were modified.

| Dataset/release | Role and identity finding | Endpoint/schema caveat | Status |
|---|---|---|---|
| Heart5 / Five States | 918 rows; all rows match observed UCI component-source records (914 unique matches; 4 ambiguous due to source missingness; 0 unmatched) | Composite provenance and source imputation history do not establish independent patients | PARTIAL |
| Mendeley 2021 cardiovascular data | 1,000-row development dataset; API CSV and codebook hashes verified | Codebook gives presence/absence but not diagnostic reference standard or angiographic cutoff; predictor timing unclear | PARTIAL |
| Mendeley 2026 heart release | 918 rows; all labelled rows duplicate Heart5 exactly | Not an independent cohort | PASS for duplicate screen; excluded as external evidence |
| UCI Cleveland/Hungary/Switzerland/VA | Used as source domains for transfer experiments | Component cohorts are represented in Heart5; no independent external claim | PARTIAL |
| UCI Statlog | 270/270 rows match Cleveland after target harmonization | Duplicate release; excluded from external testing | PASS for overlap screen |
| Z-Alizadeh Sani | 303 records from separate Tehran site | Target includes the 50% boundary; source event is greater than 50% | PARTIAL; stress test only |
| AngioCAD | 377 feature records matched to 413 labelled IDs; unmatched IDs preserved in audit | One external hospital; FBS unit undocumented; age unit provisional; exact 50% unresolved in 26–50 bin | PARTIAL; one endpoint-aligned evaluation |
| Duke ACATH | 3,504 records | Significant disease threshold is at least 75%, versus source greater than 50%; cholesterol missing in 1,246 | PARTIAL; endpoint-mismatched stress test |
| Kaggle 70K cardiovascular | Separate large benchmark | Different endpoint and feature schema; not external validation of the primary endpoint | NOT APPLICABLE to primary transfer claim |

SHA-256 manifests and attribution checks are documented in DATA_PROVENANCE.md, DATASET_COMPATIBILITY.md, and QA_REPORT.md. Available release scans found attribution for packages containing the 1,000-row Mendeley CSV; the scan did not settle rights for derived 70K result files. Redistribution permission for every source/derived artifact remains unconfirmed. Common person identifiers are not available across all releases, so cross-source patient-level overlap cannot be ruled out.

**Disposition:** Dataset hashes, duplicate screening, schemas, target counts, and unmatched-ID accounting are reproducibly audited. Patient-level independence, some endpoint definitions, feature units/timing, and several redistribution rights remain BLOCKED by absent source documentation or identifiers.
