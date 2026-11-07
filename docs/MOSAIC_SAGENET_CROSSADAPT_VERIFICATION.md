# MOSAIC, SageNet and CrossAdapt name verification

## MOSAIC

“MOSAIC” is not a unique model identity.

| Resolved work | Evidence | Relevance to CARDIODIAG |
|---|---|---|
| *Automated Machine Learning with Monte-Carlo Tree Search* — Rakotoarison, Schoenauer, Sebag (2019), [arXiv:1906.00170](https://arxiv.org/abs/1906.00170) | Primary arXiv metadata and abstract | High for pipeline/model selection; it searches per dataset rather than predicting zero-shot |
| *MOSAIC, a comparison framework for machine learning models* — Papin, Beaujeault-Taudière, Magniette (2023), [arXiv:2301.12986](https://arxiv.org/abs/2301.12986) | Primary arXiv metadata and abstract | Software framework, not an adaptive classifier |
| *MOSAIC: Modular Orchestration for Structured Agentic Intelligence and Composition* — Bao et al. (2026), [arXiv:2606.00708](https://arxiv.org/abs/2606.00708) | Primary arXiv metadata and abstract | Recent agentic AutoML/workflow construction; preprint and financial time-series focus |
| *MOSAIC: Learning Unified Multi-Sensory Object Property Representations for Robot Learning* — Tatiya et al. (2023), [arXiv:2309.08508](https://arxiv.org/abs/2309.08508) | Primary arXiv record | Multimodal robotics; unrelated |
| Radiology-report MOSAIC and other uses | Search results identify distinct clinical NLP/radiology works | Not tabular cardiovascular prediction |

**Finding:** “MOSAIC-ML” cannot be cited without an exact title, authors or
URL. The closest CARDIODIAG prior art is the MCTS AutoML paper and, more
recently, the agentic MOSAIC preprint. Neither makes a new AURA-style
reliability-aware cross-dataset predictor novel by default.

## SageNet / SAGENet

The name is even more ambiguous:

| Resolved work | Domain | Evidence |
|---|---|---|
| *Supervised spatial inference of dissociated single-cell data with SageNet* (2022) | Spatial transcriptomics GNN | [bioRxiv DOI](https://doi.org/10.1101/2022.04.14.488419) |
| *A scalable approach to investigating sequence-to-function predictions of personal genomes* (SAGE-net, 2025) | Genomics, CNN/contrastive learning | [SAGEnet repository](https://github.com/mostafavilabuw/SAGEnet) and preprint metadata |
| *SAGENet: Binaural Echo-Based 3D Depth Estimation with Sparse Angular Queries and Refined Geometric Cues* (2025) | Audio/vision robotics | [IEEE DOI](https://doi.org/10.1109/iros60139.2025.11245854) |
| *SageNet: Fast Neural Network Emulation of the Stiff-amplified Gravitational Waves from Inflation* (2025) | Cosmology/LSTM emulator | [ApJS DOI](https://doi.org/10.3847/1538-4365/ade4c6) |
| *SageNet: A Training-Free Few-Shot Image Segmentation Network...* (2026) | Computer vision | [Springer page](https://link.springer.com/chapter/10.1007/978-981-95-5758-5_19) |
| `sagenet` software documentation | Spatial transcriptomics package | [ReadTheDocs](https://sagenet.readthedocs.io/en/latest/api.html) |

**Finding:** No verified SageNet record in this search is a general-purpose
heterogeneous tabular learner. The name must not be used as CARDIODIAG prior art
without an exact citation.

## CrossAdapt

The exact resolved work is:

- **Title:** *Efficient Cross-Architecture Knowledge Transfer for Large-Scale
  Online User Response Prediction*
- **Authors:** Yucheng Wu, Yuekui Yang, Hongzheng Li, Anan Liu, Jian Xiao,
  Junjie Zhai, Huan Yu, Shaoping Ma, Leye Wang
- **Year/status:** 2026 arXiv preprint; publication status not verified
- **URL:** [arXiv:2602.01775](https://arxiv.org/abs/2602.01775)
- **Code:** [wuyucheng2002/CrossAdapt](https://github.com/wuyucheng2002/CrossAdapt)

It transfers between heterogeneous recommendation architectures through
dimension-adaptive embedding projections and progressive distillation, then uses
asymmetric teacher-student online adaptation under distribution shift. It is
relevant to continual adaptation and stability/adaptability trade-offs, but it
does not solve arbitrary-schema zero-shot tabular prediction, cardiovascular
clinical validation, or calibrated external validation.

## Disambiguation conclusion

The three names are not safe shorthand for a single prior-art family. The
registry keeps separate records for each resolved work. The project should use
full titles and persistent URLs in any future manuscript.
