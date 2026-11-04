# SRP Jan 2024: matched multi-technology assumption-only PyPSA factorial

**Verified:** [official-source full-month PyPSA workflow 41756664986](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41756664986) completed **success** with the source changes at commit `dffd8c92078de73d5c45505322da948d6f60fcb4`; [Research Methods CI 41756665009](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41756665009) completed **success**. [Artifact 13288817511](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41756664986/artifacts/13288817511) contains the four scenarios, 744-hour source and scenario outputs, capacity classification, and source SHA-256 manifests.

## Design and source-population gate

Unlike the earlier observed non-gas EIA-930 replay, **this experiment never inputs EIA-930's hourly generation by fuel as an availability curve**. EIA-930 provides January 2024 SRP *demand and net interchange only*. EIA-860 2024 Plant BA `Operable` generators provide annual nameplate; their primary `Energy Source 1` and `Prime Mover` determine a **hypothetical** six-technology inventory.

| Input classification | Verified count / capacity |
|---|---:|
| Annual EIA-860 Plant BA SRP operable generator records | 108 |
| Included in six screened supply technologies | 97 generators / **15,576.5 MW** |
| Explicitly excluded | 11 generators / **1,287.1 MW** |
| Excluded primary source codes | 9 `MWH` (storage), 2 `WAT` (PS rather than HY) |

The six included classes are gas, coal, nuclear, conventional hydro, solar PV and wind. **PS and battery storage are excluded**, not treated as freely dispatchable hydro or negative net generation. A unique EIA-860 plant/generator identity is counted once. The 15,576.5 MW is annual plant-BA assigned nameplate, **not** verified SRP contractual entitlement, transmission deliverability, or January firm capacity.

Synthetic technology availability assumptions, **not meteorological observations or validated weather-response functions**, are: gas 0.85, coal 0.85, nuclear 0.90, hydro 0.50, wind 0.35, and a nonnegative 0–0.80 solar daylight sine curve with an assumed UTC−7 local clock. The thermal derating multiplies gas/coal/nuclear hourly assumed availability by **0.80**; the wind derating multiplies wind by **0.60**. The thermal × wind compound uses both multipliers and holds all other parameters and the 744-hour demand/BA boundary constant. Every source-dependent profile and these assumptions are documented in `assumed_multitech_manifest.json`.

## Optimized four-scenario results (744 hourly PyPSA snapshots)

| Scenario | Assumed thermal multiplier | Assumed wind multiplier | Artificial model gap (MWh) |
|---|---:|---:|---:|
| Baseline | 1.00 | 1.00 | **0.0** |
| Thermal derating only | 0.80 | 1.00 | **0.0** |
| Wind derating only | 1.00 | 0.60 | **0.0** |
| Thermal + wind derating | 0.80 | 0.60 | **0.0** |

Matched factorial contrast `gap_compound - gap_thermal - gap_wind + gap_baseline` = **0.0 MWh**. The zero interaction is a *model outcome of this deliberately mild parameter set*; it does **not** establish no meteorological interaction or no real-world compound risk.

The result is consistent with a broad candidate annual nameplate inventory being able to cover the fixed January boundary under relatively permissive assumptions, especially absent realistic generator-specific hourly outages and physical transmission limits. **It does not validate January 2024 operational reliability**, independently estimate outage probability or imply that climate shocks are harmless.

## Scientific interpretation and next acceptance gate

1. **Structural limitation:** EIA-860 Plant BA assignment is not verified generator ownership, actual SRP dispatch rights or unit-level transfer deliverability. Source-boundary uncertainty is still unresolved.
2. **Weather limitation:** solar shape and other availability factors are synthetic. The model is independent of EIA-930 generation replay but **not weather-driven or weather-calibrated**. Historical ambient temperatures, wind speed, hydrology, forced outage records and demand response must be obtained independently before real climate-attribution claims.
3. **Scenario design:** the zero gaps should be reported, not excluded. A separate predeclared stress-response frontier (e.g. a grid over thermal derating and wind resource loss) could identify when this *hypothetical system* first becomes constrained, without suggesting those thresholds are empirically probable.
4. **Model extension:** include physical interties, feasible storage SOC, fuel constraints and independently validated time-dependent profiles before seeking defensible adequacy risk conclusions.

**Historical calibration certified: FALSE. Observed outages inferred: FALSE. Source-independent technology availability achieved: FALSE (profiles remain synthetic). Independent of historical EIA-930 generation replay: TRUE.**
