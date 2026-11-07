# Final CARDIODIAG data release manifest

**Status:** proposed allow-list for a **data-free code release**, not a generated or published package. No raw patient-level dataset is included. The current `dist/*.zip` archives are legacy snapshots and are expressly **not approved for public upload**. They remain unchanged in the working tree to preserve provenance.

## Release allow-list

| Category | Include in a clean code release? | Conditions |
|---|---|---|
| `src/`, `experiments/`, `tests/`, `demo/` | Yes | Source code only. Inspect generated scripts and embedded constants for copied data before packaging. Preserve repository license and dependency lock. |
| `README.md`, `pyproject.toml`, `uv.lock` | Yes | Keep research-only scope, reproducibility steps and the data-free disclaimer. No root project code license is present locally, and the [original GitHub repository](https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code) lists no root license file; its `LICENSE` URL returned 404 on 2026-11-06. Confirm source-code rights and obtain authorization before any public release. |
| Dataset audit/protocol/manifests and `data/attribution/*.md` | Yes | Include provenance, hashes, licenses, access restrictions and source URLs. Do not include source data bytes or restricted DUA materials. |
| Manuscript source and aggregate tables/figures | Conditional | Include only after current rebuild, source/hash audit, author/ethics/funding declarations, and removal of any record-level predictions or unresolved rights-bearing content. Numerical results must retain exploratory status. |
| Aggregated result JSON/CSV | Conditional/exclude by default | Exclude record-level prediction vectors, labels, split indices tied to records, and 70K-derived artifacts. Explicit allow-list: `results/new_datasets_20261107/summary.json`, the two `*_nested_metrics.json` files, `preparation_summary.json`, and four figures under `results/new_datasets_20261107/figures/`. These contain only aggregate cohort/fold statistics and no per-record labels, predictions, or split indices; raw and prepared CSV files remain excluded. |
| Any raw data, dataset ZIP/XLS/CSV, `.rar`, model bundle trained on row-level source data | No | Data-free release only. Users must obtain datasets themselves from official sources and observe their licenses/DUAs. |
| `data/access_requests/multid4cad/DUA.pdf` or restricted data | No | Do not package. DUA is not data, but its use is access-governance material and does not grant access. |
| Existing `dist/*.zip` | No | Legacy archives contain Mendeley raw data and/or large collections of 70K-derived result artifacts. They are retained unchanged but are not releasable pending item-level rights review. |
| Root archives (`*.rar`) and archived release snapshots | No | Contents and dataset terms have not been fully inventoried; do not include in a public package. |
| `heart5.csv`, Kaggle 70K raw CSV/archive | No | Exact upstream dataset rights/version unresolved; both are excluded from a data-bearing release. |
| Duke ACATH raw workbook and row-level results | No | Provider grants use with attribution; redistribution terms are not explicit. Obtain clarification before sharing. |
| MultiD4CAD | No | Not acquired; controlled access and DUA prohibits redistribution. |

## Dataset-by-dataset release disposition

