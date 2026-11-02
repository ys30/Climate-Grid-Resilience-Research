# Verified SRP shortage concentration by UTC hour (artifact audit)

**Source:** Successfully completed GitHub Actions [run 41386883075](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075), commit `568f52f17b6d0aa287353793d1be01feecc5cd7f`. Artifact ID `13115548069`, `srp_diurnal_figure_data.csv` and `srp_hourly_figure_data.csv`. Run artifact contains 16 × 168 hourly records, 16 × 24 diurnal records and 32 PNG files.

## Nonzero modeled shortfall by UTC clock hour

| Scenario | 01 UTC MWh | 02 UTC MWh | 03 UTC MWh | Total MWh |
|---|---:|---:|---:|---:|
| baseline C100/N100/G30 | 0.000 | 450.880 | 0.000 | 450.880 |
| heat_wind C100/N100/G30 | 805.801 | 2707.128 | 829.738 | 4342.666 |
| heat_wind C100/N100/G35 | 0.000 | 635.731 | 0.000 | 635.731 |
| heat_wind C50/N75/G55 | 0.000 | 352.485 | 0.000 | 352.485 |

Source numbers are rounded to three decimals; the most severe case's rounded hourly bins can differ by 0.001 MWh from its underlying full-precision total. The UTC hours correspond to 18:00, 19:00 and 20:00 Arizona Mountain Standard Time (UTC−07:00) *on the preceding local calendar date*; Arizona does not observe daylight saving time in this locale. This is a **clock-time conversion, not independent confirmation of a physical solar-output mechanism**.

Across the most severe case, 15 positive-shortfall hourly records are distributed across these UTC clock-hour bins: four at 01 UTC, six at 02 UTC, and five at 03 UTC. Remaining hours show zero material modeled shortage. The concentration in 02 UTC is consistent with the assumed demand and supply envelopes but is **not a calibrated inference about real SRP outages**.

## Figure QA

The CI archive contains the expected 32 PNG files (two per case). CI asserts that all are nonempty and that aggregate hourly and diurnal shortage energies agree. These checks establish **file production and numerical integrity**, not visual legibility or scientific validity. Manual figure aesthetic review and historical validation remain separate gates.

## Interpretation limits

- Results are deterministic, hypothetical SRP adequacy scenarios using supplied demand, candidate EIA-860 capacity mapping and assumed fuel availability, with no verified historical intertie limits or storage dispatch.
- Solar availability is an **illustrative proxy**, not EIA-923 or observed hourly solar generation.
- Four cases have modeled shortage; the other 12 have no material shortage at this tested grid resolution.
- Shortage concentration in 01–03 UTC should be treated as an exploratory temporal diagnostic, not a direct historical outage timing claim.
