# EPA–ERA5–EIA930 July 2024 leave-one-local-date-out robustness — CI verified

[Observed-source GitHub Actions run 42056418406](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42056418406) **SUCCESS**, source commit `c2856e6846f3d63fb9c1cb180c0fc30111bd30ad`; [source CSV artifact 13430221298](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42056418406/artifacts/13430221298). The code and synthetic regression tests also passed in preceding Research Methods CI.

## Study design

Ten 2024 EPA source units in Plants 141, 147 and 55129, each with 737 exact July-UTC overlap hours with the archived SRP balancing-authority EIA930 demand observations and ERA5 source-point weather. At each EPA unit, the original same-hour model contains: measured ERA5 plant-point temperature, SRP-wide EIA930 demand, Arizona MST local hour fixed effects, and 31 local-date fixed effects. We re-estimate each model **31 times, each deleting one entire local-standard date**. Outcomes: positive reported Operating Time indicator (linear probability) and gross source load in MW *conditional on observed positive operation*.

This procedure diagnoses single-calendar-day leverage; it **does not** produce a confidence interval, correct longer serial persistence, provide causality or establish EIA generator net power. Reported min/max below summarize the 31 actual date-omission coefficients, not an inferential 95% interval. The sparse gross-load models with 18 and 19 source observations remain unidentified and unreported.

## Actual unit-specific results

| EPA source unit | Operation indicator full coefficient (percentage points/°C) | Operation coefficient date-delete span (percentage points/°C) | Gross load full coefficient (MW/°C) | Gross load date-delete span (MW/°C) |
|---|---:|---:|---:|---:|
| 141/1 | −3.49 | [−4.72, −2.41] | −2.63 | [−3.51, −1.43] |
| 141/2 | −1.53 | [−2.71, −0.35] | −3.23 | [−4.55, −1.54] |
| 141/3 | −0.46 | [−1.25, +0.50] | −6.53 | [−8.14, −3.10] |
| 141/7 | −0.47 | [−2.05, +0.63] | +3.46 | [+2.18, +4.15] |
| 141/8 | +1.08 | [−0.49, +2.16] | +3.35 | [+2.27, +4.37] |
| 147/K-7 | +2.70 | [+1.21, +3.67] | +7.14 | [+3.97, +8.28] |
| 55129/DBG1 | +0.19 | [−0.51, +0.48] | +0.27 | [−0.42, +1.56] |
| 55129/DBG2 | −0.24 | [−0.32, −0.11] | +0.48 | [+0.02, +1.44] |
| 55129/DBG4 | −1.15 | [−1.35, −0.14] | Not estimable (18 valid rows) | Not estimable |
| 55129/DBG5 | −0.98 | [−1.19, +0.19] | Not estimable (19 valid rows) | Not estimable |

Results retain the original model's exact control structure and unit-level grouping, with no reconstructed demand or artificially replicated site weather. Data outputs contain additional maximum absolute date-deletion influence, classification and source observation counts.

## Relation to independently completed date-block bootstrap

The [separate actual-data day-block bootstrap run 42055813837](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42055813837) sampled 31 local dates with replacement for 120 draws, retaining within-day serial structure. Its exploratory percentile spans **frequently cross zero** even when leave-one-out spans retain a common sign (e.g. 141/1 and 141/3 conditional gross load). These results are not contradictory: the former probes variability under substantial resampling of date composition; the latter probes sensitivity to deletion of **one** original date. Neither removes unobserved dispatch selection or longer-than-day heatwave dependence.

For 147/K-7 conditional gross load, date-block bootstrap span was **[+0.77, +18.57] MW/°C** and leave-one-date-out range is **[+3.97, +8.28] MW/°C**. This is consistent direction under these two *exploratory* procedures but is **not proof that hotter ambient air increases physical plant generating capability**. Observed gross output can rise when a source is dispatched harder during heat-linked high system demand. No physical unit mapping or historical net available capacity calibration is established.

For 141/8 conditional gross load, leave-one-out sign is consistently positive, but the bootstrap had only 97/120 admissible draws, so a bootstrap percentile span is **not reportable**. Do not suppress that low-sample warning.

## Next scientific admission gates

1. Independent-year source panels and a temporal holdout, including real EIA930 August demand for the missing seven EPA local-July hours.
2. Longer block-length, alternative link-function and missing-operational-source checks to assess serial dependence and sparse source operation.
3. ECMPS historical physical unit identity confirmation plus EIA/source engineering validation of actual generator-specific available net MW before any thermal derating calibration or modelled outage/EENS claim.

**Conclusion:** This phase improves uncertainty transparency and exposes heterogeneous unit behavior. No claim of empirical physically calibrated PyPSA availability, measured electricity shortfalls or climate-caused outages is admitted.
