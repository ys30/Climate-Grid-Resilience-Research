# SRP Project C: 2024 EPA hourly source operating indicators and unit-to-generator admission

**Research status:** a reproducible **2024 archived EPA source-unit operational indicator dataset is now verified**, but genuine EIA generator-level **net** electrical MW, observed thermal derating and actual generator outage/EENS remain unverified.

## Provenance / immutable CI

- **2024 full Arizona hourly source**: publicly preserved [EDGI / Zenodo EPA CAMPD 2024 Arizona snapshot](https://zenodo.org/records/15059567), CSV 183,084,007 bytes. Published and observed **MD5 7123a5070f652890f46e819dcc890ec0**. The original archived file is not retained in the repository or exported in CI artifacts.
- [EPA hourly source/operation CI **41888598785**](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41888598785) **SUCCESS**, source unit and operating indicator artifact [13352108635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41888598785/artifacts/13352108635).
- [EPA unit to pinned crosswalk bridge CI **41889477040**](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41889477040) **SUCCESS**, associated [Research Methods CI **41889476369**](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41889476369) **SUCCESS**, match artifact [13353570245](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41889477040/artifacts/13353570245).
- Static [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk) snapshot pinned at **3c7d6724cddee38dfb6a06debca732c33a227ed6**, crosswalk original rows from independently verified run 41876110511. This static matching dataset should not be misrepresented as a verified 2024 ECMPS monitoring-plan association.

## Unit-level 2024 actual source reporting

Each observed EPA unit has precisely 8,784 *calendar-hour rows* (2024 leap year) with unique source facility/unit/date/hour. Operating Time, positive Gross Load and Heat Input are distinguished from calendar-hour row presence; the saved positive operating-time count is not the same measure as the sum of fractional operating hours.

| Plant / EPA Unit ID | Calendar rows | Operating Time > 0 rows | Reported Operating Time sum (hours) | Gross Load > 0 rows | Gross Load maximum, MW |
|---|---:|---:|---:|---:|---:|
| 141 / 1 | 8,784 | **797** | **750.56** | 658 | 109 |
| 141 / 2 | 8,784 | **1,030** | **952.65** | 830 | 110 |
| 141 / 3 | 8,784 | **1,058** | **978.10** | 883 | 179 |
| 141 / 7 | 8,784 | **386** | **286.30** | 372 | 48 |
| 141 / 8 | 8,784 | **493** | **367.95** | 475 | 49 |
| 55129 / DBG1 | 8,784 | **5,655** | **5,559.91** | 5,640 | 312 |
| 55129 / DBG2 | 8,784 | **5,458** | **5,369.55** | 5,441 | 312 |
| 55129 / DBG4 | 8,784 | **349** | **243.72** | 335 | 49 |
| 55129 / DBG5 | 8,784 | **183** | **119.22** | 166 | 48 |
| 147 / K-7 | 8,784 | **5,267** | **5,139.54** | 5,240 | 250 |

These are **reported EPA combustion-unit source metrics**, not confirmed 2024 net EIA generator power, turbine derating events, dispatch statuses, or forced outages. Gross Load is a source-reported *gross* electrical measure and is **not interchangeable** with EIA net MW; source-hour timezone interpretation was **subsequently verified** for the July 2024 EPA–ERA5 analysis: Part75 local standard time (Arizona MST, UTC−07:00). See [verified full local-July alignment](SRP_EPA_ERA5_AUGUST_BOUNDARY_744H_ADMISSION_GATE.md). Some gross-load cells are unreported even though an operating-time cell equals 0; these values must not be zero-filled. A reported zero operating time does not establish a forced outage.

## Independently audited static crosswalk on the actual 10 EPA Unit IDs

| Source EPA facility | EPA units in 2024 archive | Unit IDs appearing in pinned static crosswalk | Units without static crosswalk | Linked EIA source generator(s) |
|---|---:|---|---|---|
| **141** | 5 | **1, 2, 3** | **7, 8** | 1→AF1(ST), 2→AF2(ST), 3→AF3(ST) |
| **55129** | 4 | **DBG1, DBG2** | **DBG4, DBG5** | DBG1→CTG1(CT) and STG(CA); DBG2→CTG2(CT) and STG(CA) |
| **147** | 1 | **K-7** | none | K-7→KY7(CT) and KY7A(CA) |
| **TOTAL** | **10** | **6** | **4** | **0 direct matches to the ten target EIA860 GT generators** |

Static crosswalk mappings may be one-to-many. For example, the same EPA Unit K-7 maps to *two* EIA generator IDs at Plant 147, so allocating its full gross load to both would double count. The exact source crosswalk match is an identity association, **not proof of a unique physical generating path, generator-level electricity, or contemporaneous 2024 monitoring configuration**.

The *unmapped* 2024 EPA units (141/7, 141/8, 55129/DBG4, 55129/DBG5) are especially interesting for targeted ECMPS source investigation. But even where EPA and EIA IDs look similar (such as DBG4 versus CTG4 or Plant 141 EPA 7 versus AF7), **do not make that mapping without official association or engineering documentation**.

## Scientific inference guardrails and next gates

1. EPA source Operating Time > 0 indicates a *reported operating indicator*, not continuously operable available power. Positive Gross Load reported hours describe the EPA source-unit data; do not equate them to positive EIA net electric generation.
2. **Subsequent milestone completed:** EPA Part75 local-standard to UTC conversion and full July 744-hour ERA5 weather matching are now CI verified for all ten source units (run 41961038085). This does not resolve generator mapping or identify actual heat derating.
3. Obtain explicit 2024 ECMPS monitoring plan unit/stack associations or independent EIA boiler–generator/source mapping, especially 141 units 7/8 and 55129 DBG4/DBG5, before attributing their operation to specific gas turbines.
4. Even if gross-load and ambient air temperature are paired, observed output depends on dispatch, commitment, demand, maintenance and fuel, so *output–temperature correlation* alone does not identify derating of physically available capacity. Need OEM thermal performance, availability/outage and dispatched/not-dispatched distinctions, plus independent year holdouts.

**Acceptance:** 2024 EPA facility/unit hour and source Operating Time/Gross Load metrics are reproducible; crosswalk exact source associations for 6 EPA units have been enumerated and one-to-many mappings preserved. **Not accepted:** direct 2024 GT electrical net-MW calibration, climate-attributed production losses or empirical EENS.
