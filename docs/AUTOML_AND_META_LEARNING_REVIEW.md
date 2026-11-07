# AutoML and meta-learning review

## Selection versus prediction

AutoML solves a different problem from a universal predictor. AutoML receives a
target dataset and searches a portfolio; a foundation/meta-learning model learns
an inference procedure across many datasets and can operate on a new dataset
with little or no parameter fitting.

| Approach | Representative source | Adaptation | Main risk |
|---|---|---|---|
| Bayesian/MCTS pipeline search | Mosaic-MCTS, AutoML systems | Target validation search | Compute and validation overfitting |
| Evaluation-repository transfer | TabRepo | Predict model performance from dataset/model history | Dataset coverage and protocol bias |
| Dataset meta-features | Classical algorithm recommendation; newer TabArena analyses | Select a model from profile | Meta-features often weak under leave-dataset-out prediction |
| Hypernetwork generation | HyperFast | Generate target classifier parameters | Meta-training prior and safety/calibration |
| Dataset/column embeddings | FLAT | Generate target predictor across feature spaces | Semantic alignment and few-shot dependence |
| Agentic orchestration | MOSAIC 2026 | Retrieve, compose and execute workflow | Verification, reproducibility and execution cost |
| Foundation-model ICL | TabPFN, TabICL, APT, Mitra, TabDPT | Condition on target context | Pretraining distribution, compute, calibration |

## Implications for AURA

AURA-ML's dataset profile and inner candidate utility are reasonable engineering
components, but they overlap directly with algorithm recommendation and AutoML.
The current AURA evidence does not demonstrate leave-dataset-out meta-test
generalization. The V2 70K feasibility result also selected CatBoost in all
folds, showing that the adaptive policy may simply route to a strong baseline.
That outcome is scientifically useful but is not evidence of a new learning
algorithm.

## What a publishable next step needs

- Freeze a meta-training collection of sufficiently diverse datasets.
- Hold out entire datasets—not rows—for meta-test.
- Compare against TabPFN/TabICL/HyperFast/FLAT where executable and in-scope.
- Include a simple portfolio selector, CatBoost/XGBoost and a no-adaptation
  baseline.
- Report calibration, selective risk, compute, memory and failure rates.
- Prevent benchmark leakage through dataset identity, source overlap and repeated
  preprocessing choices.

## Sources

- [Mosaic-MCTS](https://arxiv.org/abs/1906.00170)
- [TabRepo](https://arxiv.org/abs/2311.02971)
- [HyperFast](https://arxiv.org/abs/2402.14335)
- [FLAT](https://arxiv.org/abs/2311.10051)
- [TabArena](https://arxiv.org/abs/2506.16791)
- [MOSAIC agentic AutoML](https://arxiv.org/abs/2606.00708)
