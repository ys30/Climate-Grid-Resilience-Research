# Project C — 2024 July contiguous 672h BPAT HY and separate pumped-storage SOC PyPSA optimization (CI verified)

**Genuine PyPSA optimization CI:** [42124423838](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42124423838) **SUCCESS**, with [model output and hourly SOC / charging / discharge artifact 13459598468](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42124423838/artifacts/13459598468). Reuses the source-verified original July 2024 hour-start EIA930 four-BA demand, BA point ERA5 weather, partial 2024 EIA860 gas and wind proxy; 672 genuine UTC hours × AZPS, BPAT, CISO, SRP. Also holds the prior **hypothetical conventional HY resource** constant at 2,000 MW and a total nonreplenishing July 1–28 energy budget of 598,947.6 MWh, a **scenario assumption** anchored to 10% of the observed EIA923 2024 July BPAT HY Page1 5,989,476 MWh net generation (monthly reported production is not water availability).

## Pumped storage modeled separately, NOT extra free electricity

The PS scenario is an *independent*, hypothetical BPAT storage device, **not an EIA860-verified specific BPAT pumped-storage fleet**. A dedicated Store with initial energy = 0 and terminal energy = 0 is linked to the BPAT bus by **separate charging and discharging Links**. The Store energy ceiling, electrical charge/discharge MW and roundtrip efficiency are explicit scenario inputs; both links have one-way direction and the selected charge/discharge one-way efficiency = square root of assumed roundtrip efficiency. Conservation is tested at every hour:

`SOC(t)-SOC(t−1) = sqrt(eta_roundtrip)*charge_input_MW(t) − turbine_input_MW(t)`

`electrical_PS_discharge_MW(t) = sqrt(eta_roundtrip)*turbine_input_MW(t)`

with unit hours, no initial borrowed stored energy and **zero final SOC**; consequently total PS discharge = assumed roundtrip efficiency × total PS charge. **No actual historical PS pumping or discharging schedule is inferred from EIA923 signed net generation (which is not gross discharge).** The fixed thermal+wind baseline is the original incomplete source proxy; the BA network remains isolated and no physical intertie ratings were added.

Four resource scenarios × baseline/heat-only/wind-only/heat+wind = **16 solved 672h PyPSA optimizations**, all optimal and independently passing power, SOC, final energy, roundtrip-loss and source-hour checks.

## Real CI results: source-anchored but hypothetical storage scenarios

System (all four isolated BA) modeled baseline shortage, with identical conventional HY assumption in all rows:

| Additional BPAT PS configuration assumption | Four-BA baseline modeled shortage (MWh) | Reduction from no PS (MWh) | Actual optimized baseline PS charging MWh | Delivered baseline PS discharge MWh |
|---|---:|---:|---:|---:|
| No PS | **1,508,297** | 0 | 0 | 0 |
| 500 MW charge/discharge; 2,000 MWh SOC; 80% roundtrip | **1,467,088** | **41,209** | **62,189.616** | **49,751.693** |
| 1,000 MW charge/discharge; 4,000 MWh SOC; 80% roundtrip | **1,435,938** | **72,359** | **115,456.061** | **92,364.849** |
| 1,000 MW charge/discharge; 4,000 MWh SOC; 90% roundtrip | **1,432,648** | **75,649** | **103,786.725** | **93,408.053** |

In the two 1,000-MW sensitivity cases, increasing the assumed roundtrip efficiency from 80% to 90% reduces the modeled baseline shortage by approximately **3,290 MWh** on the same source input and partial fleet. Important: **generation delivered by PS and avoided modeled shortage differ** because storage can substitute for other electricity supply or shift energy through time. Modeling outputs are not observed historic saved losses.

The original partial-fleet no-PS model and all three PS settings use a **single contiguous 28-day horizon**, not four unrelated optimizations resetting state each week. PS source-generated output and starting/ending SOC are audited, while the conventional HY budget also remains noncyclic across all 672h.

## Four-factor compound stress and storage sensitivity

