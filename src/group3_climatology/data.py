"""Source extraction and tabular data verification."""
from __future__ import annotations
import hashlib
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from .config import INPUT, SPI_FIELD, SEVERE_THRESHOLD, SOURCE_ARCHIVE_SHA256

ARCHIVE_MEMBER = '01_START_HERE/TMA_ALL_DISTRICT_MONTHLY_DATA.csv'
CORE_COLUMNS = [
    'district_id', 'region', 'district', 'month', 'chirps3_rain_mm',
    'rain_3month_mm', SPI_FIELD, 'severe_spi3_this_month', 'wfp_modis_ndvi'
]


def extract_core_data(archive: str | Path, destination: str | Path = INPUT, verify_hash: bool = True) -> pd.DataFrame:
    """Rebuild the compact, repository-tracked input table from the original TMA archive."""
    archive = Path(archive)
    if verify_hash and hashlib.sha256(archive.read_bytes()).hexdigest() != SOURCE_ARCHIVE_SHA256:
        raise ValueError('The original TMA archive checksum differs from the verified source.')
    with zipfile.ZipFile(archive) as z:
        with z.open(ARCHIVE_MEMBER) as f:
            frame = pd.read_csv(f, dtype={'district_id': str}, low_memory=False)
    absent = sorted(set(CORE_COLUMNS) - set(frame.columns))
    if absent:
        raise ValueError(f'Missing source columns: {absent}')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame[CORE_COLUMNS].to_csv(destination, index=False, compression='gzip')
    return load_data(destination)


def load_data(path: str | Path = INPUT) -> pd.DataFrame:
    """Load the exact historical SPI-3 and rainfall fields used in the baseline."""
    data = pd.read_csv(path, dtype={'district_id': str}, parse_dates=['month'], low_memory=False)
    missing = sorted(set(CORE_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f'Missing input columns: {missing}')
    data = data.sort_values(['district_id', 'month'], kind='stable').reset_index(drop=True)
    if data['month'].isna().any():
        raise ValueError('Unparseable monthly dates found.')
    return data


def audit_data(data: pd.DataFrame, strict: bool = True) -> dict:
    """Inspect uniqueness, temporal continuity, physical plausibility and SPI labels."""
    if not set(CORE_COLUMNS).issubset(data.columns):
        raise ValueError('Input table does not contain the required fields.')
    x = data[SPI_FIELD]
    valid = x.notna()
    mismatch = int((data.loc[valid, 'severe_spi3_this_month'].astype(int)
                    != (x[valid] <= SEVERE_THRESHOLD).astype(int)).sum())
    duplicate = int(data.duplicated(['district_id', 'month']).sum())
    missing_labels = int(data.loc[valid, 'severe_spi3_this_month'].isna().sum())
    wrongly_labelled_missing = int(data.loc[~valid, 'severe_spi3_this_month'].notna().sum())
    negative_rain = int(data['chirps3_rain_mm'].lt(0).sum())
    monthly_start = data['month'].dt.to_period('M').min()
    monthly_end = data['month'].dt.to_period('M').max()
    expected_months = len(pd.period_range(monthly_start, monthly_end, freq='M'))
    counts = data.groupby('district_id')['month'].nunique()
    coverage_defects = int((counts != expected_months).sum())
    checks = {
        'district_month_records': int(len(data)),
        'districts': int(data['district_id'].nunique()),
        'regions': int(data['region'].nunique()),
        'first_month': str(monthly_start),
        'last_month': str(monthly_end),
        'calendar_months': int(data['month'].nunique()),
        'valid_spi3': int(valid.sum()),
        'missing_spi3': int((~valid).sum()),
        'severe_spi3_months': int(x.le(SEVERE_THRESHOLD).sum()),
        'extreme_spi3_months': int(x.le(-2.0).sum()),
        'duplicate_district_month': duplicate,
        'districts_with_incomplete_month_coverage': coverage_defects,
        'negative_rainfall': negative_rain,
        'spi_threshold_label_mismatches': mismatch,
        'missing_labels_with_valid_spi': missing_labels,
        'nonmissing_labels_with_missing_spi': wrongly_labelled_missing,
        'available_original_ndvi_months': int(data['wfp_modis_ndvi'].notna().sum()),
        'spi_reference_period': '1981–2010',
    }
    if strict and (duplicate or coverage_defects or negative_rain or mismatch
                   or missing_labels or wrongly_labelled_missing):
        raise ValueError(f'Quality-control failure: {checks}')
    return checks


def missing_by_year(data: pd.DataFrame) -> pd.DataFrame:
    g = data.assign(year=data['month'].dt.year).groupby('year', as_index=False).agg(
        districts=('district_id', 'nunique'),
        rainfall_valid=('chirps3_rain_mm', 'count'),
        spi3_valid=(SPI_FIELD, 'count'),
        ndvi_valid=('wfp_modis_ndvi', 'count'),
    )
    g['spi3_missing'] = g['districts'] * 12 - g['spi3_valid']
    return g
