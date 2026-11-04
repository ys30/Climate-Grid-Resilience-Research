# SRP January 2024: decoupled fossil / nuclear / wind availability thresholds

**Verified full optimizer:** [SRP NG monthly plant budget PyPSA sensitivity run 41763931151](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763931151), successful [Research Methods CI 41763931178](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763931178), source commit `ba96e63e6c7dcc248b94c2676f17819e23c5364f`. Official GitHub [artifact 13291029676](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763931151/artifacts/13291029676) preserves 33 provenance, scenario and input-output evidence files, including `decoupled_grid/decoupled_factorial_grid.csv`, `decoupled_threshold_brackets.csv` and `decoupled_grid_manifest.json`.

## Scope

All 744 2024-01 UTC hours. EIA-930 hourly demand and reported net interchange are used as a fixed boundary. Annual EIA-860 SRP Plant BA operable generator nameplates are assigned to a single class by primary fuel plus prime mover (97 generator identities / 15,576.5 MW assigned; 11 / 1,287.1 MW excluded, including pumped storage and batteries). This **does not verify actual BA dispatch rights, generator hourly availability, historical month-specific dispatch or complete generation fleet coverage**.

Baseline availability values are **assumed**: NG/coal=0.85, nuclear=0.90, wind=0.35, hydro=0.50, and solar=an assumed local-daylight sine ×0.80. No historical EIA-930 fuel generation enters availability profiles, and no independent meteorology is supplied.

Three independent multipliers are now applied:
- **Fossil** NG+coal: 0.50, 0.625, 0.75, 0.875, 1.0.
- **Nuclear**: 0.75 or 1.0.
- **Wind**: 0 or 1.0.

For example, nuclear multiplier 0.75 means the assumed base nuclear 0.90 availability is reduced to 0.675, **not** that historical observed nuclear power fell to 75% of capacity.

## All 20 optimized results

Artificial portfolio gap in MWh, EIA-930 demand and interchange retained:

| Fossil factor | Nuclear .75 / wind 0 | Nuclear .75 / wind 1 | Nuclear 1 / wind 0 | Nuclear 1 / wind 1 |
|---:|---:|---:|---:|---:|
| 0.500 | 136,752.327 | 113,630.084 | 2,260.263 | 673.186 |
| 0.625 | 1,166.166 | 293.741 | 0 | 0 |
| 0.750 | 0 | 0 | 0 | 0 |
| 0.875 | 0 | 0 | 0 | 0 |
| 1.000 | 0 | 0 | 0 | 0 |

**Six of twenty** cells have positive artificial gap; maximum is **136,752.327 MWh** at fossil 0.5, nuclear 0.75, and wind 0. Every technology-availability monotonicity check passes.

The tested zero-gap bracket depends on nuclear assumptions:
- Nuclear 1.0: fossil threshold lies somewhere between **0.50 and 0.625** (both tested wind endpoints).
- Nuclear 0.75: fossil threshold lies somewhere between **0.625 and 0.75** (both tested wind endpoints).
- There is **no interpolation** or statistical estimate of a continuous critical transition.

## Critical comparison to the previous coupled model

The older 16-case synthetic experiment multiplied gas, coal and nuclear together by a common 0.50 factor, resulting in artificial gaps around 0.513–0.555 million MWh across wind settings. The present split model with fossil 0.50 **but nuclear at base 1.0** yields just **673.186 MWh** at wind multiplier 1.0, a substantially different stress response. This shows a **material model-design sensitivity to whether nuclear availability is coupled to fossil availability**.

Do not label a joint fossil/nuclear derating as an observed heat-response function. Nor should the smaller decoupled gap be taken as validation of real-world nuclear availability. Nuclear derating mechanisms, fuel-cycle constraints, planned outages, cooling water and temperature limitations require separate empirical basis and operating data.

## Scientific next steps

1. Add finer fossil multipliers within 0.50–0.625 for nuclear 1.0 and within 0.625–0.75 for nuclear 0.75, with independent weather-derived exposure only when available.
2. Vary gas and coal **separately**, and test baseline availability uncertainty. The current fossil factor groups them together for screening.
3. Keep observed non-gas EIA-930 replay only as an accounting comparison. Build independent hourly weather/plant-availability proxies with explicit location, time and source provenance; do not infer meteorology from EIA-930 generation.
4. Reconcile BA ownership and monthly EIA-923/EIA-930 generation populations before any real adequacy, measured outage, or causal climate claim.

**Historical grid calibration: NOT CERTIFIED. EENS or observed outages: NOT ESTIMATED. Climatic causal attribution: NOT ESTIMATED.**
