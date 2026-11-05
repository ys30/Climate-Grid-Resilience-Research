# 2024 SRP EPA–ERA5–EIA930 local-day-block bootstrap robustness — CI verified

**Observed-source GitHub Actions run:** [42055813837](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42055813837), **SUCCESS**, commit `c99e62bbcd32420714e71edbf4994f58a6e748d2`; [machine-readable artifact 13429286461](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42055813837/artifacts/13429286461). Full research methods CI for test creation `0adc931e` succeeded. This is a **real original-source experiment**, not synthetic-test results.

## Design

Separate regressions for each of the ten archived 2024 EPA source units, with 737 exact UTC-matched July observations per unit. Two outcomes: binary reported Operating Time >0 (linear probability) and reported gross load (MW) **conditional on positive operating time**. Predictor of interest: ERA5 site-point 2 m temperature (per °C); controls: SRP-wide EIA-930 reported demand in GW, local-standard hour indicators, and Arizona local-standard date effects. Original-source data and timestamp audit are pinned to [EPA–ERA5 run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085) and [official EIA930 H1/H2 July merge run 41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594).

The [implementation](../src/grid_resilience/srp_epa_eia930_day_block_bootstrap.py) uses **31 local-standard date blocks**; each of **120** bootstrap replications samples 31 complete date blocks with replacement. Hourly observations stay together within each sampled day; repeated days receive **new day fixed-effect labels**. Within-day demeaning implements the original OLS via Frisch–Waugh–Lovell, with an explicit numeric agreement check against the previously verified full-dummy fit. Fixed pseudorandom seed `20261105`. The 2.5th–97.5th percentile interval is published only if **at least 90%** of draws produce a numerically identified coefficient with at least 80 valid outcome records.

**Crucial interpretive limitation:** This 31-day resampling is a sensitivity exercise, **not a validated 95% confidence interval**: weather and demand have heatwave-scale persistence across days, the 31 dates are not random independent replications, models are observational, and 10 source units share weather within three sites. No p-values or independent-year validation are claimed.

## Verified original-source results

| Plant / EPA Unit | Reported-operation LPM coefficient (percentage points per °C) | Exploratory bootstrap percentile span (percentage points per °C) | Gross-load coefficient conditional on positive operation (MW per °C) | Exploratory gross-load span (MW per °C) |
|---|---:|---:|---:|---:|
| 141 / 1 | −3.49 | [−8.38, +3.07] | −2.63 | [−7.26, +2.13] |
| 141 / 2 | −1.53 | [−6.67, +5.61] | −3.23 | [−9.43, +3.72] |
| 141 / 3 | −0.46 | [−4.51, +4.86] | −6.53 | [−16.65, +1.75] |
| 141 / 7 | −0.47 | [−6.61, +5.32] | +3.46 | [−2.49, +7.56] (110/120 admissible) |
| 141 / 8 | +1.08 | [−4.73, +7.65] | +3.35 | **Not reportable** (97/120 admissible) |
| 147 / K-7 | +2.70 | [−0.66, +7.24] | +7.14 | [+0.77, +18.57] |
| 55129 / DBG1 | +0.19 | [−1.33, +1.89] | +0.27 | [−3.46, +3.20] |
| 55129 / DBG2 | −0.24 | [−1.01, +0.005] | +0.48 | [−2.68, +4.14] |
| 55129 / DBG4 | −1.15 | [−3.21, 0.00] | **No fit** (18 valid source rows) | **Not reportable** |
| 55129 / DBG5 | −0.98 | [−3.47, +0.53] | **No fit** (19 valid source rows) | **Not reportable** |

All 10 operation model resampling sequences admitted 120/120 draws; 141/8 gross-load reported only 97 qualified draws, below the prespecified 108/120 minimum. Gross outcomes at DBG4 and DBG5 are not fitted even in the original OLS. Note K-7's positive exploratory gross-load percentile span does not cross zero **under this sensitivity procedure**; it does **not** imply that heat increases available generation, and must be checked with alternative specifications, equipment dispatch evidence and truly independent source periods.

## Research admission and next actions

- Source-hour conservation, model FWL coefficient reproduction, seed reproducibility, sample failure thresholds and no weather/demand imputation were verified by CI.
- These runs **do not** identify generator availability, causal temperature derating, actual EIA GT net MW, forced outages, or observed EENS. Original ECMPS 2024 monitor plans remain inaccessible on the production API under a keyless 403 probe.
- Next checks: **leave-one-local-day-out sensitivity**, longer-block heatwave serial correlation, alternate control specifications, demand/weather collinearity, physical unit identity, and independent-year external validation.
