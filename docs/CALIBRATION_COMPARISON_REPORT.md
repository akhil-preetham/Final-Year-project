# Source-fitted calibration comparison

**Run:** 2026-11-06  
**Data:** frozen CD-XD-004 AngioCAD and source-calibration prediction CSVs.  
**Status:** exploratory post-hoc secondary analysis; not confirmatory and not a policy-selection study.

## Protocol

Five calibration candidates were fitted using the 185 source-calibration predictions only: the archived source Platt map, refitted Platt, isotonic regression, beta calibration, and scalar temperature scaling. All fitted maps used equal total weight per source cohort, matching CD-XD-004. The uncalibrated output is the baseline. The 377 AngioCAD labels were used only for fixed retrospective metrics and class-stratified bootstrap intervals (2,000 replicates, seed 20261105). No map or threshold was selected using AngioCAD labels.

The refit Platt map reproduces the frozen map to rounding, serving as a protocol consistency check. The comparison runner, source predictions, target predictions, metrics, calibration curves, and hashes are in results/second_stage_calibration_20261106_stratified/ and experiments/compare_source_calibrators.py.

## Results

| Method | Brier (95% bootstrap CI) | Log loss | 10-bin ECE | Calibration intercept / slope |
|---|---:|---:|---:|---:|
| Uncalibrated | 0.1898 (0.1841–0.1955) | 0.5686 | 0.2108 | 0.339 / 4.146 |
| Frozen source Platt | 0.1851 (0.1702–0.1996) | 0.5477 | 0.2160 | 1.219 / 1.437 |
| Refit source Platt | 0.1851 (0.1710–0.1993) | 0.5477 | 0.2160 | 1.219 / 1.437 |
| Source isotonic | 0.1969 (0.1810–0.2131) | 0.7442 | 0.2319 | 1.277 / 0.361 |
| Source beta | 0.1849 (0.1705–0.2001) | 0.5473 | 0.2156 | 1.216 / 1.428 |
| Source temperature | 0.1605 (0.1515–0.1695) | 0.4975 | 0.1473 | 0.339 / 2.173 |

ROC-AUC is unchanged by the monotone Platt, beta, and temperature maps (0.7868); isotonic changed ties/ranking slightly (0.7674). AngioCAD prevalence is 79.0% (298/377), while source-temperature mean predicted risk is 64.5%. Temperature fitted on source calibration learned T=0.524 and sharpened probabilities. It had the best fixed-target scores here, but target calibration slope remains 2.17 and this result is conditional on one previously examined site. Do not claim temperature scaling solves transport calibration or select it for deployment from this retrospective cohort.

## Interpretation and unresolved methods

- Isotonic's poor transfer is consistent with an overly flexible nonparametric map fitted on a small calibration sample; no claim of general superiority is made.
- Beta and Platt are nearly indistinguishable in this setting.
- Source-only temperature scaling is a promising candidate for a new preregistered evaluation; current target metrics cannot confirm it.
- Prevalence/label-shift correction was not fitted because target prevalence is label-derived here, and unlabeled target-prior estimation would require a separate justified protocol and assumptions such as stable class-conditional score distributions.
- Domain-specific Platt maps are not directly transferable to an unknown site without a defensible mapping or target calibration data.
- Target-labelled calibration is not confirmatory: this entire external cohort has already been inspected. A fresh within-cohort adaptation/evaluation split would only be post-hoc feasibility evidence.
- Confidence intervals are descriptive class-stratified bootstrap intervals on one cohort, not between-hospital uncertainty. Calibration-in-the-large/slope are evaluation summaries and do not indicate a fitted target calibrator.

This interpretation follows the calibration literature's caution that isotonic can overfit small samples and that model updating/calibration requires an explicit shift assumption. See [Beta calibration (Kull et al., AISTATS 2017)](https://proceedings.mlr.press/v54/kull17a.html), [Unified framework on generalizability of clinical prediction models](https://pmc.ncbi.nlm.nih.gov/articles/PMC9100692/), and [BMJ external validation guidance](https://www.bmj.com/content/384/bmj-2023-074820).
