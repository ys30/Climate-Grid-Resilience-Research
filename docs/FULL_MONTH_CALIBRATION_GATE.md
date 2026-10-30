# Full-calendar-month EIA-923 comparison gate

The new `monthly_generation_gate` converts technology-resolved hourly PyPSA output to full-month totals **only when every UTC hour is present** for every BA/technology combination. Missing hours, partial months, and duplicate technology-hours cause explicit failure.

```bash
python -m grid_resilience.monthly_generation_gate \
  --hourly outputs/multitech/generation_hourly.csv \
  --output outputs/monthly_generation
```

The existing 2024-07-01 to 2024-07-07 event is not eligible for comparison with a full July EIA-923 monthly total. A complete calendar month is necessary but **not sufficient**: plant-to-BA mapping, reported net/gross generation, technology category agreement, generation-fleet completeness, and actual observational provenance still need independent audit. The existing `generation_calibration` comparison can consume the resulting `modeled_generation_full_months.csv` only when observed EIA-923 aggregation uses matching definitions.

This gate does not download EIA data or certify historical calibration.
