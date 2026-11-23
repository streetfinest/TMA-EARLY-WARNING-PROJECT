# Predicting Drought Before the Rains Fail

## Seasonal Climatology Baseline | Research Group 3

This repository contains **one comprehensive Jupyter notebook** and supporting Python modules for reproducible drought research in Tanzania (1981–2025).

**Open:** `notebooks/Seasonal_Climatology_Research.ipynb` and select **Run → Run All Cells**.

### Contents

The single notebook proceeds through data exploration, quality control, historical drought reconstruction, the Seasonal Climatology equation and worked examples, 1–3-month forecasts, forecast verification and research conclusions. Supporting functions and automated tests remain under `src/` and `tests/`, while figures and tabular output are saved under `outputs/`.

### Mathematical specification

$$\hat p_{d,m}=\frac{D_{d,m}}{N_{d,m}}, \quad Y_{d,t}=\mathbb{1}\{SPI3_{d,t}\le -1.5\}.$$

Counts are from prior valid years in the **same district and calendar month**. No weighting, smoothing, regression or satellite-data matching is used. Satellite records are descriptive context only.

### Start using uv on Windows PowerShell

Open PowerShell in the extracted project directory and run:

```powershell
uv run --with-requirements requirements.txt jupyter lab
```

Alternatively, with an already configured Python environment:

```powershell
python -m jupyter lab
```

The complete notebook can be run from JupyterLab's **Run → Run All Cells** menu. Data inputs needed for all statistical analyses are included under `data/processed/`.

To verify the scientific implementation independently:

```powershell
uv run --with-requirements requirements.txt python -m pytest -q
```

### Methodological scope

- Data: 150 fixed NBS 2022 district units, January 1981–December 2025.
- Target: SPI-3 at or below −1.5 (severe or extreme meteorological drought).
- SPI-3 reference period in the source: 1981–2010.
- Retrospective forecasts: 2015–2025, leads 1–3 months.
- Alert threshold chosen only using 2015–2018 validation cases.
- Main case study: 2020–2022, a **retrospective** evaluation, not a pristine independent holdout.

The baseline estimates seasonal drought risk, not the exact onset of rainfall failure or agricultural damage. District geography for mapping is optional; the map cell is skipped if geopandas is unavailable.

### Data provenance and reuse

See `docs/DATA_PROVENANCE.md` and `docs/METHODOLOGY.md`. The input table is a compact lossless subset of the original TMA ZIP, included for straightforward notebook execution. Permission to redistribute source-derived data should be verified before publishing a public GitHub repository.
