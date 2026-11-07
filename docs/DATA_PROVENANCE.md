# Dataset provenance and schema audit

Raw datasets are not rewritten by the research package. Hashes below are taken
from `data/manifests/local_datasets.json` and were recomputed during the final
audit.

| Dataset | Rows | Target and counts | SHA-256 | Role | License/provenance status |
|---|---:|---|---|---|---|
| `heart5.csv` | 918 | `HeartDisease`: 0=410, 1=508 | `e4068802a044e8a1e3ae9fa81deae7025711bf4f13e3057f96e4f1cf3b0180c2` | Historical replication/development benchmark | All rows map to UCI components (914 unique, 4 ambiguous); UCI record is CC BY 4.0, but the derived file has no standalone license or full transformation history; review before redistribution |
| 2026 Mendeley Heart Disease Clinical `heart.csv` | 918 | `HeartDisease`: 0=410, 1=508 | `948420b084d8a3a0ca42b8419fce9aee175879e43f8aedf712377899a67aa49b` | Duplicate-source provenance screen; excluded from validation | Mendeley record declares CC BY 4.0; exact 918/918 labeled-row multiset match to Heart5; does not establish an independent cohort |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 | `target`: 0=420, 1=580 | `9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e` | Historical replication/development benchmark | Mendeley record identifies CC BY 4.0; codebook defines absence/presence but not the diagnostic reference standard or angiographic threshold |
| `data/kaggle_cardiovascular_70k/cardio_train.csv` | 70,000 | `cardio`: 0=35,021, 1=34,979 | `21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c` | Separate benchmark development/replication task | Kaggle metadata reports unknown license; do not redistribute until verified |
| `data/external/uci_heart_disease_45/heart_disease.zip` | 920 across 4 cohorts | `num=0`: 411; `num=1..4`: 509 | `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc` | Retrospective leave-one-source-out pilot (`CD-XD-002`); not independent external validation | UCI identifies CC BY 4.0; component sources overlap the historical Heart5 composite |
| `data/external/uci_z_alizadeh_sani_412/z_alizadeh_sani.zip` | 303 from Shahid Rajaei Center, Tehran | `Cath`: Normal=87, Cad=216 | `48210a6623fa6112423d9bc357f72fe3fca12ae77866e63e08632e15d95b724e` | Source-distinct transport stress test (`CD-XD-003`); not endpoint-identical external validation | UCI identifies CC BY 4.0; `>=50%` target threshold differs from source `>50%`; patient-level overlap cannot be ruled out |
| AngioCAD structured workbooks | 377 matched cases from Shahid Chamran Heart Center, Isfahan | 298 positive / 79 negative, derived from artery segment labels | Features `978f2415ab52f11724e1ef00bb63597b8497487afd84b97f7112fc7975a33295`; labels `5bba3f4ba8bed0df0d2f412d5e2ca6deacca0eff20d531a599fe1b8f4d897425` | Endpoint-aligned external evaluation (`CD-XD-004`); subsequent analyses post-hoc | Zenodo CC BY 4.0; 36 of 413 label IDs have no feature row; age and FBS units are absent from the feature workbook; person-level cross-dataset overlap cannot be checked |

## Quality checks

- Within-row duplicate count: zero in the three primary benchmark CSVs (`heart5.csv`, Mendeley 1,000-row dataset, and 70K); this does not imply the datasets are independent of one another.
- The separate Mendeley 2026 918-row file has an exact full-row multiset match to Heart5 across all 12 columns (11 predictors plus target); it is excluded from external evaluation. The file hash matches the Mendeley public API SHA-256.
- The Mendeley 2021 CSV and its official one-page codebook were checked against the public API SHA-256 values. The codebook defines `target=0` as absence and `target=1` as presence of heart disease, but does not specify the diagnostic reference standard or stenosis threshold. It is retained as a development/replication benchmark and is not pooled with the angiographic endpoint. See `data/manifests/mendeley_cardiovascular_2021.json` and `results/data_provenance_audits/mendeley_2021_source.json`.
- The complete field-by-field assessment of the Mendeley identifier, 12 predictors, and target is in `docs/MENDELEY_PREDICTOR_PROVENANCE_AUDIT_20261105.md`. The codebook supplies units and category codes but not measurement timing or the target reference standard. Several ECG/exercise fields and the fluoroscopy-derived vessel count may be outcome-proximal; no field is established as pre-diagnostic.
- A frozen source-row comparison maps all 918 Heart5 records to UCI Heart Disease component records on every observed source field and the binary label: 914 rows map uniquely and 4 have multiple compatible matches because of source missingness. No Heart5 rows are unmatched. The audit supports UCI attribution but does not recover missing-value imputation provenance or establish a separate cohort. See `results/data_provenance_audits/heart5_uci_lineage.json` and `heart5_uci_row_map.csv`.
- The release-data audit streamed and hashed every file in all six current `dist/*.zip` packages. None contains a byte-identical copy of the 70K Kaggle CSV. Every package containing the 1,000-row Mendeley CSV includes its source URL, DOI, and CC BY 4.0 notice. The scan does not establish permission to use the license-unknown 70K source or clear derived 70K result tables. See `results/data_provenance_audits/distribution_data_audit.json`.
- Missing target values: zero.
- Missing feature values: zero in the checked-in files.
- Identifier columns removed before modeling: `patientid` and `id`.
- External overlap checks are limited by the absence of common patient
  identifiers; no exact full tuple match was found between the 70K file and
  Mendeley on the tested common fields, but this cannot establish independence.
