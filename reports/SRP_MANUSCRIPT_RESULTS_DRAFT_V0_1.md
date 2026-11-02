# SRP modeled adequacy: manuscript Results draft v0.1 (internal research text)

**Status:** verified deterministic model sensitivity outputs, **not** historically calibrated electricity reliability. For manuscript development only.

**Provenance:** GitHub Actions [run 41386883075](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075), source commit `568f52f17b6d0aa287353793d1be01feecc5cd7f`, artifact ID `13115548069`. Numbers checked against `fine_gas_derating_threshold.csv`, `fine_gas_hourly_vulnerability_summary.csv`, and the hourly/diurnal figure data in the artifact. **The GitHub report commit is not itself a new simulation run.**

## Results: exploratory SRP adequacy sensitivity

Under the prescribed 168-hour dispatch window, the refined availability grid comprised 16 combinations of the baseline versus compound heat–wind demand/renewable profiles and assumed gas, coal and nuclear availability levels. Four scenarios produced materially positive deterministic unserved energy. At full assumed coal and nuclear availability and 30% gas availability, modeled unserved energy was 450.880 MWh for the baseline and 4,342.666 MWh for the heat–wind scenario, corresponding to an increase of 3,891.786 MWh within this matched supply-assumption comparison. The number of modeled shortage hours increased from four to fifteen. Under the heat–wind scenario, increasing gas availability from 30% to 35% reduced unserved energy from 4,342.666 to 635.731 MWh, while 40% and 45% gas availability yielded zero material shortage on the tested grid. With coal and nuclear availability constrained to 50% and 75%, respectively, the heat–wind case generated 352.485 MWh of shortage at 55% gas availability, but no material shortage at 60% or higher tested levels. Accordingly, the tested grid brackets the shortage transitions; it does not identify continuous critical thresholds.

Shortage hours were strongly concentrated during high-demand conditions within each scenario. Every nonzero-shortfall case allocated 100% of modeled unserved energy to hours in the highest quartile of that scenario's 168-hour demand distribution. In the largest-shortfall case, mean demand during the 15 shortage hours was 7,936.225 MW, compared with 6,259.423 MW across all 168 hours. In that case, 3,536.866 of 4,342.666 MWh (81.44%) occurred during hours when the assumed solar availability proxy was zero. All shortage observations occurred between 01:00 and 03:00 UTC (18:00–20:00 Arizona MST on the preceding local calendar date), with 02:00 UTC contributing the largest portion of the modeled shortage. Because these patterns are conditional on a deterministic dispatch formulation and an illustrative solar availability profile, they should be interpreted as model diagnostics, not evidence of actual outages or empirical solar causation.

## Proposed captions

**Figure A.** Hourly SRP demand and simulated unserved power in the compound heat–wind scenario with assumed coal/nuclear/gas availability of 100%/100%/30%. The two vertically aligned panels share an Arizona MST time axis and cover the 168-hour model window. Demand is the supplied input; shortage is an optimization output, not measured outage power. No historical reliability calibration is claimed.

**Figure B.** Simulated unserved energy and the number of shortage hours across the four positive-shortfall SRP scenarios. Availability percentages denote imposed model assumptions. The twelve additional refined cases yielded no material shortage and are retained in the supplementary scenario table.

## Required next work before publication

- Validate mapping of EIA-860 candidate plant capacity to balancing-authority inventories and reconcile EIA-923 annual/monthly generation, EIA-930 hourly demand/interchange, and independent-weather observations.
- Model or bound transfer availability and storage impacts rather than interpreting the current isolated BA screen as a calibrated network forecast.
- Conduct independent-year replication and uncertainty/sensitivity analyses; avoid confidence intervals for deterministic scenario grids.
- Review final figure design, data licensing, provenance and manuscript-wide consistency.

**Editorial restriction:** Do not use the terms *observed electricity outage*, *empirical EENS*, *historically calibrated*, *causal effect*, or *critical gas threshold* for these results.
