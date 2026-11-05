# Project C — Source-verified continuous 672-hour BPAT hypothetical HY PyPSA power-energy dispatch, 2024 July

**Original optimization:** [GitHub Actions 42122153716](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42122153716) **SUCCESS**, [solved hourly 16 scenario model results artifact 13460145860](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42122153716/artifacts/13460145860). **Reproducibility and coefficient accounting:** [GitHub Actions 42122742127](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42122742127) **SUCCESS**, [16 aggregated outcomes, 4 factorial comparisons and 64 exact original baseline row matches, artifact 13458348295](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42122742127/artifacts/13458348295).

## Source cohort and modeled intervention

Uses the **actual official EIA930 demand and ERA5 site weather inputs** of 2024 July 1–28 for four BAs, as separately archived in [the original corrected four-week CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361). All 672 unique source UTC hours and 2,688 four-BA hour records are required without filling. The original annual **partial gas/wind** 2024 EIA860 proxy fleet and fixed marginal costs remain unchanged; BAs are **isolated** (no assumed intertie transfers). Existing climate response assumptions are the same as the previous four-scenario factorial: +4°C added to the temperature-driven *hypothetical demand stress*, 30% assumed wind ceiling derating, and four matched cases baseline/heat-only/wind-only/heat+wind.

The new non-storage BPAT HY source is **not asserted to exist in the EIA860 verified installed capacity roster**. It is a conditional incremental model resource with a chosen **500 or 2,000 MW power limit** and an explicitly assumed **598,947.6 or 1,497,369 MWh total 28-day energy limit**, scaled at 10% or 25% of **5,989,476 MWh of real July EIA923 Page1 BPAT conventional HY monthly observed net generation** ([source verification 42117378382](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42117378382)). The 31-day recorded monthly net MWh value is **only a scale reference**, not measured water availability to this 28-day model, not a valid new generator fleet addition, not a reliable operating hydro schedule and not a physically calibrated dispatch authorization. Pumped storage PS, reservoir inflows, real import/export rights and hydrologic flow constraints remain excluded.

**Important intertemporal treatment:** The model optimizes **one contiguous 672-hour horizon**. An energy Store starts with the one assumed 28-day budget, cannot refill (no upstream charging link or water inflow), cannot become negative and does not reset on 7-day boundaries. A 100%-efficient Link from the water-energy bus to BPAT caps hourly modeled HY production at the assumed power limit. This is a deliberately simplified **physically constrained *within the model*** source scenario, not a physical calibrated hydro operating model. Source-hour production and Store balance are checked hourly, and total 28-day HY production is checked against the *single* resource budget.

## Actual solved results

All MWh in the original **four-BA isolated partial-fleet** PyPSA model across all four weeks. The control shortage comprises all 4 BA, not BPAT alone.

| HY intervention assumption | Baseline modeled shortage (MWh) | Hypothetically dispatched HY (MWh) | Reduction in modeled shortage vs no-HY (MWh) | Difference: HY dispatched minus avoided model shortage (MWh) |
|---|---:|---:|---:|---:|
| Original partial-fleet no HY | **2,107,245** | 0 | 0 | 0 |
| 500 MW, 598,947.6 MWh assumed budget | **1,900,047** | 336,000 | **207,198.466** | 128,801.534 |
| 2,000 MW, 598,947.6 MWh assumed budget | **1,508,297** | 598,947.6 | **598,947.600** | ~0 |
| 2,000 MW, 1,497,369 MWh assumed budget | **1,505,754** | 1,344,000 | **601,490.809** | 742,509.191 |

Each production and modeled-shortage-reduction quantity is conditional on **the original incomplete gas+wind supply model, assumed marginal costs, all-BAs-isolated network and hypothetical HY resource**, not an empirical estimate of true added hydro energy or historical saved outages. The wide separation in the 2,000-MW/high-budget case illustrates temporal dispatch displacement: increasing modeled HY energy production need not translate into an equal amount of modeled shortage reduction, even if the source generator output is optimized.

### Four-scenario source-hypothesis nonadditivity changes with HY assumptions

The 28-day four-case compound modeled-shortage second difference is `interaction = modeled_shortage(heat_wind) − modeled_shortage(heat_only) − modeled_shortage(wind_only) + modeled_shortage(baseline)`.

| Incremental HY assumption | 28-day modeled heat×wind factorial second difference (MWh) |
|---|---:|
| No HY | **+53,241.973** |
| 500 MW, 598,947.6 MWh | **+54,918.341** |
| 2,000 MW, 598,947.6 MWh | **+53,241.973** |
| 2,000 MW, 1,497,369 MWh | **+76,203.357** |

This is especially valuable for the project's methodological argument: **a modeled compound weather-stress interaction depends not only on climate inputs or transmission assumptions but also on the hypothetical energy/power constraints of an omitted resource category**. Its magnitude cannot be extrapolated to real BPAT reliability or an observed heat+wind causal interaction.

### Critical exact-original-source replay check

The new zero-HY control at each original week, BA and climate scenario is reconciled independently against the previously source-verified four-week 168h PyPSA isolated experiments. **64/64 comparable original-week BA scenario records match with maximum absolute modeled unserved-energy error exactly 0.000000 MWh**. Reusing one 672h source horizon therefore preserved the no-HY original-week cases and did **not** silently reset hydro energy budgets (which did not exist in the control). This constitutes reproducibility of the model—not physical calibration.

## Interpretation / remaining gates

**Already complete:** exact full 672h official source coverage and corrected UTC start-hour use; 16 genuine PyPSA solves; per-hour HY production and energy Store validations; original 64-row replay; explicit original month HY source scale; four-case factorial differences recalculated under each hypothetical resource constraint.

**Not verified and not inferred:** actual BPAT 2024 EIA860 conventional hydro **generator nameplate and grid/BA assignment**, HY production time series, reservoir operating restrictions, inter-BA flow constraints, PS pumping/discharge power, PS roundtrip efficiency and SOC, EIA923-to-EIA930 BA energy accounting equivalence, an independent season/year, or real observed EENS/LOLE/physical outages. The original partial-fleet baseline simulated shortage remains artificially high and should not be interpreted as measured lost load.

**Next experiment:** independently verify EIA860 BPAT HY generator and PS storage generator rosters, then run BPAT HY power ceilings derived from named source records with an assumed water budget and PS as a separate finite-energy **Store + charge/discharge Links** with explicit SOC/efficiency. Add real source/hourly capacity gates and bounded stress sensitivity. Do not claim historical calibration until physical model completeness and measured source-hour generator/BA consistency are established.

**Code:** [672h non-cyclic hydro PyPSA solver](../src/grid_resilience/bpat_july2024_intertemporal_hy_pypsa.py), [solver tests](../tests/test_bpat_july2024_intertemporal_hy_pypsa.py), [model/source reconciliation](../src/grid_resilience/bpat_july2024_hy_672h_model_reconciliation.py), [reconciliation tests](../tests/test_bpat_july2024_hy_672h_model_reconciliation.py), [solver workflow](../.github/workflows/bpat-july2024-672h-hydro-pypsa.yml), [reconciliation workflow](../.github/workflows/bpat-july2024-hy-672h-model-reconciliation.yml).

**No historical reliability calibration certified.** This is a controlled model intervention, not a measured generator or an actual avoided power outage.
