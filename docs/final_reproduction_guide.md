# Final reproduction guide

From the repository root in PowerShell:

```powershell
.venv\Scripts\python.exe experiments\run_tuned_ensemble.py `
  --dataset data\kaggle_cardiovascular_70k\cardio_train.csv `
  --target cardio `
  --output results\generated\kaggle70k_tuned_priority_oof_ensemble.json `
  --seed 42

.venv\Scripts\python.exe experiments\run_nested_validation.py `
  --dataset heart5.csv --target HeartDisease `
  --output results\generated\post_tuning_custom_nested_heart5.json `
  --outer-splits 3 --outer-repeats 1 --inner-splits 2 --seed 42

.venv\Scripts\python.exe experiments\run_nested_validation.py `
  --dataset MendeleyCardiovascular_Disease_Dataset.csv --target target `
  --output results\generated\post_tuning_custom_nested_mendeley.json `
  --outer-splits 3 --outer-repeats 1 --inner-splits 2 --seed 42

.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check src tests experiments
uv lock --check
git diff --check
```

The linkage command is:

```powershell
.venv\Scripts\python.exe experiments\run_stability_reliability_linkage.py `
  --dataset heart5.csv --target HeartDisease `
  --output results\generated\post_tuning_custom_linkage_heart5.json `
  --seeds 42 43 44 45 46
```

Use the analogous Mendeley arguments for the second dataset. Do not overwrite
existing artifacts; choose a new output path for reruns.
