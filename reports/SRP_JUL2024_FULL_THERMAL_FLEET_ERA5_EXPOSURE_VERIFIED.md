# SRP July 2024: complete annual Plant-BA gas/coal site ERA5 temperature exposure

**Successful official source-backed workflow:** [41773763147](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147), code commit `f66bf99529ae66b4dcb8b7d322b1e72b5390792a`. [Artifact 13296450727](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147/artifacts/13296450727) preserves EIA860 archive SHA256, complete annual BA/thermal site selection and coverage denominator, each ERA5 request URL and response SHA256, original plant-hour data, and technology-hour aggregates. The previous [initial run 41773434995](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773434995) failed because of an external SSL handshake timeout; a limited transient-network retry was added and tested, with strict schema and time validation preserved. [Methods CI 41773435006](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773435006) passed before the network-retry change.

## Source population and complete geolocation coverage

This experiment uses EIA-860 2024 operable generator rows whose **Plant-reported BA code is SRP**, assigned **exactly once** to gas (primary fuel NG; matching prime mover) or coal (primary fuel SUB; ST). EIA-860 annual nameplate is not validated SRP dispatch ownership, hourly operational capability, or transmission deliverability.

| Population measure | Natural gas | Coal |
|---|---:|---:|
| Eligible EIA860 generator identities | 64 | 2 |
| Eligible plant identities | **12** | **1** |
| Annual nameplate MW | **8,550.1** | **821.8** |
| Plants with valid official EIA860 coordinates | **12** | **1** |
| Plants selected for ERA5 retrieval | **12** | **1** |
| Share of this *eligible source nameplate* selected | **100%** | **100%** |

All **13** site-month queries returned the full **744 UTC hours** for July 2024. Total original weather observations = **9,672 plant-hours**. There were no incomplete hours, null temperature, duplicated plant-hour identities, invalid degree-Celsius units, or bad source-plant nameplate weights in the accepted run. The Open-Meteo archive query specifies `models=era5`, `timezone=GMT`, and `temperature_2m`. Every request and response hash is recorded in the delivered source manifest. Coordinates represent power-plant site entries, not cooling intake locations or turbine positions. Returned ERA5 grid cells can differ from the requested coordinates.

## Source-derived July 2024 exposure, not thermal derating

Weather exposure is first sampled at each source plant, then nameplate-weighted within the eligible gas/coal fleet. The reported hourly descriptive statistics below apply to the **744 capacity-weighted fleet temperatures** for each category, rather than to 9,672 individual observations pooled without weights.

| Metric | 12 gas sites, 8,550.1 MW | 1 coal site, 821.8 MW |
|---|---:|---:|
| Mean temperature (°C) | **37.078063** | **26.259409** |
| Median temperature (°C) | **37.101228** | **26.100000** |
| Min hourly weighted temperature (°C) | **28.276861** | **15.400000** |
| Max hourly weighted temperature (°C) | **46.370938** | **36.200000** |
| Hours weighted temperature ≥35°C | **465 / 744** | **9 / 744** |
| Hours weighted temperature ≥40°C | **231 / 744** | **0 / 744** |

The gas fleet weighted-temperature series exceeded 40°C in 231 hours. This is a **fleet mean exposure threshold**, not the number of hours each gas generator independently experienced >40°C and **not** a count of unavailable or derated generator hours.

## Comparability to January and science gate

January's prior thermal weather sample contained eight gas plants and one coal plant, corresponding to 77.64% of eligible annual gas nameplate and 100% of eligible coal capacity. **Do not naively subtract the January eight-plant mean from the July twelve-plant mean and call it a matched seasonal climate effect.** The sample composition differs. A future month-matched comparison must sample exactly the same 13 sites for January and July, or restrict both datasets to the same eight gas sites with explicit normalization.

The July mean contrast between categories reflects location and source population differences, not a causal effect of fuel technology. This is atmospheric exposure only. No validated ambient-temperature-to-MW derating coefficients, cooling-system constraints, forced-outage evidence, generator dispatch ownership, fuel availability or BA transmission ratings were used.

**Next research acceptance gate:** produce a same-plant January/July comparison (preferred: download January for all 13 plants) and independent generator equipment / operational heat-response evidence before climate-induced capacity loss or reliability attribution.

**Independent ERA5 summer weather coverage for eligible SRP annual Plant-BA gas/coal sites: VERIFIED. Weather-derived generator derating: NOT CALIBRATED. Actual unserved energy or climate-induced outage: NOT ESTIMATED.**
