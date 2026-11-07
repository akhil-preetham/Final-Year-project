# CARDIODIAG recommended dataset acquisition plan

**Updated:** 2026-11-07. This is a project-planning record based on the angiographic CAD task and the license/overlap audit. It does not establish clinical readiness.

**Acquisition outcome:** UCI HF (ID 519) and UCI MI Complications (ID 579) were downloaded from the official CC BY 4.0 records and evaluated as separate exploratory binary tasks. They remain unsuitable as CAD validation. See `NEW_DATASET_EXPERIMENTS_20261107.md` for protocols and results. The Nasarian UCI CAD record has no downloadable file bytes, so it was not used.

## Recommendation

Do not acquire any of the nine candidates as a supposed new external test of the current CAD model. Three are known to be already represented/used (UCI Heart Disease, Statlog, Z-Alizadeh Sani), PTB-XL+ is derived from PTB-XL, and the remaining candidates have incompatible outcomes or modalities. If expanding the engineering project is worthwhile, acquire one dataset only for a separately defined task, with its own protocol and results folder.

## Review of the newly supplied candidate list

The list is directionally consistent with this audit, but its official UCI link for Z-Alizadeh Sani uses dataset ID `451`; the audited official record is [UCI ID 412](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani), DOI `10.24432/C5Q31T`. UCI confirms 303 records and a CAD cutoff of `>=50%`; this source was already evaluated and does not provide an untouched independent test. The supplied Heart Disease description refers to 303 Cleveland records; the complete UCI record contains four cohorts and 920 records. The Heart Failure link should resolve to the full official [UCI ID 519 record](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords), DOI `10.24432/C5Z89R`.

The open licenses/public download workflows in UCI and PhysioNet records make the data candidates for separately scoped research under their terms; they do not make overlapping or endpoint-incompatible data valid new CAD validation. UCI lists Statlog as similar to Heart Disease, and the local exact-match audit finds 270/270 Statlog records match Cleveland after label harmonization. Heart Failure mortality and MI complications remain different outcomes; PTB-XL, PTB-XL+, Chapman, and EPHNOGRAM remain ECG/PCG tasks. Public access is not a blanket permission to redistribute unreviewed source files or derivatives.

## Candidate decisions

| Priority | Dataset | Acquisition decision | Proposed role |
|---:|---|---|---|
| 1 | PTB-XL v1.0.3 | Recommended for a distinct ECG interpretation benchmark. Public, CC BY 4.0; freeze version and cite both PhysioNet record and Scientific Data paper. Download only if CARDIODIAG project scope formally adds an ECG task. | Separate multilabel ECG diagnosis/rhythm project. Split by patient and use official folds. Not CAD external validation. |
| 2 | Chapman-Shaoxing-Ningbo PhysioNet v1.0.0 | Recommended only for an ECG arrhythmia transport experiment; public, CC BY 4.0. Download direct 1.0.0 record; avoid bundled Challenge datasets unless source IDs and overlap are isolated. | Separate patient-level ECG arrhythmia validation after dataset-specific preprocessing. Not CAD model. |
| 3 | UCI Heart Failure Clinical Records | Acquired 2026-11-07 under CC BY 4.0 and analyzed as death-event classification with follow-up time excluded. The common horizon is unspecified, so this is not time-to-event validation. | Separate exploratory HF task. Not CAD validation. |
| 4 | UCI Myocardial Infarction Complications | Acquired 2026-11-07 under CC BY 4.0 and analyzed at admission with later features and outcome proxies excluded. Participant-level IDs are unavailable. | Separate exploratory post-MI task. Not CAD validation. |
| 5 | EPHNOGRAM | Optional engineering-only signal quality or multimodal ECG-PCG task. Public ODC-By; large download, 24 healthy volunteers, no disease endpoint. | Signal-quality/activity stress task. Not disease prediction or external validation. |
| — | UCI Heart Disease | Do not newly acquire for external testing. It is already used and overlaps Heart5. | Historical internal/LOSO evaluation only. |
| — | Statlog Heart | Do not add; exact 270/270 Cleveland overlap. | Duplicate-data ingestion test only. |
| — | Z-Alizadeh Sani | Do not present as a new cohort; already acquired and evaluated. | Existing exploratory source-shift result, endpoint boundary mismatch. |
| — | PTB-XL+ | Do not acquire as independent data. If PTB-XL task proceeds, its features are optional paired inputs and must be joined to PTB-XL patient/record splits. | Derived ECG feature benchmark only. |

## Gated acquisition workflow

### Gate 0 — Choose scope

Project owner selects exactly one path:

- Keep CARDIODIAG scoped to tabular CAD prediction and stop adding incompatible cohorts; or
- Add a separate ECG task, recommended PTB-XL first; or
- Add a separate survival/complication task (HF/MI) with a separately worded objective.

