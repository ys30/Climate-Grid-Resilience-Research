# Project C — July 2024 measured upper and lower reservoir water elevations: Banks Lake, Lake Roosevelt and Grand Coulee forebay

**Scientific status:** BOTH real water-reservoir time series now obtained and source-audited at daily calendar frequency. This is an **observed dual-reservoir elevation comparison**, NOT a validated effective pump head, pump energy, reservoir water balance, storage electrical MWh, PS dispatch, climate-induced shortage or EENS.

## 1. Independently archived original source material

- **Upper reservoir:** [USBR RISE Banks Lake / Dry Falls Dam item 129466](https://data.usbr.gov/catalog/8176/item/129466), daily *instant* reservoir elevation in **feet**. [Original raw + SHA256 download CI 42132553683](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42132553683) **SUCCESS**; [31/31 original July daily observations CI 42133017279](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42133017279) **SUCCESS**, [validated Banks artifact 13463932681](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42133017279/artifacts/13463932681). USBR original raw checksum `fd58a5e3e03e91d0fb9a4b77b34c3fbeb292f7288c892b5dc47f67b1354c437d`.
- **Lower reservoir:** [USGS station 12436000 — Franklin Roosevelt Lake at Grand Coulee Dam](https://waterdata.usgs.gov/monitoring-location/USGS-12436000/), original daily-values RDB parameter **62614**, observation-statistic code **32400**. IMPORTANT: `32400` means **observation at 2400**, **not daily mean (`00003`)**. Reported water-level unit is **feet above NGVD29**. [Source RDB and SHA256 CI 42135379269](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42135379269) **SUCCESS**, [real 31/31 July USGS admission CI 42135925149](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42135925149) **SUCCESS**, [USGS 31-row measured water elevations and scope artifact 13466071040](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42135925149/artifacts/13466071040). Original RDB SHA256 `1b839c0bf030b3f7afcb406c2471e550b1e6ef97e914a4da82749cde67ea754d`.
- **Independent lower-site monthly check:** [USBR RISE Grand Coulee Power Plant item 5253](https://data.usbr.gov/catalog/4194/item/5253), 2024 July month-end **forebay elevation**, ft, official RISE timestamps placed on July 1 (first of nominal month represents **end** of that month). Two same-month original source rows have an identical month-end value and are deduplicated, not counted as two monthly observations. Source original SHA256 `18ed577bec659b472516720c24a0ca39affac1f7c11c71f8c86f52ae449b842c`. Measured site-month-end forebay should **not** be equated to the USGS July 31 observation at 2400 without exact time/datum harmonization.
- **Upper power-station monthly check:** [USBR RISE Grand Coulee Pump Generating Plant item 5226](https://data.usbr.gov/catalog/4187/item/5226), upper pond July month-end **1,568.25 ft** (one independent month-end observation represented in two identical raw source rows). Its source and interpretation were already audited in the Banks Lake CI.

## 2. Verified July 2024 original measurements

| July 2024 | Banks Lake upper (daily instant, ft) | Lake Roosevelt lower (USGS observation at 2400, ft NGVD29) |
|---|---:|---:|
| Actual observed dates complete | **31/31** | **31/31** |
| Minimum measured daily value | **1,567.95** | **1,285.24** |
| Maximum measured daily value | **1,569.62** | **1,288.91** |
| July 1 | **1,568.90** | **1,285.94** |
| July 31 | **1,568.25** | **1,286.29** |
| July 31 less July 1 value, within same site | **−0.65 ft** | **+0.35 ft** |

Independent USBR Grand Coulee **lower forebay month-end** reported **1,286.24 ft**. Note that the USGS and USBR end-month numbers are not numerically identical; differences in observation timing/datum/physical station must be independently resolved. We do not apply an invented adjustment.

**Exact source-independent paired-day CI:** [42136302520](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42136302520) **SUCCESS**; [31-date panel and strict evidence JSON artifact 13466046484](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42136302520/artifacts/13466046484). All **31 calendar dates** have both sites' actual measured elevations. **28 dates** match the original continuous July 1–28 PyPSA scenario period; **July 29–31** are additional independently observed dates and were **not** modeled as part of the existing 672h weather/dispatch experiment.

Within-site changes from July 1 are reported to avoid illegitimate cross-site datum subtraction. This panel is **date-joined** for descriptive context, not **instantaneously synchronized**: Banks daily observation records have 19:00 UTC times in the archived RISE source, while USGS 32400 describes the day's midnight observation. Site vertical datums are not independently confirmed mutually equivalent. In particular the arithmetic upper-minus-lower lake-level difference has **not been computed nor certified as plant hydraulic net head**.

## 3. Why this improves scientific validity without yet calibrating storage

The independent [2024 EIA860 six PS generator identity / 314MW nameplate audit 42126016886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886) and [USBR Grand Coulee multiuse irrigation role / unit identity 42129966383](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42129966383) establish the **John W. Keys III reversible pump-generators** PG7–PG12 and irrigated Banks Lake connection.

However the records do NOT identify:
- Harmonized physical head at each pump/generator at aligned time (needs source vertical datum, inlet/outlet water level, loss and head estimates);
- Banks Lake volume change (needs its actual **stage-to-storage rating**, not just a measured elevation);
- Water exchanged by the PS units (needs direct pump/turbine flows and irrigation diversion, other inputs/outputs, reservoir operation records);
- Effective discharge MW, pumping MW, hydraulic efficiency/roundtrip, total usable electrical reservoir energy MWh or hourly actual SOC;
- Historical observed outages or system EENS/LOLE; existing 4-BA PyPSA generating fleet and network remain incomplete.

Therefore all previous model sensitivity scenarios using assumed 314 MW symmetric electrical charge/discharge, **2h/4h** duration, **80%/90%** efficiency, **0/25/50/100%** hypothetical dispatch access remain explicitly **uncalibrated counterfactuals**. Even the 314 MW represents official EIA860 **PS generating nameplate**, not verified pumping input rating or hourly firm available PS MW.

## 4. Research manuscript and future workflow

For the private Paper C manuscript, describe this as **Source provenance and hydrologic feasibility limitations**, with measured Banks and Roosevelt elevation ranges and original-source identities in supplementary diagnostics. Do **NOT** replace the heat×wind PyPSA simulation plot with a putative physical reliability effect.

Recommended next source gate: obtain 2024 Banks Lake water-surface elevation **storage-volume relation** (rating curve with its reference vertical datum), Banks Lake pumping/inflow/outflow and irrigation deliveries; reconcile day-specific records from USBR/USACE operations with actual PG7–PG12 pump/generation logs. Source [USACE Grand Coulee project daily reporting](https://public.crohms.org/dd/nwdp/project_daily/webexec/rep?r=gcl) lists **Banks Lake Pump kcfs** and **Banks Lake Pump MWh** together with reservoir elevations, making its **July 2024 historical retrieval and unit/reporting-scope certification** the next high-value verification step. Even these are project-wide pump duties and not automatically the reversible six-unit PS-only electricity consumption.

**Code:** [USGS/USBR raw-source archive](../src/grid_resilience/grand_coulee_roosevelt_july2024_source_intake.py), [USGS 32400 and USBR monthly observed source admission](../src/grid_resilience/grand_coulee_roosevelt_july2024_admit.py), [31-day dual-reservoir observational panel](../src/grid_resilience/grand_coulee_july2024_dual_reservoir_stage_panel.py), [source CI workflow](../.github/workflows/lake-roosevelt-usgs-july2024-source.yml), [31-day admission CI workflow](../.github/workflows/lake-roosevelt-usgs-july2024-admission.yml), [paired stage CI](../.github/workflows/grand-coulee-july2024-dual-reservoir-stages.yml).

**Status: upper+lower reservoir elevation cohorts certified; hydraulic head/PS energy/water balance and historical adequacy not certified.**
