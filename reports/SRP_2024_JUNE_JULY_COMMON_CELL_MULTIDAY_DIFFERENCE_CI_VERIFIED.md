# Real-source June–July 2024 common-cell 2/3/5-date moving-block coefficient-difference sensitivity — CI verified

**Actual observed source workflow:** [GitHub Actions 42100447565](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42100447565) **SUCCESS**, code and tests commit `2ea2a5da0a8dbf3b7b0f236f0c8e0a7b8a158590`; [actual 18-row results, 6-row stability summary, methodology scope manifest: artifact 13450170685](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42100447565/artifacts/13450170685). Observed EPA–ERA5–EIA930 June/July original-hour source artifact was independently verified in [42092282072](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092282072); source restricted-cell OLS was verified in [42093112865](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42093112865). The one-date block predecessor is [42099599060](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42099599060). All current tests, archived input restoration, model calculations, provenance constraints and output upload succeeded.

## Prespecified design, outcomes and limitations

The source cohorts represent 10 EPA units across 3 distinct Arizona sites, but only **6 units with adequate observed positive-operating source gross loads in both months** pass the previously defined conditional outcome gate. The **2°C ERA5 plant-point temperature × 500-MW official SRP EIA930 BA demand × 4h Arizona MST clock bin** common-support set is frozen before resampling. Source unit profiles are genuine 2024 June and July observations (713 and 737 UTC-month intersecting hours per EPA source respectively before shared-cell restriction).

For each of the 6 units independently, two regression coefficients represent **reported EPA source Gross Load MW conditional on positive reported Operating Time** versus observed ERA5 temperature; controls: SRP BA demand in GW, local MST hour fixed effects, and separately relabeled local-date fixed effects. Exact original point coefficients were verified numerically against the previous source full-dummy OLS regression using within-day FWL residualization.

For each **2-, 3-, or 5-consecutive-local-date moving-block width** (noncircular, no month-end wrap), **120 resampled June/July date-block pairs** are generated with the fixed seed `20261105`. Draws within June and July are independent; repeated sampled dates have distinct dummy identifiers. The shared-cell definition is fixed, meaning a source hour not observed in the original common cells cannot appear in a draw. A draw fails if either month has fewer than 80 measured positive-operation Gross Load records or lacks identifiable temperature variation after controls. A 2.5–97.5% descriptive percentile span is published only if at least **108/120 (90%)** paired draws succeed.

**Warning:** These are **sensitivity spans, not statistically validated 95% confidence intervals, p-values, or confirmatory evidence**. Only one June and one July month are observed; heatwaves may persist longer than five days, and shared plant weather and SRP BA demand induce cross-unit dependence. The gross-output outcome is conditioned on dispatch-selected positive operating hours; it is not observed net available generating capacity. This experiment does not test actual out-of-month forecasting or identify physical generator derating.

## Real-source results: July minus June conditional source Gross Load temperature slope

All coefficients and spans in MW/°C. `Withheld` means fewer than 108 paired draws admitted, **not** zero uncertainty.

| EPA source | Original difference | 2-day admitted /120 and percentile span | 3-day admitted /120 and span | 5-day admitted /120 and span |
|---|---:|---|---|---|
| **141 / 1** | +6.29 | **103 — withheld** | 109: [−4.43, +25.84] | 111: [−2.48, +25.71] |
| **141 / 2** | +13.97 | 115: [−5.25, +24.04] | 110: [−7.87, +24.77] | 119: [−10.12, +23.77] |
| **141 / 3** | +11.89 | **96 — withheld** | **82 — withheld** | **89 — withheld** |
| **147 / K-7** | **+9.83** | **120: [−0.02, +24.09]** | 120: [+3.86, +21.91] | 120: [+3.02, +21.75] |
| **55129 / DBG1** | +1.00 | 120: [−6.08, +7.43] | 120: [−4.21, +5.68] | 120: [−7.07, +5.16] |
| **55129 / DBG2** | +1.04 | 120: [−4.07, +6.77] | 120: [−3.11, +7.45] | 120: [−4.62, +6.80] |

The preceding single-day-block source comparison yielded K-7 **[+0.16, +21.57] MW/°C**. That marginally positive lower endpoint **does not persist under the 2-day moving-block procedure**, which yields **[−0.0235, +24.0880] MW/°C**, even though the 3- and 5-day procedures give strictly positive spans. Their **block-length dependence is evidence *against* a confirmatory claim that the observed K-7 month difference is consistently nonzero**. K-7 remains a scientifically interesting descriptive result for further independent-month investigation, not an established equipment heat effect.

Across all six EPA units, **0/6 have a fully reportable, zero-excluding span for every 2-, 3-, and 5-day moving-block width**. Source 141/1 fails the 2-day sample-admission requirement; 141/3 fails all three; 141/2, DBG1 and DBG2 have intervals crossing zero at every reportable width. Do not present six source units as six independent ERA5-site repetitions: there are only three distinct source weather sites.

## Conclusion and evidence gating for the manuscript / PyPSA

1. **The original six-unit in-sample OLS month-difference point estimates are not uniformly stable to date-block dependence and operating-source selection.** K-7 crosses zero under 2-day blocks, other units cross zero or cannot support an admitted interval.
2. A conservative paper should show this as **exploratory observational/sensitivity analysis** in the Results or Supplement, while clearly maintaining the no-causal-derating limitation in Discussion.
3. The next compelling validation requires another genuinely independent and temperature-overlapping source month or year, external prediction diagnostics, and robust equipment/dispatch evidence if physical thermal sensitivity is to be claimed.
4. **No PyPSA generator derating coefficients, forced outage evidence, net MW availability, LOLE, EENS or real grid failure claims are authorized from these descriptive results.**

Implementation: [paired month moving-date-block code](../src/grid_resilience/srp_epa_june_july_multiday_difference_bootstrap.py), [tests](../tests/test_srp_epa_june_july_multiday_difference_bootstrap.py), [source CI workflow](../.github/workflows/srp-epa-june-july-multiday-difference.yml).
