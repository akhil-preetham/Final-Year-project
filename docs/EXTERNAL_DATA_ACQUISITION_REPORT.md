# External data acquisition and compatibility report

**Updated:** 2026-11-07. Only public datasets with official CC BY 4.0 source records were downloaded. No restricted dataset was accessed, no account or DUA was submitted, and no external party was contacted.

| Candidate | Access/provenance | Endpoint and feature compatibility | Disposition |
|---|---|---|---|
| South African Heart Disease / SAheart (462 records) | Public educational/research dataset has several derivative mirrors; source is described as a retrospective high-risk male sample from Western Cape | Baseline CHD status, not the source angiographic greater-than-50% endpoint; predictors include age, systolic BP, tobacco, LDL, adiposity, family history and alcohol. It is not a clean second site with the same measurement timing or endpoint. | Do not claim endpoint-compatible validation. Could be a separately labelled risk-factor domain stress test after provenance/license verification. |
| Framingham Heart Study | Clinical data are accessed through BioLINCC or the FHS Research Application; PI proposal and applicable IRB/ethics review are part of access pathways | Longitudinal incident cardiovascular outcomes; outcome horizon, inclusion criteria and predictor timing require a new protocol. It is not a plug-in angiographic-CAD cohort. | Strong candidate for a redesigned longitudinal risk question, BLOCKED on PI, ethics and data request. |
| MIMIC-IV / MIMIC-IV-Ext Cardiac Disease | Credentialed PhysioNet access; credentialing, human-subject training and signed DUA required | EHR diagnosis-code cohorts, with possible broad cardiac rather than angiographic stenosis endpoint; patient-level feature extraction and temporal label definition would require substantial redesign. | Not acquired; BLOCKED on credentialing/DUA and endpoint redesign. |
| Existing AngioCAD | Public files already evaluated | One endpoint-aligned site, 377 matched feature rows from 413 labels; no cross-source person IDs, FBS units undocumented | Already examined; cannot serve as a new untouched confirmation cohort. |
| MultiD4CAD | Restricted access with DUA requirement recorded locally | 118 single-site CCTA cases; endpoint comparability to invasive angiographic greater-than-50% CAD not established | Do not request/access without institutional investigator, DUA, and endpoint confirmation. |
| UCI Heart Failure Clinical Records (ID 519) | Official UCI ZIP downloaded 2026-11-07; DOI `10.24432/C5Z89R`; CC BY 4.0. Hash and attribution in `data/manifests/uci_heart_failure_519.json`. | 299 HF records; target is death by end of each patient's available follow-up. A common prediction horizon is not specified; source `time` is excluded from predictors. | Acquired and evaluated as separate exploratory binary event classification; not CAD validation. Raw data remain outside Git. |
| UCI Myocardial Infarction Complications (ID 579) | Official UCI ZIP downloaded 2026-11-07; DOI `10.24432/C53P5M`; CC BY 4.0. Hash and attribution in `data/manifests/uci_mi_complications_579.json`. | 1,700 records; UCI defines allowed predictors for admission/day 1/day 2/day 3. This run uses admission and excludes later fields, every other outcome column, ID, and two contemporaneous outcome-proxy features. | Acquired and evaluated as a separate exploratory task; not CAD validation. Raw data remain outside Git. |
| Nasarian CAD Dataset (UCI ID 557) | Official record DOI `10.24432/C5BC96`, CC BY 4.0; UCI dataset-file entry is `-` and download is 0 bytes. | 150 all-male occupational-clinic records according to UCI; no official data bytes available. | Not acquired or run. No mirror was used; representativeness would also be limited. |

The South African cohort is described as 462 records with 9 predictors and baseline CHD status in the [CRAN ncvreg data documentation](https://pbreheny.github.io/ncvreg/reference/Heart.html); a peer-reviewed application likewise describes it as a CHD classification task ([Khdair and Dasari, 2021](https://thesai.org/Publications/ViewPaper?Code=IJACSA&Issue=5&SerialNo=5&Volume=12)). This does not demonstrate endpoint equivalence to invasive coronary stenosis.

Framingham states that clinical data access is through BioLINCC or a research proposal and provides data catalogs and coding manuals ([available data](https://www.framinghamheartstudy.org/fhs-for-researchers/data-available-overview/), [application FAQ](https://www.framinghamheartstudy.org/fhs-for-researchers/research-application/research-application-faq/)). BioLINCC Gen III listing requires full or expedited IRB/ethics review ([BioLINCC listing](https://biolincc.nhlbi.nih.gov/studies/gen3/)).

PhysioNet states that MIMIC requires credentialing, approved training and a signed data-use agreement, and that individual access cannot be shared ([PhysioNet access FAQ](https://physionet.org/about/faqs/), [MIMIC-IV DUA](https://www.physionet.org/content/mimiciv/view-dua/3.0/)). These requirements cannot be bypassed by local code.

## Concrete acquisition protocol

1. Ask a faculty PI/institution to determine ethics review and data-controller eligibility.
2. Choose the scientific endpoint before selecting a cohort: angiographic stenosis versus incident clinical events are different studies.
3. Review the official codebook, predictor times, units, label adjudication, missingness, inclusion criteria and licenses.
4. Obtain lawful access and document patient/site independence and overlap.
5. Build a frozen adapter and label mapping; run schema and event-count checks before training.
6. Freeze the existing model, calibration, and thresholds before a one-way evaluation.

**Disposition:** A second independent endpoint-compatible CAD site was not acquired. The HF and post-MI datasets support distinct exploratory tasks and do not validate the angiographic-CAD model. Framingham and MIMIC require institutional/access steps and likely a redefined endpoint; SAheart is not endpoint-compatible. The Nasarian official record supplies no file bytes. The central CAD external-generalization claim remains unestablished.
