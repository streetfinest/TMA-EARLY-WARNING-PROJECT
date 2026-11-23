# Seasonal Climatology — Methods

## Forecast target

For district \(d\) and target month \(T\), the severe meteorological drought indicator is

\[
Y_{d,T}=1\{\mathrm{SPI3}_{d,T}\le-1.5\}.
\]

The underlying gamma-fitted SPI-3 series is supplied by the TMA student archive and uses a **1981–2010 reference distribution**. The project does not modify or re-estimate that SPI series.

## Baseline

For calendar month \(m=m(T)\), let \(D_{d,m}\) be the number of **valid preceding-year** observations with \(Y=1\) and \(N_{d,m}\) the number of valid preceding-year observations. The model is exactly

\[
\hat p_{d,T}=D_{d,m(T)}/N_{d,m(T)}.
\]

No smoothing, normalization of counts, nonuniform sample weighting or external explanatory predictors are used. If \(N=0\), the estimate is unavailable. Historical occurrences are conditioned only on district and calendar month.

### Forecast chronology

For a forecast issued at month \(I=T-h\), with \(h\in\{1,2,3\}\), the latest available **same-calendar-month history** ends at \(T-12\) months (previous year). That is earlier than the issue month. The source SPI reference period ends in 2010, and the evaluation is restricted to 2015 onward; source index construction therefore precedes all evaluated forecast issue months. Future SPI values are used **only after the forecast date**, to verify outcomes.

### Example

The forecast for **Nanyumbu, April 2020**, issued January 2020 at three months' lead, uses 39 valid earlier Aprils and four severe SPI-3 occurrences:

\[
\hat p=4/39=0.10256\simeq10.26\%.
\]

The observed April 2020 SPI-3 was approximately −1.769 (severe). This single observation is not a reliability estimate.

## Historical event definitions

- General drought: SPI-3 ≤ −1.0.
- Severe or more extreme: SPI-3 ≤ −1.5 (the forecast target).
- Extreme: SPI-3 ≤ −2.0.
- Episode: maximal consecutive months in one district satisfying the selected threshold. Missing months or observations above the threshold break the episode.
- New severe onset: the first severe month immediately following a valid non-severe month; no imputation through missing months.

## Validation, warnings and scoring

The warning threshold is selected by maximum F2 on **2015–2018** one-month validation targets. Candidate probability thresholds are 0.010 through 0.300 in 0.005 steps. Ties use fewer false alerts, then higher threshold. For the supplied data, the selected threshold is 0.055 (5.5%). This is a retrospective *exploratory decision rule*, not an operational TMA alert policy.

Scores are calculated for individual district-month targets with identical evaluation cases at each of 1, 2 and 3 months: Brier Score, ROC-AUC, average precision, precision, recall, true alerts, false alerts, missed events and correct non-alerts. Do **not** sum severe-event counts over leads as though they are independent events. A baseline probability issued three months early is not evidence of three months of actionable lead time.

## Interpretation boundaries

The severe-SPI target is **meteorological** drought, not vegetation failure, crop loss, livestock mortality or drought-induced displacement. Independent impact data and precise impact dates would be needed to validate pre-damage warning claims. The supplied 1981–2010 SPI reference and fixed NBS 2022 district geography may affect historical interpretation. The 2020–2022 severe SPI-3 indicators do not capture all documented rainfall deficits in northern Tanzania. The project does not claim a causal evaluation or a live forecasting service.
