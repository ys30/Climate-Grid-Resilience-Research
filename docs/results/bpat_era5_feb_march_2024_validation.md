# BPAT 29-site ERA5 wind proxy: independent March validation

**Validation evidence:** [February multi-site run](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41227782144), [March independent month run](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41238968791) (both succeeded).

The March 2024 evaluation preserves the February experiment's **29 EIA-860 wind plant coordinates and nameplate weights**, ERA5 100 m winds, and idealized fixed 3/12/25 m/s turbine power curve. March EIA-930 observed wind was not used to fit or select a new power curve.

| Metric | February 2024 | March 2024 |
|---|---:|---:|
| Hours | 696 | 744 |
| Pearson correlation | 0.893405 | 0.904463 |
| Mean modeled proxy availability | 13.8971% | 11.1022% |
| Mean observed net-wind/nameplate ratio | 19.1701% | 19.3318% |
| Mean error (proxy minus clipped observed), percentage points | −5.2730 | −8.2299 |
| MAE, percentage points | 7.4831 | 8.6477 |
| RMSE, percentage points | 10.9650 | 12.5274 |

## Independent-month inference

The **sign and magnitude of hourly temporal association** persist into March, but **generation amplitude error worsens**: March MAE rises by 1.165 percentage points and underprediction grows by 2.957 percentage points. The independent validation therefore supports wind-timing proxy usefulness, **not unbiased calibrated generation, forecasting skill, or historical shortage accuracy**.

This result is consistent with the disjoint February temporal holdout [negative calibration result](bpat_era5_feb2024_temporal_holdout.md): a one-factor amplitude correction worsened test accuracy in both directions.

## Scope and limitations

- Both months are the same winter-to-early-spring period, with only two months sampled.
- The observed target is **EIA-930 actual net wind generation**, which includes curtailment/availability/operations and is not a direct measurement of raw wind potential.
- Site-coordinate mapping is plant-based; actual turbine coordinates and power curves, turbine availability, curtailment, hub-height variation, and evolving operational fleets are not modeled.
- EIA-860 2024 nameplate fleet is applied to both months as a fixed reference, not certified contemporaneous operating capacity.
- No independent March PyPSA adequacy solve is asserted here; this is a weather-versus-generation diagnostic, not a grid outage result.

## Research decision

Retain uncalibrated ERA5 as a **screening weather input**, clearly separated from observed replay and real historical reliability claims. Next steps are additional-season months and genuine system-operating constraints rather than fitting one global correction factor to the two displayed months.