- The local `heart5.csv` composite overlaps public component datasets and is not
  eligible as an independent external cohort.
- The UCI ZIP contains Cleveland (303), Hungary (294), Switzerland (123), and
  VA Long Beach (200) cohorts. The pilot holds each cohort out in turn, but the
  component records also occur in the historical Heart5 composite. Zero
  cholesterol values (123 in Switzerland and 49 in VA) and one zero resting
  blood pressure in VA were treated as missing in the primary run, with a
  predeclared sensitivity run retaining them.
- The frozen Z-Alizadeh Sani workbook contains 303 rows, 55 predictor columns,
  `Cath`, and no missing cells. The UCI page says 54 features; this count
  difference is preserved as a provenance discrepancy. `CD-XD-003` uses only
  age, sex, and fasting glucose after a documented semantic map. Its UCI
  angiographic threshold is `>=50%`, unlike the source cohorts' `>50%`.
- The Z-Alizadeh Sani cohort is from a separate reported hospital, and no
  previous local project use was found. Public files lack person-level IDs, so
  accidental cross-dataset patient overlap cannot be checked directly.
- AngioCAD's Zenodo record reports 413 cases, but the two released workbooks
  provide only 377 matched unique IDs. An independent ID audit records the 36
  unmatched label IDs and shows that only 27 of 377 feature/label rows would
  align under a naive positional join; the model loader uses ID matching with
  one-to-one validation. The public files do not explain the missing feature
  rows. The external target is positive if any
  of 15 artery segments is labeled above 50% stenosis; the source is positive
  above 50%, so the positive cut point matches. The target's negative `26-50`
  bin includes the 50% boundary, but exact values within it are unavailable.
  Age and FBS missingness among matched rows is imputed using source-fit data
  only. Both age and FBS units are absent from the feature workbook; age-as-
  years and FBS-as-mg/dL were assumptions in the historical mapping. The
  conservative post-hoc mapping excludes FBS and flags age as provisional.
  See `data/manifests/angiocad_fbs_excluded_mapping_v1.json` and
  `docs/ANGIOCAD_FEATURE_HARMONIZATION_AUDIT_20261105.md`. AngioCAD's site differs
  from all four source sites, but public data do not support patient-level
cross-dataset linkage. Historical results retain the explicit FBS-as-mg/dL
assumption; they are not unit-verified.

## Feature mapping

| Dataset | Numeric predictors | Explicit categorical predictors |
|---|---|---|
| `heart5.csv` | `Age`, `RestingBP`, `Cholesterol`, `MaxHR`, `Oldpeak` | `Sex`, `ChestPainType`, `FastingBS`, `RestingECG`, `ExerciseAngina`, `ST_Slope` |
| Mendeley | `age`, `restingBP`, `serumcholestrol`, `maxheartrate`, `oldpeak` | `gender`, `chestpain`, `fastingbloodsugar`, `restingrelectro`, `exerciseangia`, `slope`, `noofmajorvessels` |
| AngioCAD conservative sensitivity | `Age` (provisionally assumed years) | `Sex` (male/female); FBS excluded until units are documented |
| Kaggle 70K | `age`, `height`, `weight`, `ap_hi`, `ap_lo` | `gender`, `cholesterol`, `gluc`, `smoke`, `alco`, `active` |

Similar names do not imply compatible definitions. The datasets are therefore
not concatenated and the 70K target is not treated as an external test of the
CARDIODIAG target.

## Access and redistribution rule

Do not add a restricted or unlicensed raw dataset to the repository. A future
external dataset must have a completed `data/manifests/external_dataset.json`
with source, access conditions, target definition, feature mapping, license,
hash, overlap assessment, and frozen status before labels are read by an
evaluation workflow.
# Current controlling dataset audit (2026-11-06)

For final dataset identity, DOI/version, licensing, attribution and release
decisions, use [`FINAL_DATASET_ATTRIBUTION_REGISTER.md`](FINAL_DATASET_ATTRIBUTION_REGISTER.md)
and [`FINAL_DATA_RELEASE_MANIFEST.md`](FINAL_DATA_RELEASE_MANIFEST.md). The
tables and experiment records below are historical evidence and remain
preserved; they do not establish patient-independent validation. In
particular, Heart5 overlaps UCI components, Statlog duplicates Cleveland, and
no cross-dataset patient linkage exists for the separately reported site
cohorts. The final manuscript makes no verified patient-independent external
validation claim.

