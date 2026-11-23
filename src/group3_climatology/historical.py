"""Historical drought classification, frequency and episode reconstruction."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .config import SPI_FIELD, DROUGHT_THRESHOLD, SEVERE_THRESHOLD, EXTREME_THRESHOLD


def classify(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    x = frame[SPI_FIELD]
    frame['year'] = frame['month'].dt.year
    frame['calendar_month'] = frame['month'].dt.month
    frame['is_drought'] = x.le(DROUGHT_THRESHOLD).where(x.notna()).astype('Float64')
    frame['is_severe'] = x.le(SEVERE_THRESHOLD).where(x.notna()).astype('Float64')
    frame['is_extreme'] = x.le(EXTREME_THRESHOLD).where(x.notna()).astype('Float64')
    frame['spi_class'] = np.select(
        [x.le(-2.0), x.le(-1.5), x.le(-1.0), x.gt(-1.0)],
        ['Extreme', 'Severe', 'Moderate', 'No drought'], default='Undefined'
    )
    return frame


def historical_tables(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    x = classify(data)
    district = x.groupby(['district_id', 'region', 'district'], as_index=False).agg(
        valid_spi_months=(SPI_FIELD, 'count'),
        severe_months=('is_severe', 'sum'),
        drought_months=('is_drought', 'sum'),
        extreme_months=('is_extreme', 'sum'),
        lowest_spi3=(SPI_FIELD, 'min'),
        average_rainfall_mm=('chirps3_rain_mm', 'mean'),
    )
    district['severe_frequency'] = district['severe_months'] / district['valid_spi_months']
    region = district.groupby('region', as_index=False).agg(
        districts=('district_id', 'size'), severe_months=('severe_months', 'sum'),
        valid_spi_months=('valid_spi_months', 'sum'), extreme_months=('extreme_months', 'sum'),
    )
    region['severe_frequency'] = region['severe_months'] / region['valid_spi_months']
    annual = x.groupby('year', as_index=False).agg(
        severe_months=('is_severe', 'sum'), valid_spi_months=(SPI_FIELD, 'count'),
        extreme_months=('is_extreme', 'sum')
    )
    annual['severe_frequency'] = annual['severe_months'] / annual['valid_spi_months']
    season = x.groupby('calendar_month', as_index=False).agg(
        severe_months=('is_severe', 'sum'), valid_spi_months=(SPI_FIELD, 'count')
    )
    season['severe_frequency'] = season['severe_months'] / season['valid_spi_months']
    national = x.groupby('month', as_index=False).agg(
        severe_months=('is_severe', 'sum'), valid_spi_months=(SPI_FIELD, 'count')
    )
    national['severe_frequency'] = national['severe_months'] / national['valid_spi_months']
    return {'district': district, 'region': region, 'annual': annual,
            'calendar_month': season, 'national_monthly': national}


def drought_episodes(data: pd.DataFrame, threshold: float = SEVERE_THRESHOLD) -> pd.DataFrame:
    """Maximal consecutive monthly runs below the threshold, split at gaps/missing SPI."""
    records = []
    df = data.sort_values(['district_id', 'month'])
    for district_id, g in df.groupby('district_id', sort=False):
        active = []
        prev_period = None

        def close_episode():
            if not active:
                return
            a = pd.DataFrame(active)
            peak = a.loc[a[SPI_FIELD].idxmin()]
            records.append({
                'district_id': district_id,
                'region': a['region'].iloc[0],
                'district': a['district'].iloc[0],
                'start_month': a['month'].iloc[0],
                'end_month': a['month'].iloc[-1],
                'duration_months': int(len(a)),
                'lowest_spi3': float(a[SPI_FIELD].min()),
                'peak_month': peak['month'],
                'extreme_months': int(a[SPI_FIELD].le(-2).sum()),
            })
        for row in g.itertuples(index=False):
            date = pd.Timestamp(row.month)
            value = getattr(row, SPI_FIELD)
            qualifies = pd.notna(value) and value <= threshold
            period = date.to_period('M')
            if qualifies:
                if active and period != prev_period + 1:
                    close_episode()
                    active = []
                active.append({'month': date, 'region': row.region,
                               'district': row.district, SPI_FIELD: float(value)})
                prev_period = period
            else:
                close_episode()
                active = []
                prev_period = None
        close_episode()
    return pd.DataFrame(records).sort_values(['start_month','district_id']).reset_index(drop=True)


def northern_case_study(data: pd.DataFrame) -> pd.DataFrame:
    """Season rainfall versus 1981–2010 seasonal means; separate from the SPI label."""
    x = classify(data)
    records = []
    for district in ['Longido', 'Monduli', 'Simanjiro']:
        g = x[x['district'].eq(district)].copy()
        for name, year, months in [('Vuli 2021', 2021, [10, 11, 12]),
                                   ('Masika 2022', 2022, [3, 4, 5])]:
            reference = g[g['year'].between(1981, 2010) & g['calendar_month'].isin(months)]
            baseline = reference.groupby('year')['chirps3_rain_mm'].sum().mean()
            observed = g[g['year'].eq(year) & g['calendar_month'].isin(months)]
            total = float(observed['chirps3_rain_mm'].sum())
            records.append({
                'district': district, 'season': name,
                'rainfall_mm': total, 'reference_rainfall_mm': float(baseline),
                'percent_of_reference': 100 * total / baseline,
                'last_month_spi3': float(observed.sort_values('month')[SPI_FIELD].iloc[-1]),
                'months_with_severe_spi3': int(observed['is_severe'].sum()),
            })
    return pd.DataFrame(records)
