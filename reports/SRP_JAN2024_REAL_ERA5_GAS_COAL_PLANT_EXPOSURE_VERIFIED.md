# SRP January 2024: independently sourced ERA5 gas and coal plant temperature exposure

## Successful source-backed run

Official 2024 EIA-860 Plant coordinates and operable generator census were joined by plant IDs and filtered to annual Plant BA = SRP. Full-month ERA5 2-m air temperature was downloaded at EIA source plant coordinates through Open-Meteo Historical Weather Archive, with exact UTC-hour, unit, range, identity, SHA-256 and source URL validation.

**Verified source workflow:** [41772449116](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449116) SUCCESS; [Research Methods CI 41772449058](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449058) SUCCESS, committed code `fbff0a89d13377284ede280b97dea21e8da88435`. [Source artifact 13295396867](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449116/artifacts/13295396867) includes seven machine-readable provenance, source population, selected site, full hourly weather and aggregate output files.

## Source-scope and selection

The primary energy-source and compatible prime-mover gate maps NG to gas and SUB/ST to coal. A generator is counted exactly once, and battery/pumped-storage resources are not misclassified as thermal supply. The source denominator includes every eligible generator with annual Plant BA = SRP, even when a plant has no valid coordinates or is not selected.

| Source population | Gas | Coal |
|---|---:|---:|
| EIA-860 eligible generator records | 64 | 2 |
| Distinct eligible plants | 12 | 1 |
| Annual candidate nameplate MW | 8,550.1 | 821.8 |
| Distinct plants with valid coordinates | 12 | 1 |
| Source capacity with valid coordinates | 8,550.1 MW | 821.8 MW |
| Selected top-by-nameplate plants | **8** | **1** |
| Selected site nameplate | **6,638.6 MW** | **821.8 MW** |
| Sampled share of source nameplate | **77.6435%** | **100%** |

The selected gas site IDs and corresponding annual nameplate are: 8068 (1326.0 MW), 55455 (1127.0), 55129 (745.1), 56948 (726.0), 141 (712.3), 55481 (691.6), 58557 (691.6), and 55306 (619.0). Coal is Plant 6177 (821.8 MW). Some gas plants have geographically close EIA coordinates; their distinct plant identities remain explicit, but nearby ERA5 grid exposure is not independent meteorological evidence.

## Observed ERA5 source-exposure values (not generation)

January 1 00:00 through January 31 23:00 UTC, 744 hours per selected plant, **9 × 744 = 6,696 complete site-hour values**.

| 2-m temperature, capacity-weighted across selected sites | Gas selected plant set | Coal selected plant set |
|---|---:|---:|
| Mean (°C) | **11.902894** | **2.088844** |
| Hourly minimum (°C) | **-0.044669** | **-17.000000** |
| Hourly maximum (°C) | **25.677691** | **15.300000** |
| Median (°C) | **11.894960** | **2.400000** |

The mean temperature difference of ~9.81°C arises from distinct site populations and geography. It is not evidence that any specific generator was restricted, more/less efficient, underperforming, or curtailed. The monthly sampling period does not include an independently validated summer extreme-heat event.

Source provenance: `official_eia860_sha256.json`, `srp_thermal_site_coverage_manifest.json`, and `srp_thermal_era5_manifest.json` (per-request URL, downloaded source SHA-256, requested and returned coordinates). Hourly data: `srp_thermal_era5_plant_hourly.csv` and `srp_thermal_era5_technology_hourly.csv`.

## Acceptance and limits

- **Accepted:** real independent ERA5 meteorological exposure at source EIA-860 plant coordinates, complete UTC month and signed source coverage accounting; selected nameplate coverage explicitly measured.
- **Not completed:** weather-to-generator heat derating calibrated from generator performance; nuclear cooling weather exposure; auxiliary cooling water resource and ambient wet bulb linkage; full 12-gas-plant sampled data; validated physical dispatch ownership and intertie ratings; measured outage outcome/credible EENS.
- **Critical modeling decision:** Do not apply the wind-farm ERA5 2m temperature to the thermal fleet. Do not fit heat-related production loss directly from EIA-923 monthly generator records without resolving Page1/Page4/BA coverage and alternative operating conditions.
- **Next:** evaluate the 4 unsampled gas plants and full-fleet coverage, and repeat over source-supported summer/warm-season windows to establish hazard exposure. Compare independent equipment-specific cooling/derating data before a weather-conditioned generator availability schedule is treated as a physical model.

**Annual BA is dispatch right: FALSE. Weather-derived thermal derating calibrated: FALSE. Historical outages or EENS observed: FALSE.**
