# Full-calendar EIA-923 diagnostic orchestration

This pipeline combines the full-month hourly-coverage gate with the matched BA/technology/month generation diagnostic comparison. It rejects generic thermal proxies, missing months, duplicate or mismatched observational groups, and default incomplete major-technology inventories.

```bash
python -m grid_resilience.calibration_pipeline \
  --hourly outputs/multi-tech-full-month/generation_hourly.csv \
  --observed inputs/audited_eia923_ba_technology_month.csv \
  --output outputs/eia923_comparison
```

For *explicitly labeled partial-fleet diagnostics only*, add `--allow-partial-fleet`. Passing a full set of broad technology names is not evidence of complete plant/fleet coverage. Full-month checks use UTC timestamps, so upstream local-time/month conventions require reconciliation. External EIA-923 plant-to-BA mappings, net/gross production definitions and independent capacity/fuel classification must be assessed separately.

Outputs are written to `coverage/`, `comparison/`, and `calibration_pipeline_manifest.json`. The manifest intentionally sets `historical_calibration_certified: false`. This gate is an engineering safeguard, **not** a certification of historical power-system calibration, model fit, or observed outage accuracy. Synthetic unit tests are not evidence of empirical fit.
