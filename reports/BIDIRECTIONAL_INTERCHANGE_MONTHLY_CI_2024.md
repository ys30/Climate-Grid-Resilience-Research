# Bidirectional EIA-930 boundary screen: CI engineering validation

**Verified successful CI:** [run 41479926527](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41479926527); latest implementation commit `b9c352914d3119731649598e1ac749c277049602`.

The 744-hour full-month test is **synthetic**, covering 100 importing hours followed by 644 exporting hours. The fixed import injection and fixed export load have separate nonnegative time-series. A **negative-dispatch generator** models *irreversible, same-hour surplus absorption*; the prior attempt with an intertemporal Store improperly shifted energy across hours and did not meet the intended disposal semantics. The program verifies monthly energy balance and optimizer status.

| Quantity | Test CI MWh |
|---|---:|
| Local load | 37,200 |
| Fixed external imports | 10,000 |
| Fixed external export obligations | 32,200 |
| Local modeled generation | 64,400 |
| Explicit import-surplus disposal | 5,000 |
| Unserved energy | 0 |

**Conservation:** local generation + imports + unserved = local load + exports + spill.

The CI was initially red in [run 41479506870](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41479506870) because the reversible Store shifted imported energy; after the net-metering adjustment [run 41479707248](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41479707248) still failed a test for physically irreversible spill, the final sink formulation passed.

**NOT proven:** Actual physical network transfer capacity, bilateral flows, generation mix calibration or SRP observed shortage. Imported and exported quantities are fixed measured/external schedules in this simplified single-bus model. The "spill" term is a scenario accounting construct, not observed curtailment. This module is *not yet incorporated* into the official SRP real-input end-to-end workflow. Replacing the former residual-demand approximation in empirical runs should be a separate controlled change with real hourly inputs, CI and provenance.

**Historical calibration certified: NO.**
