# Project C — First original-source verified 2024 July Banks Lake reservoir elevations and John W. Keys III pump station month-end upper-pond elevation

**Scientific advance:** a genuinely measured 2024 historical water-level cohort has now been recovered and audited, distinct from EIA860 installed PS generator nameplate and EIA923 signed monthly net generation. It does **not** imply that the physical pumped-storage usable MWh or irrigation/pumping duty has been calibrated.

## Authoritative original data and source reproducibility

**Original raw USBR Reclamation Information Sharing Environment (RISE) source fetch:** [CI 42132553683](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42132553683) **SUCCESS**, [two original official CSVs and SHA256 archive artifact 13464595826](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42132553683/artifacts/13464595826).

Original source items:
- **RISE item 129466**, [Banks Lake and Dry Falls Dam (BNK) Daily Instant Lake/Reservoir Elevation](https://data.usbr.gov/catalog/8176/item/129466) with official [Data.gov dataset listing](https://catalog.data.gov/dataset/banks-lake-and-dry-falls-dam-bnk-daily-instant-lake-reservoir-elevation-time-series-data). Official machine-readable source: `https://data.usbr.gov/rise/api/result/download?after=2024-06-28&before=2024-08-04&itemId=129466&type=csv&order=ASC`. Original SHA256 `fd58a5e3e03e91d0fb9a4b77b34c3fbeb292f7288c892b5dc47f67b1354c437d`.
- **RISE item 5226**, [Grand Coulee Pump Generating Plant Monthly Upper Pond Elevation](https://data.usbr.gov/catalog/4187/item/5226), [Data.gov original source dataset](https://catalog.data.gov/dataset/grand-coulee-pump-generating-plant-monthly-upper-pond-elevation-ft-timeseries-data). Official original CSV source: `https://data.usbr.gov/rise/api/result/download?after=2024-06-28&before=2024-08-04&itemId=5226&type=csv&order=ASC`. Original SHA256 `e186f3c1662bdcf9029ce18820852f8253ea90a24715ad97bda84fc5359e83db`.

**Data ingestion unit and time-basis contract:** RISE original CSV contains comment/metadata rows and a real `#SERIES DATA#` section, where the columns are Location, Parameter, Result, Units, Timestep, Aggregation, and **Datetime (UTC)**. Only actual data lines are admitted. Daily values have unit **feet**, frequency `daily` and aggregation `instant`; monthly readings are separately classified as `monthly` / `instant`. The monthly item metadata explicitly states that a timestamp on the **first day of a month represents the END-OF-MONTH instant for that named month**—not a daily 1st-of-month elevation. The original July monthly item has **two timestamped raw source rows** with the **same 1568.25-ft value**; these are treated as one unique July month-end measurement, not two independent monthly data points. Conflict among duplicate monthly values fails source admission.

**Original source admission CI:** [42133017279](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42133017279) **SUCCESS**, [actual 31-row admitted July daily CSV, one-row monthly upper-pond CSV, evidence manifest artifact 13463932681](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42133017279/artifacts/13463932681). Fails closed on missing days, wrong physical units, wrong observed frequency, mislabeled source metadata and contradictory month-end duplicates. It does **not** interpolate a missing day or create an assumed hourly hydro dispatch schedule.

## 2024 July Banks Lake observed daily elevations

| Original-source physical indicator | Verified observed value |
|---|---:|
| Original 2024 July daily Banks Lake RISE records | **31/31 calendar dates** |
| July minimum observed daily instant elevation | **1,567.95 ft** |
| July maximum observed daily instant elevation | **1,569.62 ft** |
| Observed July 1 daily instant elevation | **1,568.90 ft** |
| Observed July 31 daily instant elevation | **1,568.25 ft** |
| July 31 minus July 1 daily instant elevation | **−0.65 ft** |
| Grand Coulee pump generating plant July month-end reported upper pond elevation | **1,568.25 ft** (one unique monthly value; two identical source timestamps) |

**Important:** the 31 daily values represent **one instantaneous observation per day**, not the full intra-day min/max hydrograph. Accordingly the maximum minus minimum above is a **range of observed daily-instant elevations**, not necessarily July's absolute subdaily range. The daily lake and plant-level monthly upper-pond datasets are separately labeled and should not be treated as two independent hourly hydro head readings; equal recorded July 31 monthly values do not establish identical precise instrument positions, water head differences, reservoir geometry or usable pump-generator energy capacity.

## Connection to earlier 314MW Grand Coulee PS source and original PyPSA

The independent original 2024 EIA860 plant/generator source [CI 42126016886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886) verifies six 2024 BPAT PS prime-mover generators, Grand Coulee Plant **6163** PG7–PG12, sum positive 2024 nameplate **314 MW**; the independent USBR plant-site source crosswalk [CI 42129966383](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42129966383) verifies the **John W. Keys III Pump-Generating Plant** and irrigation supply responsibilities with Banks Lake as multiuse upper reservoir.

The original [672h source-anchored July PS dispatch sensitivity 42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635) tested **assumed** constant 0%, 25%, 50%, 100% PS grid-access fractions, 4h usable energy duration, 80% roundtrip efficiency, zero initial/final SOC and the **incomplete** 2024 gas/wind partial fleet, with [128/128 original control replay 42130613044](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130613044) verifying source agreement. **These scenario assumptions have not been calibrated or updated by the new water-level observations.**

The actual July reservoir levels are a new observational constraint and scientific context but are insufficient to directly infer:
- Electric hydraulic head across the pumps (requires compatible **Lake Roosevelt lower reservoir** level with aligned time and actual pump elevation/head losses);
- Water volume changes or net pumping discharge (requires Banks Lake **stage–storage curve**, irrigation withdrawals, inflows, canal leakage and return flows);
- Recoverable PS usable electric energy MWh, actual PS pump/generator electrical input/output or roundtrip losses (requires 2024 hourly plant operating measurements, efficiency and scheduled flow);
- 2024 daily fraction of the 314MW reversible generating nameplate usable for grid arbitrage, or whether electrical power was curtailed by irrigation;
- Historical power outages, real EENS/LOLE, full-grid energy adequacy or plant-specific resilience.

Thus **NO conversion from observed feet to electrical MWh is permitted in the physically-calibrated research output** at this stage. Do not label the previous assumed 2h/4h duration, constant 25%/50% fraction or 80%/90% efficiency as measured USBR water-service constraints.

## Next meaningful physical validation step

**Acquire an independently time-matched 2024 July Lake Roosevelt / Grand Coulee forebay daily reservoir elevation** from the official Pacific Northwest Hydromet GCL station, then compute *water-level difference as a proxy only after validating datum, physical pumping inlet and timestamp alignment*. Still require actual hydraulics, stage–volume relationship, irrigation diversions and reversible-generator operations before inferring electric stored energy. Favor a **daily water-level / 672h model feasibility overlay**, not a supposedly calibrated hourly hydro output. Archive original raw lower-reservoir data with checksum and separately document any data coverage gaps.

**Code and CI:** [RISE original downloader and source checksum](../src/grid_resilience/usbr_rise_banks_lake_july2024_discovery.py), [source parser/admission](../src/grid_resilience/usbr_rise_banks_lake_july2024_admit.py), [daily source unit tests](../tests/test_usbr_rise_banks_lake_july2024_admit.py), [original-source workflow](../.github/workflows/usbr-rise-banks-lake-2024-original-source.yml), [July observed hydro workflow](../.github/workflows/usbr-rise-banks-2024-july-daily-admission.yml).

**Model status: source-exact 2024 July Banks Lake elevations verified; 2024 lower reservoir/head/irrigation and hourly PS SOC still NOT validated.**
