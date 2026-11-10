# Paper C v10 — Original solver-level factorial recomputation and manuscript errata (10 November 2026)

## Verified re-audit

An independent local read of the exact immutable GitHub Actions source ZIPs (not a new PyPSA optimization) re-derived all **40** original July 2024 BA- and SYSTEM-level heat×wind second differences directly from **128** original `(event_id, network_variant, scenario, ba)` unserved-energy solver rows archived by [successful 2024 source model CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361), artifact **13451375705**. Original 2024 source code commit: `6831206284ffa86f176974972314038f49e7794f`. Checks included complete distinct scenario keys, no duplicate BA-scenario keys, one-to-one demand/weather BA-hour alignment in all four 168-hour cohorts, archived BA/SYSTEM reconciliation within 1e-5 MWh, and cross-year 2024 shared first-week anchor within 0.001 MWh against [CI 42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209), artifact **13592962046**. The [original Grand Coulee 672h PS solver artifact 13462104608](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635) was also checked for all four factorial second-difference arithmetic identities.

## Material local negative second differences

Only three BA-level modeled interactions are materially negative (using an absolute 0.001 MWh tolerance for floating-point roundoff):

| Original 2024 week | Original modeled network | BA | Recomputed signed model second difference (MWh) |
|---|---|---|---:|
| July 1–7 | Fixed hypothetical links | CISO | −5,763.712224 |
| July 15–21 | Fixed hypothetical links | BPAT | −5,918.428800 |
| July 22–28 | Fixed hypothetical links | AZPS | −3,663.801448 |

One additional original record, BPAT **isolated** in week 4, appears as approximately **−8.7 × 10⁻¹¹ MWh** when recomputed from original solver numbers (the preexisting stored summary field was approximately −5.8 × 10⁻¹¹ MWh); this is floating-point cancellation near **zero**, not a scientifically meaningful negative response. Exact last-digit numerical cancellation varies with arithmetic grouping. This tolerance is a numerical classification convention, **not a statistical significance test**.

The already verified 2024 system-level modeled second differences, summed across BAs and retrieved under both original network configurations, remain unchanged: isolated **+14,630.333 / +15,338.708 / +14,697.753 / +8,575.179 MWh**, illustrative frozen links **+22,515.998 / +16,204.695 / +25,211.030 / +15,177.070 MWh**.

## Two manuscript errata corrected in private v10

1. An old sentence in manuscript v9 still claimed the embedded Figure 2 was a summary-only figure pending replacement. That was obsolete: v7 onward already embedded the original CI **two-panel** Figure 2 from [successful figure CI 42878609152](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42878609152), artifact **13791309521**. Private v10 states the present source-correct status.
2. The private v9 Word cover subtitle still mentioned **v8**, and its Methods could be read as claiming complete executable reproduction of the original software environment. Private v10 corrects the working version and distinguishes verified archived solver-output reconstruction from an **unavailable exact historical dependency lockfile**.

Private v10 also explicitly states the code-level assumed heat-load formula (30°C threshold, +4°C and coefficient .012/°C), 30% synthetic wind shock, 3/12/25m/s proxy availability curve, source/physical limits and original PyPSA/HiGHS solver designation. These are methodological descriptions of already archived source code, not additional empirical observations.

## Scientific admission status

Numerical reconstruction of original conditional model outputs: **verified**. Historical physical availability and actual 2024 generator roster: **not verified**. Actual BA intertie rating: **not verified**. Measured reversible PG7–PG12 pumping and storage SOC: **not verified**. Exact historic solver environment/bitwise replay: **not verified**. Observed grid EENS, LOLE or climate-attributable blackouts: **not established**.

This report contains public reproducibility metadata only. The private v10 manuscript and original potentially third-party source data are **not** uploaded to this repository.
