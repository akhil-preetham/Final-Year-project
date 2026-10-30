# Final experiment index

| Evidence | Script | Dataset | Protocol | Artifact |
|---|---|---|---|---|
| Compact candidate pool | `experiments/run_compact_candidate_pool.py` | Kaggle 70k | 3 outer x 2 inner, seed 42; scalable pool; fixed soft voting and inner-OOF stacking | `results/generated/kaggle70k_compact_candidate_pool.json` |
| Compact candidate pool | `experiments/run_compact_candidate_pool.py` | heart5 | 3 outer x 2 inner, seed 42; full pool including RBF SVM/KNN | `results/generated/heart5_compact_candidate_pool.json` |
| Compact candidate pool | `experiments/run_compact_candidate_pool.py` | Mendeley | 3 outer x 2 inner, seed 42; full pool including RBF SVM/KNN | `results/generated/mendeley_compact_candidate_pool.json` |
| Prior generic benchmark | `experiments/run_model_benchmark.py` | Kaggle 70k | 3 outer x 2 inner, seed 42 | `results/generated/kaggle70k_model_benchmark.json` |
| Tuned priority models and fixed OOF ensemble | `experiments/run_tuned_ensemble.py` | Kaggle 70k | 3 outer x 2 inner, seed 42; six models; fixed 1/3 ensemble | `results/generated/kaggle70k_tuned_priority_oof_ensemble.json` |
| Custom nested validation | `experiments/run_nested_validation.py` | heart5 | 3 outer x 2 inner, seed 42; five candidates | `results/generated/post_tuning_custom_nested_heart5.json` |
| Custom nested validation | `experiments/run_nested_validation.py` | Mendeley | 3 outer x 2 inner, seed 42; five candidates | `results/generated/post_tuning_custom_nested_mendeley.json` |
| Reduced custom nested validation | `src/cardiodiag/nested_validation.py` | Kaggle 70k | 3 outer x 2 inner, seed 42; corrected/stable logistic pair | `results/generated/post_tuning_custom_nested_kaggle70k_logistic_pair.json` |
| Stability/reliability linkage | `experiments/run_stability_reliability_linkage.py` | heart5 | seeds 42–46; fit/calibration/evaluation split | `results/generated/post_tuning_custom_linkage_heart5.json` |
| Stability/reliability linkage | `experiments/run_stability_reliability_linkage.py` | Mendeley | seeds 42–46; fit/calibration/evaluation split | `results/generated/post_tuning_custom_linkage_mendeley.json` |

The tuned comparison CSV is
`results/generated/kaggle70k_tuned_model_comparison.csv`. It is a derived
table from the tuned JSON artifact, not an independently rerun result.
The complete optional-booster provenance for that completed run is recorded in
`results/generated/kaggle70k_tuned_priority_oof_ensemble.provenance.json`;
the original JSON artifact predates the provenance-helper extension and was
not overwritten.

Every listed artifact records configuration and provenance metadata. The
Kaggle dataset SHA-256 is
`21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c`.
