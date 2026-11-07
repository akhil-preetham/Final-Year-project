# CLIN-ADAPT clinical model registry

The resolved registry is stored at `results/clin_adapt/model_registry.json`.
It contains **35 records**: **20 locally executable candidates** and **15
explicitly unavailable families**. Availability was inspected in the active
`.venv`; no optional packages were installed indiscriminately.

## Executable local candidates

| Family | Candidates |
|---|---|
| Linear/probabilistic | Logistic Regression, Ridge Classifier with calibration, L1 Logistic, Elastic Net, LDA, QDA, Gaussian NB, Bernoulli NB |
| Trees/boosting | Decision Tree, Random Forest, Extra Trees, Gradient Boosting, HistGradientBoosting, AdaBoost |
| Kernel/instance | RBF-SVM, KNN |
| Neural | Small scikit-learn MLP |
| External boosting | XGBoost, LightGBM, CatBoost |

Each candidate has a deterministic seed, candidate-specific preprocessing label,
resource class and factory. Estimators are configured single-threaded so the
outer engine controls concurrency.

## Explicitly unavailable

TabNet, TabM, NODE, SAINT, FT-Transformer, GRANDE, TabPFN, TabICL, TabDPT,
Mitra, HyperFast, AutoGluon, auto-sklearn, FLAML and H2O AutoML were recorded as
unavailable because their packages were absent from the active environment or
their implementation could not be resolved locally. They were not reported as
executed.

## Execution status

| Dataset | Candidates executed | Protocol | Failures |
|---|---:|---|---:|
| Heart5 | 20 | 3 outer × 2 inner | 0/60 jobs |
| Mendeley | 20 | 3 outer × 2 inner | 0/60 jobs |
| Cardiovascular 70K | 6 priority candidates | 2 outer × 2 inner | 0/12 jobs |

The 70K run intentionally used a resource-bounded priority subset. SVC, KNN,
MLP and the small-data-only candidates were not run on 70K in this cycle; that
is a declared computational boundary, not a claim that every registry member
was evaluated on every dataset.
