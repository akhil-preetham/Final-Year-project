# Data handling

Raw and restricted datasets must not be committed to this repository. The two
small benchmark CSVs currently checked in at the repository root are retained
only because they were part of the supplied CARDIODIAG source checkout.

Use `data/manifests/local_datasets.json` to verify the expected file hashes,
schemas, target names, provenance, and licensing notes before running an
experiment. New external datasets must be registered in a separate manifest
before labels are used for model decisions.

The Kaggle cardiovascular benchmark is stored under
`data/kaggle_cardiovascular_70k/`. Its archive metadata reports an unknown
license, so the archive and extracted CSV are retained for local research use
only until upstream licensing is verified. The source contains 70,000
semicolon-delimited records with target `cardio`; age is recorded in days and
the source includes implausible blood-pressure values. No rows are silently
removed or corrected by ingestion.

The `external/uci_heart_disease_45/heart_disease.zip` archive is the UCI Heart
Disease release, obtained for the exploratory `CD-XD-002` retrospective
leave-one-source-out pilot. UCI lists the archive as CC BY 4.0; see
`manifests/uci_heart_disease_transfer_study.json` for its SHA-256, component
files, cohort counts, target definition, feature map, and prior-overlap note.
Although UCI supplies the four component cohorts, those records were already
represented in the project's historical Heart5 composite, so this is not
independent external validation.

The `external/uci_z_alizadeh_sani_412/z_alizadeh_sani.zip` archive is UCI
dataset 412, *Z-Alizadeh Sani*, licensed CC BY 4.0. It contains 303 rows from
a distinct hospital cohort and is used in `CD-XD-003` as a one-way transport
stress test with three harmonized predictors. Its outcome threshold is
`>=50%`, compared with `>50%` in the source cohorts; it is not an
endpoint-identical external validation set. See
`manifests/uci_z_alizadeh_sani_external.json` for hashes, cohort counts,
feature mappings, and limitations.

The small structured AngioCAD workbooks and Zenodo metadata are retained under
`external/angiocad_zenodo_15826856/`. The public record reports 413 patients,
but only 377 unique IDs have both clinical predictors and artery labels in the
released workbooks; 36 labeled IDs are missing feature rows. The matched cases
support `CD-XD-004`, an endpoint-aligned external evaluation with age, sex, and
FBS. See `manifests/angiocad_external.json` for file hashes, the exact target
construction, attribution, and data-completeness limits. The record is CC BY
4.0; attribute the authors before reuse.

The public Duke ACATH spreadsheet is retained under `external/duke_acath/`
for the fresh `CD-XD-005` transport stress test. Vanderbilt states that use is
permitted with source attribution. The cohort has 3,504 referred-for-chest-pain
patients and an endpoint of at least 75% stenosis, while the UCI development
cohorts use greater than 50%; therefore its results are not endpoint-identical
external validation. Cholesterol is missing for 1,246 records. See
`manifests/duke_acath_external.json` for the exact hashes, provenance, mapping,
target counts, and limitations. The `.xls` input is read using the `xlrd`
dependency declared in `pyproject.toml`.

The official UCI Statlog (Heart) release is retained under
`external/uci_statlog_heart/` as a screened candidate. Its official metadata
lists 270 records and a CC BY 4.0 license. An exact comparison against the
Cleveland component in the UCI Heart Disease release found that all 270
Statlog rows match Cleveland on all 13 predictors and the harmonized binary
outcome. It was excluded from external testing because it contributes no new
patients. See `external/uci_statlog_heart/overlap_audit.json` for the source
URL, archive SHA-256, matching definition, and counts. Attribute the UCI
repository if the archive is reused. Recreate the exact comparison with
`uv run python experiments/audit_statlog_overlap.py`.

Two additional public UCI datasets were acquired on 2026-11-07 for separate
clinical prediction tasks. `external/uci_heart_failure_519/` is UCI ID 519
(CC BY 4.0); its binary death-event experiment excludes follow-up duration
`time`. `external/uci_mi_complications_579/` is UCI ID 579 (CC BY 4.0); its
primary experiment uses the UCI admission-time input set, excludes later
observations and concurrent outcome proxies, and derives `any_lethal_outcome`
from `LET_IS`. See their manifests and attribution notices for hashes,
processing, and limitations. Neither dataset is part of the CARDIODIAG CAD
endpoint or external validation. Raw and prepared person-level files remain
ignored by Git.

The currently accessible files do not provide an untouched,
endpoint-compatible cohort with a compatible feature map: AngioCAD is aligned
but post-hoc; Duke ACATH is newly sourced but uses a >=75% endpoint; and the
UCI source components and Statlog file overlap historical development data.
Participant-level independence cannot be confirmed for the nominally separate
site cohorts where common patient identifiers are absent. See
`docs/DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md` and
`docs/FINAL_DATASET_ATTRIBUTION_REGISTER.md` for the authoritative overlap,
DOI/version/license and release decisions.

The exact upstream artifact and standalone terms for `heart5.csv` are
unresolved. The Kaggle 70K record currently lists its license as Unknown. Do
not redistribute either raw file or row-level derivatives. No raw datasets are
included in the proposed data-free code release. Existing `dist/*.zip` files
are legacy archives and are not approved for public upload; see
`docs/FINAL_DATA_RELEASE_MANIFEST.md`.
# Current release and independence policy

The controlling dataset identity, source, DOI/version, license, attribution,
overlap, and release decisions are in
`../docs/FINAL_DATASET_ATTRIBUTION_REGISTER.md`,
`../docs/FINAL_DATA_RELEASE_MANIFEST.md`, and
`../docs/DATASET_OVERLAP_AND_INDEPENDENCE_REPORT.md`. Historical descriptions
below preserve provenance but do not establish patient-level independence.
No dataset is called independent solely because its filename, download URL,
or reported site differs. No verified patient-independent, untouched,
endpoint-identical external validation has been demonstrated.