Re-solved climate scenarios use the original hypothetical +4°C heat load response and 30% wind derating assumptions, **not observed thermal derating factors**. Four-factor nonadditivity is the source-model second difference:

`U(heat_wind) − U(heat_only) − U(wind_only) + U(baseline)`.

Approximate system interactions read from the successful solver's full 16-row results:

| Hypothetical BPAT PS | Modeled system 28-day heat×wind second difference (MWh) |
|---|---:|
| No PS | **+53,242** |
| 500 MW / 2,000 MWh / 80% | **+58,401** |
| 1,000 MW / 4,000 MWh / 80% | **+67,802** |
| 1,000 MW / 4,000 MWh / 90% | **+70,558** |

Because the BA system is represented by a partial fleet, the storage and climate stress interactions are conditional **structural sensitivities**. In some stress scenarios PS charge/discharge is much less than in the baseline because the stylized supply has less spare energy to charge and/or competing dispatch impacts. Do not treat these as future electricity outage probabilities, EENS/LOLE or climate-driven causal electricity losses.

## Admission and evidence limitations

- **Verified:** original July EIA930 hour-start 672h × 4 BA source, original ERA5 point source, 2024 EIA860 partial gas/wind proxy cohort, observed EIA923 HY monthly energy *as a scale reference*, 16 optimal intertemporal PS/HY model solves, hourly SOC/power budget and zero-end SOC checks.
- **Not verified:** BPAT PS installed generator-by-generator 2024 EIA860 usable MWh, charge/discharge MW, exact plant BA identity, dispatch power conversion, real roundtrip efficiency, observed hourly PS charge/discharge, initial reservoir state, reservoir inflows, actual generator capacity availability, complete BA fuel fleet, actual intertie constraints, EIA923 vs EIA930 fuel reporting boundaries or physical outage observations.
- The original signed EIA923 BPAT PS net July amount **+293 MWh** must **not** be treated as the physical PS discharge energy, storage capacity MWh or calibration for these scenarios.
- The prior no-HY-to-HY source baseline already had an independently verified 64-row exact replay. This PS experiment keeps the **2,000 MW / 598,947.6 MWh** HY scenario constant in the PS-free control; a separate exact 64-record original HY-only comparison is provided by [CI workflow](../.github/workflows/bpat-july2024-ps-soc-hy-baseline-replay.yml), and [actual independent source replay CI 42124788065](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42124788065) **SUCCESS**, [artifact 13460875112](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42124788065/artifacts/13460875112), prove **64/64 matched BA × week × weather scenario hydro-only controls are numerically identical**, maximum absolute modeled shortage difference **0.000000 MWh**. This verifies the PS=0 intervention baseline but is not historical physical calibration.

## Manuscript contribution and next priority

These results materially extend Paper C from a loose **power/energy necessary-condition envelope** to **genuine optimally feasible intertemporal nonstorage HY and pumped-storage charge/discharge/SOC scenario modeling**. They show that the magnitude of modeled heat×wind second differences can depend on **storage power/energy/roundtrip efficiency**, all conditional on the same original weather and demand. Report scientifically as a structural scenario experiment with clear counterfactual and incomplete resource-scope limitations.

Next physically meaningful stage is **source-crosswalk and power/energy admission** for a BPAT PS generator roster from actual EIA860 2024 storage and HY/PS named plants; distinguish conventional HY (source net MWh) and PS signed net energy and enforce plant-to-BA/operability/date requirements before running physically parameterized models. The monthly PS net number does not identify charging duration or storage SOC. Cross-month/season event replication and generator/fuel/intertie calibration remain prerequisites for a full physical grid adequacy paper.

**Code and tests:** [672h HY/PS solver](../src/grid_resilience/bpat_july2024_hy_ps_soc_pypsa.py), [tests](../tests/test_bpat_july2024_hy_ps_soc_pypsa.py), [GitHub workflow](../.github/workflows/bpat-july2024-672h-ps-soc-pypsa.yml).

**No historical EENS, physical outages, causal heat derating or full-grid reliability calibration claimed.**
