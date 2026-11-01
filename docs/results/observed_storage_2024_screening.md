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
