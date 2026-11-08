# Computational performance report

The current measurements refit the saved selected configuration once per task/model/fold, time batch prediction, and record uncompressed serialized pipeline size. They exclude hyperparameter search from the refit timing. The source run separately records total search/calibration runtime. Values depend on the recorded Windows environment and package versions.

| model | median_fit_s | median_us_per_row | median_pipeline_bytes |
| --- | --- | --- | --- |
| knn | 0.046 | 333.063 | 34327.000 |
| logistic | 0.051 | 184.969 | 9407.000 |
| osec | 1.571 | 332.620 | 90504.000 |
| ovec | 0.511 | 518.978 | 1101566.000 |
| random_forest | 0.465 | 356.499 | 607062.000 |
| svm | 0.046 | 269.790 | 30011.000 |

The historical 70K tuned benchmark took about 5.6 s for Logistic Regression, 227.3 s for Random Forest, 51.3 s for HistGradientBoosting, 33.4 s for XGBoost, 16.5 s for LightGBM and 48.2 s for CatBoost. The full custom five-candidate 70K nested run was not completed. Peak memory was not instrumented, and timing differences are not benchmark-grade cross-hardware comparisons. See `metrics/runtime_metrics.csv`, `tables/runtime_summary_by_model.csv`, and `figures/runtime_inference_latency.png`.
