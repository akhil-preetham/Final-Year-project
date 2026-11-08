# Offline demonstration documentation

The desktop demonstration in `demo/app.py` is synthetic-only and is guarded to prevent the supplied synthetic example from being interpreted as an actual patient diagnosis. `demo/run_domain_guard_demo.py` exercises registered-domain checks and unknown-domain rejection using synthetic examples. The older `demo/run_demo.py` is a benchmark CLI that loads the Heart5 benchmark and reports a held-out row's actual benchmark label and score; it is not a patient-facing workflow.

Run the guarded logic check from the project environment with `python demo/run_domain_guard_demo.py --output <temporary-path>`. Start the desktop demo with `python demo/app.py` where a Windows display is available. No network or external service is required. Raw external datasets and credentials are not required for the synthetic desktop demo. Detailed results and file hashes are captured in the current verification manifest. Do not use the benchmark CLI with patient data.
