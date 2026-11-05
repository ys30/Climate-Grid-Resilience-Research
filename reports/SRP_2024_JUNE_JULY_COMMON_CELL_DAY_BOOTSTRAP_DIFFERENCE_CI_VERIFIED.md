# June–July 2024 EPA source common-cell temperature-slope difference: local-day-block sensitivity (CI verified)

**Real original-source workflow:** [42099599060](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42099599060), **SUCCESS**, source run code commit `280af480aa29d1ace478dea49145e838ea122045`. [Machine-readable six-unit paired difference CSV and scope manifest, artifact 13449117228](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42099599060/artifacts/13449117228). Existing original input provenance: verified June and July joined EPA–ERA5–EIA930 source hours from [42092282072](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092282072); original within-common-cell regressions from [42093112865](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42093112865). Original EPA Arizona source archive MD5 `7123a5070f652890f46e819dcc890ec0` is checked in the source artifact and this workflow; SRP demand derives from original official EIA930 data.

## Question and study design

For the **six EPA sources** passing the predeclared positive-operation Gross Load support threshold in **both June and July**, how sensitive is the **July minus June** difference in exploratory site-ERA5 temperature coefficients to the identity of dates included in each period?

The source panels contain **713 June UTC-calendar-matched hours and 737 July UTC-calendar-matched hours per EPA source unit** before intersection. The exact **2°C ERA5 air-temperature × 500 MW SRP BA EIA930 demand × 4-hour Arizona MST time-of-day shared occupied cell** set is **frozen before bootstrapping**. For each unit and month, the regression outcome is observed **EPA reported Gross Load (MW) conditional on positive Operating Time**, controlling for observed SRP BA demand in GW, local MST hour fixed effects and local MST date fixed effects. The original full-sample temperature coefficient is **numerically checked against the prior full-dummy OLS regression** using the Frisch–Waugh–Lovell day-within estimator.

The resampling draws **whole observed local-date contributions with replacement**, **independently for June and July**, and gives each sampled date occurrence a separate fixed-effect ID; 120 paired iterations are generated from a fixed seed `20261105`. If the observed operating/gross records in a resample are fewer than 80, or the temperature slope is not numerically identified, the draw is rejected. A percentile range is published **only if at least 108/120 paired draws** have both month slopes admitted. **No missing values are filled.**

These are **exploratory resampling sensitivity percentile ranges, NOT formal 95% confidence intervals**: a date is not independent from neighboring dates in a heatwave, the joint common-cell screen is sample-selected, source weather and BA demand are common within colocated units, 120 resamples give noisy extreme percentiles, and the original unit gross-load sample is dispatch-selected. Repeating these resamples is not independent predictive validation.

## Source-verified differences and admissible spans

All coefficients below are MW of **reported EPA source Gross Load per °C**, **conditional on positive reported operation**, not observed available EIA generator net capacity.

| EPA source | June gross-source operating rows in shared cells | July rows | June slope (MW/°C) | July slope (MW/°C) | July − June slope (MW/°C) | Admitted paired draws/120 | Exploratory 2.5–97.5% span for difference (MW/°C) |
|---|---:|---:|---:|---:|---:|---:|---|
| 141 / 1 | 110 | 309 | −7.84 | −1.55 | **+6.29** | **94** | **Withheld** |
| 141 / 2 | 120 | 310 | −17.23 | −3.26 | **+13.97** | **106** | **Withheld** |
| 141 / 3 | 98 | 352 | −19.04 | −7.15 | **+11.89** | **92** | **Withheld** |
| 147 / K-7 | 354 | 560 | −3.17 | +6.66 | **+9.83** | **120** | **[+0.16, +21.57]** |
| 55129 / DBG1 | 376 | 687 | −1.09 | −0.10 | **+1.00** | **120** | [−5.41, +8.93] |
| 55129 / DBG2 | 391 | 696 | −0.83 | +0.21 | **+1.04** | **120** | [−4.73, +8.25] |

**Key statistical restraint:** despite substantial point-difference magnitudes, **all three Plant 141 source-unit percentile ranges are blocked by the prespecified source sufficiency gate**; do not substitute empirical percentiles calculated on the surviving 94/106/92 draws, and do not imply three independent replications of the same site ERA5 weather.

K-7's positive exploratory point difference and [0.16, 21.57] one-date-block span make its observed association worth further testing. They do **not** establish a statistically significant causal thermal effect, physical heat improvement, identifiable difference in turbine availability, or independence from dispatch-selection mechanisms. At K-7, **positive reported operating-state probability** and **conditional gross output** behave differently across months, a warning against mechanical physical interpretation.

## Validated versus pending

**Validated:** exact source inputs and month-hour records; archived source MD5; verified original 6 source gross cohort; frozen cross-month joint cell gate; source-matched original point coefficients; date-wise resampling and independent month repetitions; numerical consistency with prior within-month full OLS; rejection of sparse resamples; source CI and artifact.

**Not established:** 2–5-day longer heatwave block stability, reliable serial-dependence-adjusted confidence intervals, formal source-unit multiple-comparison inference, independent forecasting/held-out error, causal generator thermal derating, EIA generator net availability, physical ECMPS unit-stack mapping, forced outage labels, actual observed historical EENS/LOLE or calibrated PyPSA generator limits.

## Next best experiment

Use **2/3/5 consecutive observed local-date block resampling separately in each month** for the same frozen common-cell source cohorts and require conservative sample admission. Because K-7's one-day percentile lower bound is near zero, longer-block sensitivity is especially important. In parallel, examine independence from dispatch controls and out-of-sample June→July source-response prediction *without* mislabeling a predictive fit as heat-driven equipment availability.

Code: [date-block difference model](../src/grid_resilience/srp_epa_june_july_common_support_bootstrap.py), [tests](../tests/test_srp_epa_june_july_common_support_bootstrap.py), [GitHub workflow](../.github/workflows/srp-epa-june-july-joint-cell-bootstrap.yml).
