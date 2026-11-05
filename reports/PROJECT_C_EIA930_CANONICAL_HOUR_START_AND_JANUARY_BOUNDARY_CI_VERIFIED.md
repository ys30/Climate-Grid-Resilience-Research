# Critical EIA-930 UTC interval-ending versus model-start normalization — source-verified correction

**Date:** 2026-11-05. **Canonical correction:** Original EIA-930 BA electricity demand is an hourly integrated value timestamped at the **END** of its UTC hour; model and ERA5 source hour is defined by the **START** of the same physical interval. Convert reported EIA `period`/official `UTC Time at End of Hour` to `timestamp_utc_start = timestamp_utc_end - 1 hour`. No calendar boundary may be wrapped, invented or set to zero.

EIA primary time-reporting documentation: https://www.eia.gov/electricity/930-content/about.html (EIA: hourly integrated values published at hour ending). The original EIA-930 Form instructions also require hourly integrated demand reported by hour ending.

## Source-verified matching evidence

The original 168h four-BA archived EIA API inputs [run 41102363806](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41102363806) and refetched July official EIA CSV + ERA5 inputs [run 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361) were compared on exact UTC keys. [First comparison CI 42104382649](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104382649) established complete original/refetched ERA5 point temperature and assumed wind availability equality but differences in same-labeled demand. [Five-lag source diagnostic 42104639488](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104639488), [artifact 13451056369](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104639488/artifacts/13451056369), found an exact **−1h old demand-label shift** at all BAs:

| BA | Genuine observed overlapping hours after correction | Exactly identical reported BA demand | MAE |
|---|---:|---:|---:|
| AZPS | 167 | 167 | 0 MW |
| BPAT | 167 | 167 | 0 MW |
| CISO | 167 | 167 | 0 MW |
| SRP | 167 | 167 | 0 MW |
| **Total** | **668** | **668** | **0 MW** |

The source-level canonical normalization CI [42107186857](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107186857), **SUCCESS**, [artifact 13451198410](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107186857/artifacts/13451198410), independently checked the same exact source hour mapping and **four genuine unsupported original/refetched boundary hours per side**. There is **no claim of an exact 168/168 same-hour source overlap**, and no imputation of unmatched hours.

## Repairs and regression gates

The following previously inconsistent EIA930 API paths now use a single shared UTC start-hour convention:
- [Canonical conversion and inclusive query period bounds](../src/grid_resilience/eia930_hour_convention.py).
- [Four-BA API EIA930 hourly demand intake](../src/grid_resilience/eia930_hourly.py): query source hour-ending UTC from the requested model **start+1h** through the requested model **exclusive end** (inclusive last EIA hour-ending), then subtract one hour in the result.
- [Normalized previously downloaded API response](../src/grid_resilience/eia930_hourly_demand.py): subtract one hour on `period` prior to the strict BA×UTC-hour coverage check.
- [Single-BA complete-month API demand intake](../src/grid_resilience/eia930_monthly_demand.py): correctly request the following month's **00:00 UTC hour-ending** as the final January model UTC 23:00 hour, and convert each source label to start-hour. No silent interpolation of a missing first or last modeled hour.
- [Unit and source regression tests](../tests/test_eia930_hourly.py), [monthly tests](../tests/test_eia930_monthly_demand.py), [raw JSON normalizer tests](../tests/test_eia930_hourly_demand.py). A dedicated [GitHub Actions workflow](../.github/workflows/eia930-hour-ending-normalization-source-ci.yml) downloads both archived source inputs, confirms 668/668 source pairs and enforces no boundary filling.

**Important historical-data restriction:** The legacy first-week four-scenario PyPSA output (+23,306.936668 MWh modeled second difference under original timestamp labels) cannot be called an exact same-input reproduction of the corrected hour-start first-week value (+22,515.997901 MWh). The difference is partly due to shifted demand-vs-weather alignment; the 4-week source-verified values remain **hypothetical model output** rather than observed grid reliability. An exact-input counterfactual would need source-matched hour starts and identical hour-boundary support and model configuration.

## Real January 2024 SRP official source limitation

Attempting direct EIA API retrieval through the historical runner returned **HTTP 403** (API access denial), not evidence of no demand. The independently retrieved original 2024 Jan–Jun official EIA930 BALANCE CSV is available, but a strict full January UTC **744-hour** admission failed for a genuine time-boundary reason. [Source-audit CI 42107615151](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107615151) verified:

- SRP source original timestamp rows available at model UTC hour-start: **737**, with **no duplicate** or **invalid / null / nonpositive** admitted demand.
- Exactly **7 source hours are missing** from the full Jan UTC calendar: **2024-01-01 00:00–06:00 UTC**. No other UTC January hours are missing.
- Consequently **do not advertise this original CSV as complete 744-hour January EIA demand**. The seven early UTC boundary hours must not be forward-filled, copied from another date, guessed, or represented as zero.

The corrected [official source CI run 42107809109](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107809109) **SUCCESS**, [artifact 13451578748](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107809109/artifacts/13451578748). It retrieves and retains a SHA256 of the original official EIA930 half-year CSV, and passes an explicitly named **SRP Jan 2024 seven-hour UTC boundary-only exception** that admits **exactly 737 source hours (2024-01-01 07:00 UTC through 2024-01-31 23:00 UTC)**. The default full-month intake remains fail-closed; the exception is unavailable for any other BA, year, month, missing interior hour or positive operation imputation. `complete_utc_month=false` and `unobserved_hours_imputed=false` are recorded.

This is consistent with previous source-verified January EPA/ERA5/EIA930 intersection 737 hours and prevents a false 744-hour observational evidence claim. It does **not** invalidate independent January **model scenario** runs that use assumptions for all 744 calendar hours; instead it forbids presenting those modeled calendar hours as 744 observed BA demand records from this specific archival CSV.

## Consequences for Project C and manuscript

1. **Time-basis correction is confirmed source-backed**; avoid comparing or pooling legacy and corrected-weather exposure or four-case interaction results as though hourly demand/weather pairing were unchanged.
2. The new four distinct July 168-hour event replication is now the version-preferred observed-input **scenario screening** under explicit structural assumptions; older source-affected plots and claims must be marked legacy/hour-label-unreconciled until separately re-executed.
3. The January official CSV source is **737-hour boundary-limited**, not a complete January month. Research model scripts must join on real original timestamps and reject the first seven UTC hours if they are not independently supported.
4. The first-week and all-four-week modeled shortages are NOT measured blackouts/LOLE/EENS or empirically calibrated physical net capacity. Source hour fixes do not cure the underlying *partial gas/wind fleet, assumed shock response, synthetic link ratings and incomplete generator available-MW* limitations.
5. No independent-year or independent-season physical validation has been obtained. Do not present the four adjacent July windows as independent heatwaves or future-year predictive verification.

**Research status:** core time-domain integrity issue corrected for the targeted EIA930 API source adapters, cross-source matching source-verified, January boundary gate verified. Full historical reruns/figures based on the old hour convention still require explicit versioned recomputation and data-admission checks.
