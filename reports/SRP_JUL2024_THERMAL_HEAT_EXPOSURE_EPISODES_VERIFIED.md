# SRP 2024-07 continuous hot-weather exposure episodes, fully matched thermal fleet

This is a source-verified *weather exposure* analysis, NOT generator derating or outage duration.

**Verified:** [full-site matched January/July source CI 41775970447](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775970447) successful; [evidence artifact 13296668625](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775970447/artifacts/13296668625) includes 744-hour technical weather summaries, site-level nameplate-exposure, episode start/end, and conservation tests. Input artifacts originate from successful **13-site January** run [41775332025](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775332025) and **13-site July** run [41773763147](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147).

## Episode definition

For **each fuel technology** (gas fleet of 12 plants; coal fleet of 1 plant), define an hourly event as the maximal uninterrupted run of UTC hours with capacity-weighted ERA5 **2m air temperature** at or above the **descriptive** 35°C or 40°C threshold. Enforce complete 744h per calendar month, no imputed hours, no duplicate source hours. Report events separately for January and July; **never concatenate two nonconsecutive months**. Test that every event's duration sums to the total count of qualifying hot hours.

This is deliberately different from site-level exposed source-nameplate MW × hours, where each individual plant crosses the threshold independently. Neither type of weather metric is electric generation nor outage measurement.

## Verified episode structure

| 2024 month | Fuel category | Threshold | Hot fleet-mean hours | Distinct contiguous events | Longest run | Runs ≥6 hours | Runs ≥24 hours |
|---|---|---:|---:|---:|---:|---:|---:|
| January | Gas, 12 plants | 35°C | 0 | 0 | 0 | 0 | 0 |
| January | Gas, 12 plants | 40°C | 0 | 0 | 0 | 0 | 0 |
| January | Coal, 1 plant | 35/40°C | 0 | 0 | 0 | 0 | 0 |
| **July** | **Gas, 12 plants** | **35°C** | **465** | **32** | **18 h** | **31** | **0** |
| **July** | **Gas, 12 plants** | **40°C** | **231** | **32** | **11 h** | **22** | **0** |
| July | Coal, 1 plant | 35°C | 9 | 3 | 6 h | 1 | 0 |
| July | Coal, 1 plant | 40°C | 0 | 0 | 0 | 0 | 0 |

Example of a longest July gas ≥35°C fleet-mean event: **2024-07-12 16:00 UTC through 2024-07-13 09:00 UTC, inclusive, 18 consecutive source hours**. This UTC period may straddle local calendar dates, so avoid misinterpreting a UTC date crossing as two distinct meteorological events. Other 18h runs occurred on July 19–20 and July 23–24 UTC. These are within-source reanalysis weather episodes; they have not been independently checked against real plant operation or station instruments.

## Complementary plant-level exposure

For July gas sites, plant-by-plant thresholding yields **4,021,180.2** source-nameplate MW × weather hours ≥35°C (63.2134% of 8,550.1 MW × 744h), and **2,002,298.5** source-nameplate MW × weather hours ≥40°C (31.4764%). The average-of-plant-temperature event construction is **not interchangeable** with these source-capacity exposure measures; the latter capture variation among ERA5 plant grid cells. Neighboring EIA-860 plants may share a grid cell and therefore have identical ERA5 time series. Do not treat all 12 plant labels as statistically independent meteorological stations.

## Scope and next hypothesis

This analysis is a reproducible foundation for *future* operational heat exposure and climate-grid vulnerability research. **No heat-to-MW derating curve, cooling-system limit, generator unavailable hours, actual EENS, climate-change trend, or causal effect is estimated.** The 35/40°C levels are analyst-specified descriptive cutoffs, not validated generator thresholds. For physical loss estimates, obtain equipment-level thermal response, wet bulb and cooling constraints, local power-generation telemetry, and independent event/year validation first.
