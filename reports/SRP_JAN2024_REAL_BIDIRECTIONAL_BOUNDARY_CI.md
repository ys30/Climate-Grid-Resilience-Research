# Real EIA-930 bidirectional boundary integration: SRP 2024-01

**CI verified success:** [run 41480406930](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41480406930), source integration commit `bcc52fc9bd6d4f1aba396c001bf006778637c2db`.

Added `src/grid_resilience/bidirectional_interchange_screen.py` to the existing official-source SRP EIA-930/EIA-860/EIA-923 full-month CI. This run uses **744 consecutive hours** of January 2024 UTC source data, and preserves a separate model case for fixed imports and exports rather than clipping negative interchange or shifting surplus between hours.

| Official hourly-source / modeled screen measure | MWh |
|---|---:|
| EIA-930 local demand | 2,455,626 |
| Observed hourly net imports, fixed injection | 0 |
| Observed hourly net exports, fixed sink | 2,643,306 |
| Modeled generation from partial EIA-860 capacity candidates | 4,625,935.045 |
| Modeled unmet supplied-energy requirement | 472,996.955 |
| Modeled irreversible spill | 0 |

The successful run passed the energy-conservation assertion across load, imports, exports, modeled generation, shortage and spill. There are no SRP net importing hours in the January 2024 source series used for this run, so the new solver reproduces the prior positive-interchange-only screening result at this granularity. The general mixed-sign importer/exporter code previously passed **separately**, under deliberately synthetic test data: [run 41479926527](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41479926527).

**Research caveats:** External net exchange is forced from observed EIA-930 schedules and *does not represent a transmission-constrained multicorridor model*. The modeled supply fleet includes only the Page-4-identity-linked subset of EIA-860 operable units, currently NG and SUB, with fuel-specific hypothetical constant hourly capacity factors/costs; hydro, pumped storage, renewables and full BA fleet not yet reconciled. The modeled 472,996.955 MWh shortage is **not actual historical energy-not-served**. Historical dispatch calibration and independent-year holdout remain **not completed**.

Next: reconcile the actual SRP full supply fleet and official generation reporting scopes; replace assumed flat technology availability with independently sourced weather-driven chronological resources before reporting reliability or dispatch accuracy.
