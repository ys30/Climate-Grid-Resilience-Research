# July 2024 real-input four-scenario screening: BA-level nonadditivity

**Verified execution:** [GitHub Actions 41269398629](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41269398629), success; [research CI 41269398639](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41269398639), success.

This is a **168-hour (July 1–7, 2024), four-BA, observed-input screening**, using actual EIA-930 demand and ERA5 temperature/wind evidence with year-end EIA-860 partial-fleet capacity. The thermal dispatch representation, weather-to-demand/availability response, and inter-BA connections are assumptions. This is **not historically calibrated** and does **not measure observed power outages**.

## System-level simulated unserved load (MWh)

| Scenario | Unserved energy MWh |
|---|---:|
| Baseline | 271,730.350 |
| Heat only | 397,760.110 |
| Wind only | 391,034.532 |
| Heat + wind | 540,371.228 |

The factorial nonadditivity is I = U(heat+wind) − U(heat) − U(wind) + U(baseline) = **+23,306.936 MWh** based on printed rounded scenario totals, and **+23,306.937 MWh** based on the workflow's unrounded machine calculation.

## BA-level modeled factorial interaction

| BA | Interaction MWh | Share of system interaction |
|---|---:|---:|
| BPAT | +15,487.959480 | 66.45% |
| AZPS | +7,013.481419 | 30.09% |
| CISO | +805.495769 | 3.46% |
| SRP | 0 | 0.00% |
| **System** | **+23,306.936668** | **100%** |

Each interaction uses the *same matched BA* across four runs. The BA-level contrasts reconcile to the system total (subject to rounding). Results are recorded in `factorial_interaction_by_ba.csv` and `factorial_interaction_summary.json` in the CI artifact.

## Interpretation and next validation

BPAT dominates the positive modeled interaction. This is **not** evidence that BPAT is inherently more weather-vulnerable. In particular:

1. Compare matched isolated-network and assumed-link four-scenario runs; quantify how much of BPAT's 15,487.96 MWh interaction changes under the assumed network.
2. Check the wind availability response and thermal proxy/partial fleet for BPAT, with explicit sensitivity bounds.
3. Repeat across independent observed weeks or months, verify consistent source/time coverage, and report null/negative effects when found.
4. Before making a reliability claim, validate full technology and plant-to-BA coverage, grid links/transfer ratings, generation and storage treatment, and ex-post historical generation matching.

**Historical generation calibration certified: false. Physical transmission validation certified: false. Compound-weather causal attribution certified: false.**
