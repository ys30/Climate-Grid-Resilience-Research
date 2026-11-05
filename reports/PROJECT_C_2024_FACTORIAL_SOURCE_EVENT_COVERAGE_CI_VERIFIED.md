# July 2024 four-BA factorial: verified event coverage and multi-event admission

**Original-source CI verification:** [42103046067](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42103046067) **SUCCESS**, [event-count manifest artifact 13450228174](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42103046067/artifacts/13450228174). Audit commit `c7e5169030eed5af529ab432d4836357111db639`. The workflow re-downloads the existing source matched EIA930/ERA5 artifact **41102363806** and source EIA860 partial-fleet inventory artifact **41107169962**, runs strict source-timestamp/BA-cohort tests, and verifies the source hour count from the original data, **not merely from the older manuscript**.

## Confirmed source event coverage

| Quantity | Verified count |
|---|---:|
| Balancing authorities | 4: CISO, AZPS, BPAT, SRP |
| BA × hour records per demand/weather input | **672** |
| DISTINCT observed hourly timestamps | **168** |
| Contiguous nonoverlapping 168-hour windows actually available | **1** |
| Four complete independent 168h events from these same archived inputs? | **NO** |
| New year or seasonal independent event from this archive | **NO** |

**Important:** 672 BA-hour rows do **not** constitute 672 distinct observed hours; the first July event is already exactly 168 UTC hours across four BAs. A purported 4×168-hour extension constructed by cutting the 672 BA rows into four blocks would be a serious pseudo-replication error. The new source-admission module and tests reject it. This is distinct from the separate SRP-only January 744-hour scenario experiment, which has a different fleet/supply parameterization and **cannot** simply be treated as a matched replicate of the July 4-BA partial-fleet design.

## Factorial science already exists; correct baseline

The earlier [2024 July four-case observed-input screening](../docs/results/july2024_factorial_interaction_by_ba.md) had the four matched scenarios at fixed input window and fixed hypothetical network assumptions:

| Scenario | Modeled shortage MWh (uncalibrated) |
|---|---:|
| Baseline | 271,730.350 |
| Heat-only | 397,760.110 |
| Wind-only | 391,034.532 |
| Heat+wind | 540,371.228 |

Modeled factorial second difference = **+23,306.936668 MWh**. The 168h baseline simulated shortage is itself **271,730 MWh**, an indication that the partial gas/wind proxy fleet is highly incomplete, not a plausible estimate of real historical outage energy. All results are scenario-response diagnostics conditional on *assumed* heat load response, wind penalty, incomplete fleet, and hypothetical BA links. This interaction was already computed; the missing science is replicated real windows, stronger source-fleet completeness and constraints.

The [paired isolated/hypothetical links](../docs/results/july2024_paired_network_factorial_interaction.md) and [5/10/20% assumed link sensitivity](../docs/results/july2024_network_rating_factorial_sensitivity.md) are also **already complete** and must not be listed as missing.

## What the source gate changes in the research progress

- **Completed / verified:** four scenarios, 168h observed-source single event, 4 BA, explicit interaction, isolated-versus-hypothetical-link contrast and link-rating structural sensitivity, plus independent SRP Jan single-BA hypothetical factorial.
- **Not completed:** second or later independent 168h 4-BA observed source windows, identical-cross-event four-case re-simulation, full BA generator availability and storage/intertie physics, historical shortfall/outage calibration, and publication-quality uncertainty across independent events.
- **Next acquisition requirement:** obtain additional matched official EIA930 hourly demand and ERA5 BA weather for **distinct second/third/fourth real 168h event windows**, with independently verified source timestamps and no fabricated or copied hours. Freeze the same EIA860 partial roster, assumed climate response, hypothetical intertie parameters, time-of-day convention and optimization treatment across those windows before comparing factorial interactions. Source data would still be incomplete for physical calibration.
- **Publication readiness:** the V2 plan and legacy Results v0.1 are not a complete updated manuscript. The independent-event replication gate is **not satisfied** and no cross-event uncertainty can be claimed.

Code: [source-coverage gate](../src/grid_resilience/srp_2024_factorial_multiwindow_admission.py), [tests](../tests/test_srp_2024_factorial_multiwindow_admission.py), [CI workflow](../.github/workflows/srp-factorial-independent-event-source-gate.yml).
