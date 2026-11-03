# SRP January 2024 — modeled shortfall duration audit

## Source and status

The values below were independently recomputed from an actual successful GitHub Actions source artifact: [run 41542019155](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155), [artifact 13186838868](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155/artifacts/13186838868), file `hy_ps_case/baseline_hourly_diagnostics.csv`. This is the *no-HY/PS baseline*, using fixed observed EIA-930 demand/interchange and **partial hypothetical derated fleet**. The model has only 6,294.045 MW of fixed screened availability.

| Metric | Artifact-backed result |
|---|---:|
| Complete hourly source records | 744 |
| Total **modeled** unmet supply requirement | 472,996.955 MWh |
| Hours with positive **modeled** shortage | 601 |
| Hours exceeding 1,000 MW model deficit | 204 |
| Largest modeled hourly gap | 2,025.955 MW |
| P95 of all hourly model deficits, including zero hours | 1,519.605 MW |
| P99 of all hourly model deficits, including zero hours | 1,780.935 MW |
| Share of modeled gap in the top 75 deficit hours (ceil of 10% of 744) | 24.676% |
| UTC days containing a model deficit | 31 |
| Largest daily modeled deficit | 25,959.92 MWh on 2024-01-03 |

These statistics describe duration and concentration of the model's **counterfactual inadequacy** when real net exports are treated as fixed external requirements and the supply fleet is incompletely inventoried. **They do not measure actual loss of load, outage incidence, involuntary curtailment, or grid resilience.**

## Reproducible method

`src/grid_resilience/srp_shortfall_duration_audit.py` is an independent, solver-free implementation using validated baseline hourly diagnostics. It refuses missing/duplicate/out-of-order timestamps, nonfinite hourly inputs, negative modeled unserved energy and nonzero hourly bus residuals.

The full workflow is now configured to produce `outputs/srp_real_screen/shortfall_duration_audit.json`; fast synthetic tests were also attached to the exchange-boundary regression CI. **New CI execution has not yet been verified as passing.**

## Scientific implication

Because the apparent deficit persists across 601 hours and 31 UTC calendar days under the **partial model fleet**, it is not appropriate to interpret these events as sporadic observed grid failures. The urgent next scientific milestone is full BA generation-fleet reconciliation and actual hourly generator availability, rather than overinterpreting this screening-model duration curve.

**Historical calibration certified: NO.**
