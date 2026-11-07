# CARDIODIAG remaining-work register

**Updated:** 2026-11-05  
**Project scope:** offline final-year engineering research prototype. Clinical
deployment readiness is not a completion gate.

## Decision

The local offline prototype and its reproducibility demonstration are
implemented. The research objective of dependable prediction under dataset
shift is **not achieved**: external calibration and feature-only OOD detection
are weak, selective coverage is low, and the registered-site gate withholds all
unseen-site scores. The project can be presented as a negative engineering
research result, not a successful generalization system.

## Remaining items

| Item | Status | Why it is open | What completes it |
|---|---|---|---|
| Confirm generalization on additional independent sites | **Requires new data** | AngioCAD is the only source-distinct endpoint-aligned patient-level cohort evaluated here (377 matched records). The current public screen found no additional open compatible cohort. | Obtain at least one, preferably multiple, untouched endpoint-compatible sites through an authorized investigator/data agreement; verify endpoint, features, access terms, and overlap; freeze the model/protocol before opening labels; run one-way evaluation with site-level results. |
| Establish feature-only OOD detection and calibration under shift | **Not achieved; partial methods audit** | Frozen kNN and Isolation Forest AUROCs on AngioCAD are 0.580 and 0.579; FBS-excluded age/sex Isolation Forest AUROC is 0.544, conditional on an unverified age-as-years mapping. The frozen-policy audit recalculates counts/AUROCs and source LODO shows high variability. Mahalanobis, robust covariance, LOF, MMD, density-ratio, and explicit missingness/range monitors were not all compared. | Select a small, justified method set and evaluate it only on held-out source domains first; freeze thresholds using source data. Evaluate once on a new untouched target. Do not use AngioCAD for method selection or confirmation. |
| Verify the Mendeley diagnostic reference standard and feature times | **Cannot be verified from the release** | Its official codebook defines absence/presence only. A same-split sensitivity removing `noofmajorvessels` leaves all five AUCs between 0.993 and 0.996, but cannot establish the outcome procedure or timing of other features. | Obtain a full data dictionary or source-author confirmation. Until then, keep Mendeley as retrospective replication evidence and make no early-detection or angiographic-endpoint claim from it. |
| Verify AngioCAD age/FBS units and recover 36 feature rows | **Cannot be verified from public files** | Independent workbook inspection finds no units for either Age or FBS. ID merge is one-to-one; all 36 unmatched label IDs are recorded and their reason is absent. A naive positional merge would align only 27/377 rows. The FBS-excluded age/sex replay is post hoc and age-as-years remains assumed. | Obtain source data dictionary, age-unit confirmation, and missing rows from the data owners. If unavailable, report the 377-row matched restriction and keep FBS excluded from future primary harmonization; retain prior results as conditional. |
| Prove patient-level separation across source and target datasets | **Cannot be verified from public identifiers** | Site-level provenance differs, but the files do not share a person-linkage key. | Request privacy-preserving record linkage or a data-controller overlap attestation. Until then, describe source-distinct site provenance without claiming person-level independence. |
| Reproduce the original article exactly | **Cannot be verified from the supplied source snapshot** | The historical notebooks conflict on split, preprocessing, resampling order, model/search settings, and result-table lineage; exact LoRAS parameters/environment are missing. | Obtain the original executable environment, LoRAS parameters, and table-to-run provenance from the source authors. Keep the current historical runner labelled an approximation. |
| Complete every original A–L condition in one matched factorial | **Partially addressed; original key missing** | `docs/ABLATION_A_L_MATRIX_20261105.md` maps 12 current workstreams, but no authoritative source key mapping the original letters to conditions was found. The five-candidate nested comparison is matched; other work is separate. Exact LoRAS/LIME branches cannot be reconstructed. | Recover the original A--L condition key and protocol. Until then, call the matrix a workstream crosswalk and do not claim a completed original factorial. |
| Complete the 70K five-candidate custom nested run | **Not required for the primary shift objective; not completed** | The 70K `cardio` target and measurements differ from the angiographic endpoint, so it cannot resolve external generalization. Previous full nested attempts exceeded the chosen runtime. Official Kaggle metadata reports license `Unknown`. | Retain the existing separate benchmark evidence. Run a full nested benchmark only if a separate research question and compute budget justify it, and do not redistribute the data/results until rights are cleared. |
| Clear dataset redistribution rights | **Partially addressed** | UCI Heart Disease, Mendeley 2021, and AngioCAD source records identify CC BY 4.0. Heart5 rows map to UCI sources but the derived composite lacks a standalone license notice and transformation history. The official Kaggle 70K record reports `Unknown`; historical packages contain derived 70K outputs. | Keep new releases data-free; obtain rights/attribution confirmation for Heart5 derivation and the 70K source/results before redistribution. |
| Finalize manuscript metadata and journal formatting | **NO-GO for submission; facts pending** | Names and shared affiliation are provisional. Author order and individual affiliations, ethics/data-use determination, funding, two coauthor contributions, competing interests, final approval, and target journal remain unconfirmed. | Confirm factual declarations with each author and the institution, obtain all-author approval, choose a venue, and format using its current instructions. Checklist: `docs/AUTHOR_METADATA_CHECKLIST_20261105.md`. |

