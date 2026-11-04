# 2024 Arizona EPA CAMPD hourly source: 3 SRP thermal plant IDs verified

## Successful, independently checksummed public historical snapshot

[GitHub Actions run 41887521083](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41887521083) **SUCCESS**; [Research Methods CI 41887521217](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41887521217) **SUCCESS**. [Artifact 13351063803](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41887521083/artifacts/13351063803) contains individually verified EPA unit IDs, source hourly row coverage and a machine-readable admission manifest. The source archive is the [EDGI Zenodo record 15059567, 2024 Arizona hourly CAMPD preservation snapshot](https://zenodo.org/records/15059567) and was downloaded with **MD5 7123a5070f652890f46e819dcc890ec0**, exactly matching the published checksum; received file size **183,084,007 bytes**.

Initial run [41878365283](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41878365283) failed **only on CSV schema assumptions** (real source uses `Facility ID`, `Unit ID`, `Date`, `Hour`, `Operating Time`, `Gross Load (MW)`, `Heat Input (mmBtu)`, rather than a `year` column). A corrected source-identity and calendar hour parser passed all tests, source MD5, 2024 date validation, range 0–23 and uniqueness of each normalized EPA facility/unit/date/hour row.

## Actual source-unit-level evidence

| EIA/ORIS plant ID | Distinct *EPA source-unit IDs* | 2024 archived source rows |
|---|---|---:|
| **141** | **1, 2, 3, 7, 8** | **43,920** |
| **55129** | **DBG1, DBG2, DBG4, DBG5** | **35,136** |
| **147** | **K-7** | **8,784** |
| **TOTAL** | **10 distinct EPA source units** | **87,840** |

2024 is a leap year: 366 × 24 = **8,784 calendar hours**. The count is exactly 8,784 rows per identified source EPA Unit ID. This confirms the **archive's row structure** for each EPA source unit, **not** 8,784 hours actually operated, generated, emitted, or had positive gross load. The source Date/Hour timezone has **not been established**; blindly merging Date/Hour to ERA5 UTC hours is prohibited until checked.

The EPA source IDs are not EIA-860 generator IDs. For example, the EIA-860 Operable EIA GT candidates at these sites are:
- Plant **141**: `AF4, AF5, AF6, AF7, AF8` (5 GT, 321.9 MW source nameplate).
- Plant **55129**: `CTG4, CTG5` (2 GT, 99.0 MW).
- Plant **147**: `KY4, KY5, KY6` (3 GT, 173.7 MW).

There is **no verified one-to-one crosswalk** between these 10 annual EIA GT generators and the 10 *separately identified* EPA source combustion units. Prior pinned public [EPA-EIA crosswalk audit](SRP_GT_EPA_CAMD_EIA_CROSSWALK_DATA_ADMISSION_VERIFIED.md) identified plant-level crosswalk rows at all three sites, but **0 of 10** target annual EIA GT generator identities had a direct EPA Unit ID crosswalk match. Similarities among naming patterns are not sufficient evidence of physical identity.

## Current admissibility and next quantitative analysis

The source **contains** Operating Time, Gross Load (MW), Heat Input (mmBtu) and emissions fields. However, the first certified CI analyzed **only source unit identity and source-calendar-hour row completeness**, not the numerical values of operating time or gross load. A follow-on implementation [source module](../src/grid_resilience/srp_epa_2024_az_hourly_admission.py) is separately testing per-unit positive and zero operating time, reported/positive gross load, explicit missing data and conservation against the source-identity row count. **Do not report actual operating hours or gross load statistics until its CI succeeds.**

These hours represent **EPA source observations** and not independently validated generator-hour dispatch, EIA net MWh, actual outages or heat-related generator derating. EPA source gross load must be distinguished from EIA net electrical generation and, if apportioned or common-stack, reconciled to a validated physical unit. Missing observations or reported zeros do not automatically establish failed equipment.

**Confirmed:** official-source-preservation checksum, facility and EPA Unit ID, 2024 hourly row presence and uniqueness. **Outstanding:** temporal timezone source documentation; actual positive operating time, specific gross-load measurement interpretation, ECMPS monitoring plans, EPA-to-EIA unit-gen association, independently validated electrical net MW and physically calibrated heat derating.
