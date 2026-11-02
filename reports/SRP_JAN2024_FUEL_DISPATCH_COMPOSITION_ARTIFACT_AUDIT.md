# SRP January 2024 actual artifact — dispatch composition audit

Actual [successful run 41408327414](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41408327414), [artifact 13124397333](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41408327414/artifacts/13124397333), inspected the **CSV files** `fuel_assumption_capacity_screen.csv` and `fuel_scenario/modeled_monthly_generation.csv`.

| EIA-860 primary energy code | Original selected nameplate MW | Hypothetical derating | Effective screened MW | Modeled January MWh |
|---|---:|---:|---:|---:|
| NG | 6,631.3 | 0.85 | 5,636.605 | 2,455,626 |
| SUB | 821.8 | 0.80 | 657.440 | 0 |
| **Total** | **7,453.1** | — | **6,294.045** | **2,455,626** |

The entire simulated generation is NG, and no SUB dispatch occurs. This is a **mechanical result of model assumptions**: NG marginal cost is set to 55 (arbitrary model units) versus SUB 80, and assumed NG firm hourly capacity suffices for all simulated hourly load. There is no calibrated fuel cost series, unit commitment or minimum run level.

**Critical source-scope audit:** The exact EIA-860 Operable × partial EIA-923 Page-4 SRP generator identity join supplied **only NG and SUB candidates**. It omitted all other potentially relevant SRP supply sources (including observed hydro and PS on EIA-923 Page 1, renewables, storage and interchange). The resulting NG 100% simulated share is **not** a real-world NG generation share and must not be used as a calibrated historical result. EIA-923 monthly generation totals elsewhere in the repository are on different reporting grains and cannot safely be compared as if they were complete matching dispatch observations.

**Required methodological pivot:** Prioritize independent BA fleet completeness and source-defined technology crosswalk, hourly renewables and energy constraints. Build a **matched-scope** monthly comparison only after reviewed source entries have compatible BA, calendar month, fuel, and reporting coverage. Until then, all modeled-versus-observed technology calibration metrics remain **NOT COMPUTED / NOT CERTIFIED**.
