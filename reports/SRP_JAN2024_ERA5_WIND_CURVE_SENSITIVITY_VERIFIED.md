# SRP 2024-01: ERA5 wind-plant point weather → three uncalibrated turbine curves

**Verified official weather workflow:** [41771290045](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771290045), [research methods CI 41771290065](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771290065), both SUCCESS on code `d8223360c566d32d1844fe52a067e98e7caa1d91`. [Artifact 13295195909](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771290045/artifacts/13295195909) preserves 11 evidence files including source URL/SHA256 provenance, raw site-hour ERA5 weather, per-plant curve proxies, per-hour fleet proxies, sensitivity summary and uncertainty flags.

## Input scope

Two eligible SRP wind sites extracted from official EIA-860 2024 Plant coordinates and nameplate: plant **57098**, **63 MW**, and plant **66110**, **163 MW**, totaling **226 MW**. ERA5 via Open-Meteo Historical Weather Archive returned **744 UTC wind-speed_100m (m/s) and temperature_2m (°C) observations per plant**, 1,488 complete plant-hours. The EIA-860 coordinates are plant locations, not turbine hub coordinates; the ERA5 point is an interpolated grid-cell reanalysis rather than an anemometer at any turbine.

The nonlinear idealized wind power curve is applied at **each individual plant and hour first**. After transforming wind to a dimensionless proxy in [0,1], outputs are averaged with source site-nameplate shares 63/226 and 163/226. This avoids the incorrect alternative of passing capacity-weighted mean wind speed through a nonlinear power curve.

Three *assumed*, **non-calibrated** curves use the same piecewise idealized cubic model `P(v) = (v³ - v_in³)/(v_rated³ - v_in³)` between cut-in and rated wind speeds, zero below cut-in or at/above cut-out, and one between rated and cut-out.

| Curve scenario | Cut-in m/s | Rated m/s | Cut-out m/s | Mean fleet proxy | Idealized January proxy energy MWh | Hours with zero modeled fleet proxy |
|---|---:|---:|---:|---:|---:|---:|
| low_cut_in | 2.5 | 10.0 | 25.0 | 0.267189 | 44,926.199 | 46 |
| reference | 3.0 | 12.0 | 25.0 | 0.177521 | 29,849.115 | 110 |
| high_cut_in | 4.0 | 14.0 | 25.0 | 0.114913 | 19,321.854 | 231 |

The largest simulated proxy energy is approximately **2.325×** the smallest on identical underlying ERA5 weather and wind nameplate, illustrating the sensitivity of derived production to turbine curve assumptions. These proxy energies are **not observed generation**, not estimates from turbine-specific manufacturer curves, and not validated SRP-wide wind capacity factors.

## Code and quality gates

- `src/grid_resilience/srp_era5_wind_curve_sensitivity.py` applies curves per plant-hour, checks complete January UTC 744h grids, uniqueness of plant IDs and timestamps, finite 100m wind speeds, positive nameplate, constant per-plant weight, and normalized source weights matching the annual EIA nameplate.
- Unit tests reject missing hours, duplicate plant-hours, bad timestamps, inconsistent weights, invalid curves, and verify per-plant nonlinear transformation before fleet averaging.
- The ERA5 workflow uploads `srp_era5_wind_curve_plant_hourly.csv`, `srp_era5_wind_curve_fleet_hourly.csv`, `srp_era5_wind_curve_sensitivity_summary.csv`, and the scientific caution manifest. Source acquisition URLs and source response hashes are retained in the companion actual ERA5 source manifest.

## Manuscript interpretation and next gate

This is a concrete advance from purely synthetic constant wind availability toward **weather-dependent but deliberately uncalibrated proxy profiles**. It also demonstrates substantial **model-form uncertainty**. It is **not** a validation of actual SRP January 2024 wind electricity, plant outage schedules, wind power curtailment, or regional reliability. In particular:

1. Verify whether independent plant-level (not merely BA total fuel) actual wind output or telemetry is available with matching geography, UTC timestamps and generation ownership.
2. Investigate turbine types, hub height, wake and terrain treatment, turbine power curves and curtailment before claims of predicted wind output.
3. Evaluate whether inserting any of these profiles into PyPSA changes stress-screen outcomes **while holding the other synthetic resource assumptions fixed**. Such an experiment must remain a model uncertainty test, not a causal climate or observed blackout estimate.
4. For gas/coal/nuclear heat mechanisms, use site-specific weather at *their own locations*, not the wind-farm temperature proxy.

**Actual plant-level wind generation validated: NO. Weather source/UTC source lineage verified: YES. Historical EENS or climate-driven outage estimated: NO.**
