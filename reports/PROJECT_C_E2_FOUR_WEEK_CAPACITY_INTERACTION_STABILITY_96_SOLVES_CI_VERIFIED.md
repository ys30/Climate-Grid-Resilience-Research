# Paper C E2 — FOUR-WEEK capacity interaction stability (96 PyPSA solves, CI VERIFIED; scope frozen)

**CI success:** [run 42923134596](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42923134596), [original 120-contrast result CSVs, capacity input files and scope artifact 13812172591](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42923134596/artifacts/13812172591). This replaces *only the scope* of the earlier successfully CI-tested 48-solve Week 1/3 subset; the earlier output is retained for traceability. All four fixed, non-overlapping, adjacent 2024 July 168h weeks (1–7, 8–14, 15–21, 22–28 UTC), 4 BAs (AZPS/BPAT/CISO/SRP), unchanged source EIA930 demand, point-proxy ERA5 and 2024 frozen *partial* EIA860 source, fixed synthetic three-edge 10%-of-smaller-endpoint Week 1 peak interties (or isolated), plus fixed +4°C threshold heat and 30% synthetic wind availability shock. Incremental hypothetical perfectly firm generic thermal proxy MW equals 0%, 25%, or 50% of each BA's original Week 1 peak demand, **not actual installed or available capacity**.

3 fixed capacity cases × 4 weeks × 2 networks × 4 factorial climate arms = **96 successful optimal PyPSA solves** generating 384 BA-arm records and 120 BA+SYSTEM factorial second-difference rows. Source gate: the zero-addition arm matches original July 2024 4-week BA/system model summary to maximum **5.82e-11 MWh** numerical arithmetic deviation, far tighter than the 0.001 MWh admission bound. The original source model results were independently archived under [CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361).

## Complete modeled SYSTEM heat×wind factorial second difference (MWh)

| Source week (2024) | Network | 0% hypothetical extra firm | 25% hypothetical extra firm | 50% hypothetical extra firm |
|---|---|---:|---:|---:|
| 1 (July 1–7) | Isolated | +14,630.333329 | +5,203.677739 | +1,205.833802 |
| 1 | Frozen illustrative links | +22,515.997901 | +1,473.655651 | +45.244849 |
| 2 (July 8–14) | Isolated | +15,338.707755 | +14,548.089529 | +499.704411 |
| 2 | Frozen illustrative links | +16,204.694604 | **+18,602.414792** | 0.000000 |
| 3 (July 15–21) | Isolated | +14,697.752803 | +10,575.038076 | +1,879.050891 |
| 3 | Frozen illustrative links | +25,211.030026 | +3,291.243059 | +589.437873 |
| 4 (July 22–28) | Isolated | +8,575.179452 | +2,593.085860 | 0.000000 |
| 4 | Frozen illustrative links | +15,177.069664 | +2,013.432631 | 0.000000 |

**Nonmonotonic interaction:** the Week 2 links model **increases by about 14.80%** (16,204.695 → 18,602.415 MWh) under the +25% assumed firm MW setting, *despite a sharp drop in the model baseline gap* (480,492.999665 → 13,630.427429 MWh). This does not contradict decreased supply shortfall: the factorial **second difference** is a different, nonlinear contrast of four outcomes.

BA-local modeled second-difference observations with negative values materially beyond ±0.001 MWh numerical-roundoff tolerance:

| Capacity assumption | Network | Material negative local BA cases |
|---|---|---|
| +0% | Isolated | None |
| +0% | Frozen links | Week 1 CISO (−5,763.712); Week 3 BPAT (−5,918.429); Week 4 AZPS (−3,663.801) |
| +25% | Isolated | None |
| +25% | Frozen links | Week 2 CISO (−903.583) |
| +50% | Either | None |

Tiny floating-point signed values below tolerance are treated as numerical zero, not as negative physical effects. These 4 weeks are **adjacent and not independent weather-event samples**; no inferential p-value is assigned.

## Why this settles the E2 question — and what it does not settle

**The original model interaction amplitude and BA-local sign are not robust to the predeclared resource-capacity assumption.** Replacing the original generic thermal proxy with perfectly firm *synthetic* BA peak additions can sharply shrink, eliminate, or in one case increase system-level interaction. In some arms the baseline screening-model shortage becomes essentially zero while a factorial interaction remains positive in another modeled scenario: a result of the nonlinear optimized counterfactual contrasts, not historical EENS.

This is **not** evidence that an actual July 2024 Western grid outage occurred, that 25% or 50% real additional nameplate is needed, that EIA860 excluded storage is continuously dispatchable, or that the assumed transmission links reproduce actual BA connectivity. The [E1 frozen 3,268-generator source audit](PROJECT_C_E1_FINAL_3268_GENERATOR_KEYED_643_EXCLUSIONS_AND_BATTERY_CORRECTION_CI_VERIFIED.md) explicitly establishes why annual nameplate and EIA923-selected proxy populations are different and why hourly available capacity is unidentified.

**E2 declared four-week 0/25/50% bounded screening experiment: COMPLETE.** Further invented capacity fraction grids, more weeks or arbitrary network ratings are not justified for the frozen manuscript strategy. **E3 still open:** use one distinct-year time window under an identical *explicitly frozen surrogate resource specification*, with a sourced year-specific roster diagnostic retained separately. Do not reuse 2024 Week 1 as an independent validation; do not pretend E3 addresses actual physical intertie/operational calibration.

Paper placement: replace the earlier selected two-week sensitivity as the primary result with the complete 4-week sensitivity. The Week 2 +25% counterexample should be made prominent in Results/Discussion, not silently summarized as a monotone declining trend. The original primary CI figures remain valid **only for the base +0% model arm**.
