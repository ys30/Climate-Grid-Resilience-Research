# 2024 January EPA–ERA5–EIA930 demand/hour/day-controlled source-unit comparison to July — CI verified

**Final corrected original-source run:** [42073650813](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42073650813) **SUCCESS**, [artifact 13437766161](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42073650813/artifacts/13437766161), source code/test commit `015bf9da075632479d1ae8aa90883422c239ac16`.

## Independently archived evidence

- Source-certified January EPA–ERA5 panel: [run 42072156313](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42072156313). Original EPA Arizona 2024 data archived at Zenodo 15059567, original source MD5 verified upstream. The 2024 January local standard time data (UTC−7) contain **744 local-source hours per each of 10 monitored EPA units**; 737 overlap the verified **UTC January** ERA5 weather source.
- Independently validated **official EIA930 January SRP BA demand 744 UTC hours**: [run 41407182014](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407182014), formed from 7 source-verified 2023 Jul–Dec archive rows plus 737 source-verified 2024 Jan–Jun rows. Both raw source archive SHA256 recorded upstream; never imputed.
- Independent controlled July EPA unit regression: [run 41967906150](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41967906150). Precisely the same ten EPA source identities in both seasonal model outputs.

At each EPA unit, the January exploratory model uses observed source site-point ERA5 temperature, contemporaneous SRP BA demand in GW, Arizona MST local hour indicators and local calendar-date indicators. The outcomes are (i) reported EPA Operating Time >0 (linear probability) and (ii) **EPA reported gross MW conditional on positive reported operation**. These are within-month partial associations, not cross-season predictive tests or physical availability measurements.

## Actual winter–summer temperature associations

| EPA source | January positive reported operating hours / 737 | Jan operating LPM coefficient, percentage points per °C | Jul operating LPM coefficient, percentage points per °C | Jan conditional Gross Load coefficient, MW per °C | Jul conditional Gross Load coefficient, MW per °C |
|---|---:|---:|---:|---:|---:|
| 141 / 1 | 0 | **Not estimable: constant operation outcome** | −3.49 | **Not estimable** | −2.63 |
| 141 / 2 | 0 | **Not estimable: constant operation outcome** | −1.53 | **Not estimable** | −3.23 |
| 141 / 3 | 0 | **Not estimable: constant operation outcome** | −0.46 | **Not estimable** | −6.53 |
| 141 / 7 | 6 | −0.77 | −0.47 | **Not estimable** | +3.46 |
| 141 / 8 | 6 | −0.72 | +1.08 | **Not estimable** | +3.35 |
| 147 / K-7 | 354 | −0.30 | +2.70 | **−3.93** | **+7.14** |
| 55129 / DBG1 | 599 | +0.24 | +0.19 | +3.24 | +0.27 |
| 55129 / DBG2 | 656 | −1.18 | −0.24 | +1.23 | +0.48 |
| 55129 / DBG4 | 11 | +0.22 | −1.15 | **Not estimable** | **Not estimable** |
| 55129 / DBG5 | 10 | +0.06 | −0.98 | **Not estimable** | **Not estimable** |

Raw winter source temperatures averaged **11.25–11.45°C** at these plants, while July averaged **36.22–37.27°C** in the prior independent seasonal run. These are separate, markedly different weather regimes, and common support of the full conditional feature distributions has **not** been demonstrated. Source-unit Gross Load should **never** be interpreted as an EIA generator's net electric power.

### Scientific significance and interpretation

**Main result:** K-7's conditional Gross Load partial temperature association changes from **−3.93 MW/°C in January to +7.14 MW/°C in July**; its reported positive-operation LPM association also changes from approximately **−0.30 to +2.70 percentage points/°C**. This is evidence that the **observational model coefficients are season-specific**, not independent confirmation of a physical generator-temperature slope.

For Plant 141 units 1/2/3, 0/737 January positive-operation hours create complete outcome nonvariation. The initial uncorrected CI run [42073480491](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42073480491) numerically reported approximately zero operating LPM slopes, which would be misleading: the corrected model now explicitly emits **`constant_outcome_no_operational_variation`** and blank temperature coefficients. It also never fabricates gross MW from nonoperating hours. [Final corrected CI 42073650813](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42073650813) passed the expanded all-zero/all-one regression tests and archived corrected data.

For Plant 141 units 7/8 and 55129 DBG4/DBG5, January positive-operation records number only 6, 6, 11, 10. The 80-record minimum prevents estimating conditional gross models. Although their binary LPMs have some variation and numerically fitted coefficients, these are extremely sparse events and merit substantial skepticism.

### What is—and is not—verified

**Verified:** independent January and July real source operating data; exact January source-month UTC demand reporting; matching 10 EPA source identifiers; demand/hour/date-adjusted exploratory OLS and nonvariation gates; no source-hour imputation; archived GitHub CI artifacts.

**Not verified:** causal seasonal transfer, externally predictive January or July regression, shared support/overlap, serial-dependence-valid uncertainty, equipment physical derating, EPA-to-EIA generator electrical identity, EIA net MW, forced outages, LOLE, EENS, or historic PyPSA reliability calibration.

## Next empirical admission priorities

1. Explicit **winter/summer temperature and SRP demand common-support overlap audit** before treating model coefficients as scientifically comparable; zero operation and nonoverlap must be flagged, not extrapolated.
2. Independently held-out hot season/month/year for temperature-slope validation, with actual source weather, official BA demand and source operation.
3. ECMPS period-valid plant/unit/stack/EIA generator documentation; verify unavailable net MW against engineering/dispatch evidence before fitting thermal derating.
4. Consider serial-correlation-robust uncertainty once enough independent source periods and appropriate operating-state records are available.

Code: [January control/transfer diagnostic](../src/grid_resilience/srp_epa_2024_january_eia930_controlled_transfer.py) and [unit regression and admission tests](../tests/test_srp_epa_2024_january_eia930_controlled_transfer.py).
