# GitHub finalization status

## Current state

- Local branch: `main` tracking `origin/main`.
- Remote configured in this checkout:
  `https://github.com/jaffarkulachi/Cardio-Diag-Approach-Code.git`.
- The project prompt identifies a different intended repository,
  `akhil-preetham/Final-Year-project`.
- The working tree contains substantial pre-existing uncommitted research work,
  including expanded archives and generated artifacts.

## Blocker

No branch, commit, push, or pull request was created because publishing this
working tree to the configured remote could send the work to the wrong GitHub
repository. This is an intentional safety stop, not a failed experiment.

## Safe continuation commands

After confirming the correct remote and reviewing the staged-file allow-list:

```text
git remote set-url origin <confirmed-repository-url>
git switch -c audit/public-finalization-20261102
git add README.md LICENSE_AND_ATTRIBUTION.md pyproject.toml uv.lock .gitignore
git add src tests experiments demo docs paper results/final_publication
git add data/README.md data/manifests
git diff --cached --check
git diff --cached --stat
git commit -m "docs: finalize reproducible CARDIODIAG research package"
git push -u origin audit/public-finalization-20261102
gh pr create --base main --head audit/public-finalization-20261102
```

Do **not** stage raw datasets, `dist/`, `catboost_info/`, virtual environments,
secrets, or the expanded historical archive directories without separately
reviewing their redistribution rights and intended release status. Do not merge
the pull request automatically.
