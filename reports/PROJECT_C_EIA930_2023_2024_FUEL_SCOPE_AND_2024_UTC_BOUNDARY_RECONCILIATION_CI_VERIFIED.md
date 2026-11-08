# Paper C — EIA-930 observed fuel reporting scope and 2024 July six-month file boundary

## Source-verified results and CI

- [Seven-day EIA-930 raw-fuel reporting versus incomplete PyPSA baseline-output scope CI 42442266145](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42442266145), [four year/network audit CSV files and source hashes](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42442266145/artifacts/13602136929).
- [2024 UTC half-year partition reconciliation CI 42442420391](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42442420391), [original-source BA/hour attribution and fully recovered net/gas totals](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42442420391/artifacts/13602410607). Both CI runs passed. [Source boundary code](../src/grid_resilience/paperc_eia930_halfyear_utc_boundary.py) and [fuel reporting code](../src/grid_resilience/paperc_eia930_sevenday_generation_scope.py).

The seven-day model windows remain **2023-07-10–16 UTC** versus **2024-07-01–07 UTC**, each 168 hours × 4 BAs. EIA-930 official *raw* net generation and gas fuel rows are source observations, whereas the year-specific EIA-860 gas/wind nameplate and PyPSA baseline gas/wind dispatch are **unmatched, incomplete, conditional model inputs and outputs**.

## Essential finding 1 — what initially appeared to be missing source BA-hours was a partition artifact

Auditing **only** the official `EIA930_BALANCE_2024_Jul_Dec.csv` finds **644 of 672** July 1–7 UTC four-BA hours. Independently downloading the official **2024 Jan–Jun** balance file recovers **exactly seven additional UTC hours per BA (28 total)**, with **no overlap and no remaining missing BA-hours**. The six-month CSV partition has a BA-local-date boundary that does not coincide with the UTC study window; it is scientifically incorrect to interpret the originally apparent 28 hours as missing historical generation. No imputation was used.

| BA | Jan–Jun source hours | Jul–Dec source hours | Complete observed 168h BA net generation (MWh) | Complete observed 168h natural gas generation (MWh) |
|---|---:|---:|---:|---:|
| AZPS | 7 | 161 | **522,280** | **203,967** |
| BPAT | 7 | 161 | **1,763,554** | **116,528** |
| CISO | 7 | 161 | **4,653,684** | **2,076,666** |
| SRP | 7 | 161 | **1,355,280** | **492,311** |

These figures are **signed EIA-930 BA-wide reported raw generation integrated over 168 one-hour intervals**. They are not 2024 historical EENS, out-of-service capacity, or identical to modeled generic thermal output; imports, exports and physical BA boundary reporting must be addressed separately.

## Essential finding 2 — official EIA-930 fuel reporting schema changed at the boundary

The historical 2023 source exposes **nine older fuel categories**, including combined `Hydropower and Pumped Storage`, `Wind` and `Solar`. The 2024 Jul–Dec source instead has **16 explicit fuel/storage categories**, including separated conventional hydro and pumped storage, solar and wind with versus without integrated battery, and dedicated storage entries. The **Jan–Jun 2024 7-hour portion and Jul–Dec 2024 161-hour portion have different official fuel schemas.**

The strict 2023 seven-day report has **29/36 fully present BA × fuel combinations** and **7 incompletely reported combinations**; missing values are never zeros. The preliminary **Jul–Dec-only** 2024 file had **0/64 complete 168-hour BA × fuel groups**, chiefly because it does not contain the 7-hour portion from the preceding half. **That figure must not be cited as evidence that 2024 fuel reporting is absent.** Reconciled total BA net generation and `Natural Gas` are full-period comparable fields; wind, solar and hydro/pumped-storage subcategories cannot simply be summed across old/new categories and labeled an observed uniform series without an explicit transparent crosswalk.

## Scientific limitation for the paper

The modeled `generic_thermal_proxy` does not correspond to the exact EIA-930 `Natural Gas` fleet; model `wind` output is not necessarily the same physical population as the EIA-930 pre-2024 `Wind` or post-split `Wind without Integrated Battery Storage` category. Nor does subtracting the model's partial-fleet output from BA-reported net generation yield a physical supply residual, an unexplained outage, or real expected energy not served.

### Next material steps

1. Build explicitly versioned, provenance-preserving gas/wind/hydro reporting crosswalks across both halves. Preserve split solar/wind-plus-storage and pumped storage **without silently attributing their MW** to conventional generation.
2. Compare **observation-hour-matched** reported gas and non-integrated wind versus the model's proxy generator traces, with source coverage/denominator gates and interval-level diagnostics. Treat that as model scope comparison, not plant identity or dispatch calibration.
3. Add full-fleet generation technologies, verified inter-BA flows, available generator capacities and source-specific hydropower/storage constraints before claiming realistic system adequacy.

**Current status:** Official 2023 and 2024 four-BA EIA-930 raw source acquisition, missingness census and **full 2024 672h net/gas UTC boundary recovery** are reproducibly verified. The simulation remains an incomplete-fleet screening experiment, not actual physical supply gap.
