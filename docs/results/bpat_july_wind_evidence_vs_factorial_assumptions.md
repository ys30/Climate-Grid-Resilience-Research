# BPAT wind evidence gate for interpreting July 2024 factorial results

## Independent weather–wind diagnostic

Source: [successful July 2024 29-site ERA5/EIA-930 workflow, run 41254992133](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41254992133).

- **29** EIA-860-linked wind-farm sampling sites; **737 of 744** July UTC hourly observations matched to reported BPAT wind output.
- Pearson correlation of capacity-weighted idealized ERA5 wind proxy with clipped reported wind generation-to-nameplate ratio: **0.8643594**.
- Mean idealized weather-proxy availability: **0.1293265**; mean *reported output / eligible nameplate*: **0.2250110**.
- Mean difference (idealized proxy minus reported ratio): approximately **−0.09568 pu (−9.57 percentage points)**. This is material amplitude bias despite high temporal correlation.

The independent validation workflow explicitly reports `regional_weather_model_calibrated: false` and `wind_fleet_actual_generation_independently_predicted: false`.

## Implications for July four-scenario PyPSA

The July factorial result ([CI 41270337858](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41270337858)) used observed EIA-930 demand and ERA5 weather, **but a separate, proxy-based partial fleet**. It used a uniform 30% wind derating in the wind-only and compound scenarios and an assumed heat response. The 29-site wind correlation is *external diagnostic evidence*, not validation of the four-scenario model's specific 30% derating assumption, generator dispatch or loss of load.

The substantial −9.57 percentage-point amplitude mismatch is evidence against describing the weather-to-generation relationship as calibrated. Correlation alone cannot validate energy magnitude, curtailment, availability, dispatch decisions or generator completeness.

For any paper result, keep clear distinctions among **observed wind output**, **site-weighted idealized meteorological proxy**, and **hypothetical scenario generation loss**. Do not transfer a numerical site-proxy correlation into a claim of robust compound-weather reliability impacts.

## Gate before stronger inferential claims

1. Independently benchmark wind availability *magnitude* and shape across separate months, correcting for coverage, curtailment and fleet composition.
2. Estimate technology-specific derating from external evidence with explicit uncertainty; avoid using a single 30% fixed assumption as if empirical.
3. Replace hypothetical network limits with source-backed rated interties or report topology sensitivity as the main uncertainty.
4. Run held-out compound events and historical generation checks at matched BA-hour and technology resolution.

**Historical generator/weather calibration certified: false. Actual transmission topology/rating verified: false.**
