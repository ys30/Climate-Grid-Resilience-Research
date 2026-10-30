# EIA-930 official hourly BA demand intake

EIA publishes hourly Balancing Authority operating data through its official API v2 `electricity/rto/region-data` endpoint. The `type=D` series is reported actual demand; hourly `value` is in MWh per reporting interval. It is numerically equivalent to mean MW over a one-hour interval, subject to confirming time labeling.

Reference: https://www.eia.gov/opendata/ and https://www.eia.gov/opendata/documentation.php

A downloaded JSON response can be converted with:

```bash
python -m grid_resilience.eia930_hourly_demand \
  --json inputs/eia930_region_data_2024_02.json \
  --start 2024-02-01T00 --end 2024-02-29T23 \
  --output outputs/eia930_2024_02
```

Only `type=D` and exactly the four project BAs (CISO, AZPS, BPAT, SRP) are accepted by default. All February 2024 UTC hours (696 × 4 records) must be present, pagination must be complete, and no missing/negative/duplicate values are silently imputed. The resulting `hourly_ba_demand.csv` is compatible with multi-technology PyPSA demand input schema.

**This module processes input JSON; it does not itself acquire EIA data, validate the API request parameters or establish source authenticity.** A full historical model additionally requires observed BA-specific technology capacities, availability, and observed intertie limits; successfully normalizing demand alone does not make the solve empirically calibrated.
