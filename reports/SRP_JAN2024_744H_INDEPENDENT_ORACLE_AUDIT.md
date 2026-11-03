# SRP January 2024: independent full-hour screening dispatch oracle

## Reanalysis of a real successful run artifact

Historical GitHub Actions [run 41542019155](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155), [artifact 13186838868](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155/artifacts/13186838868), was downloaded and its **744 source diagnostic rows** independently examined, without running PyPSA.

From the artifact:
- Assumed **screened, derated** dispatchable capacity (NG + SUB): **6294.045 MW**.
- Dispatch under the fixed EIA-930 demand and observed interchange schedules: **4,625,935.045 MWh**.
- **Model's unmet supply requirement**: **472,996.955 MWh** in **601 of 744 UTC hours**.
- Peak hourly model shortfall: **2,025.955 MW**.
- Difference between **each hour** of modeled dispatch and analytic clipped demand requirement: **0 MW** within printed precision.
- Maximum difference in hourly unserved result: approximately **1.14e-13 MW**, numerical rounding only; spill difference **0 MW**.

Analytic identity for this particular **positive marginal cost, constant-capacity, no-HY/PS, fixed-boundary** screening model:

```
required_t = demand_t + export_t - import_t
local_generation_t = clip(required_t, lower=0, upper=6294.045)
unserved_t = max(required_t - local_generation_t, 0)
spill_t = max(-required_t, 0)
```

This is a direct independent verification of the source-artifact model's **counterfactual** rather than an EIA-930 historic adequacy conclusion. EIA-860/EIA-923 input matched a **partial** set of BA generators, with hypothetical hourly constant availability and costs, no actual unit commitment, and missing fleet / transmission topology. The observed real balancing-authority demand was met; no conclusion of historical failures or unserved energy is warranted.

## Reproducible CI gate

`src/grid_resilience/srp_hourly_oracle_audit.py` now checks for complete sorted UTC coverage, the model's assumed generator-cost range, zero HY/PS components, valid observed interchange sign splitting, and per-hour dispatch/bus-balance agreement with the analytical merit-order oracle. The full SRP CI workflow is configured to run this after producing its baseline hourly CSV and upload the resulting manifest.

**The new CI run has not yet been confirmed passing.** The numbers reported above were independently recomputed from the prior **successfully uploaded source artifact**, not invented from an unobserved new run.

**Calibration certified:** NO.
