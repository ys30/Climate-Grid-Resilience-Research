# EIA-930 February 2024 BA accounting: observed diagnostics

Source: official EIA-930 Balance and Interchange January–June 2024 six-month files, processed in GitHub Actions. Last verified runs:

- Bilateral-versus-total interchange reconciliation: https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41161269917
- Hourly energy-accounting residual: https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41159032456
- Raw-versus-adjusted comparison: https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41159284417

All values below concern four BAs during **February 2024**, with 696 UTC hourly records per BA. EIA hour-ending timestamps were shifted by one hour when converted to PyPSA hour-starting snapshots.

| BA | sum(bilateral)-reported total interchange (MWh) | sum absolute bilateral difference (MWh) | signed G-D-I residual (MWh) | hours exceeding balance residual threshold |
|---|---:|---:|---:|---:|
| AZPS | 0 | 0 | 0 | 0 |
| BPAT | +221 | 327 | -3,152,089 | 696 |
| CISO | 0 | 0 | -213,709 | 545 |
| SRP | +4 | 4 | 0 | 0 |

The bilateral aggregation reproduces the EIA Balance total interchange nearly exactly. It therefore **does not explain** the large BPAT accounting imbalance; CISO matches exactly. Adjusted versus raw series yield identical signed residuals in this observed month.

These observations **do not establish** that the residual is transmission loss, missing generation, a measured reliability deficit, a physical transfer constraint, or an error in any particular EIA field. Further investigate EIA published definitions, corrections, balancing-authority metering, embedded entities, interchange conventions, and system boundaries. Do not use `generation-demand` as verified interchange or interpret directed bilateral reports as physical `Line` capacities.

**Historical calibration remains uncertified.** The February PyPSA solve currently mixes observed EIA-930 hourly demand with hypothetical gas fleet 1.5× peak, 100% availability, and no links.
