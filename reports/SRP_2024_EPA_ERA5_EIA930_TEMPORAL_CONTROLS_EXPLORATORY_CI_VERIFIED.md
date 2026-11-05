# SRP July 2024 EPA–ERA5–EIA930 temporal controls — observed exploratory OLS

**Executed source CI:** [run 41967906150](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41967906150), **SUCCESS**, commit `6553e7aebfc9d9fd21cb39746c83997027eec66d`. [CSV and model-scope artifact 13387869251](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41967906150/artifacts/13387869251). Source inputs: [EPA–ERA5 complete July panel run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085) and [official July EIA930 source merge run 41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594). Regression tests and actual ten-source-unit fits passed.

## Models and admissible interpretation

For each source EPA unit separately, fit **exploratory linear probability** for reported `Operating Time >0` and **exploratory OLS** for gross electrical load *conditional on positive reported operation and nonmissing gross load*. Each fit includes site-point ERA5 temperature (°C), actual **SRP balancing-authority** demand (GW), local **standard** hour indicators (hour of day), and local calendar day indicators. Both use a single 737-hour exact UTC source intersection within EPA's 744-hour local July. The seven 2024-August-UTC EIA demand hours are absent from official UTC-July input; **never imputed**. No standard errors, p-values, confidence intervals, time-series dependence correction, lagged terms, cross-unit causal identification or out-of-period validation were performed.

These estimates are conditional **within-source-unit partial associations**, not calibrated generator availability, physical thermal derating or causal heat effects. Gross load is **EPA-reported gross** measurement and may be dispatch-selected, unlike a turbine's available net MW. Regressions are fitted separately on observations with `Operating Time > 0` for the gross load outcome, which introduces selection. One SRP BA demand series is shared by all sites, not independent demand observations at each plant.

## Source results

| Plant / EPA unit | Positive reported operating rows (out of 737) | Operating indicator temperature coefficient (percentage points / °C) | Gross load conditional rows | Gross load temperature coefficient (MW / °C) |
|---|---:|---:|---:|---:|
| 141 / 1 | 329 | −3.49 | 329 | −2.63 |
| 141 / 2 | 330 | −1.53 | 330 | −3.23 |
| 141 / 3 | 383 | −0.46 | 383 | −6.53 |
| 141 / 7 | 111 | −0.47 | 111 | +3.46 |
| 141 / 8 | 99 | +1.08 | 99 | +3.35 |
| 147 / K-7 | 612 | +2.70 | 612 | +7.14 |
| 55129 / DBG1 | 722 | +0.19 | 722 | +0.27 |
| 55129 / DBG2 | 730 | −0.24 | 730 | +0.48 |
| 55129 / DBG4 | 18 | −1.15 | 18 | **Not estimated: insufficient records** |
| 55129 / DBG5 | 19 | −0.98 | 19 | **Not estimated: insufficient records** |

All operation-indicator models use 737 source rows and were admitted for descriptive OLS. Reported operation temperature coefficients are linear probability change **in percentage points per 1°C** (not relative percentages). Gross load is conditioned on operation and requires a minimum of 80 valid observations; DBG4/DBG5 do not qualify. Neither an R² nor a large coefficient establishes physical causation.

## Lessons / research limitations

1. Strongly heterogeneous signs persist after demand/hour/day controls. Simple heat-bin contrasts and temporal-control associations can differ, underscoring confounding and model dependence.
2. Hour/date controls do not eliminate endogeneity of dispatch, fuel cost, plant availability, maintenance, grid constraints or the potential shared weather–load structure. No causal temperature–availability relationship is identified.
3. Within-site ERA5 is repeated across colocated source units; estimates are **not independent across units**, even if fitted separately. No cross-unit pooled uncertainty or causal synthesis is presented.
4. Official 2024 ECMPS unit-stack evidence and physical EPA–EIA GT generator identity remain unresolved; existing API probes returned HTTP 403 without a key.
5. **No coefficients in this report are suitable for direct PyPSA derating or historical EENS calibration.**

## Next rigor upgrades

- Add hour/date-matched *nonparametric* or alternative-specification diagnostics and a clearly defined correlated-error uncertainty plan (date-block bootstrap / autocorrelation robust SE), with dependence-aware identification limitations.
- Obtain August-UTC EIA930 to complete the seven missing demand-context hours, without reconstructing observations.
- Retrieve time-valid original EPA ECMPS and plant engineering/EIA electrical crosswalk records before assigning GT-generator net production or outage labels.
- Compare physically estimated thermal performance to independent engineering/OEM references and a separate calendar/heatwave validation period before any PyPSA physical availability admission.
