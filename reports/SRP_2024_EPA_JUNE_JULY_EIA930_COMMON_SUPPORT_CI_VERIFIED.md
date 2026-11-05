# 2024 June–July EPA–ERA5–EIA930 true common support — verified actual-source CI

**Primary real-source run:** [42091711862](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42091711862) **SUCCESS**, artifact [13444684476](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42091711862/artifacts/13444684476). All seven targeted synthetic regression/source-admission tests passed; the real workflow retrieved three newly requested **June 2024 ERA5 site time series** with response hashes, independently downloaded **2024 EPA Arizona full original hourly file** and verified its pinned Zenodo MD5, and downloaded **official EIA-930 2024 January–June H1 Balance CSV** with SHA256 retained. Existing certified July EPA/ERA5 and official July H1/H2-adjusted EIA930 observations were reused. No weather, demand, or EPA operating observations were imputed.

## Exact time, source, and unit coverage

EPA Part75 observation clock: Arizona Mountain Standard Time, fixed UTC−7. June *local standard* source includes **720 hours per EPA source unit** (June 1–30); the official EIA/ERA5 **UTC June** datasets provide only **713 overlapping hours per unit** (2024-06-01 07:00–2024-06-30 23:00 UTC). The seven 2024-07-01 UTC boundary hours are excluded, not substituted. July local source includes 744 hours/unit, with **737 UTC July overlap hours/unit**. The same ten source EPA IDs at Plants 141, 147 and 55129 have 7,130 June and 7,370 July source unit-hours; weather is shared at three EPA facility-point ERA5 site series. Gross Load is a **reported source gross** value, *not net EIA generator available MW*.

## Measured June–July temperature and demand support

| EPA facility | Monitored source units | Genuine June ERA5 range | Genuine July ERA5 range | Shared continuous temperature range width | Shared 2°C × 500-MW × 4h observed covariate bins | June/July covered site-hours per unit in shared bins |
|---|---|---|---|---:|---:|---|
| 141 | 1, 2, 3, 7, 8 | **22.7–44.8°C** | **28.2–46.3°C** | **16.6°C** | **63** | **451 / 685** |
| 147 | K-7 | **21.7–45.1°C** | **27.4–46.4°C** | **17.7°C** | **62** | **412 / 676** |
| 55129 | DBG1, DBG2, DBG4, DBG5 | **21.5–44.2°C** | **26.1–46.1°C** | **18.1°C** | **67** | **415 / 702** |

These are real observed single-site temperature ranges, not one standard error or modeled response. The source prespecifies 2°C ERA5 air-temperature × 500-MW SRP BA-demand × 4-hour local-clock cells. Both months need at least 80 matched source hours spanning at least 10 source dates. **All 10/10 EPA units pass this descriptive covariate occupancy screen**, unlike the prior January–July **0/10** temperature/common-support screen. This screen is only a preliminary condition for comparing observational models; it **does not establish conditional exchangeability**, equal dispatch, or causal identification. Since ERA5 weather and BA demand are shared across colocated units, matched bin counts should **not** be treated as independent experimental replicates.

## Separately audited operating-support selection

Shared-bin **observed positive-operation and gross-reported hours per unit**:

| EPA unit | June | July | Prespecified 80/80 conditional gross observation gate |
|---|---:|---:|---|
| 141 / 1 | 110 | 309 | **Pass** |
| 141 / 2 | 120 | 310 | **Pass** |
| 141 / 3 | 98 | 352 | **Pass** |
| 141 / 7 | 7 | 96 | **Fail — June sparse** |
| 141 / 8 | 7 | 84 | **Fail — June sparse** |
| 147 / K-7 | 354 | 560 | **Pass** |
| 55129 / DBG1 | 376 | 687 | **Pass** |
| 55129 / DBG2 | 391 | 696 | **Pass** |
| 55129 / DBG4 | 0 | 12 | **Fail — no June shared-bin gross source** |
| 55129 / DBG5 | 0 | 14 | **Fail — no June shared-bin gross source** |

**Six of ten** source units pass a positive-operation conditional gross-load support threshold. The four remaining source units are **not** eligible for meaningful shared-bin conditional gross-load slope comparisons. A nonoperating reported hour does not establish a forced outage.

## Scientific contribution and next step

Compared with January/July, June/July provides **the first directly verified, nonempty real source weather-demand-time common-support window** for this observational panel. That is a necessary prerequisite to an independent-month diagnostic for the summer source-unit temperature relationship, and eliminates extrapolation across totally disjoint temperature ranges. The next source-controlled experiment should compare June and July **within these jointly occupied cells** and preserve seasonal operation selection and temporal dependence caveats. Before interpreting coefficients as technology-specific true derating or feeding calibrated PyPSA availability, secure independently verified EPA/EIA GT electrical identities, net available MW and actual dispatch/outage observations.

The EPAs' gross-load and reported Operating Time data are not observed generator available net MW, historical outage rates, empirical EENS or causal climate-attributed electricity loss. No parameter from this support screen may be admitted directly to physical PyPSA derating calibration.

**Source code and reproducibility:** [June/July source-hour admission and support code](../src/grid_resilience/srp_epa_june_july_2024_common_support.py), [source integrity tests](../tests/test_srp_epa_june_july_2024_common_support.py), [real CI workflow](../.github/workflows/srp-epa-june-july-common-support.yml).
