# Benchmark framework comparison

| Framework | Purpose | Dataset scope | Supported algorithms | Evaluation/protocol | Metrics | Reproducibility | CARDIODIAG use |
|---|---|---|---|---|---|---|---|
| TabArena | Living tabular leaderboard | Versioned curated tabular tasks; current count is release-dependent and reported around 51 in current records | GBDT, deep tabular, foundation models and ensembles | Declared budgets, validation variants, maintained leaderboard | Elo/ranking and task metrics; inspect current site for exact per-task metrics | Public code, data curation and maintenance protocol | Best general-purpose comparison target after schema/license review |
| TALENT | Unified deep-tabular toolbox | Broad tabular benchmark collection; paper reports >20 methods | Deep tabular methods with common interface | Unified preprocessing/training and fair method comparisons | Classification/regression metrics | Open-source GitHub toolbox | Add AURA as a target-trained baseline; not enough for external validity alone |
| TabRepo | Stored model evaluations/predictions | 200 classification/regression datasets | 1,310 recorded models in paper | Reuse predictions for analysis, transfer and ensembling | Stored metrics and predictions | Dataset/repository paper; version must be frozen | Meta-learning/model-selection training resource |
| OpenML | Dataset/task repository and API | Very broad, heterogeneous | Any compatible implementation | Task definitions and benchmark suites such as CC18 | Task-specific standard metrics | Strong APIs and identifiers; data licensing varies | Source for leave-dataset-out meta-learning, with strict provenance filtering |
| AutoML benchmark suites | Compare AutoML systems | Suite-specific datasets, often OpenML | Auto-sklearn, AutoGluon, H2O, FLAML and others | Fixed time budgets/repeated runs | Dataset-appropriate predictive metrics and runtime | Reproducible if exact versions/budgets are frozen | Baseline portfolio-search comparison |
| TabReD | Industry/time-split stress benchmark | Eight industry-grade datasets | Classical and deep tabular models | Time-based splits and industrial feature conditions | Dataset-specific metrics | Public benchmark/code according to paper record | Important shift/temporal stress complement to IID benchmarks |
| TableShift | Distribution-shift benchmark | Real-world domain/geographic/temporal shifts | Multiple tabular models | Explicit OOD splits | Classification metrics and shift gaps | Public benchmark ecosystem | Source for cross-domain reliability tests if target semantics fit |

## Recommendation

Use a layered evaluation:

1. **TALENT** for reproducible architecture integration.
2. **TabArena** for current broad model comparison and compute-aware ranking.
3. **TabRepo/OpenML** for leave-dataset-out model-selection meta-learning.
4. **TabReD/TableShift** for realistic temporal/domain shift.
5. A new CARDIODIAG clinical schema/unit/label-shift suite only after provenance
   and licensing are frozen.

Do not claim general-purpose learning from one of the local three datasets.
