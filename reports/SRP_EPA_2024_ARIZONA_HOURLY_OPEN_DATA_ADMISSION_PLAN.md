# SRP 2024 EPA hourly emissions: independent public Arizona source-admission experiment

## Why this experiment exists

A source-backed [EPA facility API probe](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41875589498) received HTTP 403 for three ORIS codes (141, 55129, 147). The EPA [ECMPS public portal](https://easey.epa.gov/ecmps) nevertheless states that public facility monitoring plans, emissions and QA submissions can be viewed without login; EPA's [CAMPD bulk files](https://campd.epa.gov/data/bulk-data-files) and [Power Sector Data guide](https://www.epa.gov/power-sector/power-sector-data) provide independent public access paths. The production API 403 therefore does **not** demonstrate an absence of CEMS monitoring or operating observations.

## Independently preserved 2024 hourly dataset

The Environmental Data & Governance Initiative (EDGI) archived EPA CAMPD **2024 hourly emissions by state**, [Zenodo record 15059567, March 2025](https://zenodo.org/records/15059567). This is a **third-party preservation snapshot of EPA source data**, not a direct 2024 ECMPS monitoring-plan submission nor an EPA guarantee of identity mapping. Arizona file: `emissions-hourly-2024-az.csv`, approximately 183.1 MB, published MD5 **7123a5070f652890f46e819dcc890ec0**.

The [source-admission implementation](../src/grid_resilience/srp_epa_2024_az_hourly_admission.py) and [versioned CI workflow](../.github/workflows/srp-2024-epa-arizona-hourly-public-admission.yml) attempt to retrieve that exact public archive, verify **byte-level MD5 before parsing**, require unambiguous facility/unit/year source columns, fail closed if target rows are not in **2024**, process the file in chunks, and retain *only* per-facility EPA unit IDs and reporting-row counts. Original full-state 183 MB data are not added to the GitHub repository or attached as CI artifacts.

Target facility IDs: **141, 55129, 147**. Prior 2024 EIA860 candidates: 10 GT generators, but **none** has a direct validated mapping to a CAMD Unit ID in the pinned EPA–EIA public crosswalk. Any EPA facility/unit ID observed in the independent 2024 archive remains an **EPA source reporting identity**, not automatically an EIA860 GT generator.

## Strict scientific admission criteria

| Evidence level | Requirements | Interpretation permitted |
|---|---|---|
| 2024 emissions source observed | Correct checksum, facility ID, unit ID, and calendar-year field | Evidence that the source archive contains rows attributed to an EPA unit |
| Time-series coverage | Verified hourly timestamp, timezone, duplicate key, contiguous-coverage definitions and missing/zero distinctions | Descriptive hourly reporting coverage, **not necessarily all operating hours** |
| Actual monitored operations | ECMPS monitoring plan and method evidence, matching unit/stack topology and operating-time semantics | Selected unit operational or emissions indicators only |
| Real electrical performance | Independently validated 2024 source gross-load and net-load basis; EIA generator-to-CAMD unit link; plant operating/dispatch context | Candidate temperature/performance study, not automatically causal |
| High-heat physical derating | OEM curve or measured available-MW/dispatch-restricted operating observations, wet-bulb/ambient thermodynamic basis, matched hourly weather, independent controls and validation | Only after all gates pass may MW response be calibrated |

**Critical caveat:** CAMD hourly reported or apportioned emissions and heat input are not EIA923 generator net MWh. EPA gross load may be plant/unit gross electrical generation, not net, and certain complex unit configurations can be apportioned. Missing EPA source rows are not verified unit downtime, outages or zero electric output.

## Current status and next analysis

The code and regression tests have been committed. The [official-source archive retrieval and intake run](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/workflows/srp-2024-epa-arizona-hourly-public-admission.yml) is the mandatory success gate for any claims that 2024 hourly source records were actually downloaded. **Until that workflow is successful with output artifacts, treat 2024 EPA source unit coverage as unverified.**

Once admitted, compare actual EPA Unit IDs from the 2024 source with the preserved 9 pinned crosswalk plant-level rows; separately inspect monitoring plan relationships to EIA generator IDs. Do not infer electrical net MW or thermal derating from the source-row counts or descriptive gross-load fields.

**At this stage: weather exposure verified, 2024 EPA GT source-unit operational intake pending, generator-specific electrical performance calibration NOT established.**
