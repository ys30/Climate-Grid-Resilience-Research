# SRP July 2024: coincident temperature exposure across source-eligible thermal plants

## Verified immutable source and workflow

The [matched plant-hour and concurrent heat exposure workflow, run 41779881137](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41779881137) succeeded, as did the corresponding [Research Methods CI run 41779881139](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41779881139), at code commit `62fd85860e6acccbe1398b8b45a5fe27025decb1`. [Artifact 13297839220](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41779881137/artifacts/13297839220) contains 12 datasets and metadata files, including `site_coincident_heat_hourly.csv`, `site_coincident_heat_episodes.csv`, `site_coincident_heat_summary.csv` and `site_coincident_heat_manifest.json`.

Sources are original verified ERA5 January and July 2024 plant-point temperatures at official EIA-860 2024 Plant coordinates, via Open-Meteo Historical Archive. The January/July comparison has identical **12 gas plants (8,550.1 MW)** and **one coal plant (821.8 MW)**, matched by plant identity and year-source nameplate.

## Method

For each July UTC hour and each eligible technology, threshold the **individual plant point** ERA5 2m air temperatures before summing source-eligible EIA-860 annual nameplate MW. For each technology and weather threshold (35°C, 40°C), let

`exposed_capacity_share(t) = sum_i(nameplate_MW_i * 1[ERA5_temp_i(t)>=threshold]) / sum_i(nameplate_MW_i)`.

The indicator specifies **the source-nameplate share whose plant-location reanalysis temperature exceeds a descriptive threshold**. It is not the fraction of operational generating capacity derated or offline. Across complete 744-hour UTC months, count maximal consecutive hourly runs for exposed shares >=50% and >=75%. Every episode's duration is verified to sum to the associated qualifying hour count.

This source-grain indicator is distinct from an event based on the capacity-weighted mean temperature. In particular, plant identity does not imply independent atmospheric samples: several nearby locations share one ERA5 grid cell.

## Verified July gas-source findings

| Individual-site temperature condition | Simultaneous source-nameplate share | Hours in July 2024 | Number of contiguous events | Longest event | Episodes >=6h | Episodes >=24h |
|---|---:|---:|---:|---:|---:|---:|
| At least 35°C | >=50% | **486** | 32 | **20h** | 32 | 0 |
| At least 35°C | >=75% | **441** | 32 | **18h** | 31 | 0 |
| At least 40°C | >=50% | **257** | 32 | **12h** | 27 | 0 |
| At least 40°C | >=75% | **197** | 32 | **10h** | 21 | 0 |

All 12 gas-plant source identities are included, 8,550.1 MW annual nameplate. The total site-level *nameplate exposure* is **4,021,180.2 MW×weather-hours** for >=35°C and **2,002,298.5 MW×weather-hours** for >=40°C, corresponding to 63.2134% and 31.4764% of annual source capacity-hours. The unit MW×weather-hours is **not electricity generated, unserved MWh or lost electrical energy**.

The single eligible coal plant (821.8 MW) has **9** July hours >=35°C in **3** episodes (longest 6h), and **0** hours >=40°C. A single plant is either at 0% or 100% of its source eligible coal nameplate in this indicator, so the >=50% and >=75% categories coincide for coal.

## Scientific limits and next gates

All threshold choices are explicitly descriptive, not inferred generator engineering limits. ERA5 at EIA-860 coordinates is not direct intake-air measurement, cooling-water condition, wet bulb, source-plant dispatch status or observed loss in generator capability. The EIA Plant-BA code is not dispatch-ownership certification. Although atmospheric exposure is reproducible, **equipment-specific temperature-output response and actual outage/EENS calibration remain incomplete**.

The next higher-value analysis is to reconcile these coincident exposure hours to an independent plant- or unit-level operating performance and outage dataset, without assuming generic threshold-to-MW losses. Independent-year and multi-event source validation is required before external climate risk claims.

**Verified:** official source-plant location/weather, hour-by-hour completeness, source-nameplate and simultaneous exposure, event-duration conservation. **Not verified:** thermal derating, forced outage, climate causation or actual historical grid reliability.
