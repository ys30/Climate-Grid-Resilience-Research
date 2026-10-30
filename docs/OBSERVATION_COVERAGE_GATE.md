# Observation coverage and reporting-basis gate

Prepared EIA-923-like plant-month data must carry `plant_id,technology,period,generation_mwh,source_file,reporting_basis`. An independently assembled expected-key inventory must contain exactly `plant_id,technology,period` for each expected observation.

```bash
python -m grid_resilience.observation_coverage \
  --observed inputs/plant_technology_month.csv \
  --expected inputs/expected_plant_technology_month.csv \
  --output outputs/eia923_coverage
```

The module rejects missing/extra keys, duplicates, non-finite generation, missing provenance labels, and mixed reporting bases. A measured zero is preserved and is **not** conflated with an absent record. Important: this does not verify whether the supplied expected-key inventory is itself complete, or whether source labels reflect genuine EIA publications. Those checks remain independent research tasks. It does not adjust for unit gross-vs-net conversion or EIA reporting exceptions.

After external confirmation, the checked rows can be projected to plant-month generation, then matched using year-specific BA crosswalks and full-calendar PyPSA output.
