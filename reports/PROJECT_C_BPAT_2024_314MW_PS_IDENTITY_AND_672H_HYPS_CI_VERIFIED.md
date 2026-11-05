# Project C — BPAT 2024 EIA860 pumped-storage identity and 314 MW roster-anchored 672h PyPSA sensitivity

**Original EIA860 source-identity verification:** [GitHub CI 42126016886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886) **SUCCESS**, [official-source plant/generator/energy-storage identity manifest and individual PS records artifact 13461735459](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886/artifacts/13461735459). **Actual 672-hour source-matched PyPSA solver:** [CI 42126570062](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126570062) **SUCCESS**, [16 solved scenarios, hourly SOC/charge/discharge and model scope artifact 13461497205](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126570062/artifacts/13461497205). **Independent original HY-only control replay and factorial decomposition:** [CI 42126890603](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126890603) **SUCCESS**, [64 matched original-model rows and new interaction tables artifact 13461557333](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126890603/artifacts/13461557333).

## Genuine 2024 EIA860 source findings: confirm nameplate but NOT usable energy

The original official 2024 EIA860 Plant, Operable Generator and Operable Energy Storage worksheets were downloaded and the ZIP SHA256 recorded. Using exact **Plant Code + Generator ID** and the official **2024 Plant BA Code**:

| Evidence field | Verified original-source result |
|---|---:|
| BPAT Operable generator records | 394 |
| BPAT physical pumped hydro generators with prime mover code PS | **6** |
| BPAT PS generator records with positive nameplate | **6** |
| Sum of BPAT PS nameplate capacity | **314.0 MW** |
| BPAT original Energy Storage worksheet records, ALL storage technologies | 5 |
| BPAT PS generators matching the Energy Storage worksheet by full generator key | **0** |
| BPAT PS generator records with verified energy MWh AND charge/discharge MW | **0** |

**Essential interpretation:** the **314 MW is genuine EIA860 PS generator nameplate**, *not a directly observed storage charging rate, discharging rate, firm hourly capacity or storage reservoir MWh*. The five 2024 EIA860 Energy Storage worksheet records are **not simply equivalent** to pumped hydro. None matches the six actual BPAT PS prime-mover generator keys. Therefore **no historical BPAT PS device has all MW/MWh/SOC parameters physically calibrated from these data**, and 2-hour/4-hour duration MUST NOT be reported as source-measured. Other storage technologies are not PS by default. Historical initial SOC and roundtrip efficiency are also unobserved.

The previous exploratory 500- and 1,000-MW PS interventions were **larger than the now identified 314 MW official PS nameplate** and must remain visibly labeled **hypothetical resource experiments**, not actual installed PS configurations.

## Original observed source cohort and new scenario construction

Same genuinely source-verified 2024 July 1–28 UTC EIA930 four-BA demand and ERA5 representative-point meteorology, 672 consecutive hourly snapshots, four isolated BA buses, frozen EIA860 *partial* gas+wind system model, unchanged climate stress responses, and fixed previously defined **hypothetical conventional HY resource**: 2,000 MW and one nonreplenishing 598,947.6 MWh 28-day water/energy store. The original EIA923 BPAT July conventional HY monthly net generation **5,989,476 MWh** is *only an energy-scaling reference*, not source-verified real water availability.

Each new incremental PS configuration adopts **314 MW symmetric charge/discharge power as a scenario assumption anchored to the 314 MW PS nameplate**, not an observed PS charge or discharge rating. Assumed energy MWh is nameplate power × chosen duration. Assumed roundtrip efficiencies and durations are deliberately separated from EIA860 source facts. PS has an independent Store with 0 initial and terminal SOC, a charge link, and a separate discharge link, and 672-hour continuity. Hourly charging power, delivered discharging MW, stored energy conservation, SOC bounds, and charge-to-discharge energy losses are checked against the solved PyPSA timeseries.

Four PS assumptions × baseline/heat-only/wind-only/compound climate cases = **16 genuine 672-hour optimized PyPSA scenarios**:

| Source-anchored PS nameplate scenario | Assumed PS energy MWh | Assumed roundtrip efficiency | Four-BA baseline model shortage MWh | Modeled baseline shortage reduction versus no PS MWh | 28-day heat×wind second difference MWh |
|---|---:|---:|---:|---:|---:|
| No PS | 0 | N/A | **1,508,297.367** | 0 | **+53,241.973** |
| 314 MW; 2 hours assumed | 628 | 80% | **1,492,855.502** | **15,441.865** | **+53,582.312** |
| 314 MW; 4 hours assumed | 1,256 | 80% | **1,480,655.730** | **27,641.637** | **+55,385.708** |
| 314 MW; 4 hours assumed | 1,256 | 90% | **1,479,331.696** | **28,965.671** | **+56,151.671** |

The PS intervention's modeled baseline benefit is thus sensitive to assumed energy duration and efficiency, even while holding the generator nameplate anchor fixed. At an assumed four-hour duration, changing roundtrip efficiency 80→90% changes baseline modeled shortage by **1,324.034 MWh**. This is **a source-scaled structural sensitivity**, not an estimate of real BPAT pumped hydro reliability impact or measured avoided outages.

### Independent control replay

The **no-PS** scenario in this new source-anchored study was independently matched to the original conventional-HY-only 672-hour PyPSA result across four BAs × four actual July weeks × four climate cases. [Run 42126890603](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126890603) checked **64 of 64** BA-week-climate observations with **maximum absolute modeled-shortage difference = 0.000000 MWh**. The difference between the no-PS and PS interventions is therefore not caused by a changed source timestamp convention, climate stress cohort, base fleet, or HY reference budget.

## Research interpretation and remaining evidence gates

This materially tightens the previous paper's exploratory PS section: a genuine BPAT 2024 PS nameplate is available, so power-scale scenarios can be tied to **reported installed capacity**, while explicitly acknowledging that **usable storage MWh and input/output PS operating power are not reported for those six exact PS keys**. The difference in the *modeled* heat×wind nonadditivity follows directly from the assumed PS duration and efficiency; it is not a causal physical weather interaction.

**Still incomplete for historical/calibrated reliability research:** BPAT PS generator plant-level reservoir identity, charge/discharge pump ratings, actual water-basin upper/lower storage MWh or hydrologic head/volume, real initial/final SOC, efficiency, real BA net generation classification and interties, full nonstorage thermal/hydro generating fleet and generator availability, historical observed outages/EENS/LOLE. EIA923 BPAT PS net signed production in July **+293 MWh** cannot serve as a gross-output, gross-pumping, or energy-capacity substitute.

**Source and run code:** [EIA860 PS identity and parameter admission](../src/grid_resilience/bpat_2024_eia860_ps_generator_power_energy_admission.py), [source-gated actual PyPSA runner](../src/grid_resilience/bpat_july2024_ps_314mw_source_anchored.py), [672-hour HY+PS optimizer](../src/grid_resilience/bpat_july2024_hy_ps_soc_pypsa.py), [source-verified EIA860 workflow](../.github/workflows/bpat-2024-eia860-ps-source-admission.yml), [314-MW PS PyPSA workflow](../.github/workflows/bpat-july2024-ps-314mw-source-anchored.yml), [independent exact replay](../.github/workflows/bpat-314mw-ps-hy-source-reconciliation.yml).

**Historical EENS/forced outages inferred: NO. Physically calibrated PS MWh and pumping/roundtrip capability: NO. Full-grid generation and transmission capacity calibration: NO.**
