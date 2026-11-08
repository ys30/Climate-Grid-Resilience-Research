# Paper C — Fleet-specification robustness: frozen 2024 proxy versus year-specific EIA-860 gas/wind nameplate scenarios

## Independent workflows and source provenance

- [Year-specific 2023/2024 original EIA-860 Operable generator / Plant BA source reconciliation CI 42441328634](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441328634), [original-source candidate archive](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441328634/artifacts/13601444011).
- [Source-reconciled 2023/2024 annual nameplate gas/wind PyPSA factorial sensitivity CI 42441502302](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441502302), [16 optimized scenario results + annual capacity scope artifact](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441502302/artifacts/13602040965). Both network assumptions, each of four hazard cases, each year.
- [Earlier frozen 2024 partial-proxy, cross-year input factorial CI 42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209).

**Design:** The same source-observed EIA-930 load and representative-point ERA5 weather periods are used for 2023 July 10–16 and 2024 July 1–7 (168 UTC hours × 4 BAs per year). Same assumed +4°C heat increment and 30% wind proxy derating, no measured weather-induced generator outages. Isolated BA and a fixed **hypothetical** July 2024-demand-derived three-link network are compared. The new capacity sensitivity uses **official annual Operable single-fuel gas/wind nameplates grouped by EIA Plant BA code** rather than the **fixed 2024 generic thermal/wind partial proxy** in the previous cross-year study.

**The two formulations differ in both the gas/wind capacity magnitudes AND their source/technology inclusion criteria.** A contrast between their outputs should **not** be attributed exclusively to changes between the 2023 and 2024 real-world generation fleets.

## Source-CI-verified interaction values (MWh per seven-day four-BA period)

| Year | Network representation | Frozen 2024 generic partial-fleet proxy | Year-specific EIA-860 gas/wind candidate |
|---|---|---:|---:|
| 2023 | Isolated | +12,968.975027 | **+6,044.647931** |
| 2023 | Frozen illustrative 10%-peak links | +12,886.902774 | **+8,042.624543** |
| 2024 | Isolated | +14,630.333329 | **+18,457.415980** |
| 2024 | Frozen illustrative 10%-peak links | +22,515.997901 | **+14,762.078828** |

Interaction is `U(heat+wind) - U(heat only) - U(wind only) + U(baseline)`; `U` is the model-only shortage from an incomplete supply roster, **not** historical EENS.

For the **year-specific gas/wind** annual-nameplate scenario the baseline modeled gaps are **~1,021,296 MWh** in 2023 isolated; **~746,255 MWh** in 2023 illustrative links; **~1,010,306 MWh** in 2024 isolated; and **~763,469 MWh** in 2024 illustrative links. The exceptionally high counterfactual supply gaps underscore the missing fuel classes and physical constraints, not actual observed electricity outages. Do not use any of these simulated totals to estimate real reliability or economic damage.

## Scientific significance: an essential negative calibration finding

1. Positive model factorial second differences occur in both July years under *both* incomplete supply representations. However, magnitude and assumed intertie-response vary substantially, so **cross-year sign persistence is not equivalent to structural robustness in magnitude**.
2. The 2023 annual inventory differs from the 2024 source inventory (for example AZPS wind 412.5 versus 628.5 MW; SRP wind 63 versus 226 MW), confirming that a fixed fleet is not an accurate annual inventory replay.
3. The source-year-specific nameplate model is **not validated dispatchable MW**. It excludes solar/hydro/nuclear/coal, ambiguous/multi-fuel units, storage, imports and other BA resources, lacks actual hourly generator outages, and the assumed link ratings are not physically certified.
4. Therefore the most scientifically defensible main narrative at this stage is **conditional climate stress with pronounced fleet and network representation dependence**, not a calibrated quantification of climate-driven unserved energy.

## Publication next steps

- Create a compact figure contrasting model interaction for **both fleet formulations**, stratified by year and network assumption. The figure must label both as incomplete-fleet screening scenarios, rather than implying the year-specific inventory is a firm-capacity forecast.
- Derive year-specific capacity-to-observed-EIA930 fuel-generation coverage diagnostics, and incorporate excluded technologies in a transparent supply accounting; retain full-source status and site-to-BA ambiguity checks.
- Obtain physical intertie and generator available MW before making real reliability statements.
