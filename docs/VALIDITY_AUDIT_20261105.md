# CARDIODIAG engineering validity audit

**Audit date:** 2026-11-05  
**Scope:** validity of the engineering research claims, dataset handling,
evaluation code, and paper interpretation. Clinical deployment is outside this
project's stated engineering scope and is not a completion gate here.

## Decision

The software and saved results support a **reproducible exploratory engineering
prototype**. No direct target-column, identifier, or cross-fold preprocessing
leakage was found in the corrected pipeline. The results do **not** support the
stronger claims that the model reliably detects unseen dataset shift, has
dependable external calibration, or generalizes across sites. A paper making
those stronger claims would be invalidated by the evidence currently available.

The Mendeley score near 0.995 is not explained by its potentially
post-diagnostic fluoroscopy variable alone: removing `noofmajorvessels` changed
five nested fold-mean AUCs by only +0.0003 to +0.0007. That does not resolve the
dataset's undocumented target reference standard or establish when its other
features were measured. It remains a retrospective benchmark, not early-
detection evidence.

## Threats that could invalidate a claim

| Threat | Evidence and consequence | Action taken | Remaining limit / best resolution |
|---|---|---|---|
| Predictor available only after diagnosis | The Mendeley source article maps `noofmajorvessels` to the number of major vessels seen by fluoroscopy. Its timing relative to the target is not documented. An early-detection claim using it would be invalid. | Added a same-split, three-outer/three-inner-fold run excluding the field. All five candidates remained near their full-feature AUCs; see the generated table and results JSON below. Manuscript now calls Mendeley retrospective replication evidence. | Timing of the other Mendeley features and the original target-label procedure cannot be reconstructed from this release. Obtain source documentation or keep the dataset out of prediction-time claims. |
| Unknown Mendeley reference standard | The source codebook defines only disease absence/presence; it does not identify the diagnostic procedure or stenosis threshold. High CV AUC therefore does not establish prediction against a known disease endpoint. | Dataset compatibility notes and manuscript now state the target limitation and prohibit pooling it with the UCI/AngioCAD angiographic endpoint. | Resolve only with a definitive source data dictionary or author confirmation. Otherwise retain as a benchmark with an unspecified label construct. |
| Undocumented AngioCAD FBS unit | The workbook has numeric FBS values but no unit. The primary mapping assumes mg/dL from the value range. A wrong unit could alter the binary threshold. | Added a source-only age/sex sensitivity run using the same source splits. AUC was 0.787 with FBS and 0.788 without it; calibrated Brier was 0.185 versus 0.176. This shows similar ranking in this examined cohort, not that the unit is known. | Ask the dataset authors for the workbook data dictionary or use a predeclared predictor set that omits FBS. The sensitivity is post hoc because AngioCAD outcomes were already examined. |
| External reliability and OOD claim | On AngioCAD, the feature-only source/target OOD AUROC was 0.589 (95% conditional bootstrap interval 0.541–0.635). The age/sex-only sensitivity was 0.544 (0.496–0.592). Neither supports useful feature-only shift detection. Source-calibrated ECE was 0.216 in the primary run. | Reframed the result as a negative reliability finding. The trusted-domain registry gate is described as metadata-based fail-closed behavior, not learned OOD recognition. | Develop any new detector using source-only/domain-held-out data and evaluate on additional untouched target sites. Do not use AngioCAD to tune and then call it confirmation. |
| Target reuse / post-hoc analysis | AngioCAD was scored in CD-XD-004, then revisited in CD-XD-006 and the FBS sensitivity. CD-XD-006 and this sensitivity are not fresh confirmation. | Manuscript and manifests identify them as post hoc. The primary CD-XD-004 analysis remains distinct from the replay and is not presented as universal transport evidence. | A new target dataset is needed for confirmatory testing after method freeze. Re-analysis of the same labels cannot restore independence. |
| Too few independent target sites | The only endpoint-aligned source-distinct cohort analyzed here is one hospital with 377 matched records. Z-Alizadeh Sani and Duke have different thresholds. Bootstrap intervals condition on this cohort's 79 negatives and 298 positives; they cannot estimate between-site variance. | Results and intervals are labeled as one-site transport evidence. Dataset compatibility records show why the other cohorts cannot be combined as equivalent targets. | Acquire multiple independent, endpoint-compatible cohorts and freeze the mapping/model before labels are viewed. Public data or a data-sharing partner are required; no code change can create this evidence. |
| Patient overlap is not provably excluded | Site provenance differs between UCI and AngioCAD, but the releases do not provide common person identifiers. Heart5 also contains rows from the UCI components used as source data. | Heart5 is restricted to internal development/replication; UCI leave-one-source-out is labeled retrospective. AngioCAD is described as source-distinct at site level, with patient-level linkage unverified. | Obtain privacy-preserving linkage from data controllers or author confirmation. Without it, avoid asserting person-level independence. |
| Missing target predictors | AngioCAD labels include 413 IDs, but only 377 have clinical-feature rows. The missing 36 could differ systematically from matched patients. | Analysis cohort is explicitly restricted to the 377 matched rows and target counts are reported. | The absent predictors cannot be imputed from this release. Request missing feature rows or report the restricted cohort and its selection risk. |
| Novel algorithm claim | Logistic regression, Platt scaling, Isolation Forest, conformal prediction, and feature selection are established methods. The evaluation did not show a consistent advantage for the proposed selector. | Manuscript states that no new algorithm is claimed and frames the contribution as a reproducibility/reliability evaluation with negative findings. | Keep the claim at protocol/evidence level unless a systematic literature review and a genuinely new method justify more. |
| Code or fold leakage | `load_dataset` separates the binary target; identifier columns are dropped. Corrected transforms and selectors are inside model pipelines; hyperparameter selection is inside inner folds. AngioCAD target fields are excluded from predictors. | Added checks that feature exclusions preserve schema metadata and reject absent columns. The sensitivity audit verifies same outer splits/labels and exactly-once scoring for every Mendeley row. External sensitivity metrics were recomputed from saved predictions. | No code-level leakage was found in the audited path. Original historical scores involving preprocessing before split remain historical artifacts and are not treated as corrected evidence. |
| Small effective replication and intervals | Internal Mendeley/Heart5 evidence uses one three-fold outer partition; fold SD and bootstrap on out-of-fold predictions do not capture all training or site variability. External intervals condition on class counts. | Manuscript labels internal fold summaries descriptive and external bootstrap intervals conditional. | Use more independent source cohorts and untouched target sites; do not interpret these intervals as population/site confidence intervals. |
| Data access and redistribution | The upstream license for the Heart5 composite is not supplied and the Kaggle 70K listing reports unknown licensing. This does not erase local analysis, but sharing those raw files or derived bundles may violate terms. | Existing distribution audit flags these files and avoids claiming rights. | Obtain upstream permissions or distribute only code, hashes, and legally cleared data instructions. This is a release constraint, not a model-performance fix. |

