# July 2024: compound heat–wind interaction sensitivity to assumed BA intertie ratings

**Verified source:** [PyPSA CI 41270622515](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41270622515) and [research CI 41270622440](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41270622440), both success.

All comparisons use the same 168 observed hours in July 2024, EIA-930 demand, ERA5 point weather and partial EIA-860 thermal/wind proxies, with assumed heat and wind responses. Network edges and their ratings are entirely hypothetical: 5%, 10% or 20% of the smaller endpoint BA peak load. This is a model-structure *screening sensitivity*, not an actual transmission constraint assessment.

## Factorial nonadditivity in modeled unserved energy (MWh)

Interaction = unserved(heat+wind) − unserved(heat) − unserved(wind) + unserved(baseline).

| BA | Isolated | Hypothetical 5% | Hypothetical 10% | Hypothetical 20% |
|---|---:|---:|---:|---:|
| AZPS | 1,174.974837 | 252.517634 | 7,013.481419 | 5,364.709102 |
| BPAT | 223.721600 | 1,916.523452 | 15,487.959480 | 8,612.336506 |
| CISO | 14,038.101876 | 14,696.073670 | 805.495769 | 17,393.614673 |
| SRP | 0 | 0 | 0 | 1,269.005535 |
| **System** | **15,436.798313** | **16,865.114756** | **23,306.936668** | **32,639.665816** |

**Finding:** The regional *factorial interaction* is nonmonotonic in assumed network capacity. BPAT's interaction peaks among tested assumptions at 10%; CISO's falls sharply at 10% and rises again at 20%. The system interaction increases over these four discrete settings, but this does not establish global monotonicity. The underlying *optimized system unserved load for any fixed weather scenario* and the factorial second difference are different mathematical objects; the latter is not constrained to be monotone.

**Scientific boundary:** The experiment has not validated actual BA line topology, directional transfer ratings, technology-specific historical outage probabilities, calibrated heat demand response, or observed outage outcomes. None of these MWh figures can be interpreted as actual climate-caused blackout energy. More than one independent event, sensitivity of physical weather response and empirical BA generator coverage are needed before an inferential claim.

Reproduction: `.github/workflows/real-factorial-2024.yml`; files `outputs/network_rating_sensitivity/rating_sensitivity_by_ba.csv` and `rating_sensitivity_system.csv` in the workflow artifact. An additional CI reconciliation guard is committed separately and must be verified independently.

**Historical calibration certified: false. Actual transmission ratings certified: false.**
