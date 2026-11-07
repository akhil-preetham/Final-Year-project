# CARDIODIAG Master Scientific Remediation Report

**Assessment date:** 2026-11-05  
**Scientific decision:** `NO-GO` for the stated claim of reliable,
uncertainty-calibrated prediction under unseen dataset shift.  
**Engineering decision:** `GO` for a completed offline final-year research
prototype that demonstrates the workflow, preserves negative evidence, and
fails closed on unknown sites.  
**Publication decision:** `NO-GO` for journal submission until the manuscript
and author/data declarations are completed.

## Why an editor or examiner could reject the strong claim

The system has not shown that it recognizes when predictions are unreliable
on new datasets. On the only endpoint-aligned source-distinct cohort, kNN and
Isolation Forest distinguish AngioCAD from source rows weakly (AUROC 0.580 and
0.579). The post-hoc integrated selective rule outputs on only 5.6% of
AngioCAD; its 21 accepted cases are all positive, so the zero observed errors
do not establish useful risk control. The trusted-domain gate withholds all
377 AngioCAD and all 3,504 Duke scores because neither site is registered.
That is an honest fail-closed safety boundary, not evidence that the model
predicts on unseen sites.

Calibration is not dependable across shift. AngioCAD calibrated ECE is 0.216
in the primary run. Duke's different >=75% outcome cohort has AUC 0.661 and
source Platt scaling worsens Brier and ECE. One post-hoc external cohort, even
with a conditional bootstrap interval, cannot estimate variability between
hospitals. More tuning on the already examined AngioCAD outcomes would add
selection bias, not evidence.

## Direct answers to the ten decision questions

| Question | Answer | Evidence and consequence |
|---|---|---|
| 1. Has the original CARDIODIAG method been faithfully reproduced? | **No.** | Percentile rules, LoRAS settings, LIME/PCA logic, ensemble learners, splits, and table lineage conflict or are missing. The historical implementation is an approximation; the corrected pipeline is separate. |
| 2. Has leakage been adequately controlled? | **For the corrected audited paths, largely yes.** | Transformations and model selection are training/fold-local; external fit/calibration uses source rows only; target labels are evaluation-only. Historical notebook outputs include leakage-prone paths and remain historical. This does not validate the estimand or labels. |
| 3. Does the model generalize to independent external datasets? | **Not established.** | AngioCAD is one site, post-hoc in later studies, and patient-level overlap cannot be ruled out. Duke and Z-Alizadeh Sani are endpoint-mismatched stress tests. No untouched endpoint-compatible cohort is available. |
| 4. Does feature-based OOD detection work? | **Not usefully demonstrated.** | AngioCAD kNN/IF AUROCs are 0.580/0.579; the FBS-excluded age/sex replay has IF AUROC 0.544, conditional on an unverified age-as-years mapping. LODO values vary substantially. The site registry uses trusted metadata, not feature recognition. |
| 5. Is calibration reliable under dataset shift? | **No.** | AngioCAD ECE is 0.216 in CD-XD-004; Duke Brier/ECE worsened after source Platt scaling. Source exchangeability does not guarantee external calibration. |
| 6. Does selective prediction provide useful coverage? | **No evidence of useful coverage.** | AngioCAD registered combination covers 5.6% (0/21 errors, one observed class); Duke covers 11.4% with 10.2% accepted error. The unknown-site gate covers 0%. |
| 7. Is the system suitable for a clinical deployment claim? | **No.** | No clinical workflow, prospective study, clinical utility, human factors, or regulatory validation is present. The project is an offline research prototype. |
| 8. What is the actual research contribution? | **A reproducible, provenance-aware evaluation with negative reliability findings.** | The work separates source-only calibration, feature-only shift diagnostics, selective coverage, and metadata gating, and documents when transport claims fail. No novel prediction algorithm is established. |
| 9. Which limitations remain unresolved? | **New cohorts and source/team facts.** | Independent endpoint-compatible validation; AngioCAD missing 36 features and FBS unit; Mendeley endpoint/timing; person-level linkage; exact original reconstruction; full A--L factorial; data rights; author/ethics/funding/venue metadata. |
| 10. Is the manuscript suitable for journal submission? | **No, not yet.** | See `SUBMISSION_READINESS_REPORT_20261105.md`; manuscript needs synchronized results and confirmed author, ethics/data-use, funding, conflicts, approval, and venue declarations. |

