# Input provenance and reproducibility

**Original user-supplied archive:** `TMA_ALL_AVAILABLE_DATA_FOR_STUDENTS(1).zip`  
**SHA-256:** `6ea63133fbbd335ede2065f2acedd3f207527a123a52641fc337ab51f6d8ad9f`

Original archive members used:

- `01_START_HERE/TMA_ALL_DISTRICT_MONTHLY_DATA.csv` — main 31-variable, 81,000-row source table.
- `02_GEOGRAPHY/NBS_2022_districts.gpkg` — district polygons used for the optional map.
- `02_GEOGRAPHY/district_adjacency_edges.csv` — retained as geographic documentation; not a baseline input.
- `04_PROVENANCE_AND_QUALITY/DATA_DICTIONARY_31_COLUMNS.csv` — source variable descriptions and coverage.

**Derived, repository-tracked input:** `data/processed/tma_baseline_inputs.csv.gz` contains only `district_id`, `region`, `district`, `month`, `chirps3_rain_mm`, `rain_3month_mm`, `spi3_gamma_ref1981_2010`, `severe_spi3_this_month`, and `wfp_modis_ndvi`. It preserves the original values without interpolating missing data or computing alternate SPI indices.

To regenerate: `python scripts/rebuild_from_tma_zip.py <original-zip-path>`.

The compact dataset and geography are supplied in the deliverable ZIP and can be used without re-extracting the original archive. Original datasets may have distribution restrictions; obtain appropriate permission before placing their derivatives in a public GitHub repository.
