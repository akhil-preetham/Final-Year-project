# CARDIODIAG dependency license inventory

**Generated:** 2026-11-06 using `pip-licenses` against the clean `uv sync --locked` environment. This reports package metadata; it is not legal review of complete license texts or all bundled third-party assets.

| Package | Version | Reported license |
|---|---:|---|
| ImageIO | 2.38.1 | BSD-2-Clause |
| Pygments | 2.21.0 | BSD-2-Clause |
| CatBoost | 1.2.10 | Apache-2.0 |
| cloudpickle | 3.1.2 | BSD |
| colorama | 0.4.6 | BSD |
| contourpy | 1.3.3 | BSD |
| coverage | 7.17.0 | Apache-2.0 |
| cycler | 0.12.1 | BSD |
| et_xmlfile | 2.0.0 | MIT |
| fonttools | 4.67.0 | MIT |
| graphviz | 0.21 | MIT |
| imbalanced-learn | 0.14.2 | MIT |
| iniconfig | 2.3.1 | MIT |
| joblib | 1.6.0 | BSD-3-Clause |
| kiwisolver | 1.5.1 | BSD |
| lazy-loader | 0.6 | BSD-3-Clause |
| LightGBM | 4.7.0 | MIT |
| LIME | 0.2.0.1 | BSD |
| Matplotlib | 3.11.2 | Python Software Foundation License |
| narwhals | 2.28.0 | MIT |
| NetworkX | 3.6.1 | BSD-3-Clause |
| NumPy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| openpyxl | 3.1.5 | MIT |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pandas | 2.3.3 | BSD |
| Pillow | 13.0.0 | MIT-CMU |
| Plotly | 7.1.0 | MIT |
| pluggy | 1.7.0 | MIT |
| pyparsing | 3.3.3 | MIT |
| pytest | 8.4.2 | MIT |
| pytest-cov | 6.3.0 | MIT |
| python-dateutil | 3.0.0 | Apache OR BSD |
| pytz | 2026.5 | MIT |
| Ruff | 0.13.3 | MIT |
| scikit-image | 0.26.0 | BSD |
| scikit-learn | 1.7.2 | BSD-3-Clause |
| SciPy | 1.17.1 | BSD |
| six | 1.17.0 | MIT |
| sklearn-compat | 0.1.6 | BSD |
| threadpoolctl | 3.7.0 | BSD-3-Clause |
| tifffile | 2026.3.3 | BSD-3-Clause |
| tqdm | 4.70.1 | MPL-2.0 AND MIT |
| tzdata | 2026.5 | Apache-2.0 |
| XGBoost | 3.2.0 | Apache-2.0 |
| xlrd | 2.0.2 | BSD |

## Findings

- The clean lock installation resolved 54 packages and installed 45 third-party packages plus the local project. `pip-licenses` showed the local `cardiodiag-research` package as `UNKNOWN` twice because the editable project is represented more than once by the environment metadata. This is expected in the absence of a software `LICENSE`, and it confirms that the project itself has no declared software license.
- Reported third-party license metadata is present for the installed dependencies. Packages with composite expressions (NumPy, packaging, python-dateutil, tqdm) require preserving their respective bundled notices. This inventory does not substitute for checking license texts, third-party code copied into notebooks, system libraries, fonts, model artifacts, or data licenses.
- No software license has been added. Public distribution is still blocked on project ownership and approval, a complete bundled-code review, file-level package scan, and clean archive test.

To reproduce the inventory, install `pip-licenses` as an isolated tool and run it against the project environment:

```powershell
uvx --from pip-licenses pip-licenses --python .venv-clean-check\Scripts\python.exe --format=markdown
```
