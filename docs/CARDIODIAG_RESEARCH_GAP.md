# CARDIODIAG research gap assessment

## Problems substantially addressed already

- Strong target-dataset model selection: AutoML, Mosaic-MCTS and model portfolios.
- Zero-shot/few-shot unseen-table prediction: TabPFN, TabICL, APT, Mitra,
  HyperFast and related foundation models.
- Heterogeneous-schema transfer: CARTE and FLAT.
- Real/synthetic tabular pretraining: TabDPT, Real-TabPFN, TABULA-8B.
- Dynamic/online adaptation: CrossAdapt and drift-resilient PFN variants.
- Feature attention/selection and ensembles: TabNet, TabM, SAINT, FT-Transformer,
  retrieval models and many AutoML systems.

## Problems partially addressed

1. Calibration under distribution shift: reported, but not solved reliably;
   recent foundation models can rank well while being miscalibrated.
2. Dataset-level meta-features: useful for analysis, but leave-dataset-out
   prediction of model superiority remains difficult.
3. Cross-schema transfer: CARTE/FLAT address structural heterogeneity, but
   clinical units, endpoints, measurement processes and missingness remain hard.
4. Reliability-aware routing: ensembles and selective prediction exist, but
   deployment-safe routing under unseen shift is not settled.
5. Compute-aware universal learning: current foundation models improve quickly,
   but memory, licensing and reproducibility constraints remain.

## Problems not adequately addressed for CARDIODIAG

- No frozen independent cardiovascular cohort with compatible endpoint/schema and
  verified licensing is currently available in the repository.
- Existing local results do not establish cross-dataset transportability.
- A principled decision rule for refusing adaptation when semantic mapping is
  unsafe is missing.
- Clinical calibration, prevalence shift and selective prediction need a
  prospective-like protocol rather than random row splits.
- No local study compares AURA against executable TabPFN/TabICL/HyperFast/FLAT
  under leave-dataset-out and reliability metrics.

## Novelty verdict for current AURA

AURA's present components—profiling, adaptive preprocessing, multiview features,
feature selection, inner model selection, fusion and calibration—are all
represented in prior work. The repository's empirical stability/reliability
audit is defensible as an engineering/reproducibility contribution, but a new
algorithmic novelty claim is unsupported.

## Most defensible gap

The strongest gap is an **auditable cross-dataset clinical tabular transfer and
reliability benchmark** that jointly tests:

- schema/unit/endpoint compatibility;
- leave-dataset-out prediction;
- target-unlabeled adaptation versus target-labeled calibration;
- shift detection and abstention;
- calibration and selective risk;
- compute, memory, provenance and failure-to-adapt rates.

The contribution may be a benchmark/protocol plus a narrowly new refusal or
adaptation mechanism, rather than another generic ensemble.
