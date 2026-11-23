# Reproducibility checks

## Verified input

- Original TMA archive: SHA-256 `6ea63133fbbd335ede2065f2acedd3f207527a123a52641fc337ab51f6d8ad9f`.
- Records: 81,000 across 150 districts and 540 months.
- Valid SPI-3 values: 80,700; defined severe district-months: 4,364.
- Duplicate district-month keys: zero; negative CHIRPS rainfall values: zero; source severe-flag disagreements: zero.

## Model verification

- All 59,400 model forecasts for 2015–2025 reproduce the historical forecast table to exported CSV precision.
- Nanyumbu April 2020 calculation: 4/39 = 10.2564%.
- Lead-specific predictions coincide for identical target district-months.
- No future same-calendar-month observation enters a past forecast; a shortened-history regression test verifies predictions are unchanged.
- Alert cutoff selected on 2015–2018 targets only: 0.055.

## Case study, January 2020–December 2022

- Forecast opportunities: 5,400 unique district-months at each lead.
- Severe outcomes: 150.
- True warnings: 84.
- Missed severe months: 66.
- False warnings: 2,307.
- Correct non-alerts: 2,943.
- Recall: 56.0%; precision: approximately 3.51%.
- ROC-AUC: 0.5501702; Brier Score: 0.0287445.

## Execution

- `python -m pytest -q`: 13 passed.
- Seven notebooks executed without cell errors; their stored outputs were inspected.
- Full command-line pipeline executed, including district map and saved figures.

These are reproducibility checks of supplied-data analysis, **not** independent validation of the SPI reference, data acquisition, climate causation or operational early-warning reliability.
