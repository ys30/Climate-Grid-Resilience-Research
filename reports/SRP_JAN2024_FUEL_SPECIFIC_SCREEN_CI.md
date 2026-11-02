# SRP January 2024: illustrative fuel-specific screening run

**Verified CI:** [run 41408327414](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41408327414), commit `d939dc4de974e230482c420f2e5c614f544485fd`.

## What changed

Added `src/grid_resilience/fuel_specific_screen_assumptions.py` with explicitly **hypothetical** fuel-code dependent marginal costs and flat capacity multipliers. Unknown EIA-860 primary fuel codes fail closed. The inputs continue to use genuine EIA-930 SRP 2024-01 demand (744 UTC hours) and a **partial, identity-linked** subset of EIA-860 2024 nameplate capacities; no complete SRP fleet, verified renewable dispatch, transmission flows or outage schedules are claimed.

The CI run used the transformed supply scenario and independently checked its monthly power balance:

| Output | Actual CI |
|---|---:|
| Official SRP January demand | 2,455,626 MWh |
| Modeled supply with illustrative fuel-dependent costs and capacities | 2,455,626 MWh |
| Modeled unserved energy | 0 MWh |
| CI conclusion | Success |

**Strong limitation:** The fuel-specific 'capacity factor' constants were implemented as *flat hourly maximum-capacity multipliers*, **not** chronological wind/solar generation profiles, storage constraints or hydro energy budgets. Consequently, the scenario is strictly a computational sensitivity and dispatch-order test, **not historical generation calibration or a validated reliability assessment**.

Next gates: inspect the actual modeled generation by EIA-860 primary fuel, normalize EIA-923 actual observed technology coding and Page-1 vs Page-4 scope, then compare *matching* monthly observations. Include solar/wind hourly shape and time-varying gas availability rather than treating a monthly scalar as a physically valid profile. Holdout-year validation remains unperformed.

**Historical calibration certified: NO.**
