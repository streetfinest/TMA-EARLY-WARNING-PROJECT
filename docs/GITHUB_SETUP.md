# GitHub repository setup

The project folder is intended to be a single GitHub repository. Its compact model input and district geography are included; the original source archive and generated numerical outputs are ignored by Git.

## First publication

From a terminal opened in the extracted `group3-seasonal-climatology` folder:

```bash
git init -b main
git add .
git commit -m "Establish reproducible seasonal climatology baseline"
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Create an empty repository on GitHub beforehand; substitute its real HTTPS or SSH URL for `YOUR_GITHUB_REPOSITORY_URL`.

If Git requires an identity, configure `user.name` and `user.email` locally before committing.

## Verification before pushing

```bash
python -m pytest -q
python scripts/run_pipeline.py --no-plots
```

All seven notebooks can be executed with:

```bash
python scripts/run_notebooks.py
```

The included GitHub Actions workflow runs the test suite, pipeline and notebooks on Python 3.11 after every push and pull request. **Data-publication rights:** confirm the licensing and redistribution permissions for the processed climate and NBS boundary data before making the repository public. A private repository avoids inadvertent public sharing, but permissions should still be respected.
