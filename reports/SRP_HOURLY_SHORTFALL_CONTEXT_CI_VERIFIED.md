# CI-verified SRP hourly shortage context: demand and assumed solar availability

## Evidence

This report is derived from the **actual downloaded artifact** of successful
[Actions run 41386883075](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075)
at commit `568f52f17b6d0aa287353793d1be01feecc5cd7f`.
Artifact ID `13115548069`; SHA-256
`784e93871ded9cd109e428c5bae05c3041c8200dd3c490b5394bb4a4fe10746a`.
Source files: `fine_gas_hourly_vulnerability_summary.csv` and
`fine_gas_derating_threshold.csv`. This is a model-based sensitivity
exercise, **not observed outages**, historical plant-availability reconstruction
or causal identification.

## Four nonzero-shortfall scenarios

All 16 modeled cases were checked; the other 12 reported no materially
positive shortage. For the four positive cases, high-load is the upper
quartile of **each case's full 168-hour SRP demand profile**.

| Scenario (coal/nuclear/gas percent availability) | Shortage hours / 168 | Shortage MWh | Max hourly shortfall MW | Mean load in shortage hours MW | Mean load, all hours MW | Share of shortage MWh in high-load hours | Share of shortage MWh when solar proxy is zero |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline C100/N100/G30 | 4 | 450.880 | 258.970 | 7704.250 | 5972.946 | 100% | 100% |
| heat_wind C100/N100/G30 | 15 | 4342.666 | 706.306 | 7936.225 | 6259.423 | 100% | 81.44% |
| heat_wind C100/N100/G35 | 5 | 635.731 | 323.551 | 8058.491 | 6259.423 | 100% | 100% |
| heat_wind C50/N75/G55 | 3 | 352.485 | 255.831 | 8148.200 | 6259.423 | 100% | 100% |

The scenario with the largest shortfall (heat_wind, C100/N100/G30) had
11 of 15 shortage hours with solar availability proxy equal to zero and
3,536.866 of 4,342.666 MWh (81.44%) in those hours. In the other
three positive-shortage cases, *all* shortage hours had zero assumed solar
availability. The solar proxy is an illustrative time-of-day schedule, not
observed solar generation.

Compared to the baseline at identical C100/N100/G30 supply assumptions,
heat_wind has 3,891.786 MWh more modeled shortfall and 11 additional
shortage hours in the 168-hour window. This is a conditional modeled
scenario difference; do not interpret as weather-attributable historical
outages.

## Important analytic qualifications

1. The high-demand classification is **within-scenario**, so demand thresholds
   differ across baseline and heat_wind; it is not a common absolute MW cut-off.
2. A deterministic optimizer makes shortfalls appear when demand exceeds
   modeled available dispatch options. The observed strong association with
   load is partly inherent to that structure; do not call it an independently
   identified causal mechanism.
3. Solar is an assumed daylight proxy. Nighttime overlap cannot establish an
   empirical solar-supply mechanism.
4. No historical calibration of generators/interties, storage or independent
   study-year validation is claimed. Marginal costs and hydro energy budget
   are assumptions.
5. No statistical confidence intervals or probabilities are justified by
   these 16 deterministic runs.

## Recommended manuscript placement

Use in Results as **Exploratory SRP adequacy sensitivity and temporal context**,
followed by a Discussion cautioning that historical EIA-923/930 and weather
reconstruction remain prerequisites to claims about actual grid resilience.
Figure candidates are the CI-produced hourly shortage/demand overlays, with
labels explicitly distinguishing modeled shortfalls and assumed solar proxy.