## Corrective work completed in this remediation pass

1. Reconciled frozen OOD threshold counts and AUROC from saved prediction CSVs
   using round-trip float parsing; no tie or threshold error remained.
2. Added an independent AngioCAD matching audit with the 36 unmatched public
   IDs, exact hashes, duplicate checks, one-to-one ID join, missingness, and a
   row-order counterfactual (only 27/377 positionally aligned IDs).
3. Marked AngioCAD FBS as unusable for unit-verified primary harmonization;
   preserved an FBS-excluded post-hoc age/sex sensitivity while recording that
   age-as-years is still provisional; corrected the 26--50 feature/label
   confusion.
4. Audited all 13 Mendeley predictors plus the identifier and outcome from its
   checked-in codebook and source article. Mendeley remains a retrospective
   benchmark with undocumented reference standard and timing.
5. Added a seven-subset age/sex/FBS post-hoc ablation and an audit comparing
   frozen policy components. These describe already examined targets and do
   not select a new model or threshold.
6. Added the original-method reconstruction matrix, A--L workstream crosswalk,
   statistical consistency report, author checklist, and journal readiness
   decision.

Only kNN support and Isolation Forest have frozen quantitative OOD comparisons.
Mahalanobis/shrinkage covariance, LOF, MMD, domain-classifier/density-ratio,
and explicit range/missingness monitors were not all implemented or compared.
This remains a limitation; already inspected AngioCAD labels cannot be used to
select a detector and then provide confirmatory evidence. See
`docs/OOD_METHOD_SELECTION_AUDIT_20261105.md`.

## Evidence needed to change the `NO-GO` research conclusion

- An untouched, endpoint-compatible cohort from a separate institution with
  provenance, feature dictionary, reference-standard description, legal
  access, and a one-way frozen evaluation protocol.
- Additional independent sites to estimate site-level variability; one cohort
  is insufficient for broad generalization.
- A feature set with measurement units, timing, and availability at the
  declared prediction time documented. For AngioCAD, obtain the FBS unit and
  reason for missing feature rows or exclude those records/fields as specified.
- Evaluation of calibrated probabilities and selective risk on the new cohort
  without using its labels for threshold or model selection.
- Exact historical source settings if the paper claims faithful reproduction.
- Author/institution facts for manuscript declarations.

These dependencies cannot be solved by synthetic records, repeated analysis
of the same target labels, or relabeling the current prototype. The correct
outcome is to retain the project as a rigorous negative engineering result
until new evidence changes the conclusion.

## Local remediation closeout

The locally addressable remediation is complete. The manuscript was updated
with the unmatched-ID and unit findings, predictor-timing audit, seven-subset
AngioCAD sensitivity, frozen selective-policy comparison, and an explicit
research `NO-GO` conclusion. Tectonic 0.17.0 produced a 14-page PDF; all pages
were rendered, every page was reviewed in the contact sheet, dense pages 4, 5,
13, and 14 were inspected at full size, and text extraction succeeded on all
14 pages. The source and result-input hashes, page renders, contact sheet, and
PDF hashes are recorded in
`paper/build/research_draft_20261105_remediation/publication_manifest.json`.

The full repository suite collected 106 tests and passed. `ruff check .`,
Python bytecode compilation, and `uv lock --check` passed. The TeX build has no
overfull boxes or unresolved references; it still reports underfull spacing,
font fallback, and the desktop runtime's missing Fontconfig configuration.
These software and artifact checks establish reproducibility of this local
prototype, not the generalization claim. The deliverable is complete as a
negative engineering result; new endpoint-compatible external data and
unconfirmed author/institution facts remain external blockers, so research and
submission decisions stay `NO-GO`.
