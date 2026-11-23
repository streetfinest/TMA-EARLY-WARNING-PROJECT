# Group 3 — Seasonal Climatology results

## Data

- District-month records: 81,000
- Districts: 150
- Valid SPI-3 values: 80,700
- Severe district-months (1981–2025): 4,364
- Consecutive severe episodes: 2,859

## Model

Unweighted seasonal frequency: p(d,m) = D(d,m)/N(d,m). Severe drought: SPI-3 <= -1.5.

## 2020–2022 retrospective verification (one lead)

- Observations: 5,400
- Severe SPI-3 months: 150
- Threshold selected on 2015–2018 validation: 5.5%
- True alerts: 84
- Missed severe months: 66
- False alerts: 2,307
- Correct non-alerts: 2,943
- Recall: 56.00%
- Precision: 3.51%
- ROC-AUC: 0.5502
- Brier Score: 0.02874
- Onset months warned: 55 of 109

## Limitations

This is a retrospective SPI-3 meteorological-drought evaluation. Seasonal probabilities do not adapt to current climate observations; 1–3-month lead equivalence is not a demonstrated early-detection lead time. Reference SPI-3 uses 1981–2010 climatological fits; the dataset applies 2022 district boundaries to earlier dates. No independently dated agricultural damage labels were used. The period 2020–2025 has previously been inspected and is not an untouched independent holdout.
