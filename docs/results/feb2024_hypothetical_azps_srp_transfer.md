# Paired AZPS–SRP hypothetical transfer sensitivity: February 2024

**Verified source:** [GitHub Actions run 41267838381](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41267838381), success. All scenarios solve the identical 696-hour real EIA-930 demand and eligible EIA-860 nameplate capacity screening model with **illustrative** fixed costs, uniform generator availability and an **assumed lossless AZPS–SRP link**.

| Hypothetical transfer rating MW | AZPS shortfall MWh, availability 70% | AZPS shortfall MWh, availability 40% |
|---|---:|---:|
| 0 | 3,553.52 | 601,098.08 |
| 250 | 704.80 | 431,743.52 |
| 500 | 0.56 | 282,157.16 |
| 1000 | 0 | 79,967.04 |

At 40% hypothetical availability, a 1,000 MW hypothetical Link reduces AZPS simulated unserved energy by **521,131.04 MWh (86.70%)**, without eliminating it. At 70%, the same assumed Link removes 3,553.52 MWh of simulated shortage. The 0.56 MWh residual at 500 MW should not automatically be labeled numerical noise.

**Not claims of physical system performance:** observed monthly EIA-930 interchange is not a MW transfer rating; AZPS–SRP link topology, available transfer capability and dispatchable imports have *not* been verified. Uniform generator availability is not historical plant operation, and the modeled shortages are not actual outages. Both reporting and topology uncertainties remain material.

**Reproducibility:** `.github/workflows/feb2024-eia-capacity-screening.yml` runs `feb2024_hypothetical_transfer_pairs.py`. A later commit adds system-wide shortfall monotonicity and shortage-redistribution diagnostics, whose CI evidence must be checked separately.

**Historical calibration certified: false.**
