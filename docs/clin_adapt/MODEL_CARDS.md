# CLIN-ADAPT model cards

## Scope

The registry in `results/clin_adapt/model_registry.json` is the source of truth
for candidate availability. These cards describe intended use and evaluation
status; they do not imply clinical validation.

## Local executable candidates

| Candidate family | Intended use | Main risks | Evaluation status |
|---|---|---|---|
| Logistic/L1/Elastic-Net/Ridge | Small or moderate mixed clinical tables after encoded scaling | Linear misspecification and calibration drift | Executed in Heart5 and Mendeley full portfolios |
| LDA/QDA | Low-dimensional discriminant structure | Covariance assumptions and QDA instability | Executed in Heart5 and Mendeley full portfolios |
| Gaussian/Bernoulli NB | Fast probabilistic baselines | Conditional-independence misspecification | Executed in Heart5 and Mendeley full portfolios |
| Decision Tree/Random Forest/Extra Trees | Nonlinear interactions and tree baselines | Variance, calibration and resource cost | Executed in Heart5 and Mendeley; priority coverage on 70K where selected |
| Gradient/Histogram Boosting/AdaBoost | Nonlinear tabular prediction | Overfitting, tuning sensitivity and shift | Executed in Heart5 and Mendeley; priority boosting coverage on 70K |
| RBF-SVM/KNN | Geometry-based alternatives | Scaling, memory and poor large-table scalability | Executed in Heart5 and Mendeley only |
| MLP | Small nonlinear neural baseline | Optimization sensitivity and limited tabular inductive bias | Executed in Heart5 and Mendeley only |
| XGBoost/LightGBM/CatBoost | Strong practical boosting baselines | Shift, tuning and probability reliability | Executed in all three declared development runs where included |

## Unavailable candidates

TabNet, TabM, NODE, SAINT, FT-Transformer, GRANDE, TabPFN, TabICL, TabDPT,
Mitra, HyperFast, AutoGluon, auto-sklearn, FLAML and H2O AutoML were recorded
but not executed because the required packages or implementations were absent.
They require separate dependency, hardware, licensing and reproducibility
review before inclusion in a scientific comparison.

## Clinical-use restrictions

No candidate is approved for clinical deployment. The experiments are
development benchmarks on public or project-local datasets. They do not
establish clinical utility, subgroup fairness, transportability, prospective
performance or external validation.
