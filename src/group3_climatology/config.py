"""Study configuration and source-field definitions."""
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
INPUT = PROJECT / 'data' / 'processed' / 'tma_baseline_inputs.csv.gz'
GEOGRAPHY = PROJECT / 'data' / 'geography' / 'NBS_2022_districts.gpkg'
OUTPUT = PROJECT / 'outputs'
SPI_FIELD = 'spi3_gamma_ref1981_2010'
SEVERE_THRESHOLD = -1.5
DROUGHT_THRESHOLD = -1.0
EXTREME_THRESHOLD = -2.0
LEADS = (1, 2, 3)
EVALUATION_START = 2015
EVALUATION_END = 2025
VALIDATION_YEARS = (2015, 2018)
CASE_STUDY_YEARS = (2020, 2022)
SOURCE_ARCHIVE_SHA256 = '6ea63133fbbd335ede2065f2acedd3f207527a123a52641fc337ab51f6d8ad9f'
