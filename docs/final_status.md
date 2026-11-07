# CARDIODIAG final project status

**Status date:** 2026-11-05  
**Historical snapshot:** superseded by `docs/handoff.md`, `docs/QA_REPORT.md`,
`docs/MASTER_DIRECTIVE_COMPLETION_MATRIX.md`, and
`docs/REAL_WORLD_READINESS_WORKFLOW.md`. The notes below describe the earlier
checkpoint and should not be used as the current project status.

**Overall status:** reproducible research package complete through internal
validation, reliability analysis, and one endpoint-aligned source-distinct
external evaluation. The focused shift-evaluation prototype is complete;
dependable calibration/OOD rejection, multi-hospital replication, and final
venue-specific manuscript completion remain open.

## Completed

- Historical notebook audit and protocol comparison.
- Leakage-controlled corrected pipeline.
- Nested internal validation on both supplied datasets.
- Stability-aware feature-selection implementation and ablations.
- Calibration, selective-risk, and split-conformal summaries.
- Repeated feature-stability evidence, repeated uncertainty-evidence summaries,
  and paired stability--reliability linkage analysis.
- External-manifest freeze gate.
- Frozen multi-source transfer on four UCI cohorts and one-way source-distinct
  transfer stress test to the Z-Alizadeh Sani hospital cohort (`CD-XD-003`).
- Endpoint-aligned external evaluation to the AngioCAD hospital cohort
  (`CD-XD-004`), with byte-identical repeat predictions and independent metric
  recalculation.
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
generalization. The separate Z-Alizadeh Sani transport stress test achieved
ROC-AUC 0.720; source-only Platt calibration modestly reduced Brier score but
paired intervals included no change. The OOD score AUROC was 0.604. Its target
outcome is `>=50%` stenosis versus `>50%` in source, so it does not count as
endpoint-identical validation.

The exact-endpoint AngioCAD study (`CD-XD-004`) achieved ROC-AUC 0.787
(95% bootstrap interval 0.734–0.838) on 377 matched patients. Calibration
changes were small and inconclusive; calibrated ECE was 0.216 and the OOD
AUROC was 0.589 (95% interval 0.541–0.635). The target was 79.0% positive.
Thus endpoint-aligned one-site testing is complete, but useful uncertainty
calibration and OOD rejection are not established. See
`TRANSFER_STUDY_RESULTS_20261105_ANGIOCAD.md`.

## Remaining gates

1. Replicate the frozen, endpoint-aligned evaluation on additional independent
   hospitals or a prospective cohort with patient-level linkage or a documented
   overlap procedure.
2. Improve calibration and OOD warning using source-only development; reserve
   the next independent cohort for evaluation and do not tune on AngioCAD labels.
3. Complete remaining feature/target overlap and licensing reviews.
4. Complete the final literature novelty review and select an IEEE journal.
5. Rebuild the manuscript PDF after adding the CD-XD-004 methods and results.
6. Replace manuscript placeholders only with generated verified artifacts.
7. Add author metadata, ethics statements, funding, and contributions only when
   factually supplied and applicable.

The endpoint-aligned one-way evaluation uses
`experiments/run_angiocad_transfer.py` and its frozen CD-XD-004 protocol. The
generic one-way evaluator remains available at
`experiments/run_external_evaluation.py` for additional frozen cohorts.

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