| Dataset artifact | Local status | Rights finding | Public raw-data disposition |
|---|---|---|---|
| `heart5.csv` | 918 rows; SHA-256 `e4068802a044e8a1e3ae9fa81deae7025711bf4f13e3057f96e4f1cf3b0180c2` | Derived composite; exact 1,190-row Kaggle source/terms and transformations unresolved. UCI source CC BY alone is insufficient to clear this derivative. | Exclude. |
| `MendeleyCardiovascular_Disease_Dataset.csv` | 1,000 rows; SHA-256 `9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e` | Mendeley v1 DOI `10.17632/dzz48mvjht.1`; CC BY 4.0. | License permits sharing with attribution/change notice. Excluded from proposed data-free code release; notice supplied. |
| UCI Heart Disease archive | 920 rows; SHA-256 `b17cd273da9ce1caa4710fce80227ea454d4dbf9fcbc8e6a9121672751563adc` | UCI ID 45; DOI `10.24432/C52P4X`; CC BY 4.0. | License permits sharing with attribution/change notice. Excluded from proposed data-free code release; notice supplied. |
| UCI Statlog archive | Local archive; see overlap audit for archive hash | UCI ID 145; DOI `10.24432/C57303`; CC BY 4.0; exact Cleveland row duplicate. | License permits sharing with attribution/change notice. Excluded from proposed data-free code release; notice supplied. |
| Z-Alizadeh Sani archive/workbook | SHA-256 in `data/manifests/uci_z_alizadeh_sani_external.json` | UCI ID 412; DOI `10.24432/C5Q31T`; CC BY 4.0. | License permits sharing with attribution/change notice. Excluded from proposed data-free code release; notice supplied. |
| AngioCAD features/labels workbooks | SHA-256s in `data/manifests/angiocad_external.json` | Zenodo DOI `10.5281/zenodo.15826856`; CC BY 4.0. | License permits sharing with attribution/change notice. Excluded from proposed data-free code release; notice supplied. |
| Mendeley 2026 `heart.csv` | 918 rows; SHA-256 `948420b084d8a3a0ca42b8419fce9aee175879e43f8aedf712377899a67aa49b` | Mendeley v1 DOI `10.17632/nt4y898vyh.1`; CC BY 4.0; exact duplicate of Heart5. | License permits sharing with attribution/change notice; excluded due duplication and data-free policy. |
| Kaggle Cardiovascular 70K | 70,000 rows; SHA-256 `21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c` | Kaggle currently lists license `Unknown`; exact upstream source version not resolved. | Exclude raw data and row-level derivatives pending rights confirmation. |
| Duke ACATH | 3,504 records; hashes in manifest | Provider permits use with attribution; redistribution not explicit. | Exclude raw data and row-level derivatives pending written clarification. |
| UCI Heart Failure Clinical Records | 299 records; source and CSV hashes in `data/manifests/uci_heart_failure_519.json` | UCI ID 519; DOI `10.24432/C5Z89R`; CC BY 4.0. | Raw CSV and prepared person-level table excluded from the data-free release; attribution notice included. |
| UCI Myocardial Infarction Complications | 1,700 records; source hashes in `data/manifests/uci_mi_complications_579.json` | UCI ID 579; DOI `10.24432/C53P5M`; CC BY 4.0. | Raw data and prepared person-level table excluded from the data-free release; attribution notice included. |
| UCI HF/MI experiment summaries | Aggregate-only JSON and fold-mean figures under `results/new_datasets_20261107/`; preparation and run manifests included. | Derived from the CC BY 4.0 datasets above; source/processing details in attribution notices and `docs/NEW_DATASET_EXPERIMENTS_20261107.md`. | Explicitly allow-listed after file review: no record-level data, predictions, labels or split indices; user must obtain raw data from UCI. |
| MultiD4CAD | Not acquired | Controlled access; DUA requires approval and prohibits redistribution. | Exclude. |
| PTB-XL, PTB-XL+, Chapman, EPHNOGRAM | Not acquired | Official licenses documented in audit; no local source bytes. | No files to release; no downloads undertaken for this task. |

## Legacy archive audit

The prior `results/data_provenance_audits/distribution_data_audit.json` scanned six ZIP archives and found no byte-identical Heart5 or Kaggle 70K raw CSV. That does **not** clear their contents: four archives contain 70K-derived result files and all six contain the 1,000-row Mendeley CSV. The scan was not a file-by-file rights review and does not establish rights to publish derived 70K results. Therefore none of the legacy ZIPs is included in the allow-list, even where the Mendeley file itself is CC BY 4.0.

## Reproducible data acquisition rules

For any later dataset acquisition, download only the frozen official version after recording official URL, DOI/version, current license and access requirements. Create an exact file hash and schema/missingness report, patient/record split unit, lineage/overlap screen and data-specific notice. Do not add any candidate solely to increase dataset count. Never mix ECG diagnosis, heart-failure mortality, MI complications and angiographic CAD into one target.

## Release gate

This manifest is an allow-list specification, not an attestation that a clean ZIP was produced. A public source-code release is **BLOCKED** until code licensing/redistribution authority is established, a clean data-free package is built, and a file-level scan confirms prohibited material is absent. A data-bearing release is **NO-GO** until Heart5/Kaggle rights and Duke redistribution are resolved.