## Reproducible fixes and evidence

The corrected nested runner now supports repeated `--exclude-feature` options,
records excluded columns in its configuration and provenance, and fails on
unknown names. The Mendeley experiment used the same seed-42 outer and inner
splits as the saved full-feature run; all 1,000 rows were tested exactly once.
The five fold-mean AUC differences were +0.0003, +0.0003, +0.0007, +0.0003,
and +0.0006. Therefore, the major-vessel variable is a timing/estimand risk,
but removing only that field does not explain the very high Mendeley score.

The FBS-free AngioCAD run reused the original source-fit/calibration partitions
and logistic/Platt/Isolation Forest settings. It withheld FBS from both source
and target predictors. A standalone audit checked target IDs and labels, source
splits, recomputed raw and calibrated metrics from the saved prediction files,
and recomputed OOD AUROC from source and target scores. The audit passed.

## Scientific remediation addendum (2026-11-05)

The separate seven-subset age/sex/FBS comparison is stored under
`results/interpretability_posthoc_20261105/angiocad_feature_ablation/`. It is
strictly post hoc: AngioCAD target labels had been examined, all seven
comparisons are unadjusted, and the target is not a fresh validation set. The
age-plus-sex AUC was 0.788 versus 0.787 with FBS added, with a paired AUC
difference of -0.0009 (95% conditional bootstrap interval -0.0060 to 0.0048).
This does not validate FBS units. The feature workbook also lacks an age unit;
age-as-years remains an explicit assumption even in the FBS-excluded replay.

