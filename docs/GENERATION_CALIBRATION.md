# EIA-923 generation comparison: audit gate

This repository provides a **diagnostic comparison**, not a certified historical calibration. The module accepts two separately prepared CSVs with the same columns:

`ba,technology,period,generation_mwh`

- **observed:** generation aggregated from EIA-923 by an *audited and documented* plant-to-BA crosswalk and technology classification. The module does not download data or infer BA assignment.
- **modeled:** matched PyPSA generation output aggregated into the exact same BA, technology, calendar period and units. The existing partial-fleet factorial dispatch does **not yet export this complete comparison**, and the reference 2024 case omits hydro, solar and nuclear; these must not be represented as zero output.
- Both sources must use aligned reporting conventions (gross versus net generation, storage treatment, timezone, and month cutoffs). Reject incomplete group matches rather than filling absent periods with zeros.

## Command

```bash
python -m grid_resilience.generation_calibration \
  --observed inputs/eia923_ba_technology_month.csv \
  --modeled outputs/pypsa_ba_technology_month.csv \
  --output outputs/generation_comparison
python -m pytest -q
```

The output contains `generation_matched.csv`, `generation_calibration_summary.csv`, and `generation_calibration_manifest.json`. Per-group diagnostics include total signed bias, mean absolute error per matched period, and weighted absolute percentage error (WAPE = sum of absolute errors / sum of absolute observed generation). WAPE is undefined where the observed denominator is zero and is not reported as 0.

**Important:** matching technology-month generation totals alone cannot validate hourly reliability, constrained transmission, extreme-event forcing, or out-of-sample performance. Complete generation composition and independent data audit remain required before scientific interpretation of climate-shock results.
