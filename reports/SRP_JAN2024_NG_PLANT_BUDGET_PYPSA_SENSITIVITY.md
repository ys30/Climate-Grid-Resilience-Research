# SRP Jan 2024: isolated NG plant monthly-energy budget PyPSA sensitivity

**Verified full-month optimized workflow:** [SRP NG monthly plant budget PyPSA sensitivity, run 41754035735](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41754035735), [Research methods CI 41754035422](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41754035422), source commit `958591698dea4514c59cd7e3dd9b8ad224fe498f`. Both completed successfully. [Artifact 13286483558](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41754035735/artifacts/13286483558) contains 10 source and scenario evidence files, including `ng_portfolio_budget_comparison.csv`, `ng_plant_budget_scenarios.csv`, `ng_portfolio_budget_manifest.json`, and official EIA archive SHA-256 provenance.

## Motivation and modeling boundary

Modeling question: *What changes when a gas-only plant portfolio's hypothetical monthly energy budget is tightened while the official SRP January 2024 hourly demand and reported net-interchange schedules remain fixed?*

EIA-923 Page1 NG source: 24 original rows, 11 plants, total **1,902,868.304 MWh**. Candidate EIA-860 2024 plant-BA nameplate, deduplicated by generator identity within each plant: **8,342.3 MW**. Every plant passes the necessary January 744-hour nameplate energy upper-bound check. **These are annual nameplate candidate capacities and cross-source monthly energy observations, not independent hourly generator availability or dispatch rights.**

PyPSA represents 11 standalone NG plant units using candidate nameplate MW as `p_nom`. The optional `e_sum_max` constraint is a plant-specific **assumed upper bound**, never a forced minimum or equality target. The cases are (a) no monthly energy cap, (b) cap at 1.0× Page1 plant-reported NG MWh, and (c) cap at 0.75× Page1 NG MWh. The last factor is a sensitivity assumption; its near numerical agreement with the EIA-930 gas category is *not* a validated cross-source calibration.

The bus includes official hourly SRP demand, fixed reported export sinks and import injections, an artificial positive-cost portfolio-gap generator, and an explicit import-spill sink. It **does not** include the rest of SRP's nuclear, coal, solar, wind, hydro or storage supply, physical transmission, unit commitment, start-up fuel, generation ownership, hour-specific forced outages or intertie transfer constraints.

## Successful 744-hour solver results

| NG-only scenario | NG generation (MWh) | Artificial portfolio gap (MWh) | Maximum hourly bus balance residual |
|---|---:|---:|---:|
| Unlimited monthly NG budget, nameplate bound only | 5,098,932.000 | 0.000 | <1e-9 MW |
| NG budget cap 1.00× EIA-923 Page1 source MWh | 1,902,868.304 | 3,196,063.696 | <1e-9 MW |
| NG budget cap 0.75× EIA-923 Page1 source MWh | 1,427,151.228 | 3,671,780.772 | <1e-9 MW |

Fixed observed domestic demand = **2,455,626 MWh**; fixed observed export sink = **2,643,306 MWh**; total imposed generation requirement = **5,098,932 MWh**. This is 5 MWh higher than the EIA-930 directly reported generation sum of 5,098,927 MWh due to the raw source's summed 5 MWh energy-balance rounding residual; the model is balanced against the *imposed load/export schedule* and not forced to match source generation. The successful run has no observed imports or modeled disposal in this monthly scope. Hourly optimization balance residual is ≤ 9.1e-13 MW.

The modeled portfolio-gap difference from unlimited to 1.0× is **3,196,063.696 MWh**, and from 1.0× to 0.75× is **475,717.076 MWh**. These are changes in the artificial NG-only coverage requirement, **not** blackout magnitudes, grid reliability, or measured shortfalls.

## Interpretation, limitations and next steps

1. In an NG-only single-bus model, removing its monthly energy constraint permits gas to serve the entire artificial 5.099 TWh requirement; this demonstrates optimizer behavior, not historical gas supply.
2. Imposing the source-conditioned Page1 monthly bounds strongly limits gas output even though the candidate plant nameplate capacities are ample; these bounds remain assumptions because Page1 plant fuel generation is not certified as SRP BA-dispatch availability.
3. Increasingly tight budgets produce nondecreasing simulated portfolio gap, and all three scenarios pass plant budget checks and hourly/monthly energy conservation.
4. The difference between EIA-923 Page1 NG (1,902,868.304 MWh) and EIA-930 SRP Natural Gas (1,425,116 MWh) is **477,752.304 MWh** and remains a reporting-scope attribution issue. The 0.75× case must not be presented as an EIA-930 calibration even though its total is close (1,427,151.228 versus 1,425,116 MWh).
5. Next analytical step: introduce other technologies only after confirming non-overlapping BA supply scopes and carrying resource-specific monthly limits and hourly availability with explicit uncertainty. Do not replace already modeled NG assets by adding an overlapping generator population.

**Historical calibration certified: FALSE. Observed unserved energy inferred: FALSE. Physical BA fleet coverage certified: FALSE. Source-observation-conditioned sensitivity only.**
