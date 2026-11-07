# CARDIODIAG demonstration

Run:

```text
uv run python demo/run_demo.py
```

The demonstration shows a prediction probability, a conformal prediction set,
and an abstention state. It is a research prototype only and is not clinically
validated.
# CARDIODIAG demonstrations

## Basic inference

Run:

```powershell
uv run python demo/run_demo.py
```

This small example shows a prediction probability, conformal prediction set,
and abstention state. It is a research prototype and is not clinically
validated.

## Domain-aware abstention

After generating the CD-XD-005 model bundle, run:

```powershell
uv run python demo/run_domain_guard_demo.py
```

The domain-aware demo runs four synthetic cases against the saved inference
bundle:

- Registered source and in-support: classify and return the probability and
  singleton conformal set.
- Registered source but uncertain conformal set: abstain and withhold the
  probability.
- Registered source but outside feature support: abstain and withhold both
  the probability and conformal set.
- Unknown site: abstain and withhold both the probability and conformal set.

The default bundle is the Duke ACATH stress-test artifact. To demonstrate the
AngioCAD bundle as well, run:

```powershell
uv run python demo/run_domain_guard_demo.py --bundle results/transfer_20261105_angiocad_domain_guard/model_bundle.joblib
```

The machine-readable outputs and hashes are saved beside each model bundle as
`domain_guard_demo.json` and `domain_guard_demo_manifest.json`. These are
synthetic policy demonstrations, not patient predictions or clinical decision
software.
