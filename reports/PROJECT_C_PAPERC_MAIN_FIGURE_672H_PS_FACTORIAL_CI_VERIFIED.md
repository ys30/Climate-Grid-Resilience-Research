# Paper C — 672-hour Grand Coulee factorial sensitivity, source-audited main figure

**CI-verified figure:** [successful figure workflow 42413252700](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42413252700) · [download PNG, PDF and audited table artifact 13590706258](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42413252700/artifacts/13590706258) · [plotting code](../src/grid_resilience/paperc_ps_factorial_figure.py).

## Figure content and conditional identification

Panel A: four matched hazard scenarios (baseline, heat only, wind only, heat + wind), each over the same 672-hour July 1–28, 2024 source-input window, for assumed 0%, 25%, 50%, 100% availability of the 2024 EIA-860 314 MW Grand Coulee PS generator nameplate. The nonzero assumptions use 4 hours of usable energy and 80% roundtrip efficiency; the model also assumes an incremental 2,000 MW HY resource with a **single, hypothetical 598,947.6 MWh** 28-day energy budget. Results are four isolated BA sums with a partial generation fleet, **not physical historical grid shortage or EENS**.

Panel B: modeled second difference (heat + wind) − (heat only) − (wind only) + baseline, computed separately under every matched hypothetical PS setting. The positive result is evidence of model-conditional nonadditivity **only**; one 28-day season cannot support causal identification or generalization to independent years.

The figure and companion numeric CSV were generated **directly** from [successful 16 × 672h model-plus-independent-SOC audit run 42397840448](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42397840448), not transcribed from manually rounded logs. CI refuses missing/duplicate scenarios, nonfinite gaps, changed assumed power/energy fractions, missing positive SOC group audits, or assertions of calibrated grid reliability. It also verifies the model's full-PS baseline reduction relative to no-PS equals **27,641.637 MWh** to rounding tolerance.

## Suggested journal caption

**Figure X. Conditional power-system screening response to compound heat and wind perturbations under hypothetical pumped-storage availability.** (a) Total optimized 672-hour model supply gap in four isolated balancing-authority representations as the assumed available fraction of the six Grand Coulee reversible generating units' 314 MW nameplate changes, holding the original July source-input cohort and other model assumptions fixed. (b) Nonadditive heat–wind factorial contrast under each availability setting. Nonzero storage settings additionally assume 4-hour energy duration and 80% roundtrip efficiency; hydropower, generator fleet and transfer constraints are not historically calibrated. These deterministic results are neither observed outages nor probabilistic expected energy not served.

## Result distinctions required in the manuscript

- **Observed:** 2024 USACE 31-day whole-project pumping electricity and independent lake-level record; the station-wide meter is not PG7–PG12-only charging.
- **Modeled:** four-BA optimized shortfall, factorial interactions and assumed PS access effects.
- **Verified method:** independent numerical SOC and HY budget consistency over all 16 × 672 hourly trajectories.
- **Not identified:** actual PS unit charging/discharging schedule or efficiency, water-energy conversion, observed irrigation share, full BA fleet ratings, actual transfer limits, actual outages or independent-period validation.

Keep the observed pump-energy and reservoir-level figures as supplementary source-descriptive evidence. Do not overlay the site-wide USACE meter with simulated PS dispatch as if they were the same equipment, or label the hypothetical capacity axis as measured irrigation-access fractions.
