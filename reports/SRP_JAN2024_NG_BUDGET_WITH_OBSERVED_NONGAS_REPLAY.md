# SRP January 2024: NG budget sensitivity with observed non-gas EIA-930 replay

**Verified solver results:** successful [SRP PyPSA source-conditioned workflow 41755749615](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41755749615) and [Research Methods CI 41755749604](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41755749604), code commit `cf374893b38470b66063c6890dd75778f0b5166f`. [Artifact 13288032238](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41755749615/artifacts/13288032238) contains 17 evidence files, including all four 744-hour dispatch tables, scenario summaries, and original EIA source URL/SHA256 provenance.

## Motivation: controlling the fleet omission in the earlier NG-only portfolio experiment

The preceding *NG-only* model omitted all non-gas generation and reported a 100%-Page1-budget artificial coverage gap of **3,196,063.696 MWh**. This was **not** observed shortage. To isolate the effect of that omission, the present PyPSA comparison holds fixed the observed EIA-930 **signed hourly** generation from coal, nuclear, hydro/pumped storage, solar, wind, and other reported fuels, while optimizing the EIA-860 candidate NG plant portfolio subject to hypothetical month-long EIA-923 Page 1 energy caps.

The replayed non-NG fuel groups total **3,673,811 MWh** for the selected UTC month. EIA-930's reported gas generation is **1,425,116 MWh**, and its BA-wide reported generation is **5,098,927 MWh**. The two categories with no EIA-930 hourly reporting — **All Petroleum Products** and **Unknown Fuel Sources**, each blank in all 744 hours — remain explicitly flagged as **missing, not zero**. Numeric closure of reported categories is not proof of complete fuel reporting.

All scenarios hold EIA-930 reported domestic demand (**2,455,626 MWh**) and export sink (**2,643,306 MWh**) fixed, a combined **5,098,932 MWh** source-balance requirement. This exceeds the EIA-930 source generation sum by **5 MWh**, attributable to reported energy-balance rounding, and is not converted to physical outage. Imports and explicit disposal are zero in this selected source-month comparison.

## Four actual full-month PyPSA solves

| Hypothetical NG budget scenario | Optimized gas MWh | Fixed reported non-NG replay MWh | Artificial portfolio gap MWh | Maximum hourly bus residual MW |
|---|---:|---:|---:|---:|
| Unlimited month budget, nameplate only | 1,425,121.000 | 3,673,811 | 0 | 0 |
| NG plant-specific budgets = 100% Page1 NG MWh | 1,425,121.000 | 3,673,811 | 0 | 9.095e-13 |
| NG plant-specific budgets = 75% Page1 NG MWh | 1,425,121.000 | 3,673,811 | 0 | 9.095e-13 |
| NG plant-specific budgets = 50% Page1 NG MWh | 951,434.152 | 3,673,811 | **473,686.848** | 9.095e-13 |

Source NG Page 1 monthly total = **1,902,868.304 MWh** across 11 plants. The 75%-budget ceiling sums to **1,427,151.228 MWh**, just **2,030.228 MWh** above the modeled residual gas requirement of 1,425,121 MWh; the 50%-budget ceiling = **951,434.152 MWh**. Numerical zero gap in the 75% case is a finding of this optimized **assumption-driven** replay, not verification that plant-by-plant or network-constrained historical dispatch was feasible.

The earlier NG-only artificial gap at the 100%-budget case, 3,196,063.696 MWh, falls to **zero** when non-NG historical hourly generation is replayed; this is a direct demonstration of the effect of **omitting important resource technologies from the accounting boundary**. The 50%-budget scenario produces the expected additional **473,686.848 MWh artificial gap**, exactly equal to the reduction in potential NG budget below the imposed residual requirement when other factors are held fixed. It is **not** observed unserved electricity.

## Reproducibility and scientific limits

- Solver: PyPSA optimization with HiGHS, 744 UTC hourly snapshots, explicit hourly demand and export sinks, fixed observed non-gas signed replay, candidate NG nameplate capacity from 2024 EIA-860 Plant BA roster, and per-plant `e_sum_max` budgets derived from scale multipliers of source-reported EIA-923 Page1 NG monthly MWh.
- Source original reporting grain is retained; no split of repeated Page1 monthly records into individual generator MWh. Candidate generators are deduplicated for plant nameplate calculation.
- All optimization, monthly budget, monotonicity, and hourly energy-conservation tests passed in CI. Source and generated CSVs accompany the successful workflow artifact.
- This is **not** an independent observed-outcome test because actual EIA-930 non-gas generation is explicitly replayed; it can nearly close the EIA-930 reported source balance by construction. It does **not** estimate the effect of weather shocks or dynamically model nuclear, coal, hydro, wind, solar, storage or transmission dispatch availability.
- Actual oil/unknown fuel reporting remains missing, not assumed zero. EIA-923 versus EIA-930 NG boundary difference (+477,752.304 MWh) remains unresolved.
- Model output `artificial_portfolio_gap_mwh` is a *conditional portfolio accounting gap*, never real outages, EENS, LOLE, verified shortfalls, or proof of historical grid reliability.

**Next acceptance gate:** replace observed non-gas replay with independently specified technology capacity and hourly weather/availability bounds in matched counterfactual experiments. Keep the replay only as a documented accounting/coverage control, and quantify the impact of source/fleet boundary uncertainty separately from climatic drivers.

**Independent historical calibration: FALSE. Actual unserved electricity observed: FALSE. Climate-attributable outage inferred: FALSE.**
