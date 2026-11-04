# SRP 2024-01: independently sourced ERA5 wind-plant weather exposure

## Verified source and reproducibility

**Official EIA-860 plus actual ERA5 download:** successful [GitHub Actions workflow 41769462584](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41769462584), at commit `9ec764720bd097106744e3426f7de043fb268032`, with [artifact 13294151892](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41769462584/artifacts/13294151892). The workflow first extracts officially reported EIA-860 2024 wind-plant coordinates and matches operable generator nameplate, then downloads ERA5 2024-01 hourly wind speed at 100 m and temperature at 2 m through the Open-Meteo Historical Weather Archive. The download manifest preserves each request URL, response SHA-256, EIA plant coordinate, API returned grid-cell coordinate and grid elevation. EIA archive SHA-256 is retained independently.

**Source time:** 2024-01-01 00:00 UTC to 2024-01-31 23:00 UTC, exactly 744 hourly periods. The weather dataset is separate from EIA-930 electrical generation, EIA-923 source net MWh and all previous artificial wind-supply scenarios.

## Plant coordinate and coverage evidence

| EIA plant code | Eligible EIA860 2024 nameplate | EIA plant lat/lon | ERA5 returned grid-cell lat/lon |
|---|---:|---|---|
| 57098 | 63.0 MW | 34.6596, -110.2842 | 34.75, -110.25 |
| 66110 | 163.0 MW | 35.627731, -111.867942 | 35.75, -111.75 |

Two SRP wind-plant rows in the eligible primary-fuel, single-fuel extraction; **226 MW** total eligible wind nameplate, **226 MW** with valid EIA plant coordinates, **100% coordinate coverage within this eligible extraction population**. This is not a certification of all wind electricity physically delivered to the BA. EIA plant coordinates are not turbine hub points; API returned ERA5 grid centers are visibly distinct.

**Data integrity:** two sites × 744 verified UTC hours = **1,488** plant-hour observations. Wind variable `wind_speed_100m` has source unit m/s, temperature `temperature_2m` uses Celsius. The parser rejects missing, duplicated, misaligned, nonfinite or invalid readings and incorrect units. Both individual source response SHA-256 hashes are in `srp_era5_wind_source_manifest.json`.

## January hourly source-exposure statistics

Site-nameplate-weighted weather exposure, computed from the independent ERA5 point data:

| Metric | 100 m wind speed m/s | 2 m air temperature °C |
|---|---:|---:|
| Mean | **5.381047** | **1.633975** |
| Median | **4.357788** | **1.890265** |
| Minimum | **0.543805** | **-10.829204** |
| Maximum | **15.210442** | **13.396903** |

The fleet exposure series in `srp_era5_wind_fleet_hourly_exposure.csv` has 744 complete, ordered UTC hours; raw per-site data are in `srp_era5_wind_plant_hourly.csv`. Weighted mean weather is a descriptive exposure indicator, **not** a physical wind fleet generation curve. The 2024 wind-fleet source-hour record does not independently identify wind turbine hub height, performance curves, wake losses, curtailment, outage scheduling, transmission constraints or availability.

## Scientific acceptance gate

- **Succeeded:** independent weather ingestion with noninvented source plant coordinates and auditable provenance.
- **Not yet done:** station-level verification, wind 100m-to-hub-height extrapolation, site-specific turbine power curves, bias correction, and validation against independent actual wind plant-level generation records.
- **Not yet done:** independently sourced and plant-weighted weather exposure for gas/coal, nuclear cooling facilities, or solar arrays.
- **Explicitly forbidden inference:** interpreting a 100m ERA5 wind speed (or a naive cube-law transformation) directly as a calibrated wind generator power output or a measured SRP historical reliability event.

**Weather-source availability: YES. Historical wind production calibration: NO. Historical system adequacy or EENS calibration: NO. Climate-attributable shortfall: NOT ESTIMATED.**

## Data lineage

The purpose of this work is to move the SRP PyPSA climate-resilience study away from free-form synthetic availability factors. Future weather-conditioned sensitivity work must keep this independent ERA5 point weather and its limitations visible in model manifests, compare a documented uncalibrated proxy with the earlier synthetic base, and only claim technology-specific climate mechanism after separate validated evidence.
