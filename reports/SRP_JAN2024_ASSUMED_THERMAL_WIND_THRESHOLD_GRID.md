# SRP Jan 2024: 16-cell synthetic thermal × wind availability threshold grid

**Verified real-source / synthetic-availability optimization:** successful [SRP PyPSA workflow 41763168397](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763168397) and [Research Methods CI 41763168384](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763168384), code commit `7342fe5568a60326e2882fda24d4d7ade2708233`. Artifact: [13290919074](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41763168397/artifacts/13290919074) (29 files). Data products: `assumed_threshold_grid/thermal_wind_threshold_grid.csv`, `thermal_no_gap_grid_boundary.csv`, `thermal_wind_discrete_interactions.csv`, `threshold_grid_manifest.json`.

## Input independence and scope

Official EIA-930 2024-01 **hourly BA demand and net interchange**, plus 2024 EIA-860 annual **Plant BA operable nameplate** supply inventory. The primary fuel and prime-mover crosswalk classifies gas, coal, nuclear, hydro, solar and wind; **97 included generator identities, 11 excluded**, with 15,576.5 MW classified nameplate. Pumped storage and batteries are excluded rather than misrepresented as freely dispatchable generation. Annual generator presence, actual dispatch rights and hourly availability are **not certified**.

Generation **is not replayed** from EIA-930; EIA-923 fuel net-generation observations are not used to manufacture hourly resource availability. All profiles are synthetic: base gas/coal = 0.85, nuclear = 0.90, hydro = 0.50, wind = 0.35; solar uses an uncalibrated assumed daylight sine profile. The first grid dimension multiplies **gas, coal and nuclear together** by {0, 0.25, 0.50, 1.00}, while the second multiplies wind by {0, 0.50, 0.75, 1.00}. A zero thermal factor is an intentionally extreme stress, **not an observed or plausible simultaneous outage**.

No storage SOC, line-flow topology, hourly ramping, unit commitment, heat-response fit, meteorological predictors, or calibrated forced-outage physics is modeled. The network is an isolated BA supply screen with exogenous observed net interchange.

## Confirmed 744-hour PyPSA + HiGHS artificial modeled coverage gaps

| Thermal (gas + coal + nuclear) multiplier | Wind ×0 | Wind ×0.50 | Wind ×0.75 | Wind ×1.00 |
|---:|---:|---:|---:|---:|
| 0.00 | 4,748,418 MWh | 4,718,993 MWh | 4,704,280 MWh | 4,689,568 MWh |
| 0.25 | 2,562,034 MWh | 2,532,608 MWh | 2,517,896 MWh | 2,503,183 MWh |
| 0.50 | 554,783 MWh | 533,792 MWh | 523,371 MWh | 512,969 MWh |
| 1.00 | 0 MWh | 0 MWh | 0 MWh | 0 MWh |

- **12 / 16** grid cells show a strictly positive artificial coverage gap; four have zero.
- The maximum gap is **4,748,418.012 MWh**, when thermal and wind multipliers are both zero. This is a designed stress-screen artifact, **not historical EENS or an observed blackout**.
- The grid-based minimum tested thermal multiplier with zero artificial gap is **1.00 for each tested wind factor**. This is not a continuously estimated critical threshold: the interval (0.50, 1.00) is untested, and the true conditional transition is not identified.
- Tightening either dimension never decreases the optimized artificial gap. Full-source workflow and all regression checks pass.
- Adjacent-cell interaction estimates are near zero in the most extreme [0, 0.25] thermal interval, and positive in several less extreme intervals (e.g., +20,990.66 MWh for thermal 0.50→1.00, wind 0→0.50). These are *finite differences of a synthetic optimization*, **not causal climate interactions**.

## Interpretation and next gate

The grid responds much more strongly to the *joint thermal-and-nuclear* factor than to wind, but the technologies were bundled and annual nameplate with uncalibrated assumed availability was used; **this does not isolate a realistic heat derating mechanism**. It may overstate what is operationally dispatchable, and the zero-gap baseline does not certify grid reliability.

**Next:** (1) refine 0.5–1.0 thermal multipliers while separately varying gas/coal and nuclear to avoid interpreting nuclear as a weather-derated thermal unit; (2) add only independently sourced and temporally matched weather-based availability profiles, retaining provenance; (3) compare a matched synthetic control and stress simulation with full fuel/technology and boundary uncertainty documented.

**Historical calibration: FALSE. Meteorological climate effect estimated: FALSE. Actual outages or EENS inferred: FALSE.**
