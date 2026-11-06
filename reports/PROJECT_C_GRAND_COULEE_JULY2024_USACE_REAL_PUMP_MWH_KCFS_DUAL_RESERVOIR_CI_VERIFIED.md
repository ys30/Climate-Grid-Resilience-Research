# Project C — Grand Coulee July 2024: source-verified historical Banks Lake pumping electricity and flow, reconciled with both reservoirs

**MAJOR OBSERVATIONAL MILESTONE:** An independent authentic 2024 **USACE Grand Coulee project daily report** with actual Banks Lake pumping electrical MWh, water flow kcfs, Banks Lake elevation and Lake Roosevelt elevation has been recovered, fully audited for **2024 July 1–31** and reconciled with independent USBR and USGS reservoir time series. This is a major empirical upgrade over hypothetical pumping electricity assumptions. It **does NOT identify the six reversible pump-generators' individual 2024 pumping power, storage electrical MWh, actual generation dispatch, efficiency or physical grid adequacy**.

## 1. Original official source

USACE Grand Coulee historic project daily report: [2024 July original report using USACE month-back query](https://public.crohms.org/dd/nwdp/project_daily/webexec/rep?ago=28&r=gcl). Source page visibly identifies **Grand Coulee Dam, July 2024**, with direct columns **Banks Lake Pump MWh**, **Banks Lake Pump kcfs**, **Banks Lake Elev**, and **Midnight Reservoir Elevation**.

- Original July 2024 historical archive probe [GitHub CI 42136906572](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42136906572) **SUCCESS**, [original HTML and checksum artifact 13465577770](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42136906572/artifacts/13465577770). Original HTML SHA256 `2c2f14d3701c9556d05c76557457bf99fdd9a6f6362e23f032316bd4917e01f9`.
- Real exact-date admission, column checks and no-imputation [GitHub CI 42137162460](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137162460) **SUCCESS**, [31-day original reported pumping MWh/kcfs/dual-lake observations artifact 13465373167](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137162460/artifacts/13465373167).
- Three independently retrieved original-source reconciliations [GitHub CI 42137443592](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137443592) **SUCCESS**, [31-date joined USACE, USBR, USGS report CSV and manifest artifact 13465378514](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137443592/artifacts/13465378514).
- Other original sources are [USBR Banks Lake RISE item 129466 July 31 daily](PROJECT_C_BANKS_LAKE_JULY2024_31_DAILY_REAL_RESERVOIR_ELEVATION_CI_VERIFIED.md) [CI 42133017279](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42133017279) and [USGS Lake Roosevelt site 12436000 daily parameter 62614, statistic 32400](PROJECT_C_GRAND_COULEE_JULY2024_BANKS_ROOSEVELT_DUAL_RESERVOIR_REAL_WATER_LEVEL_CI.md) [CI 42135925149](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42135925149). Original Banks and Roosevelt daily source points are **not a physically synchronized head measurement**.

## 2. Actual project pumping in July 2024

| Genuine USACE reporting field / source subset | Verified value |
|---|---:|
| July USACE project daily calendar dates | **31/31** |
| USACE Banks Lake Pump MWh reported dates | **31/31** |
| USACE Banks Lake Pump kcfs reported dates | **31/31** |
| USACE Banks Lake lake elevation reported dates | **31/31** |
| USACE Roosevelt midnight elevation reported dates | **31/31** |
| **July 1–31 Banks Lake project-wide pumping electricity** | **175,641 MWh** |
| **July 1–28 Banks Lake project-wide pumping electricity** (overlaps original PyPSA 672h) | **169,160 MWh** |
| July 29–31 Banks Lake project-wide pumping electricity | **6,481 MWh** |
| Maximum reported single-day project pumping electricity | **10,735 MWh** |
| USACE vs independent USBR Banks Lake same-calendar-date maximum abs elevation discrepancy | **0.00 ft** |
| USACE Roosevelt midnight vs independent USGS 32400 same-calendar-date maximum abs level discrepancy | **0.16 ft** |

The 31-date comparison is complete. USACE and USBR Banks Lake daily elevation values are **identical to reported precision** across all 31 days, supporting source provenance consistency (possibly shared upstream gauge data; this is **not 31 independent measurements of physics**). USACE and USGS Roosevelt lake elevation differ by at most 0.16 ft on a same-date comparison; the records use potentially different sampling conventions, locations and datum transformations. We **do not** silently correct or average them, nor interpret the differences as elevation measurement error or pump head.

## 3. Crucial equipment and water-use reporting scope limitations

The USACE **Banks Lake Pump MWh** field is *reported project-wide pumping electricity use* for the Grand Coulee/Banks Lake pumping installation. It is not specifically identified as the 2024 actual electrical input of EIA860 **Plant 6163 reversible pump-generators PG7–PG12 alone**. Original USBR documentation separately identifies **six dedicated irrigation pumps** and **six reversible pump-generators** at the John W. Keys III plant. Source identity/nameplate [CI 42126016886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886): PG7–PG12 have total **314 MW generating nameplate**, not verified PS-only pumping input MW or hourly firm dispatchable electrical output.

A single USACE **daily** Banks Lake whole-project pumping observation reaches **10,735 MWh**, while the hypothetical 314-MW symmetric-power PS model could consume at most **314×24 = 7,536 MWh per day**. This **does not identify** the real reversible PS pumping MW, but makes it particularly unsafe to equate the entire pumping station demand to a six-unit 314-MW battery-style representation. The source-driven project has substantial irrigation purpose and dedicated equipment outside those six PS generator keys.

USACE **Banks Lake Pump kcfs** reports a flow-rate unit, not a complete volume-delivery integral: unless the daily statistic definition and averaging period are certified, multiplying by 24h/seconds to infer total water volume would be underjustified. More importantly, Banks Lake has irrigation releases, surface water inflows and other operations; even a known total pumped water volume would not directly identify recoverable reservoir electrical storage MWh.

The independently source-audited EIA923 BPAT July Page1 **PS signed net generation +293 MWh** is not equivalent to USACE total Banks Lake project pumping electrical input **175,641 MWh** or discharge. EIA923 source reporting classes, generator identity and BA assignment also differ.

## 4. Scientific consequences for Project C 672h PyPSA and manuscript

**Original 672h source experiment:** The four-BAs isolated incomplete EIA860 gas/wind proxy, representative ERA5 meteorology and official EIA930 July 1–28 demand remain unchanged. Earlier modeled conventional HY was **2,000 MW / assumed 598,947.6 MWh across 28 days**; original PS hypothetical capacity **314 MW generator-nameplate anchor**, assumed **2h/4h** energy duration, **80%/90%** efficiency, 0 initial and terminal SOC, and hypothetical 0%,25%,50%,100% access under irrigation. Source data **do not** justify replacing these assumptions with physical measurements.

**What is newly empirical:** The July 1–28 source calendar now has actual **169,160 MWh reported whole-project Banks Lake pumping use**; original July all month **175,641 MWh**, with actual reported site flow rate and two reservoirs' independently audited elevations. This offers a significantly more concrete physical and service-demand context for the *modeling limitations and future energy balance* than a generic reservoir hypothesis.

**What is not inferred:** The fraction of Banks Lake site pumping attributable to the six reversible units, their actual PS charging schedule and power, hydraulic turbine discharge power, reservoir water operating volume, PS storage MWh, efficiency, head and water rights; annual EIA860 314MW generator nameplate cannot supply these. Modelled shortage reductions in earlier scenario sensitivity are **not observed avoided electricity outages or historic EENS/LOLE**.

**Priority next physical step**: obtain actual **PG7–PG12 unit-level daily/hourly pump-generation operation**, six dedicated irrigation-pump disaggregation, verified pump-flow aggregation/statistic, Banks Lake stage–volume rating and irrigation withdrawal, plus source aligned lower/upper lake level and datum. Then estimate water volume balance and PS-specific available electric power only after full identities and hydraulic head verified. If inaccessible, present a bounded *partial identification* study instead of fabricated calibration. Independent seasons/years plus complete BA generating fleet and intertie validity remain needed for a physical grid-reliability paper.

## Observational figures for Paper C supplement

The archived **actual-source, non-simulated figures** are built from the fully source-audited 31-day USACE/USBR/USGS joined input: [original July historical pumping and dual-reservoir figure CI 42137937886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137937886) **SUCCESS**, [download both high-resolution PNG figures artifact 13465469574](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42137937886/artifacts/13465469574).

- **Fig. Hydro-S1:** observed daily **whole-project** USACE Banks Lake pumping MWh from July 1–31, a dashed mark after July 28 identifying the original PyPSA 672h model calendar cohort. It does not infer PS-generator-specific charging energy or grid shortages.
- **Fig. Hydro-S2:** observed **within-each-reservoir** stage change relative to July 1 at Banks Lake and Lake Roosevelt, **not their absolute-elevation subtraction**. Source clocks, water-surface datum and actual hydraulic energy are not harmonized. The diagram illustrates observed daily variability and does not infer recoverable electric storage MWh.

Reproducible plotting code: [original source-only figures](../src/grid_resilience/grand_coulee_2024_july_observed_hydro_figures.py), [figure build CI](../.github/workflows/grand-coulee-july2024-observed-hydro-figures.yml). Avoid including these charts without their reporting-scope and time-definition captions.

## Code and fully automated source checks

[USACE historical original July access](../src/grid_resilience/grand_coulee_usace_july2024_pump_data_access_probe.py);
[actual USACE 31-day MWh/kcfs/elevation source parser](../src/grid_resilience/usace_grand_coulee_july2024_pump_observation_admit.py);
[USACE/USBR/USGS full July and 28-day original PyPSA cohort reconciliation](../src/grid_resilience/grand_coulee_2024_july_pump_hydro_source_reconciliation.py);
[historical source workflow](../.github/workflows/grand-coulee-usace-july2024-pumping-historical-access.yml);
[source admission workflow](../.github/workflows/usace-grand-coulee-july2024-pump-observation.yml);
[three-source integrity CI](../.github/workflows/grand-coulee-july2024-usace-pump-three-source-reconciliation.yml).

**Observed project-wide Banks Lake pumping electricity complete and cross-source validated. Observed six-unit PS storage energy and actual grid adequacy NOT calibrated.**
