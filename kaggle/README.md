# Kaggle execution

The notebooks in `kaggle/notebooks/` are:

- `CARDIODIAG_Kaggle.ipynb`: self-contained workflow; recommended starting
  point.
- `CARDIODIAG_Kaggle_Quickstart.ipynb`: compact CPU smoke workflow.
- `CARDIODIAG_Complete_Research.ipynb`: extended workflow using the bundled
  source package.

## Run in Kaggle

1. Create a Kaggle Notebook with a standard CPU runtime.
2. Click **Add data** and attach this GitHub repository as a dataset, or
   download the repository and upload it as a private Kaggle Dataset.
3. Attach optional datasets separately only when their licensing permits:
   `heart5.csv` has unresolved composite-source redistribution terms, and
   the Kaggle 70k dataset reports an Unknown license.
4. In a notebook cell, locate the attached repository:

   ```python
   from pathlib import Path
   import sys

   repo = next(Path("/kaggle/input").glob("**/CARDIODIAG-GitHub-Publish"))
   sys.path.insert(0, str(repo / "src"))
   %cd /kaggle/working
   ```

5. Install dependencies if the Kaggle image does not already provide them:

   ```python
   !python -m pip install numpy pandas scipy scikit-learn imbalanced-learn \
       xgboost lightgbm catboost matplotlib pytest ruff
   ```

6. Open `kaggle/notebooks/CARDIODIAG_Kaggle.ipynb` and use **Run All**.
   The self-contained notebook writes results to
   `/kaggle/working/CARDIODIAG_results/`.

## Run scripts

From a writable copy of the repository:

```bash
python -m pytest
python -m ruff check src tests experiments
python experiments/run_internal_stage.py
python experiments/run_model_benchmark.py --help
python experiments/run_nested_validation.py --help
python experiments/run_stability_evidence.py --help
python experiments/run_stability_reliability_linkage.py --help
```

Run the reduced/smoke configuration first where supported. Review each
runner's `--help` output before launching expensive nested or repeated
experiments. Write generated files to `/kaggle/working/`, not the read-only
`/kaggle/input/` mount.
