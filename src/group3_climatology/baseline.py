"""Unweighted Seasonal Climatology forecasts from historical counts D/N."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .config import SPI_FIELD, SEVERE_THRESHOLD, LEADS


def forecast_table(data: pd.DataFrame, start_year: int = 2015,
                   end_year: int = 2025, leads: tuple[int, ...] = LEADS) -> pd.DataFrame:
    """Construct one retrospectively issued forecast per district, target and lead.

    For h <= 3, the previous observation in the same calendar month always
    predates the issue month. Counts exclude the current target observation.
    """
    if any(h < 1 or h > 11 for h in leads):
        raise ValueError('The preceding-year guarantee requires lead times from 1 to 11 months.')
    x = data.sort_values(['district_id', 'month']).copy()
    x['calendar_month'] = x['month'].dt.month
    x['year'] = x['month'].dt.year
    valid = x[SPI_FIELD].notna()
    x['observed_severe'] = x[SPI_FIELD].le(SEVERE_THRESHOLD).where(valid).astype('float64')
    history = x.loc[valid, ['district_id','month','calendar_month','observed_severe']].copy()
    keys = ['district_id','calendar_month']
    history['N'] = history.groupby(keys, sort=False).cumcount()
    history['D'] = (history.groupby(keys, sort=False)['observed_severe'].cumsum()
                    - history['observed_severe']).astype(int)
    history['probability'] = np.where(history['N'].gt(0),
                                     history['D']/history['N'].replace(0, np.nan), np.nan)
    x = x.merge(history[['district_id','month','N','D','probability']],
                on=['district_id','month'],how='left',validate='one_to_one')
    x['previous_spi3'] = x.groupby('district_id')[SPI_FIELD].shift()
    previous_month = x.groupby('district_id')['month'].shift()
    x['severe_onset'] = (x['observed_severe'].eq(True)
                         & x['previous_spi3'].gt(SEVERE_THRESHOLD)
                         & (previous_month.dt.to_period('M') + 1 == x['month'].dt.to_period('M')))
    x = x[x['year'].between(start_year,end_year) & x[SPI_FIELD].notna() & x['N'].gt(0)].copy()
    result = []
    for lead in leads:
        one = x.copy()
        one['horizon_months'] = lead
        one['issue_month'] = one['month'] - pd.DateOffset(months=lead)
        one['latest_used_month_upper_bound'] = one['month'] - pd.DateOffset(years=1)
        if not (one['latest_used_month_upper_bound'] < one['issue_month']).all():
            raise AssertionError('A forecast uses a historical observation at or beyond issue time.')
        one = one.rename(columns={
            'month': 'target_month', SPI_FIELD: 'observed_spi3',
            'N': 'historical_valid_years', 'D': 'historical_severe_years',
            'probability': 'predicted_probability'
        })
        result.append(one[[
            'district_id','region','district','issue_month','target_month','horizon_months',
            'calendar_month','historical_severe_years','historical_valid_years',
            'predicted_probability','observed_spi3','observed_severe','severe_onset',
            'latest_used_month_upper_bound'
        ]])
    out = pd.concat(result, ignore_index=True)
    out['observed_severe'] = out['observed_severe'].astype(int)
    out['severe_onset'] = out['severe_onset'].astype(int)
    out = out.sort_values(['target_month','district_id','horizon_months']).reset_index(drop=True)
    if not out['predicted_probability'].between(0,1).all():
        raise AssertionError('Forecast probability outside [0,1].')
    for _, grouped in out.groupby(['district_id','target_month']):
        if grouped['predicted_probability'].nunique() != 1:
            raise AssertionError('Baseline probability must be identical for every lead.')
    return out


def climatology_snapshot(data: pd.DataFrame, cutoff: str = '2019-12-01') -> pd.DataFrame:
    x = data[data['month'].le(pd.Timestamp(cutoff)) & data[SPI_FIELD].notna()].copy()
    x['calendar_month'] = x['month'].dt.month
    x['severe'] = x[SPI_FIELD].le(SEVERE_THRESHOLD).astype(int)
    counts = x.groupby(['district_id','region','district','calendar_month'], as_index=False).agg(
        D=('severe','sum'), N=('severe','size'))
    counts['probability'] = counts['D'] / counts['N']
    return counts.sort_values(['region','district','calendar_month']).reset_index(drop=True)


def inspect_forecast(forecasts: pd.DataFrame, district: str, target: str,
                     lead: int = 3) -> pd.DataFrame:
    """Return a traceable one-district calculation from the full forecast register."""
    if lead not in LEADS:
        raise ValueError('Use a lead of 1, 2, or 3 months.')
    d = forecasts[(forecasts['district'].str.casefold() == district.casefold())
                  & forecasts['target_month'].eq(pd.Timestamp(target))
                  & forecasts['horizon_months'].eq(lead)]
    return d.copy().reset_index(drop=True)
