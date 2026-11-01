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
