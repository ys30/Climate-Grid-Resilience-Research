# EIA-930 balance discrepancy: official definition and interpretation

**Official reference:** https://www.eia.gov/electricity/930-content/about.html

EIA defines hourly demand as **net generation minus total net interchange**, where positive interchange indicates net exports and negative indicates net imports. The raw physical-data convention aims to exclude virtual transfers from pseudo-ties and dynamic scheduling, but EIA explicitly warns that some reporting areas cannot fully exclude these arrangements. BA generation may be a metered subset and may not agree with other electricity publications. These are candidate explanations for imbalances, **not proven causal findings**.

The official EIA-930 source explicitly notes:

- System energy balance generally requires `demand = net_generation - total_interchange`.
- Pseudo-ties and dynamic scheduling can affect reporting boundaries.
- Metering availability, corrections, anomalous data, and balancing arrangements vary across BAs.
- Bilateral interchange is collected later than initial total interchange and BA counterpart reporting can disagree.
- Reported hourly raw BA values are published without imputation.

**Verified February 2024 project diagnostics** (696 hours/BA):

| BA | G-D-I MWh | Bilateral minus total interchange MWh | Hourly balance flags |
| --- | ---: | ---: | ---: |
| AZPS | 0 | 0 | 0 |
| BPAT | -3,152,089 | 221 | 696 |
| CISO | -213,709 | 0 | 545 |
| SRP | 0 | 4 | 0 |

These establish that bilateral reporting sums nearly match BA total interchange for all four BAs, but they **do not explain** BPAT/CISO energy residuals.

## Next diagnostics

1. Check whether EIA-930 reported total net generation matches the sum of reported generation by energy source hourly; this distinguishes generation-component inconsistency from demand/interchange inconsistency.
2. Investigate month/day/hour anomaly concentration and reported/imputed/adjusted series.
3. Do not force balance by replacing measured interchange with `G-D`, and do not treat measured interchange as a known `Line` thermal rating.
4. Keep empirical calibration certification false until reconciliation, physical model parameters and held-out validation are demonstrated.

Sources: official EIA-930 information page above and historical reproducible workflow logs under `actions/runs/41161269917`, `41159032456`.
