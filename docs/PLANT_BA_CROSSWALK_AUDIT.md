# EIA-923 plant-to-BA provenance gate

The plant crosswalk aggregation step accepts two **upstream prepared**, source-labeled files:

- `generation.csv`: `plant_id,period,technology,generation_mwh` — one row per plant/technology/month after deliberate aggregation of generator records.
- `crosswalk.csv`: `plant_id,ba,technology,mapping_source` — one unambiguous BA assignment per plant/technology with nonempty source label.

```bash
python -m grid_resilience.plant_ba_crosswalk \
  --generation inputs/prepared_eia923_plant_month.csv \
  --crosswalk inputs/audited_plant_ba_crosswalk.csv \
  --output outputs/eia923_ba
```

Output `observed_ba_technology_month.csv` matches the `generation_calibration` schema. **Refuse missing or ambiguous mappings:** no silent drop of unmapped generators, no assignment based on nearest BA, and no conversion of absent observations into zero. Labels and source claims are not independently verified by this tool. Temporal changes in BA assignment, unit ownership, fuel-specific technology and net vs gross reporting must be reconciled externally before a historical claim. This implementation uses an invariant mapping across periods and is unsuitable when a plant's BA affiliation changes within the observation window.

The test fixture is synthetic; no EIA-923 field data are included in this commit.
