# Calibration and uncertainty report

The frozen run includes Brier score, ten-bin expected calibration error, split-conformal prediction sets and source-only 95th-percentile feature-support thresholds. ECE depends on binning; estimates from small held-out partitions are noisy. Conformal coverage depends on calibration/evaluation exchangeability, which is not established under cohort shift.

## Split-conformal coverage

| nominal_coverage | empirical_coverage_min | empirical_coverage_mean | empirical_coverage_max | average_set_size_mean | group_n |
| --- | --- | --- | --- | --- | --- |
| 0.800 | 0.529 | 0.815 | 0.951 | 1.081 | 114 |
| 0.900 | 0.791 | 0.920 | 1.000 | 1.383 | 114 |
| 0.950 | 0.898 | 0.973 | 1.000 | 1.700 | 114 |

There are 114 task/model/fold combinations per nominal level, including a single official test for SPECTF. Mean empirical coverage is pooled over heterogeneous tasks and must not be read as a global guarantee. Class-conditional coverage and set-size diagnostics are reported per row in `metrics/conformal_metrics.csv`; the 90% level can be compared with the frozen primary table at `metrics/source_conformal_metrics_90.csv`.

![Conformal coverage by nominal level](../results/final_research_20261108/figures/conformal_coverage_80_90_95.png)

No calibrated clinical threshold is established. The uncertainty results support only retrospective method diagnostics.

<!-- DUPLICATE_SAFE_CONFORMAL START -->
## Duplicate-safe conformal sensitivity

For Hungary and VA Long Beach, the exact duplicates were removed before folds and calibration sets were formed. At nominal levels, the mean empirical coverage across the two datasets, six models and three folds is:

- 10%: mean 0.909, range 0.806–1.000

These finite-sample estimates remain conditional on exchangeability; the re-created splits are not the original calibration/test partitions.
<!-- DUPLICATE_SAFE_CONFORMAL END -->
