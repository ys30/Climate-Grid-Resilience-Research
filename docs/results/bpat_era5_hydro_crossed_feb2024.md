# BPAT February 2024: matched wind-weather × hydro scenario results

**Verified workflow:** [BPAT 29-site ERA5 comparison, run 41234205089](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41234205089) (successful). **Scope:** 696 hourly periods, 29 geolocated BPAT wind power plants, four modeled Western U.S. balancing authorities. PyPSA is used to solve a conditional dispatch-screening model, **not** a calibrated reliability or historic outage reconstruction.

## Actual modeled shortfalls (GWh)

Each cell lists ERA5-based shortfall / EIA-930 reported-wind-replay shortfall / ERA5 minus replay shortfall. The hydro monthly energy allowance is a hypothetical fraction of *observed mixed hydro and pumped net generation*; hourly power is a hypothetical fraction of separately inventoried EIA-860 non-storage hydro nameplate. These categories differ, and are not actual water/power availability.

| Hydro energy fraction | Hydro power 10% | Hydro power 20% | Hydro power 30% |
| --- | --- | --- | --- |
| 5% | 1490.802 / 1353.393 / **137.409** | 1490.802 / 1353.393 / **137.409** | 1490.802 / 1353.393 / **137.409** |
| 25% | 602.802 / 465.393 / **137.409** | 602.802 / 465.393 / **137.409** | 602.802 / 465.393 / **137.409** |
| 50% | 395.317 / 315.678 / **79.639** | 1.084 / 0.774 / **0.310** | 0 / 0 / **0** |
| 100% | 395.317 / 315.678 / **79.639** | 1.084 / 0.774 / **0.310** | 0 / 0 / **0** |

The results exhibit a *conditional constraint-regime shift*. In the low-energy regimes, increasing installed-hourly hydro power availability does not reduce modeled shortage. In the higher-energy regimes, more hourly hydro power substantially reduces both absolute shortage and the contrast between wind inputs. At these selected points, 50% and 100% monthly energy allowances yield the same results.

## Wind inputs and diagnostics

- Independent weather proxy: ERA5 hourly wind at 29 plant locations, nameplate-weighted, simplified idealized fixed power curve, **not calibrated** against EIA-930 generation.
- Replay: EIA-930 observed BPAT net wind generation clipped into a dispatch ceiling; this is **not** an independent meteorological counterfactual.
- Hourly ERA5-versus-reported wind generation ratio correlation: **r = 0.8934**, 696 hours.
- ERA5 proxy monthly mean: **13.90%** of BPAT inventoried wind nameplate; observed reported ratio: **19.17%**.
- ERA5 proxy MAE: **7.48 percentage points** (696 hours), RMSE: **10.96 percentage points**, mean bias: **−5.27 percentage points**.
- Shared 672-hour benchmark window: ERA5 proxy **R² = 0.7197**; previous-hour observed persistence **R² = 0.9771**; previous-day observed persistence **R² = 0.0048**. Persistence relies on actual observed generation and is a diagnostic baseline, **not a fair weather forecast comparison**.

## What this does and does not establish

1. The 24 optimizations correspond to 12 crossed hydro assumptions × 2 BPAT wind-input cases. All other modeled generator availability stays synthetic; the model has no validated transmission flows, missing technology attribution, calibrated hourly hydro inflows, or pumping dynamics.
2. The 12 differences are **sensitivity contrasts**, not actual electricity outages and not estimates of avoided historical outage loss.
3. Hydro energy availability and hydro maximum hourly output can independently determine whether wind-availability differences result in model shortage. The observed 50% and 100% convergence is not a general threshold for a real electric grid.
4. Results are for one month only; independent cross-month verification has not been completed. Weather-generation amplitude calibration is still incomplete.
5. A physical consistency audit verified that only BPAT wind availability differs between the two weather/replay scenarios; the 696 modified cells yielded a **137,408.70 MWh** shortage difference in the no-hydro control, balanced against changes in total generation within numerical tolerance.

**Suggested next empirical steps:** independent March/another-season time split, validation of EIA-860-to-BA attribution and historical available hydro capacity, verified interconnection data, and stress-testing model input quality. No claim of historical reliability validation should be made until these are addressed.
