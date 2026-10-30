# End-to-end EIA-923-like observed generation comparison

This is a reproducible **mechanical validation chain**, not a source-authenticated historical calibration.

Inputs: (1) observed prepared plant/technology/month generation with source label and reporting basis, (2) independent expected observation keys, (3) year-scoped plant-to-BA crosswalk, and (4) full-month hourly technology-resolved modeled generation.

```bash
python -m grid_resilience.observed_to_model_pipeline \
  --observed inputs/observed_plant_month.csv \
  --expected inputs/expected_plant_month_keys.csv \
  --crosswalk inputs/plant_ba_by_year.csv \
  --modeled-hourly outputs/full_month/generation_hourly.csv \
  --output outputs/eia923_end_to_end
```

The default rejects partial fleet comparisons. Add `--allow-partial-fleet` only for narrow, clearly identified technology diagnostics. The pipeline performs exact observation-key coverage validation, year-scoped BA matching, complete UTC-calendar-month coverage checking, then technology/BA/month bias and WAPE comparisons.

No EIA-923 downloads, authenticated plant assignments, source verification, or predictive holdout evaluation are performed by this command. The example tests use synthetic values and do not validate historical grid adequacy.
