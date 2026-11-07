# Existing adaptive and universal model comparison

**Audit date:** 2026-11-03  
**Evidence boundary:** This is a prior-art audit, not a systematic review or a
claim that the registry is exhaustive. Primary papers, arXiv records, official
repositories and official benchmark pages were preferred. Where only an
abstract or secondary mention was available, the record says so.

## Identity and capability matrix

| Model | Exact paper | Year | Research category | Tabular support | Unseen-dataset support | Adaptation mechanism | Training requirement | Code | Evidence status |
|---|---|---:|---|---|---|---|---|---|---|
| Mosaic-MCTS | *Automated Machine Learning with Monte-Carlo Tree Search* | 2019 | AutoML/search | Yes | Dataset-level search, not zero-shot | MCTS over pipelines and hyperparameters | Target dataset search | Not verified | VERIFIED_PRIMARY_SOURCE |
| MOSAIC framework | *MOSAIC, a comparison framework for machine learning models* | 2023 | Experiment framework | Generic | No model claim | Configured execution and run management | User-provided models | Not verified | VERIFIED_PRIMARY_SOURCE |
| MOSAIC agentic | *MOSAIC: Modular Orchestration for Structured Agentic Intelligence and Composition* | 2026 | Agentic AutoML | Structured-data claim | Retrieval/workflow transfer, not verified zero-shot | Task profile, retrieved modules, executable blueprint | Agentic search/execution | Not verified | VERIFIED_PRIMARY_SOURCE |
| CrossAdapt | *Efficient Cross-Architecture Knowledge Transfer for Large-Scale Online User Response Prediction* | 2026 | Online transfer | Structured recommendation features | Streaming/architecture transfer | Distillation, asymmetric co-distillation, shift-aware adaptation | Teacher, history and stream | [GitHub](https://github.com/wuyucheng2002/CrossAdapt) | VERIFIED_OFFICIAL_CODE |
| TabPFN | *TabPFN: A Transformer That Solves Small Tabular Classification Problems in a Second* | 2022 | Tabular foundation model | Yes | Yes, within small-task limits | PFN/ICL over synthetic priors | Offline pretraining; context at inference | [GitHub](https://github.com/automl/TabPFN) | VERIFIED_OFFICIAL_CODE |
| TabPFN v2 | Version/release, not separately verified canonical paper | 2025 | Foundation-model version | Yes | Yes, version-dependent | ICL | Pretrained weights | [PriorLabs](https://github.com/PriorLabs/TabPFN) | PARTIALLY_VERIFIED |
| TabICL | *TabICL: A Tabular Foundation Model for In-Context Learning on Large Data* | 2025 | Foundation model | Yes | Yes | Column-then-row encoder and ICL | Synthetic pretraining | [GitHub](https://github.com/soda-inria/tabicl) | VERIFIED_OFFICIAL_CODE |
| TabDPT | *TabDPT: Scaling Tabular Foundation Models on Real Data* | 2025 | Foundation model | Yes | Yes | Real-data pretraining and ICL/retrieval | Large pretraining corpus | [GitHub](https://github.com/layer6ai-labs/TabDPT-inference) | VERIFIED_OFFICIAL_CODE |
| APT | *Zero-shot Meta-learning for Tabular Prediction Tasks with Adversarially Pre-trained Transformer* | 2025 | Zero-shot meta-learning | Yes | Yes | Adversarial synthetic task agents | Offline synthetic pretraining | Not verified | VERIFIED_PRIMARY_SOURCE |
| Mitra | *Mitra: Mixed Synthetic Priors for Enhancing Tabular Foundation Models* | 2025 | Foundation model | Yes | Yes | Mixture of synthetic priors | Offline pretraining | [Hugging Face](https://huggingface.co/autogluon/mitra-classifier) | VERIFIED_OFFICIAL_CODE |
| HyperFast | *HyperFast: Instant Classification for Tabular Data* | 2024 | Hypernetwork/meta-learning | Yes | Yes | Generates target classifier from dataset | Meta-training; target context | [GitHub](https://github.com/AI-sandbox/HyperFast) | VERIFIED_OFFICIAL_CODE |
| CARTE | *CARTE: Pretraining and Transfer for Tabular Learning* | 2024 | Schema-heterogeneous transfer | Yes | Yes | Open-vocabulary graph representation | Background tables plus transfer | Not verified | VERIFIED_PRIMARY_SOURCE |
| FLAT | *Tabular Few-Shot Generalization Across Heterogeneous Feature Spaces* | 2023 | Few-shot/meta-learning | Yes | Yes | Dataset/column embeddings and generated predictor | Meta-training plus few-shot target rows | Not verified | VERIFIED_PRIMARY_SOURCE |
| Drift-Resilient TabPFN | *Drift-Resilient TabPFN: In-Context Learning Temporal Distribution Shifts on Tabular Data* | 2024 | Shift-aware foundation model | Yes | Temporal OOD | Shifting SCM prior | Offline shifted-prior pretraining | Not verified | VERIFIED_PRIMARY_SOURCE |
| TABULA-8B | *Large scale transfer learning for tabular data via language modeling* | 2024 | Foundation model/LLM | Yes | Yes | LLM fine-tuned on table corpus | Very large pretraining | Publisher record; code not verified here | PARTIALLY_VERIFIED |
| Real-TabPFN | *Real-TabPFN: Improving Tabular Foundation Models via Continued Pre-training With Real-World Data* | 2025 | Continued pretraining | Yes | Transfer to new tasks | Curated real-table pretraining | Large real-table corpus | Not verified | VERIFIED_PRIMARY_SOURCE |
| TabM | *TabM: Advancing Tabular Deep Learning with Parameter-Efficient Ensembling* | 2025 | Tabular architecture | Yes | No special mechanism | Shared-parameter implicit ensemble | Target supervised training | [GitHub](https://github.com/yandex-research/tabm) | VERIFIED_OFFICIAL_CODE |
| FT-Transformer | *Revisiting Deep Learning Models for Tabular Data* | 2021 | Tabular architecture | Yes | No special mechanism | Feature tokenization and attention | Target supervised training | [GitHub](https://github.com/yandex-research/rtdl-revisiting-models) | VERIFIED_OFFICIAL_CODE |
| SAINT | *SAINT: Improved Neural Networks for Tabular Data via Row Attention and Contrastive Pre-Training* | 2021 | Tabular architecture | Yes | No verified zero-shot mechanism | Row attention and contrastive pretraining | Target supervised training | Not verified | PARTIALLY_VERIFIED |
| TabNet | *TabNet: Attentive Interpretable Tabular Learning* | 2020 | Tabular architecture | Yes | No | Sequential instance-wise feature masks | Target supervised training | Not verified | VERIFIED_PRIMARY_SOURCE |
| NODE | *Neural Oblivious Decision Ensembles for Deep Learning on Tabular Data* | 2019 | Neural tree ensemble | Yes | No | Differentiable oblivious trees | Target supervised training | Not verified | PARTIALLY_VERIFIED |
| Trompt | *Trompt: Towards a Better Deep Neural Network for Tabular Data* | 2023 | Tabular architecture | Yes | No verified zero-shot mechanism | Learned table/sample prompts | Target supervised training | Not verified | VERIFIED_PRIMARY_SOURCE |
| TabR | *TabR: Tabular Deep Learning Meets Nearest Neighbors in 2023* | 2023 | Retrieval-augmented model | Yes | No universal pretraining claim | Learned nearest-neighbor retrieval | Target training set required | [GitHub](https://github.com/yandex-research/tabular-dl-tabr) | VERIFIED_OFFICIAL_CODE |
| GRANDE | *GRANDE: Gradient-Based Decision Tree Ensembles for Tabular Data* | 2023 | Gradient-based trees | Yes | No | End-to-end tree optimization | Target supervised training | [GitHub](https://github.com/s-marton/GRANDE) | VERIFIED_OFFICIAL_CODE |
| ExcelFormer | *ExcelFormer: A neural network surpassing GBDTs on tabular data* | 2023 | Tabular architecture | Yes | Dataset-versatile, not zero-shot | Semi-permeable attention and augmentation | Target supervised training | Not verified | VERIFIED_PRIMARY_SOURCE |
| ModernNCA | Exact primary paper not isolated | N/A | Retrieval/nearest-neighbor | Mentioned secondarily | Not verified | Not verified | Not verified | Not verified | NAME_AMBIGUOUS |
| AutoIRAD | Exact candidate not identified | N/A | Unknown | Not verified | Not verified | Not verified | Not verified | Not verified | NOT_FOUND |
| AURA-ML | Local CARDIODIAG prototype | 2026 | Adaptive policy | Yes | No external validation | Profile, candidate selection, fusion and calibration | Nested target-dataset fitting | Local repository | LOCAL_PROTOTYPE_NOT_LITERATURE |

## Central innovation and gap matrix

| Model | Central innovation | Main strength | Main limitation | Similarity to CARDIODIAG objective | Potential research gap remaining |
|---|---|---|---|---|---|
| Mosaic-MCTS | Search over pipeline structures | Explicit algorithm selection | Expensive target search; no universal predictor | High for AutoML selection | Reliability and shift-aware selection under strict nested evaluation |
| TabPFN | Synthetic-prior Bayesian ICL | Strong small-data zero-shot behavior | Context, schema, calibration and distribution-shift limits | Very high | Clinically verified shift/calibration guarantees |
| TabICL | Scalable column/row ICL | Larger context than early PFNs | Pretraining cost and deployment compute | Very high | Low-resource, mixed-schema clinical calibration |
| TabDPT | Real-data self-supervision plus ICL | Uses real-table diversity | Data governance and compute burden | Very high | Provenance-controlled medical pretraining |
| APT | Adversarial synthetic task generation | Explicit prior diversification | Synthetic prior may miss clinical structure | Very high | Shift-aware, interpretable prior selection |
| Mitra | Mixed synthetic priors | Better prior diversity | Still foundation-model compute and prior dependence | Very high | Reliability under domain shift and transparent prior auditing |
| HyperFast | Dataset-conditioned hypernetwork | Instant target model generation | Meta-training distribution determines transfer | Very high | Safety constraints and calibrated abstention |
| CARTE | Schema-agnostic graph table representation | Cross-table transfer without column matching | Relational/string representation complexity | Very high | Clinical schema/unit semantics and outcome alignment |
| FLAT | Dataset/column embeddings plus generated target predictor | Explicit heterogeneous feature-space transfer | Few-shot/meta-training burden | Very high | Robust calibration and causal/clinical semantics |
| Drift-Resilient TabPFN | Shifted causal prior | Direct temporal OOD target | Focused on temporal shift, not all heterogeneous shift | High | Multi-source clinical shift with missingness and label shift |
| TabM | Parameter-efficient implicit ensemble | Strong practical supervised baseline | Requires target training; no cross-dataset prior | Medium | Dataset-level reliability routing, not architecture alone |
| FT-Transformer | Feature tokenized attention | General tabular DL baseline | Often needs tuning and target data | Medium | Better calibration/shift handling |
| TabNet | Instance-wise attentive feature selection | Interpretability and feature masks | Not universal; can be unstable on small data | Medium | Stability evidence under external shifts |
| TabR | Learned nearest-neighbor retrieval | Strong use of local target context | Requires target training set and can leak if misused | Medium | Retrieval with provenance-safe cross-domain memory |
| GRANDE | Gradient-optimized hard trees | Tree inductive bias with differentiability | Target training only | Medium | Dataset-conditioned tree structure with uncertainty |
| TabArena | Living benchmark | Versioned, realistic comparisons | Benchmark is not adaptation method | High for evaluation | Clinical-domain shift suite and calibration governance |
| TabRepo | Precomputed model-evaluation repository | Enables meta-learning cheaply | Coverage/protocol bias in recorded evaluations | High for algorithm selection | Leave-dataset-out reliability and deployment cost objectives |

## Evidence and interpretation rules

1. “Dataset-versatile” means evaluated on several datasets; it does not mean
   zero-shot prediction on a new schema.
2. “In-context learning” means the target rows/context are supplied at
   inference. It is not the same as external validation without target data.
3. Accuracy/AUC values from different benchmark suites are not comparable.
4. Preprint claims are not upgraded to peer-reviewed claims without a verified
   venue record.
5. No model in this matrix establishes clinical utility or transportability for
   CARDIODIAG's cardiovascular datasets.

The complete source metadata and verification notes are in
`docs/EXISTING_MODELS_REGISTRY.json`.
