# SRP January 2024 — matched four-scenario PyPSA weather-proxy wind comparison

## Verified evidence

Successfully completed [ERA5/EIA860/EIA930 source-backed PyPSA workflow 41771806677](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771806677) and [Research Methods CI 41771806686](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771806686), source commit `c30f76bf4d0349f171d159c6770a1f175e340ef1`. [Artifact 13295182034](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41771806677/artifacts/13295182034) has source EIA archive, EIA-930 source URL/hash, independently fetched plant-point ERA5, curve scenarios, complete four 744h PyPSA output tables, and assumption flags.

## Matched counterfactual design

All four cases share precisely the same 744 UTC January 2024 EIA-930 SRP reported **hourly demand plus signed net interchange**, EIA-860 annual SRP Plant BA generator roster mapped to mutually exclusive primary-fuel / prime-mover technology classes, candidate nameplate capacities, identical non-wind availability profiles, costs, and solver.

Thermal **gas multiplier 0.50**, coal **0.50**, and nuclear **0.75** are imposed on existing synthetic base availability 0.85, 0.85, 0.90, respectively, to obtain a stress-screen region with nonzero modeled coverage gaps. These factors are not observed 2024 plant availability, heat-response regressions, or climate attribution.

Only wind availability changes: an assumed fixed **0.35** across all hours, or hourly profiles derived from real ERA5 100m point winds at two SRP EIA-860 wind-plant locations (226 MW eligible annual nameplate) through three uncalibrated turbine power curves. Each wind curve is applied at site-hour grain before capacity weighting. No EIA-930 historical fuel generation is replayed.

## Actual optimization results

| Wind assumption | Mean wind availability or proxy | Artificial modeled coverage gap (MWh) | Positive-gap hours |
|---|---:|---:|---:|
| Fixed 0.35 | 0.350000 | **113,630.084** | 278 |
| ERA5 low cut-in/rated (2.5/10/25 m/s) | 0.267189 | **114,696.233** | 274 |
| ERA5 reference (3/12/25 m/s) | 0.177521 | **120,556.753** | 281 |
| ERA5 high cut-in/rated (4/14/25 m/s) | 0.114913 | **125,449.974** | 287 |

Compared with a fixed 0.35 wind availability assumption, the reference ERA5 curve increases artificial modeled gap by **6,926.669 MWh** and modeled positive-gap hours by **3**. Across the three ERA5 curves the coverage gap spreads by **10,753.741 MWh**. These gaps describe a fixed stress-screen under assumed resources, not a physical estimate of SRP reliability or actual unserved energy.

The low-cut-in ERA5 case has **274** positive-gap hours, fewer than the fixed assumption's **278**, even though its monthly artificial gap is slightly larger. Thus comparing annual/monthly mean availability without preserving temporal shape loses information, but temporal correlation is only one model mechanism; do not infer observed wind production.

## Critical caveats and next validation gates

- Input wind exposure is independently sourced but ERA5 100m reanalysis at plant coordinates is **not turbine hub height or measured wind production**. Turbine manufacturer/plant fleet curves, terrain, wakes, forced outages and curtailment remain unknown.
- The 2024 annual EIA-860 *Plant BA* roster is not certified SRP ownership, controllability or real dispatch right; line flow, physical transfer ratings, storage SOC, operational constraints, and alternate fuels are not fully represented.
- The NG/coal/nuclear availability factors are synthetic. No temperature-plant heat response, nuclear cooling mechanism or empirical forced outage is estimated. Demand and observed net interchange are held fixed exogenously.
- Monthly difference in modeled gap is **not** a weather causal effect, actual energy-not-served (EENS), historical blackout, or calibrated reserve assessment.
- The most valuable next step is matched, independently sourced plant-level wind **actual** monthly/hourly production or documented turbine types, then multi-event/year weather holdout validation. Also derive thermal site exposure separately rather than using temperature at wind sites.

**Observed real shortage: NO. Weather-to-plant production calibrated: NO. PyPSA source/temporal comparison verified: YES.**