`experiments/audit_angiocad_compatibility.py` independently confirms a
one-to-one ID merge: 377 feature rows matched, 36 label IDs lacked feature
rows, and only 27/377 rows would align under a naive position-by-position
join. The reason for the 36 absent features is not present in the public
record/workbooks. The audit and all unmatched IDs are in
`results/data_provenance_audits/angiocad_compatibility/`.

`experiments/audit_selective_policy_components.py` now recalculates alert
counts and AUROCs from saved CSVs using round-trip float parsing. The apparent
one-ULP count discrepancy from default CSV parsing was an import-precision
artifact; no threshold tie or stored-result error was found. The component
audit shows 5.6% integrated coverage on AngioCAD, 11.4% on Duke, and 0%
unknown-site gate coverage. The AngioCAD accepted set contains only positives
(21/21), so its zero observed errors do not establish useful selective risk.
Target-scored results are post hoc and descriptive.

The full Mendeley codebook review is recorded in
`docs/MENDELEY_PREDICTOR_PROVENANCE_AUDIT_20261105.md`. All 13 predictors, the
identifier, and the target are classified; no field has documented timing
relative to the outcome. The target reference standard remains unspecified,
and test-derived fields prevent early-detection claims.

The FBS-excluded AngioCAD map
`data/manifests/angiocad_fbs_excluded_mapping_v1.json` is a future-facing
conservative mapping proposal, not a new locked confirmatory model. It retains
age-as-years as provisional and excludes FBS until units are sourced. Detailed
methods, A--L workstream crosswalk, and publication decision are in
`docs/ORIGINAL_REPRODUCTION_MATRIX_20261105.md`,
`docs/ABLATION_A_L_MATRIX_20261105.md`, and
`docs/SUBMISSION_READINESS_REPORT_20261105.md`.

Reproduce the changes from the repository root:

```powershell
uv run python experiments\run_nested_validation.py `
  --dataset MendeleyCardiovascular_Disease_Dataset.csv `
  --target target --exclude-feature noofmajorvessels `
  --outer-splits 3 --outer-repeats 1 --inner-splits 3 --seed 42 `
  --output results\validity_audit_20261105\mendeley_without_major_vessels.json

uv run python experiments\run_angiocad_fbs_sensitivity.py `
  --output-dir results\validity_audit_20261105\angiocad_without_fbs_reproduction
uv run python experiments\audit_validity_sensitivities.py `
  --angiocad-dir results\validity_audit_20261105\angiocad_without_fbs_reproduction `
  --output results\validity_audit_20261105\validity_sensitivity_reproduction_audit.json
```

Artifacts:

- Mendeley feature-exclusion result: `results/validity_audit_20261105/mendeley_without_major_vessels.json`
- AngioCAD age/sex predictions and manifest: `results/validity_audit_20261105/angiocad_without_fbs_final/`
- Independent sensitivity audit: `results/validity_audit_20261105/validity_sensitivity_audit.json`
- Manuscript tables: `paper/tables/validity_sensitivity_mendeley.tex` and `paper/tables/validity_sensitivity_angiocad.tex`

## Engineering-project status

No hospital workflow, clinical trial, regulatory review, or clinical-use gate
is required to complete the stated engineering project. The working code and
demonstration are valid as an offline research prototype. The strongest paper
claim that survives this audit is: *a reproducible, source-only transfer and
reliability evaluation was implemented; one endpoint-aligned site had
moderate ranking performance but poor calibration and weak feature-only shift
detection, while selective/unknown-site handling remains conservative and has
low useful coverage.*

Claims that broad generalization, dependable calibration, feature-only OOD
detection, early-stage diagnosis, or a novel prediction algorithm were
established would be invalid. The remaining blockers are evidence/data
limitations and require source documentation or new independent cohorts, not
further tuning on already examined target labels.