Do not describe separate-task metrics as answering the tabular CAD generalization claim.

### Gate 1 — Freeze source and legal record

Before downloading, create an immutable acquisition manifest with source URL, exact DOI/version, license and license URL, citation, access workflow, date, intended use, redistribution conditions, and SHA-256 for each source file. Keep license text and source-provided notices. For EPHNOGRAM, record ODC-By separately from CC BY datasets. Do not acquire MultiD4CAD unless authorization is obtained under its DUA; that candidate is outside this list and restricted.

### Gate 2 — Define the target and timing

- PTB-XL / Chapman: set a specific ECG diagnosis or rhythm target and label harmonization before fitting; preserve multilabel labels where applicable.
- Heart Failure: choose time origin, follow-up horizon, censoring assumptions, and target; exclude information observed after the prediction time.
- MI complications: choose one of admission/24h/48h/72h prediction times and exclude later-observed fields; predeclare missingness handling.
- EPHNOGRAM: use signal quality/activity tasks only; the dataset has no disease target.

### Gate 3 — Audit unit, schema, missingness, and overlap

Record person count separately from recording count, repeated recordings per subject, channels/units/sample rate, target distribution, missingness by field/label, source population, and split groups. Check upstream references and challenge package composition. Do not claim no overlap unless record linkage supports it; document unresolved linkage explicitly.

### Gate 4 — Build isolated task pipeline

Use a new task identifier and separate target/feature module. Do not silently feed ECG signals or derived ECG features into the existing 11-feature tabular CAD pipeline. Use patient-group splits; fit transforms only on training folds; calibrate/threshold using development data only; preserve untouched evaluation data.

### Gate 5 — Demonstrate and release

Produce a reproducible manifest, environment lock, pipeline tests, data dictionary, exact source citations/license files, patient-grouped split indices, metrics with confidence intervals, failure analysis, and an explicit statement that benchmark performance is not clinical validation. Release code/results only after scanning for restricted/unknown-license raw data, row-level outputs, and unauthorized derivatives.

## Acquisition defaults

- **If the goal remains generalization-aware tabular CAD:** no candidate in this list solves the missing untouched, endpoint-compatible external cohort. The appropriate next step is collaboration/access to a new cath-lab cohort with documented reference standard, prediction-time predictors, governance, and an authorized data-use pathway. Existing AngioCAD is already exposed and has unresolved feature units/missing cases; it is useful evidence but not a pristine confirmatory test.
- **If a public additional benchmark is needed for final-year engineering demonstration:** choose PTB-XL, but clearly label the new ECG task as separate. Chapman is a candidate external source for that new ECG task only if labels and shared source records are controlled.
- **Do not download or redistribute restricted data.** Candidate datasets listed as public-open may be downloaded under their cited license; retain attribution, version and hashes.

## Required acceptance record for any acquisition

Before declaring a new dataset integrated, the following must exist:

- Official source record, exact version/DOI, license text, and citation notice.
- A legal/access decision that distinguishes download availability from permitted reuse and redistribution.
- File hashes, acquisition date, row/record counts, data dictionary, units, missingness, and target definition.
- Patient-level grouping/overlap procedure and source lineage note.
- A written compatibility rationale and role (development, internal benchmark, stress test, independent external test, or separate task).
- A frozen protocol with prediction-time features and no test-set tuning.
- Reproduced results and integrity report for the exact frozen files.

## Source records

- [PTB-XL v1.0.3](https://physionet.org/content/ptb-xl/1.0.3/); [PTB-XL+ v1.0.1](https://physionet.org/content/ptb-xl-plus/1.0.1/).
- [Chapman-Shaoxing-Ningbo v1.0.0](https://physionet.org/content/ecg-arrhythmia/1.0.0/); [EPHNOGRAM v1.0.0](https://physionet.org/content/ephnogram/1.0.0/).
- [UCI Heart Failure](https://archive.ics.uci.edu/dataset/519/heart%2Bfailure%2Bclinical%2Brecords); [UCI MI Complications](https://archive.ics.uci.edu/dataset/579/myocardial%2Binfarction%2Bcomplications).
- [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease); [Statlog Heart](https://archive.ics.uci.edu/dataset/145/statlog%2Bheart); [Z-Alizadeh Sani, UCI ID 412](https://archive.ics.uci.edu/dataset/412/z%2Balizadeh%2Bsani).
- Current CARDIODIAG status and caveats: [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md), [`DATASET_COMPATIBILITY.md`](DATASET_COMPATIBILITY.md), [`EXTERNAL_DATA_ACCESS_PATHWAYS.md`](EXTERNAL_DATA_ACCESS_PATHWAYS.md).
