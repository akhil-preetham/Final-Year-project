# Tabular foundation models review

## Taxonomy

| Family | Representative methods | What transfers | Target-data requirement | Main limitation |
|---|---|---|---|---|
| Prior-data fitted networks | TabPFN, Drift-Resilient TabPFN | A learned inference procedure from synthetic tasks | Labeled context rows at inference; no parameter update in standard mode | Prior coverage, context limits, calibration and shift |
| Scalable synthetic-prior ICL | TabICL, APT, Mitra | A task prior and row/column inference mechanism | Context rows; some versions support larger tables | Large pretraining and prior mismatch |
| Real-data pretraining | TabDPT, Real-TabPFN, TABULA-8B | Representations/inference behavior from many real tables | Context or light adaptation | Data licensing, memorization, schema and compute burden |
| Schema-heterogeneous transfer | CARTE, FLAT | Column/entity semantics and dataset representations | Background tables or few-shot target examples | Semantic/unit alignment and complex implementation |
| Dataset-conditioned generation | HyperFast | Generated predictor parameters | Dataset representation/context | Meta-training distribution determines transfer |
| Retrieval/embedding transfer | TabR, Universal Embeddings | Neighbor/entity information | Target or background retrieval corpus | Leakage, privacy, and unavailable neighbors |

## Strong conclusions

1. AURA's current candidate selection is not a tabular foundation model. It
   fits target-dataset models and chooses among them.
2. Dataset profiling alone is not a novel universal-learning mechanism. TabRepo,
   meta-learning and agentic AutoML already establish dataset-level selection.
3. A new model claiming unseen-table generalization must be evaluated with
   leave-dataset-out meta-test splits. Random row splits across the same tables
   cannot establish that claim.
4. Calibration is not inherited automatically from foundation-model status.
   The repository's Mendeley V2 results and recent calibration/shift studies
   reinforce that discrimination and reliability must be evaluated separately.
5. Cardiovascular data adds meaningful structure only if the method models units,
   measurement processes, missingness, temporal/population shift or endpoint
   semantics—not merely because the application domain is medical.

## Relevant sources

- TabPFN: [arXiv 2207.01848](https://arxiv.org/abs/2207.01848)
- TabICL: [arXiv 2502.05564](https://arxiv.org/abs/2502.05564)
- TabDPT: [arXiv 2410.18164](https://arxiv.org/abs/2410.18164)
- APT: [arXiv 2502.04573](https://arxiv.org/abs/2502.04573)
- Mitra: [arXiv 2510.21204](https://arxiv.org/abs/2510.21204)
- HyperFast: [arXiv 2402.14335](https://arxiv.org/abs/2402.14335)
- CARTE: [arXiv 2402.16785](https://arxiv.org/abs/2402.16785)
- FLAT: [arXiv 2311.10051](https://arxiv.org/abs/2311.10051)
- TabRepo: [arXiv 2311.02971](https://arxiv.org/abs/2311.02971)
- TabArena: [arXiv 2506.16791](https://arxiv.org/abs/2506.16791)
