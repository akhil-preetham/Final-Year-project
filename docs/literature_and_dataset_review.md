# Targeted literature and dataset review

**Review date:** October 26, 2026

This is a targeted review of the contribution and external-data options, not a
systematic review. The repository must not convert it into a novelty claim
without a broader database search and author review.

## Methodological findings

1. Feature-selection stability is an established methodological topic. The
   Nogueira, Sechidis, and Brown chance-corrected stability statistic is a
   suitable comparator for this project, but the statistic or resampling alone
   is not a new contribution.
2. Conformal prediction and selective prediction are also established. A
   prediction-set or abstention layer alone should not be presented as novel.
3. Recent cardiovascular work already combines uncertainty-aware prediction
   with multi-center or leave-one-center-out evaluation. Recent clinical
   conformal-prediction work also studies interpretability and distribution
   shift. Therefore, the project should not claim novelty for “uncertainty plus
   external validation” in isolation.
4. External cardiovascular validation is itself a recognized methodological
   requirement, and published reviews document substantial heterogeneity in
   transport performance. The lack of an independent cohort is therefore a
   central limitation, not a minor reporting detail.

## Narrower contribution supported by this repository

The defensible contribution is a **stability--reliability decoupling audit**:
under a leakage-controlled protocol, test whether more stable selected feature
sets actually produce better discrimination, calibration, confidence-error
ranking, or risk-coverage behavior.

This is an empirical and falsifiable contribution, not a new classifier. The
new runner uses identical repeated fit/calibration/evaluation splits for
corrected OSEC and stable OSEC, records selector stability on training data, and
reports paired reliability differences plus rank correlations.

Current internal evidence does not show a general benefit:

- Five States: stable-minus-corrected ROC-AUC difference `-0.0007`
  (95% bootstrap CI `[-0.0020, 0.0003]`); confidence-error AUC difference
  `-0.0071` (`[-0.0180, 0.0047]`); AURC difference `+0.0025`
  (`[0.0002, 0.0055]`). Positive AURC means worse selective risk.
- Mendeley: ROC-AUC difference approximately `0.0000`
  (`[-0.0007, 0.0008]`); confidence-error AUC difference `+0.0080`
  (`[-0.0111, 0.0338]`); AURC difference approximately `+0.00003`
  (`[-0.00044, 0.00047]`).

The result supports a cautious negative or mixed finding: feature-set stability
and predictive/selective reliability are not interchangeable outcomes in these
benchmarks. The finding requires replication on independent cohorts before it
can be generalized.

## External-data review

| Source | Verified role | Why it is not frozen here |
|---|---|---|
| UCI Heart Disease | Overlap/reproducibility audit | Its component sources overlap the Five States composite. |
| NHANES public-use files | Population/prevalence stress test | Outcome is typically self-reported, survey design must be respected, and feature alignment is incomplete. |
| MIMIC-IV | Long-term independent hospital validation candidate | Credentialed PhysioNet access, training, data-use agreement, phenotype construction, and feature mismatch are unresolved. |
| eICU-CRD | Multi-center ICU shift candidate | Credentialed access and ICU-specific case-mix/endpoint alignment are unresolved. |

No external dataset was downloaded, inspected for labels, or silently substituted
after seeing the internal results. The external manifest remains intentionally
unfrozen.

## Review sources

- Nogueira, Sechidis, and Brown, “On the Stability of Feature Selection
  Algorithms,” *JMLR*, 2018.
- Angelopoulos and Bates, “Conformal Prediction: A Gentle Introduction,”
  *Foundations and Trends in Machine Learning*, 2023.
- Wessler et al., “External Validations of Cardiovascular Clinical Prediction
  Models: A Large-Scale Review of the Literature,” *Circulation: Cardiovascular
  Quality and Outcomes*, 2021, DOI `10.1161/CIRCOUTCOMES.121.007858`.
- TRIPOD+AI reporting guidance for clinical prediction models.
- PhysioNet MIMIC-IV and eICU-CRD official access/documentation pages.
- CDC/NCHS NHANES official public-use and survey documentation.
