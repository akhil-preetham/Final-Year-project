# Adaptive machine learning literature review

## Executive synthesis

Adaptive learning is not one problem. The literature separates into at least
five mechanisms:

1. **Dataset-level search:** AutoML systems choose transformations, models and
   hyperparameters for a target dataset. Examples include Mosaic-MCTS,
   Auto-sklearn/BOHB-style systems and AutoGluon.
2. **Dataset-conditioned prediction:** HyperFast and FLAT learn a mapping from a
   dataset/task description to a predictor or predictor parameters.
3. **In-context universal prediction:** TabPFN, TabICL, TabDPT, APT, Mitra and
   related models learn the learning algorithm offline and condition on target
   rows at inference.
4. **Cross-schema representation transfer:** CARTE and FLAT explicitly address
   heterogeneous columns or feature spaces.
5. **Shift/online adaptation:** Drift-Resilient TabPFN, CrossAdapt, domain
   generalization, test-time adaptation and continual learning address changes
   after deployment.

Calling a target-dataset pipeline “adaptive” does not establish membership in
 categories 2–5. AURA-ML V1/V2 currently belongs primarily to category 1: it
 performs nested target-dataset selection and reliability gating. It does not
 have a pretrained task prior, a cross-table representation, or an independent
 target-domain adaptation protocol.

## What is established

- Meta-features have long been used for algorithm recommendation; TabRepo makes
  large collections of model evaluations available for transfer/meta-learning.
- Hypernetworks can generate task-specific predictors, as in HyperFast.
- Dataset and column embeddings can support heterogeneous feature-space transfer,
  as in FLAT.
- Synthetic-task pretraining can learn a general-purpose tabular predictor,
  beginning with TabPFN and continuing through APT, TabICL, Mitra and newer
  systems.
- Real-table pretraining and retrieval are established through TabDPT,
  TABULA-8B and CARTE.
- Dynamic routing/ensembling and calibration-aware selection are established
  engineering and research strategies, not novel merely because they are used
  on cardiovascular data.

## What is not yet settled

The recent literature leaves several defensible questions:

- Which pretraining priors cover clinically realistic missingness, measurement
  units, label shift and small-sample selection bias?
- Can a model choose between ICL, target-trained GBDT, linear, retrieval and
  abstention strategies using a genuinely held-out dataset-level meta-test?
- Can reliability and calibration be guaranteed under schema shift rather than
  optimized on IID validation rows?
- How should model selection account jointly for performance, calibration,
  subgroup robustness, inference cost, memory and provenance?
- How can target-domain adaptation use unlabeled rows without becoming a hidden
  source of evaluation leakage?

## Implication for CARDIODIAG

The strong research question is no longer “can we combine profiling, feature
selection and an ensemble?” That space is crowded. A credible contribution must
either:

- introduce a new, benchmarked task-level meta-learning mechanism;
- provide a clinically grounded cross-schema/unit/label-shift adaptation method;
- provide a reliability objective with formal selective-risk or calibration
  guarantees under domain shift; or
- produce a new benchmark and negative-result analysis that exposes failures of
  current universal tabular models on cardiovascular transport.

## Primary sources

- [TabPFN](https://arxiv.org/abs/2207.01848)
- [TabICL](https://arxiv.org/abs/2502.05564)
- [TabDPT](https://arxiv.org/abs/2410.18164)
- [APT](https://arxiv.org/abs/2502.04573)
- [Mitra](https://arxiv.org/abs/2510.21204)
- [HyperFast](https://arxiv.org/abs/2402.14335)
- [CARTE](https://arxiv.org/abs/2402.16785)
- [FLAT](https://arxiv.org/abs/2311.10051)
- [Drift-Resilient TabPFN](https://arxiv.org/abs/2411.10634)
- [Mosaic-MCTS](https://arxiv.org/abs/1906.00170)
