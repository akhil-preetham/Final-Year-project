# CARDIODIAG independent project review

**Updated:** 2026-11-05
**Scope:** offline final-year research engineering project; clinical deployment
is not a completion requirement.

## Decision

The engineering prototype is complete and reproducible. It trains on multiple
source cohorts, performs source-only transfer and uncertainty analyses, and
fails closed when a site is not registered. The project's central empirical
claim is deliberately bounded: it does **not** establish reliable prediction,
calibration, or feature-only recognition of arbitrary unseen sites.

The corrected code path has no direct target, identifier, or fold leakage in
the audited runs. The paper and research package are valid as an engineering
evaluation with negative findings, provided they do not claim broad
generalization or a new prediction algorithm.

## Evidence

The fresh 3x3 internal run stores predictions and split indices for all 918
Heart5 rows and 1,000 Mendeley rows; its fold means match the prior authoritative
stage. Corrected OVEC AUC was 0.9295 on Heart5 and 0.9957 on Mendeley. These are
internal replication results, not independent transport evidence.

The primary endpoint-aligned external study, CD-XD-004, trained on four UCI
source cohorts and tested AngioCAD from a distinct hospital. Among 377 matched
records, AUC was 0.7868 (95% class-stratified interval 0.734–0.838), calibrated
Brier was 0.1851, ECE was 0.216, and feature-only OOD AUROC was 0.589
(0.541–0.635). Predictions reproduce byte-for-byte and independent metrics
match saved artifacts. The later CD-XD-006 policy replay and FBS sensitivity
reuse the same target and are post hoc. The feature-based warning is weak;
the site-metadata gate withheld all scores for unknown sites.

Z-Alizadeh Sani (AUC 0.720) and Duke ACATH (AUC 0.661) are endpoint-mismatched
stress tests. Statlog duplicates Cleveland. A 2026 Mendeley dataset duplicates
the 918-row Heart5 table. No new untouched endpoint-compatible public cohort
was found in the follow-up search.

## Remaining work and why

| Item | Current state | Why it cannot be closed locally | Best next action |
|---|---|---|---|
| Multi-site confirmatory evaluation | Open | CARDIIGAN reports 4,888 patients but says additional data are unavailable; the 2026 APPROACH/Ottawa/UHN paper is a restricted study protocol, not public patient-level data. | Obtain authorized data through a research partner/DUA, verify endpoint and overlap, freeze the evaluation, then test untouched sites. |
| Mendeley target standard and feature timing | Open | Its public codebook specifies presence/absence but no diagnostic reference standard or timing. A same-split ablation excludes the fluoroscopy-derived major-vessel field; it cannot identify the other feature timings or label procedure. | Get source documentation/author confirmation, or retain this dataset only as a retrospective replication benchmark. |
| AngioCAD FBS unit and 36 unmatched records | Open | The Zenodo workbooks expose FBS values but no unit dictionary; labels exist for 413 IDs while features match only 377. | Ask the source authors for the data dictionary and missing rows. The age/sex-only sensitivity is already recorded but is post hoc. |
| Patient-level cross-dataset overlap | Open | Public files contain no common person identifier. | Seek privacy-preserving linkage or a data-controller attestation; avoid asserting person-level independence without it. |
| Exact original-paper reproduction | Open | The notebooks conflict on preprocessing, split, resampling, model/search settings, and table lineage; LoRAS parameters/environment are not frozen. | Obtain the original executable environment and artifact mapping. Keep the current historical run labelled an approximation. |
| Complete original A–L factorial | Partial | Existing comparisons cover corrected baselines, OVEC/OSEC, stable selection, AURA, calibration and selective prediction, but not all original-method branches in one common experiment. Original LoRAS/LIME branches cannot be reconstructed from available materials. | Limit conclusions to the matched comparisons that exist; run further common-fold ablations only for implementable, defined components. |
| Licensing and redistribution | Partial | Official UCI source data are CC BY 4.0, but the derived Heart5 file lacks its own notice/transformation history; the official Kaggle 70K page reports `Unknown`. Historical packages include 70K-derived outputs. | Keep new public bundles data-free until rights are reviewed; obtain the composite and 70K rights from the owners before redistributing data or derived outputs. |
| Submission metadata | Partial | Author names and one shared affiliation were supplied provisionally. Author order and each author's affiliation, ethics/data-use, funding, contributions for two coauthors, competing interests, and target journal remain unconfirmed. | Confirm the facts with all authors and the institution, then apply the selected venue's current instructions. |

The complete status/evidence/next-step table is in
`docs/REMAINING_WORK_REGISTER_20261105.md`; limitation disposition is in
`docs/LIMITATION_RESOLUTION_MATRIX.md`.

## Verification

The latest recorded suite passes all 106 collected tests. Ruff, compilation, dependency-lock,
independent transfer/sensitivity audits, dataset/result hashes, and the
current manuscript build pass. A follow-up search found access leads but no
new publicly downloadable endpoint-compatible multi-site cohort. See
`docs/QA_REPORT.md`, the remaining-work register, and the current publication
manifest.
