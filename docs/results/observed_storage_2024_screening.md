# July 2024 observed-input storage screening (four isolated BAs)

**Status:** CI-verified numerical screening, **not** a calibrated power-system reliability estimate.

**Reproducible workflow:** [2024 EIA-930/ERA5 observed-input storage CI](../../actions/workflows/observed-storage-2024-screening.yml). Checked successful run [#41283713592](../../actions/runs/41283713592), and methods CI [#41283713097](../../actions/runs/41283713097).

## Data/assumptions

- Real input time series: EIA-930 BA load and matched ERA5 meteorology, July 1–7, 2024 (168 hours × four BAs: AZPS, BPAT, CISO, SRP).
- EIA-860 2024 capacity sources: storage reported energy and maximum charge/discharge power; non-storage generation is a **partial, uncalibrated gas/wind supply proxy**, not the complete fleet.
- Isolated BA buses: **no** reconstructed physical interties, historical imports or transmission contingencies. Dispatch, initial SOC (50%) and charging/discharging efficiencies (90% each direction) are *assumptions*, not measurements.
- Four counterfactual conditions: baseline, heat-only, wind-only and compound heat/wind, using *hypothetical* weather-induced effects. Reported unserved energy is model residual shortage, **not observed customer outages**.

## Modelled unserved energy, compound heat-and-wind scenario

All values below are **simulated** MWh, not historical unserved energy.

| BA | No storage (MWh) | Storage (MWh) | Difference (MWh) |
|---|---:|---:|---:|
| AZPS | 207,290.816 | 200,982.551 | 6,308.265 |
| BPAT | 257,298.770 | 256,694.270 | 604.499 |
| CISO | 239,474.091 | 65,948.065 | 173,526.026 |
| SRP | 0.000 | 0.000 | 0.000 |

## Storage operations in the compound scenario

| BA | Initial SOC assumed (MWh) | Charge (MWh) | Discharge (MWh) | Final SOC (MWh) |
|---|---:|---:|---:|---:|
| AZPS | 1,071.3 | 6,597.648 | 6,308.265 | 0 |
| BPAT | 63.2 | 676.073 | 604.499 | 0 |
| CISO | 20,019.1 | 191,986.217 | 173,526.026 | 0 |
| SRP | 2,222.0 | 0.000 | 1,999.800 | 0 |

Conservation (1 h intervals): SOC[t] = SOC[t-1] + 0.9·charge[t] − discharge[t]/0.9. Maximum hourly numerical residual across the reported compound scenario is below 4 × 10⁻¹² MWh. Across all 16 BA × weather cases, no hourly simultaneous charging and discharging and no charging in a modeled-shortfall hour were detected (numerical activity threshold 1e-5 MW).

**Interpretation caution:** CISO's large modeled shortage reduction requires substantial recharge across the simulated week. The zero-overlap check only shows *internal feasibility in this simplified partial-fleet model*; it cannot establish that historic generation surplus, networks, market behavior, or battery control would have supported such charge quantities. All four compound-scenario batteries end the week depleted. The seven-day endpoint and assumed 50% initial SOC matter, so these numbers cannot be used as real outage mitigation or economic benefit estimates.

## Requirements before empirical research claims

1. Replace the partial gas/wind capacity proxy with comprehensive, audited hourly generation and resource availability, including hydro, solar, imports and other fuels.
2. Validate simulated BA energy balance and interchanges against EIA-930 historical observations; establish defensible transmission constraints or explicitly maintain isolated-BA scope.
3. Calibrate storage initial SOC/charging behavior to operational data where available and run boundary-condition/horizon sensitivity.
4. Independently test observed outages and weather-impact coefficients rather than treating assumed weather derates as measured events.

**No claim of completed historical calibration or observed reliability improvement is made here.**

## Initial SOC sensitivity: why CISO simulated shortages stay unchanged

In the 168-hour compound heat-and-wind screening, CISO's modeled unserved energy is 65,948.065 MWh at initial SOC 25%, 50% and 75%, despite distinct initial stored energy. The verified [SOC trajectory CI](../../actions/runs/41285126521) shows:

| Assumed initial SOC | CISO cumulative charging (MWh) | CISO cumulative discharge (MWh) | Final stored energy (MWh) |
|---|---:|---:|---:|
| 25% | 203,107.939 | 173,526.026 | 0 |
| 50% | 191,986.217 | 173,526.026 | 0 |
| 75% | 180,864.495 | 173,526.026 | 0 |

The charge difference of approximately 11,121.722 MWh per 25 percentage points in SOC, at an assumed 90% charging efficiency, replaces approximately 10,009.55 MWh of initial stored energy. Thus simulated delivery is unchanged because the optimization substitutes charging for initial energy; this is **a modeled flexibility effect**, not evidence that historical CISO had these charging opportunities. By contrast, AZPS and BPAT modeled shortfalls decrease by about 964.17 and 56.88 MWh, respectively, between initial SOC 25% and 75%, in each weather scenario. SRP has no modeled shortages in these cases.

The [cross-SOC energy substitution CI](../../actions/workflows/observed-storage-2024-screening.yml) now checks the complete SOC energy identity (initial energy, charging, discharging, final energy) for each of the 16 BA-by-weather groups. Actual historical storage dispatch, market and intertie constraints remain unverified. 

## Verified model-horizon and terminal-SOC boundary sensitivity

The [verified 72/120/168-hour workflow](../../actions/runs/41285666070) solved nested prefixes of the same compound heat-and-wind scenario, retaining the same assumed initial SOC and partial generation model. Modelled storage-related reductions in residual shortages (MWh) were:

| BA | 72 h | 120 h | 168 h |
|---|---:|---:|---:|
| AZPS | 2,975.660 | 4,843.724 | 6,308.265 |
| BPAT | 360.075 | 587.595 | 604.499 |
| CISO | 56,960.224 | 106,560.571 | 173,526.026 |
| SRP | 0 | 0 | 0 |

These are different-length *modelled* windows, not directly comparable historical outage events. CISO's average relief per modelled day increased across these windows, while BPAT's decreased. Do not extrapolate linearly across durations.

The [verified exact terminal-SOC workflow](../../actions/runs/41285853425) then solved the **same full 168-hour compound scenario** with an initial SOC assumption of 50% and alternative **exact** terminal SOC levels (not merely lower bounds):

| BA | Unrestricted terminal SOC, modelled shortage MWh | Exactly 25% terminal SOC | Exactly 50% terminal SOC |
|---|---:|---:|---:|
| AZPS | 200,982.551 | 201,464.636 | 201,946.721 |
| BPAT | 256,694.270 | 256,722.710 | 256,751.150 |
| CISO | 65,948.065 | 65,948.065 | 65,948.065 |
| SRP | 0 | 0 | 0 |

The endpoint constraints were confirmed against the solved SOC trajectories. Requiring energy at the end of the horizon raises modeled shortage in AZPS/BPAT but not CISO. Combined with the earlier cross-initial-SOC charge substitution result, this indicates substantial *modelled* charging flexibility for CISO in this partial-fleet, isolated-BA experiment. It **does not verify** actual historical charging opportunities. Terminal constraints also do not remove other baseline biases from missing generation, imports, interties or dispatch costs.

**Methodological priority before a publication-grade reliability claim:** reconcile supply and charging availability with measured EIA-930 generation/interchange, examine daily net load and surplus generation by BA, then calibrate storage operation and outage constraints. Do not treat any of the modeled shortage reductions above as actual avoided outages or policy benefits.

## EIA-930 observed net generation versus modeled partial gas+wind fleet (168h)

[Verified CI run 41337609622](../../actions/runs/41337609622). These are **coverage/mismatch diagnostics, not calibration accuracy**: observed EIA-930 NG represents the entire BA and the counterfactual modeled dispatch has only partial gas+wind generators, with no transfers. Scenarios with heat/wind perturbations are not historical generation replay.

| Scenario | BA | Observed EIA-930 NG MWh | Modeled partial fleet MWh | Modeled minus observed MWh | Hourly MAE MW | Descriptive WAPE |
|---|---|---:|---:|---:|---:|---:|
| Baseline | AZPS | 521,162 | 847,877 | +326,715 | 1,945 | 62.7% |
| Baseline | SRP | 1,354,967 | 1,003,455 | −351,512 | 2,092 | 25.9% |
| Heat+wind | AZPS | 521,162 | 843,486 | +322,324 | 1,919 | 61.8% |
| Heat+wind | SRP | 1,354,967 | 1,051,583 | −303,384 | 1,806 | 22.4% |

**Modeling gate:** The baseline AZPS simulation exceeds all-fuel observed net generation despite only representing a subset of technology types; review inventory scope, BA plant attribution, must-run assumptions, and dispatch economics before treating generation magnitudes as representative. The SRP deficit may reflect missing technologies/production, fleet scope or dispatch assumptions. None of these descriptive differences constitutes a calibrated complete-fleet validation. Historical reliability benefit and avoided outage claims remain unsupported.

## AZPS and SRP partial-fleet modeled generation mix (verified)

[CI run 41338136865](../../actions/runs/41338136865) decomposed the **modeled** partial-fleet dispatch into gas and wind (168 hourly intervals). Values below are rounded MWh, not historical fuel-specific generation estimates.

| BA | Scenario | Modeled gas MWh | Modeled wind MWh | EIA-930 observed total BA NG MWh |
|---|---|---:|---:|---:|
| AZPS | Baseline | 789,984 | 57,894 | 521,162 |
| AZPS | Heat+wind | 802,961 | 40,526 | 521,162 |
| SRP | Baseline | 979,629 | 23,826 | 1,354,967 |
| SRP | Heat+wind | 1,034,905 | 16,678 | 1,354,967 |

The inventory and dispatch are gas-dominated, but EIA-930 NG is an **all-technology, actual BA observation**. AZPS gas dispatch alone exceeds observed total NG, suggesting a material representativeness/accounting mismatch; check BA generator mapping, capacity sources (including generic thermal proxy), temporal availability, and dispatch scope. SRP partial gas+wind totals understate observed total NG, potentially because other technologies are absent. No technology-specific calibration or empirically measured storage benefit is claimed.

## Critical inventory interpretation gate: generic thermal proxy mislabeled as gas

Source-workflow audit (November 2026): `.github/workflows/observed-storage-2024-screening.yml` explicitly asserts that every capacity source contains `GENERIC_THERMAL_PROXY`, then maps `gas_mw` to a generator labeled `gas` with fixed 100% hourly availability and marginal cost 70. Therefore the reported *modeled gas* generation in the AZPS/SRP 168-hour decomposition is **dispatch from a generic thermal proxy**, NOT independently verified EIA-860 gas-only BA capacity or EIA-923 gas generation. Prior labels should be interpreted accordingly.

This model was built for isolated-BA stress screening and retains a partial, unverified generation fleet. Replacing the proxy with real gas capacities requires an independently validated plant-to-BA crosswalk, generator status and technology classification; it must not be achieved by a post-hoc normalization coefficient. The observed-versus-modeled comparison is a **model scope diagnostic** rather than a calibration validation. The repository's `eia860_ba_capacity_gap.py` independently identifies missing verified full BA attribution.

## Official 2024 EIA-860 BA-attributed nameplate capacity candidates

[Verified EIA-860 intake CI 41339744603](../../actions/runs/41339744603) joins the official 2024 Plant BA code to operable generator rows and conservatively retains eligible single-fuel gas and wind units. These are nameplate candidates, **not** time-varying available output or a complete, historically calibrated BA fleet.

| BA | Fuel class | Official nameplate MW | Generator rows |
|---|---|---:|---:|
| AZPS | Gas | 2,471.2 | 27 |
| AZPS | Wind | 628.5 | 5 |
| SRP | Gas | 7,655.1 | 53 |
| SRP | Wind | 226.0 | 2 |

The previous screening inputs were generic thermal proxy capacities labeled gas. These official values should not silently replace proxy inputs; first compare capacities in a separate explicit diagnostic scenario and review generator status, firm availability, omitted technologies, and BA operational boundaries. EIA-860 nameplate MW is not comparable directly with EIA-930 generated MWh without a validated dispatch and availability model.

## Official EIA-860 versus generic-proxy capacity paired screening (verified)

[CI run 41340432611](../../actions/runs/41340432611) successfully ran the separate AZPS/SRP 168-hour, isolated-BA, no-storage paired experiment, replacing **only gas-labeled generic thermal proxy MW** with EIA-860 2024 Plant-BA-attributed single-fuel **gas nameplate MW**. Wind MW, demand, scenario weather/availability, marginal costs and model topology were held fixed. This contrasts different technology scopes, not independently verified like-for-like gas fleets.

| BA | Technology | Previous capacity MW | Official candidate nameplate MW | Candidate / previous |
|---|---|---:|---:|---:|
| AZPS | Gas-labeled thermal proxy → official gas | 4,818.8 | 2,471.2 | 0.5128 |
| AZPS | Wind | 628.5 | 628.5 | 1.0000 |
| SRP | Gas-labeled thermal proxy → official gas | 9,263.9 | 7,655.1 | 0.8263 |
| SRP | Wind | 226.0 | 226.0 | 1.0000 |

| BA | Scenario | Proxy shortfall MWh | Official-candidate shortfall MWh | Additional modeled shortfall MWh |
|---|---|---:|---:|---:|
| AZPS | Baseline | 154,772.620 | 529,594.640 | +374,822.020 |
| AZPS | Heat+wind | 207,290.816 | 595,089.968 | +387,799.152 |
| SRP | Baseline | 0 | 142.700 | +142.700 |
| SRP | Heat+wind | 0 | 5,712.510 | +5,712.510 |

**Interpretation gate.** This confirms large **capacity-definition sensitivity**, not empirically observed unserved energy. The original gas-labeled input was a generic thermal proxy; EIA-860 gas-only candidates are not necessarily the same fleet. The candidate capacity excludes other fuels and potentially excluded/multifuel units, while gas availability remains fixed at 100%, transmission imports are absent, and plant status/dispatch are uncalibrated. Neither the apparent change in AZPS generation mismatch nor the increased model shortfall establishes historical performance or avoided outages.

**Next validation:** audit omitted fuel capacities and generator attrition by BA, then address actual hourly availability/operational status before using official candidates as a full replacement model.

## Verified EIA-860 2024 AZPS/SRP omitted fleet scope

[Official EIA-860 CI 41341668303](../../actions/runs/41341668303) confirms that gas+wind-only sensitivity cases omit substantial other eligible single-fuel nameplate capacity. All MW below are **candidate nameplate**, not validated hourly generation capability.

| BA | Eligible single-fuel gas + wind MW | Other eligible single-fuel MW | Excluded positive nameplate MW | Excluded unit rows |
|---|---:|---:|---:|---:|
| AZPS | 3,099.7 | 2,679.5 | 1,478.6 | 24 |
| SRP | 7,881.1 | 6,800.4 | 2,182.1 | 22 |

The *other eligible* fuel categories are AZPS coal 1,636.2 MW, oil 123.8 MW, solar 919.5 MW; SRP coal 821.8 MW, hydro 94.1 MW, nuclear 4,209.6 MW, solar 1,674.9 MW. The excluded generator roster includes mixed/secondary-fuel units, storage and unmapped fuel classifications. Excluded nameplate MW is **not dispatch-ready**, and storage MW cannot be treated as incremental thermal generation.

**Implication:** The paired gas+wind-only capacity stress test (CI 41340432611) provides a *scope sensitivity*, not a bound on full-system shortfall. In particular, omitting 4,209.6 MW of eligible SRP nuclear nameplate materially changes the modeled technology representation; nameplate magnitude does not demonstrate actual hourly nuclear dispatch. Priority before reliability calibration: technology-resolved generator selection, 2024 operational status, observed source-specific production, unit availability and BA imports. Do not directly add all excluded capacities or calibrate shortages using arbitrary scale factors.

## CI-verified official multi-technology extreme availability sensitivity

[Workflow 41345391809](../../actions/runs/41345391809) solves separate 168-hour AZPS/SRP EIA-860 single-fuel capacity scenarios. Existing gas 100% availability and wind profiles are held fixed; the additional coal, solar, nuclear, hydro and oil categories are assigned **either 0% or 100%** availability in every hour. Marginal costs are assumptions; no BA transfers or storage are modeled.

| BA | Scenario | Other fuels 0%: simulated shortfall MWh | Other fuels 100%: simulated shortfall MWh | Difference MWh |
|---|---|---:|---:|---:|
| AZPS | Baseline | 529,594.640 | 118,554.611 | 411,040.029 |
| AZPS | Heat+wind | 595,089.968 | 164,578.423 | 430,511.545 |
| SRP | Baseline | 142.700 | 0 | 142.700 |
| SRP | Heat+wind | 5,712.510 | 0 | 5,712.510 |

These **extreme availability assumptions** are not empirically established upper/lower limits on actual outages or reliability, and must not be interpreted as physically feasible historical operation. The baseline AZPS residual even under 100% other-fuel availability may reflect missing imports, BA metering/reporting boundaries, excluded units, or structural assumptions rather than a historical supply shortage. A next empirical step must validate technology-specific hourly wind/solar output, nuclear operating status, hydro power and energy constraints and inter-BA flows independently before treating any run as calibrated.

## CI-verified illustrative daylight-only solar sensitivity

[CI run 41347960481](../../actions/runs/41347960481) compared an intermediate daylight-only solar availability proxy against two extreme 168-hour availability cases. All other additional single-fuel technologies remain at 100% availability in the daylight proxy case, gas remains 100% available, and wind uses the existing scenario profile. The solar shape is a deterministic illustrative clock-time sine profile, **not** ERA5 irradiance, observed photovoltaic production, or a verified geographic solar capacity factor.

| BA | Scenario | Other fuels unavailable shortfall MWh | Daylight solar proxy shortfall MWh | All additional fuels always available shortfall MWh |
|---|---|---:|---:|---:|
| AZPS | Baseline | 529,594.640 | 184,696.512 | 118,554.611 |
| AZPS | Heat+wind | 595,089.968 | 246,553.378 | 164,578.423 |
| SRP | Baseline | 142.700 | 0 | 0 |
| SRP | Heat+wind | 5,712.510 | 0 | 0 |

For AZPS heat+wind, the daylight-only solar restriction increases modeled shortage by **81,974.955 MWh** compared with impossible all-hours solar availability, holding the other optimistic assumptions fixed. This is *model timing sensitivity*, not a historical outage estimate. Nuclear/coal/hydro dispatch and BA interchange must be constrained with independently verified data before calibration or measured reliability claims.

## Verified illustrative 48-full-load-hour hydro energy budget

[CI run 41348287162](../../actions/runs/41348287162) added an assumed 48 full-load-hour cumulative hydro production budget over 168h, while preserving illustrative solar daylight availability and the other-fuels-fully-available assumptions.

| BA | Scenario | Solar daylight without hydro budget: shortfall MWh | Same with 48h hydro budget: shortfall MWh | Difference MWh |
|---|---|---:|---:|---:|
| AZPS | Baseline | 184,696.512 | 184,696.512 | 0 |
| AZPS | Heat+wind | 246,553.378 | 246,553.378 | 0 |
| SRP | Baseline | 0 | 0 | 0 |
| SRP | Heat+wind | 0 | 0 | 0 |

**Interpretation:** In this narrowly defined, other-thermal-and-nuclear-always-available experiment, the budget makes no observable difference to aggregate modeled shortage. AZPS has no eligible hydro capacity in the included candidate set; SRP has 94.1 MW eligible hydro nameplate, but unchanged shortfall does **not** prove the hydro generation budget binds, or that hydro cannot influence reliability under different fuel, transmission, and demand assumptions. Verify simulated hydro generation and 48h utilization before asserting the constraint is active. Budget length and source availability are illustrative, not measured historical flows.

## SRP hydro budget binding audit — verified

[CI 41348711208](../../actions/runs/41348711208) verified that the illustrative 48-full-load-hour SRP hydro generation budget **does bind**, even though total modeled unserved energy remains zero in both scenarios.

| Scenario | SRP hydro MWh without budget | SRP hydro MWh with budget | Suppressed hydro MWh | Budget fraction |
|---|---:|---:|---:|---:|
| Baseline | 12,073.514 | 4,516.800 | 7,556.714 | 100% |
| Heat+wind | 13,588.299 | 4,516.800 | 9,071.499 | 100% |

SRP official included hydro nameplate is 94.1 MW; the hypothetical total energy budget is therefore 94.1 MW × 48 h = **4,516.8 MWh**. This is a modeled binding energy limit, not a reservoir measurement. Because shortages remain 0 MWh under the fully available other-fuels case, redispatch is apparently sufficient to cover the reduced hydro output; the precise compensating generator contributions must be checked separately before attributing them to any specific technology. AZPS has no eligible hydro in this filtered fleet. Do not interpret zero shortage sensitivity as absence of hydro operational effects.
