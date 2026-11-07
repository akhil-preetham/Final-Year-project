# CARDIODIAG desktop research demonstration

## Launch

From the repository root in the locked environment. Before loading, the app
checks the bundle SHA-256 against its adjacent
`domain_guard_demo_manifest.json`:

```powershell
uv run python demo/app.py
```

The default research bundle is `results/transfer_20261105_duke_acath_final/model_bundle.joblib`. To choose another saved bundle:

```powershell
uv run python demo/app.py --bundle results/transfer_20261105_angiocad_domain_guard/model_bundle.joblib
```

## Screens and behavior

- **Overview:** research version, model bundle version/hash, dataset compatibility status, declared feature order and registered source domains.
- **Research demo input:** accepts the bundle's exact fields, checks required/extra fields, allowed categories, finite values, and broad numeric input bounds. Fields are assembled in the bundle's declared order. Unknown/unregistered domain is the default and abstains.
- **Evaluation evidence:** reads the internal nested summary CSV, transfer `study_metrics.json`, CD-XD-003 run manifest and AngioCAD validity-sensitivity artifact; it displays the actual project plots from `paper/figures/master_directive_20261105_final/` when present. It labels the 0.604 ZAS, 0.589 primary AngioCAD, and later 0.5787/0.5801 AngioCAD diagnostics as distinct runs/cohorts.
- **Explanation limits:** explains the policy reason for abstention. It does not fabricate local feature contributions; the bundle has no validated per-instance explanation artifact.

The UI does not persist user-entered values or expose a network endpoint. **Use synthetic values only; do not enter patient data.** Numeric limits are data-entry sanity checks, not clinical reference intervals. A registered-domain choice is a synthetic policy demonstration and is not a way to verify source identity. Model probability and class are shown only when the existing domain-aware policy accepts the row. Abstention withholds them.

## Evidence and limitations

The interface uses existing frozen artifacts, not demo-generated metrics. Internal CV remains internal. AngioCAD and Duke are exploratory stress tests with limitations documented in `EXTERNAL_VALIDATION_REPORT.md`. The system is not clinically validated and must not be used for medical decisions.

## Testing

`tests/test_demo_app.py` checks bundle hash verification, schema rejection, bounds/category validation, order preservation and fail-closed unknown-domain behavior. Run the full `python -m pytest -q` suite and visually launch the GUI after modifying app code. A missing bundle or integrity manifest causes startup to fail with an explicit command-line error; the evaluation tab omits plots whose files are absent.
