# CARDIODIAG Kaggle setup

This archive preserves the original CARDIODIAG source, experiment runners,
tests, reports, manuscript, and historical result artifacts. It does not
include a local Python environment.

## Kaggle

1. Create a private Kaggle Notebook with a standard CPU runtime.
2. Upload this archive as a private Kaggle Dataset, or extract it locally and
   upload the staged directory.
3. Add the dataset to the notebook. Kaggle exposes it read-only below
   `/kaggle/input/`.
4. Work from a writable copy under `/kaggle/working/`:

   ```python
   from pathlib import Path
   import shutil

   source = next(Path("/kaggle/input").glob("**/CARDIODIAG_Original_Kaggle"))
   work = Path("/kaggle/working/CARDIODIAG_Original_Kaggle")
   if not work.exists():
       shutil.copytree(source, work)
   ```

5. Install dependencies without copying a local environment:

   ```bash
   python -m pip install -e . --no-deps
   python -m pip install numpy pandas scipy scikit-learn imbalanced-learn \
       xgboost lightgbm catboost matplotlib pytest ruff
   ```

   Internet must be enabled for installation. If it is disabled, use a Kaggle
   image or attached wheel source that already provides the dependencies.

## Data policy

The bundled `MendeleyCardiovascular_Disease_Dataset.csv` is CC BY 4.0:

`https://data.mendeley.com/datasets/dzz48mvjht/1`

Its SHA-256 is
`9376367dde41e79e432d6402ea5d9e44223fc318ff54ed09966d721923947d1e`.

`heart5.csv` is not bundled because its composite-source redistribution terms
were not verified. Attach it separately only after checking the upstream
component licenses.

`cardio_train.csv` is not bundled because the Kaggle metadata reports an
Unknown license. Attach it manually from:

`https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset`

The expected Kaggle file is semicolon-delimited, has target `cardio`, and has
SHA-256
`21a705d23381b0dfd6a6416da701b490744f1fc3b47e9ff3db3968c420ffa10c`.
Do not silently substitute one dataset for another.

## Running the project

Run commands from the writable project copy. Existing scripts use repository
relative paths; place attached datasets at the paths documented in
`data/manifests/local_datasets.json`, or pass the runner's supported
`--dataset` and `--target` arguments.

Examples:

```bash
python -m pytest
python -m ruff check src tests experiments
python experiments/run_internal_stage.py
python experiments/run_model_benchmark.py --help
python experiments/run_nested_validation.py --help
```

Write new generated outputs to `/kaggle/working/` rather than the read-only
input mount. Expensive nested, stability, and linkage workflows should first
be run with their supported reduced/smoke configuration; review each script's
`--help` output before launching a full experiment. The full original workflow
has not been claimed as Kaggle-compatible without verifying its dependencies,
datasets, runtime, and output paths in the target notebook.
