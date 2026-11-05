# June–July 2024 actual-source independent-month observed-covariate predictive transfer — CI verified

**Actual verified CI run:** [42101433771](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42101433771), **SUCCESS**; [full 32-row model-evaluation CSV and manifest, artifact 13448318808](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42101433771/artifacts/13448318808). Source model revision commit `d9500de201dbb03f139ce158c7707b492ad6f489`. Inputs: actual EPA–ERA5–official EIA930 source joined June (713/10 source-unit hours per unit) and July (737/10 per unit) from [verified original source CI 42092282072](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092282072), preserving original EPA archived MD5. The shared temperature, BA-demand and local-hour cells are fixed by the preceding source overlap analysis [42091711862](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42091711862).

## Predictive question and design

On month-external source records *within the original jointly occupied covariate cells*, can real observed ERA5 ambient temperature improve the prediction of either (a) **EPA reported Operating Time >0** or (b) **reported EPA source Gross Load MW conditional on an observed positive-operating hour** above a simple demand/hour model?

Fit each EPA source unit separately; train on **June, test on July**, then reverse **train July, test June**, without refitting on the validation month's outcomes. The no-temperature baseline is linear regression on intercept, SRP EIA930 **contemporaneously observed** BA demand (GW) and 23 local MST hour indicators; the augmentation adds **contemporaneously observed site ERA5 temperature °C**. There are **no held-out local-date fixed effects**, because calendar day identifiers from the training month cannot transfer to a new month. The *running probability* predictions are clipped to [0,1] and evaluated by held-out RMSE/Brier and MAE; conditional Gross Load is assessed by held-out MW RMSE/MAE on actual **observed positive-running hours only** (not an ex-ante combined operation+output forecast).

This is an **observed-covariate month-external evaluation**, *not* an ex-ante operating forecast. The shared occupied-cell universe was defined by actual covariate values from **both** months (transductive support screening), even though no validation outcomes were used for training. Candidate test-time weather and demand are therefore known when scoring, and source runtime is used to decide which gross-output rows qualify. No within-cell covariate balancing, weather forecasting, source outage labels or causal variation is claimed.

A model is withheld if fewer than 80 observed target outcomes exist, positive-operation source history is constant in the training month (for binary running), or the fit design is not full-column-rank at its sample size. Missing/no-operation observations are **never imputed as physical available MW**.

## Important real-source results for EPA unit 147/K-7

| Cross-month direction | Outcome | Demand + local-hour RMSE | Demand + hour + observed ERA5 temperature RMSE | Temperature incremental RMSE gain (positive=better) |
|---|---|---:|---:|---:|
| June → July | Reported running status (probability) | 0.388723 | 0.395108 | **−0.006384** |
| July → June | Reported running status (probability) | 0.335246 | 0.389466 | **−0.054220** |
| June → July | Gross MW conditional on operation | 38.350148 MW | 38.334554 MW | **+0.015594 MW** |
| July → June | Gross MW conditional on operation | 45.217339 MW | 45.543086 MW | **−0.325748 MW** |

For the **gross** response, June→July temperature augmentation improves K-7's test RMSE by only ~0.016 MW, while the reverse direction deteriorates by ~0.326 MW. For reported running-status prediction, adding temperature deteriorates both directions. Thus **a strong in-sample or bootstrap source temperature association does not establish incremental performance on the other month**. The source gross observation is dispatch-conditioned, and no generator physical thermal availability is identified.

### Additional descriptive checks

- Full 32-row source matrix comprises **20 operating-state candidate evaluations** (10 units × 2 directions) plus **12 conditional gross candidates** (6 previously eligible source units × 2 directions). Some candidates are explicitly not reportable due to constant operation or design rank failure; do not count such records as prediction successes.
- For **55129/DBG1**, June→July held-out gross RMSE is **28.719 MW** without temperature versus **29.143 MW** with it (worse), and July→June is **47.323478 MW** without versus **47.323481 MW** with it (essentially no material gain).
- For **55129/DBG2**, June→July gross RMSE is **30.064 MW** without temperature versus **30.360 MW** with it (worse), and July→June **46.342 MW** versus **46.336 MW** (minimal positive difference).
- June source operating records for 55129/DBG4/DBG5 are constant zero within admitted covariate cells. Their June→July binary model is withheld. They never qualify for cross-month gross transfer.
- Three Plant 141 units have some transfer gross-model directions withheld due to **unidentified training design**: 141/1 June→July, 141/2 both directions, and 141/3 June→July. This is a real operating-subset identifiability limitation, not data fabrication.
- Data from units sharing ERA5 weather site or BA demand are dependent; ten unit rows cannot be interpreted as ten independent meteorological model evaluations.

## Research interpretation and manuscript/paper C implications

The robust, defensible contribution is the **source-by-source evidence admission and counterexamples**: site weather exposures, apparent within-month temperature associations and month-to-month differences can all be documented from actual source data, **but they do not establish weather-augmented held-out predictive value, thermal derating, unavailable generator capacity, historic observed forced outage or EENS**. This aligns with previously verified 2/3/5-day moving-date-block sensitivity [42100447565](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42100447565), in which **no source unit (0/6) exhibited consistently zero-excluding, reportable July-minus-June coefficient-difference exploratory spans under every block width**.

The V2 PyPSA paper remains a reproducible **structural adequacy sensitivity and weather-exposure study**, not a historically calibrated climate-attributable grid failure model. The available V2 Results manuscript draft v0.1 (168h deterministic sensitivity) must not be confused with a completed paper incorporating all the subsequent source audits. Independent source-month transfer here tests predictive *association*, not the reproducibility or physical validity of PyPSA unserved-load shocks; source-reconciled net capacity, true BA transfer limits and reliability calibration remain outstanding.

## Next admissions required for a paper-quality revision

1. Predefine forecast task and validation source periods, ideally an independent **2025/2023 early-summer source panel**, and repeat under source-verified date/month source gates with no weather imputation.
2. Compare simpler and appropriately regularized temporal baselines for low-sample conditional Gross Load, plus operation-aware two-stage predictions, with strictly out-of-month tuning and model-complexity controls; do not hide singularity by silently reusing validation data.
3. Audit true generator IDs and observed net available MW/dispatch/outages before deriving a thermal derating factor.
4. Complete multi-window BA-level PyPSA factorial heat-only/wind-only/compound scenario design, explicit real-versus-assumed transmission limits, and uncertainty, before discussing policy-relevant causal impacts or submission readiness.

Source code: [two-way source-month transfer](../src/grid_resilience/srp_epa_june_july_month_predictive_transfer.py), [source-guard tests](../tests/test_srp_epa_june_july_month_predictive_transfer.py), [GitHub workflow](../.github/workflows/srp-epa-june-july-month-transfer.yml).
