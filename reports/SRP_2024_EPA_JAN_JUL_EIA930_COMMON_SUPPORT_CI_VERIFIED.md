# SRP EPA–ERA5–EIA930 January/July 2024 common support — CI verified

**Verified actual-source workflow:** [42079419601](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42079419601), **SUCCESS**, corrected test commit `357bda53ca92022048c1bc1d79f532acaea336fb`; [data artifact 13440023073](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42079419601/artifacts/13440023073). The initial attempts failed due to inaccurate *test assertions*, not because the archived inputs were missing. The final workflow passed actual source downloads, all targeted tests, the strict timestamp/identity/evidence audit, and upload.

## Research question and sources

Can the separate January and July 2024 per-EPA-unit ambient-temperature regression coefficients be interpreted as comparisons within overlapping environmental and system-demand conditions? Previously successful CI runs establish genuine January EPA/ERA5 ([42072156313](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42072156313)), official January EIA930 SRP demand ([41407182014](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407182014)), genuine July EPA/ERA5 ([41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085)) and official July EIA930 SRP demand ([41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594)). Ten identical EPA source unit IDs, across three sites, are each represented by exactly **737 genuine UTC-month overlap site weather hours in January and July**. Source-hour identities are audited, with EPA time fixed at Arizona MST UTC−7 and official EIA930 reporting end-hour converted to start-hour. The seven source-month boundary hours are never fabricated or filled.

## Confirmed lack of temperature common support

| EPA facility | EPA units | January maximum site temperature | July minimum site temperature | Observed temperature gap | January/July SRP BA demand marginal ranges intersect? | Shared 2°C × 500 MW × 4h source bins | Descriptive joint support admitted? |
|---|---|---:|---:|---:|---|---:|---|
| 141 | 1, 2, 3, 7, 8 | **25.2°C** | **28.2°C** | **3.0°C** | Yes | **0** | **No** |
| 147 | K-7 | **25.1°C** | **27.4°C** | **2.3°C** | Yes | **0** | **No** |
| 55129 | DBG1, DBG2, DBG4, DBG5 | **25.5°C** | **26.1°C** | **0.6°C** | Yes | **0** | **No** |

There are **zero overlapping continuous temperature ranges for all ten source units**, so intersection of temperature, SRP demand and time-of-day cannot hold, irrespective of the shared BA marginal demand range. The binned audit prespecifies 2°C site-temperature × 500 MW SRP BA-demand × 4-hour MST time-of-day cells. All ten source units have zero shared occupied joint bins, zero covered hours within these bins for either month, and zero units that pass the conservative `>=80 covered hours and >=10 observed dates per month` descriptive common-support threshold. **None can support a within-overlap January/July conditional Gross Load comparison either.**

These counts reflect same-site weather *repeated* across EPA source units; ten unit rows do not imply ten independent meteorological site samples. The audit refuses to coarsen bins post hoc to manufacture overlap, and it does not use extrapolated or imputed observations.

## Scientific interpretation

1. **Winter and summer conditional temperature coefficients cannot be compared as though they were estimates over a shared observed temperature regime.** In particular, 147/K-7's exploratory January conditional gross-load coefficient **−3.93 MW/°C** and July **+7.14 MW/°C**, and the similar reversal in its running-state LPM coefficient, are model-specific descriptive associations over **disjoint weather support**, not an identified physical seasonal response shift.
2. Both months have some overlapping SRP BA demand values, which does not rescue the missing site-temperature positivity. Higher-dimensional overlap cannot exist if a required one-dimensional covariate has none.
3. July 2024 day bootstrap, multi-day blocks, date deletion and January comparisons remain informative **descriptive sensitivity analyses**, but they are neither independent validated tests of a transferable heat–electricity causal mechanism nor evidence of physical turbine available net MW.
4. January Plant 141 source units 1,2,3 also have zero positive Operating Time source hours, causing an independent outcome-support failure for conditional gross-load modeling. This is distinct from the missing covariate common support.
5. Alternative seasons/months with truly overlapping source temperature and demand conditions are necessary for valid out-of-sample parameter testing. June, September, spring/shoulder seasons or a separately verified hot-year cohort are candidates **only after their actual EPA/ERA5/EIA930 sources and overlap have been verified**.
6. Neither EPA source gross electricity nor reported Operating Time is equivalent to observed available EIA-generator net MW, forced-outage observation, source 2024 ECMPS electrical identity, historical EENS or actual derating. **No PyPSA physical derating calibration is admitted.**

## Implementation and next gate

[Source-level 3D overlap audit](../src/grid_resilience/srp_epa_jan_jul_common_support.py), [strict coverage and no-imputation tests](../tests/test_srp_epa_jan_jul_common_support.py), and [real original-source workflow](../.github/workflows/srp-epa-jan-jul-common-support.yml). Next experiment should acquire validated EPA hourly + EIA930 BA demand + ERA5 for a genuine **shoulder-season month or another summer month/year**, then check actual nontrivial joint support before trying slope stability or external prediction. Maintain the distinction between support, association, prediction and physically calibrated reliability.
