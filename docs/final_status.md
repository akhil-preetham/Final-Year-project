# CARDIODIAG final project status

**Status date:** 2026-10-26  
**Overall status:** reproducible research package complete through internal
validation and reliability analysis; independent external validation and final
venue-specific manuscript completion remain blocked by the absence of a frozen,
compatible independent dataset and journal/author metadata.

## Completed

- Historical notebook audit and protocol comparison.
- Leakage-controlled corrected pipeline.
- Nested internal validation on both supplied datasets.
- Stability-aware feature-selection implementation and ablations.
- Calibration, selective-risk, and split-conformal summaries.
- Repeated feature-stability evidence, repeated uncertainty-evidence summaries,
  and paired stability--reliability linkage analysis.
- External-manifest freeze gate.
- Machine-readable results and generated summary tables.
- Editable IEEE-style manuscript skeleton with placeholders.
- Non-clinical demonstration with prediction-set abstention.
- Automated tests and lint checks.

## Scientific finding so far

The stability-aware selector is not uniformly superior to corrected baselines.
Repeated feature-set analysis found positive comparative stability evidence on
the Mendeley benchmark but an inconclusive difference on `heart5.csv`. Paired
linkage analysis found near-zero ROC-AUC differences and no consistent
confidence, conformal, or calibration improvement from the stable selector.
The defensible contribution is therefore a stability--reliability decoupling
audit: stable selected features are not a dependable proxy for reliable
predictions. This remains internal evidence, not a broad claim of improved
generalization.

## Remaining gates

1. Select and freeze a genuinely independent compatible dataset.
2. Complete feature/target overlap and licensing review.
3. Run one-way external evaluation without fitting or tuning on external data.
4. Decide whether the contribution is positive, negative, or inconclusive.
5. Complete the final literature novelty review and select an IEEE journal.
6. Replace manuscript placeholders only with generated verified artifacts.
7. Add author metadata, ethics statements, funding, and contributions only when
   factually supplied and applicable.

The one-way evaluator is now implemented at
`experiments/run_external_evaluation.py`; its remaining blocker is the missing
frozen independent dataset manifest and data file.

## Final commands

```text
uv run python experiments/run_internal_stage.py
uv run python experiments/run_reliability.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_reliability.json
uv run python experiments/run_stability_reliability_linkage.py --dataset heart5.csv --target HeartDisease --output results/generated/heart5_stability_reliability_linkage.json
uv run python experiments/generate_paper_assets.py
uv run python demo/run_demo.py
```

The external gate must pass before any external results are described as
validation:

```text
uv run python experiments/check_external_manifest.py data/manifests/external_dataset.json
```
