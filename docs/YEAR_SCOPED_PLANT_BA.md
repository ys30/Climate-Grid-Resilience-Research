# Year-scoped plant-to-BA crosswalk

The `year_scoped_plant_ba` module assigns observed EIA-923-like prepared generation to balancing authorities by **plant ID + technology + year**, not an assumed time-invariant mapping. Input columns:

- generation: `plant_id,period,technology,generation_mwh` (YYYY-MM)
- crosswalk: `plant_id,source_year,technology,ba,mapping_source`

Run:

```bash
python -m grid_resilience.year_scoped_plant_ba \
  --generation inputs/audited_eia923_plant_technology_month.csv \
  --crosswalk inputs/audited_plant_ba_year.csv \
  --output outputs/eia923_year_scoped
```

Missing and ambiguous plant-year assignments fail closed. This is a mechanical mapping gate, **not** external confirmation of EIA records or BA affiliations. The year-wide attribution assumption is inappropriate for changes *within* a year; those require month/effective-date crosswalks. Net/gross conventions, generator-technology assignments, plant closures/transfers and original-source provenance must still be independently audited before a historical calibration claim.

All tests use synthetic fixtures; no EIA-923 observational data are included.
