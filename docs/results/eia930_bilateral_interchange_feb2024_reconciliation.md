# Official February 2024 EIA-930 bilateral interchange reconciliation

**Source:** [successful GitHub Actions run 41256532481](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41256532481).

The official EIA-930 *INTERCHANGE* and *BALANCE* 2024 Jan–Jun archives were independently ingested. February 2024 contains 696 matched hourly observations for each of four balancing authorities. The metric below sums hourly absolute deviations between the sum of **reported directed bilateral interchange** and the BA's **reported total interchange**; it is not a line-capacity measure.

| BA | Matched hourly observations | Sum of absolute hourly discrepancies (MWh) |
|---|---:|---:|
| AZPS | 696 | 0 |
| BPAT | 696 | 327 |
| CISO | 696 | 0 |
| SRP | 696 | 4 |
| **Total** | **2784** | **331** |

The official dataset supplies consistent directed bilateral totals for most BA-hours; the 331 MWh aggregate absolute discrepancy requires localization before concluding perfect agreement. A comparison of *net sums* must not substitute for these absolute differences because positive and negative errors can cancel.

**Research scope:** BA exchange-flow accounting, **not** facility-level transmission topology, thermal transfer capability, intertie capacity, or historical unserved demand. No calibrated PyPSA transfer constraints can be inferred from these four rows alone.
