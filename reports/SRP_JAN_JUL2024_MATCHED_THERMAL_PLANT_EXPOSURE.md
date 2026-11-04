# SRP January versus July 2024: matched-plant ERA5 thermal weather comparison

## Audited successful source inputs

- **January 2024:** official EIA860 2024 + ERA5 source-backed workflow [41772449116](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449116), [artifact 13295396867](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449116/artifacts/13295396867). Eight natural-gas sites + one coal site, 6,696 complete plant-hours.
- **July 2024:** official EIA860 2024 + ERA5 source-backed workflow [41773763147](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147), [artifact 13296450727](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147/artifacts/13296450727). Twelve natural-gas sites + one coal site, 9,672 complete plant-hours. July source-nameplate coverage is 100% of the eligible EIA860 Plant BA SRP gas/coal annual roster (8,550.1 MW gas + 821.8 MW coal). July source download followed a retry for an intermittent external SSL handshake timeout; no input-validation bypass was used.

## Match the *same plant identities* before comparing months

January gas sites are plant IDs `8068`, `55455`, `55129`, `56948`, `141`, `55481`, `58557`, `55306`; these are also in July. The matched eight-site gas fleet is **6,638.6 MW**, i.e. **77.6435%** of the annual EIA860 eligible source-nameplate gas denominator. Coal is the same Plant `6177` in each month, **821.8 MW**.

To compute the descriptive weather contrast, retain only identical plant IDs in both month-specific source CSVs, ensure unchanged EIA860 site nameplate for each ID, and aggregate each month's 744 UTC hourly temperatures by (site nameplate × temperature) divided by sum of matched site nameplates. The comparison **does not reuse July's unmatched four gas sites**; it also does not describe all SRP delivered gas generation.

| ERA5 exposure (capacity-weighted across matched sites) | January 2024 | July 2024 | July minus January |
|---|---:|---:|---:|
| Same 8 gas sites, mean 2m temperature °C | **11.902894** | **37.001422** | **+25.098528°C** |
| Same 1 coal site, mean 2m temperature °C | **2.088844** | **26.259409** | **+24.170565°C** |
| Gas matched fleet-mean hours ≥35°C | 0/744 | **461/744** | not a derating count |
| Gas matched fleet-mean hours ≥40°C | 0/744 | **226/744** | not a derating count |
| Coal site hours ≥35°C | 0/744 | **9/744** | not a derating count |

For reference, **July all 12 gas sites** mean is **37.078063°C**, and its 35°C/40°C fleet-temperature exposure hours are **465** and **231**, respectively. Those are not directly comparable to the January *eight-site* mean. The identity-matched comparison above is preferred.

## Interpretational restrictions

- ERA5 is atmospheric reanalysis with EIA860 plant-coordinate proxies, not unit intake temperature, measured cooling-water conditions, humidity/wet bulb, turbine capacity factor, or generator-specific efficiency.
- The monthly weather contrast is a **descriptive same-site seasonal exposure difference**, not observed performance, MW derating, actual blackout, climate-change trend or a causal effect.
- This study still has no independent generator-level summer heat-response calibration, verified 2024 BA dispatch ownership, physical transfer ratings, storage operation, or actual event-level energy-not-served measurements.
- Rigorous next gate: obtain unit/cooling-system constraints or independent weather-varying realized generator availability; implement alternative sensitivity curves only when marked as *hypothetical*; repeat across additional extreme events/independent years for external validity.

**Full-fleet July weather source coverage verified; identical-site Jan–Jul descriptive comparison verified. Actual generator heat derating and reliability calibration NOT verified.**