## Work completed in the scientific remediation pass

- Added an independent AngioCAD ID-join audit, retained the exact 36 unmatched
  public label IDs, and demonstrated the row-order mismatch counterfactual.
- Audited the AngioCAD workbook metadata and documented that neither age nor
  FBS units are present. Added a conservative FBS-excluded mapping that still
  labels age-as-years provisional; preserved the historical CD-XD-004 run.
- Re-ran the seven-subset age/sex/FBS comparison with target labels held out of
  every fit/calibration function and all result artifacts hashed. It remains
  post hoc and unadjusted for multiple comparisons.
- Recalculated frozen alert counts, OOD AUROCs, coverage, and accepted errors
  for saved CD-XD-005/006 predictions using round-trip CSV parsing.
- Added field-level Mendeley predictor provenance, original-reproduction and
  A--L crosswalk matrices, a statistical consistency report, a submission
  readiness report, and a final scientific decision report.
- Revised manuscript source and tables to make negative results, missing
  units, unmatched records, low coverage, one-class acceptance, and pending
  metadata explicit. Built a 14-page PDF, extracted text from all pages,
  rendered and reviewed every page, recorded source/output hashes, and reran
  the 106-test suite, Ruff, compilation, and lockfile checks. Local artifact
  QA is complete; the research NO-GO is unchanged.

## Public-data/access search completed

The follow-up search found two relevant non-public access leads, not a new
test cohort:

- **CARDIIGAN:** its paper reports 4,888 elective angiography patients and an
  outcome of at least 50% stenosis in a main coronary artery, but its data
  sharing statement says no additional data are available. It is a single
  center and its `>=50%` boundary differs from the source `>50%` definition.
  [Study and data-sharing statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC5558815/).
- **APPROACH/Ottawa/UHN:** a 2026 protocol describes five institutions and an
  expected sample of about 6,000, but patient data remain in secure
  institutional environments and are not publicly released. This is the best
  multi-site access lead if an authorized collaboration is available, not a
  dataset that can be downloaded now. [Protocol](https://bmjopen.bmj.com/content/16/4/e108799).
- **CathAI/MHI QCA:** the published dataset is video/image- and lesion-level,
  with QCA labels and a selected trial population, so it does not match the
  tabular patient-level feature/endpoint map. [Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC10421915/).
- **AngioCAD source files:** the Zenodo record confirms the released workbook
  files but supplies no FBS unit dictionary. [Zenodo record](https://zenodo.org/records/15826856).
- **Rights:** UCI identifies its source dataset as CC BY 4.0, while the Kaggle
  70K record continues to show `Unknown`.
  [UCI license](https://archive.ics.uci.edu/dataset/45/heart%2Bdisease),
  [Kaggle dataset page](https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset).

No restricted dataset was treated as acquired, no DUA was signed, and no
third-party data owner was contacted. Any access request needs an identified
investigator and the project team's authorization.

## Work completed during this closeout

- Replaced the stale limitation table with current statuses and resolution
  actions.
- Rechecked public cohort access, the AngioCAD Zenodo workbook contents,
  Kaggle's unknown license, and UCI's CC BY 4.0 record.
- Updated the project README and roadmap to center the stated
  generalization/uncertainty goal and report its negative external reliability
  result.
- Added the user-supplied provisional author/affiliation information and
  explicitly marked all unconfirmed ethics, funding, contribution, and
  submission statements as pending in the manuscript.

For detailed evidence, see `docs/VALIDITY_AUDIT_20261105.md`,
`docs/EXTERNAL_DATA_ACCESS_PATHWAYS.md`,
`docs/LIMITATION_RESOLUTION_MATRIX.md`, and `docs/QA_REPORT.md`.
