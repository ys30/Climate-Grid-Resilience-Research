# Project C — BPAT July 2024 EIA923 Page 1 HY/PS hydro reporting evidence and partial PyPSA supply limitations

**Real official-source CI:** [42117378382](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42117378382) **SUCCESS**, original source CSV/JSON [artifact 13456577759](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42117378382/artifacts/13456577759). EIA923 official Page 1 HY/PS monthly source archive [41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401), EIA930 official 2024 July BA total source archive [41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594), and EIA860 partial gas/wind model capacity from the audited four-week PyPSA source inputs [42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361). Source changes and tests are versioned in the links below.

## Verified July 2024 BPAT observational energy sources

| Original-source measurement | Original observed value |
|---|---:|
| EIA923 Page 1 conventional HY July reported net MWh | **5,989,476** |
| HY Page 1 BPAT plant-month source records | **55** |
| EIA923 Page 1 pumped storage PS July signed net MWh | **+293** |
| PS Page 1 BPAT plant-month source records | **1** |
| EIA923 July BPAT Page1 HY+PS signed net MWh | **5,989,769** |
| EIA930 BPAT BA reported July total net-generation MWh, full UTC month | **7,709,322** |
| EIA930 official July BA-total source coverage | **744/744 UTC start-hours** |
| BPAT original model partial EIA860 gas nameplate MW | **3,177.9** |
| BPAT original model partial EIA860 wind nameplate MW | **3,617.1** |
| BPAT model partial gas+wind proxy nameplate MW | **6,795.0** |

**Critical missing field**: the independently restored **official EIA930 BALANCE 2024 July** artifact has `Net Generation (MW)` BA total, but **does NOT contain** `Net Generation (MW) from Hydropower and Pumped Storage`. The strict first attempt to calculate the hydro-to-total contribution failed this source schema gate, and the corrected workflow **preserves NULL / unavailable** for this EIA930 fuel group, hydro-group share, cross-source hydro-group residual, and HY/PS ratio. The final CI intentionally admits source-level monthly HY/PS evidence without manufacturing an EIA930 fuel-group estimate from BA totals or model shortfalls.

These measured energy magnitudes from distinct reporting scopes **must not** be divided into a calibrated fuel share or interpreted as identical geographic/electrical generation boundaries. The annual EIA923 Page1 plant-reported BA assignments and EIA930 operational BA reporting categories need independent coverage validation; not all reported hydro can be assumed deliverable hourly to the model loads. In particular **PS signed net MWh is NOT discharge or gross turbine electricity**, and actual pumping schedules/energy losses are not observed in this monthly aggregate.

## Implications for the original four-week July PyPSA screening model

The original 2024 July four-BA PyPSA factorial relies only on an **EIA860 partial gas+wind proxy**, weather-derived wind availability and hypothetical BA links. It has no physically admitted hydro reservoir energy budget or actual hydro hourly dispatch, no pumped storage state of charge and no independently calibrated cross-BA transmission limits. In the prior [official EIA930 partial fleet net-generation audit](PROJECT_C_JULY2024_PARTIAL_FLEET_OFFICIAL_NETGEN_COVERAGE_CI_VERIFIED.md), BPAT original BA total reported net generation **exceeded the partial gas+wind nameplate in all 672 of 672 observed July 1–28 UTC hours**, while the *isolated partial model* produced approximately **795,414 MWh of baseline modeled unserved energy** over the same four weeks. The new independent EIA923 monthly HY evidence makes it much clearer that a **substantial observed resource category was excluded from the model**, not that true BPAT electricity shortage was measured.

**Important attribution limit:** This does not prove by how much a properly constrained real BPAT hydro resource would reduce model shortages, because its hourly firm power, dispatch rights, system import/export interactions, energy budget, in-month storage reservoir dynamics, and compatible BA/geographic boundaries are not validated. One cannot add 5,989,769 MWh uniformly, convert signed monthly HY/PS net to a 744-hour firm capacity, or use EIA923 monthly generation directly as PyPSA generator availability.

## Updated evidence gate

- **Verified now:** official BPAT July Page1 HY 55 plant-month source records, Page1 PS 1 record, distinct signed net monthly MWh, and complete original EIA930 BA total July net generation (744h); original partial EIA860 gas/wind capacities fixed; strict fail-closed missing EIA930 hydro-fuel-group field, not falsely treated as zero.
- **Still missing:** a verified July EIA930 fuel-specific generation file (separate from BALANCE) if cross-source HY/PS mixed-category accounting is desired; full year-scoped EIA860 BPAT HY/PS generator-by-plant source roster/BA identity, plant-level monthly energy completeness and per-unit reporting overlap; hourly operating water/energy constraints; storage SOC/efficiency; credible real intertie ratings; resource-calibrated PyPSA reruns.
- **Next highest priority:** archive and admit actual EIA860 BPAT nonstorage hydro nameplate separately from pumped storage with generator/BA status and stable seasonal availability assumptions, then build **explicit upper/lower sensitivity scenarios**, not a calibrated hourly hydro response. Distinguish monthly EIA923 measured HY MWh from assumed scenario energy budgets.
- **Manuscript:** this evidence supports a Results subsection about *structural technology omission and historical source coverage limitations*, and Discussion's restriction that modeled heat×wind shortage interactions are stylized responses rather than actual observed electricity losses.

**Reproducibility:** [source cross-report script](../src/grid_resilience/bpat_july2024_hydro_cross_source_scope.py), [missingness and identity tests](../tests/test_bpat_july2024_hydro_cross_source_scope.py), [GitHub Actions source workflow](../.github/workflows/bpat-july2024-hydro-source-scope.yml).

**Historical observed EENS certified: NO. Full BA-generator fleet certified: NO. Hydro hour-by-hour firm availability certified: NO.**
