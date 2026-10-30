# Model research landscape

This document records the candidate families considered for the CARDIODIAG
benchmark. The primary generic benchmark is an available-package comparison,
not a claim that every modern tabular family was evaluated. Optional-family
citations and links below are provided for protocol planning; they were not
used to manufacture results for unavailable dependencies.

| Family | Rationale | Current environment | Decision |
|---|---|---|---|
| DummyClassifier | Sanity baseline for prevalence-only performance | scikit-learn available | Include |
| Logistic regression | Strong interpretable linear baseline and calibration reference | scikit-learn available | Include |
| LDA | Classical low-complexity discriminant baseline | scikit-learn available | Include |
| Gaussian NB | Simple probabilistic baseline | scikit-learn available | Include |
| Random Forest / Extra Trees | Established bagging tree baselines | scikit-learn available | Include |
| HistGradientBoosting | Efficient native tabular boosting in scikit-learn | scikit-learn available | Include |
| Gradient Boosting / AdaBoost | Established boosting baselines | scikit-learn available | Include |
| XGBoost | Widely used regularized gradient boosting; official package installed | xgboost 3.2.0 available | Include |
| CatBoost | Strong categorical-aware boosting; requires separate dependency and license review | 1.2.10 installed and evaluated | Include in bounded tuning |
| LightGBM | Efficient gradient boosting; requires separate dependency and license review | 4.7.0 installed and evaluated | Include in bounded tuning |
| Explainable Boosting Machine | Interpretable generalized additive boosting | `interpret` unavailable | Defer |
| MLP | Neural tabular challenger with explicit regularization | scikit-learn available | Include |
| TabM | Modern tabular deep-learning challenger | PyTorch/official package unavailable | Defer |
| TabPFN / TabICL | Foundation-model challengers with dataset-size and API constraints | unavailable; 70k full run requires separate feasibility audit | Defer |

Optional families are not installed blindly. Their inclusion requires verified
primary sources, official documentation, API compatibility, license review,
and a separate runtime/sampling protocol.

## Primary sources and implementation references

- XGBoost: Chen and Guestrin, “XGBoost: A Scalable Tree Boosting System,”
  KDD 2016, DOI `10.1145/2939672.2939785`,
  [official documentation](https://xgboost.readthedocs.io/).
- CatBoost: Prokhorenkova et al., “CatBoost: unbiased boosting with
  categorical features,” NeurIPS 2018,
  [paper and official documentation](https://catboost.ai/docs/).
- LightGBM: Ke et al., “LightGBM: A Highly Efficient Gradient Boosting
  Decision Tree,” NeurIPS 2017,
  [official documentation](https://lightgbm.readthedocs.io/).
- Explainable Boosting Machine: Nori et al., “InterpretML: A Unified
  Framework for Machine Learning Interpretability,” arXiv:1909.09223,
  [official InterpretML repository](https://github.com/interpretml/interpret).
- TabPFN: Hollmann et al., “TabPFN: A Transformer That Solves Small Tabular
  Classification Problems in a Second,” ICLR 2023,
  [paper](https://openreview.net/forum?id=cp5PvcI6w8) and
  [official implementation](https://github.com/PriorLabs/TabPFN).
- TabM: Gorishniy et al., “TabM: Advancing Tabular Deep Learning With
  Parameter-Efficient Ensembling,” ICLR 2025,
  [paper](https://openreview.net/forum?id=loV9f0J5x4) and
  [official implementation](https://github.com/yandex-research/tabm).
- TabICL: the repository and paper should be checked against the exact
  release used before inclusion; it was not available in this environment and
  therefore contributes no result here.

Package licenses, model-card constraints, and dataset-size limits must be
rechecked at the time an optional dependency is installed. The failed
background source-verification attempt is not treated as evidence that an
optional family is suitable or unsuitable.
