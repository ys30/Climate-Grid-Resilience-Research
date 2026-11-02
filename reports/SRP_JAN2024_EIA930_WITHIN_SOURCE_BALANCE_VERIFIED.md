# EIA-930 actual SRP January 2024 generation–interchange–demand balance

**Verified [GitHub Actions run 41410208607](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41410208607)**, implementation commit `7fd684fc875a0f9950b9bcf9f9fcf6587412fb17`.

The workflow combines source-preserved EIA-930 Balance CSVs for 2023 Jul–Dec and 2024 Jan–Jun, selects the complete **744 hours** of January 2024 UTC, and reads from the **same EIA-930 reporting source**: `Demand (MW)`, `Net Generation (MW)`, and `Total Interchange (MW)`. EIA labels timestamps as **UTC Time at End of Hour**, normalized to hour starts by subtracting one hour. The audit verifies a continuous UTC month, nonduplicate timestamp keys, and finite observations.

| Official monthly sum of hourly MW over 1-hour intervals | MWh |
|---|---:|
| Net generation | 5,098,927 |
| Total net interchange (positive outbound) | 2,643,306 |
| Demand | 2,455,626 |
| Net generation minus interchange minus demand | **−5** |

The maximum absolute hourly balance residual was **1 MW**, and **5** hourly records had nonzero residuals. This is a highly consistent EIA-930 *within-source* accounting identity, but the exact reason for tiny deviations has not been established; do not attribute to rounding with certainty.

**Key interpretation:** The **2,643,306 MWh positive monthly net interchange** is an actual EIA-930 BA-reported outflow under the official sign convention. The 295,354 MWh gap previously observed between EIA-930 demand and a subset of EIA-923 Page-4 plant generation must **not** be interpreted as observed imports or physical unserved energy.

**Important cross-system caution:** The EIA-923 Page-4 2,160,272 MWh generator-month extracted sample and Page-1 HY/PS January +883 MWh are source-grain and population subsets, **not interchangeable with EIA-930 BA total net generation** and cannot be used to independently close the whole BA balance. In particular, using EIA-930 demand as a standalone isolated-BA load and matching all dispatched generation to it omits the actual interchange sink. This is a structural limitation of the existing PyPSA screen.

Next upgrade: represent net export explicitly (at least as a verified hourly exogenous sink) while retaining the fact that the screen's 7,453.1 MW model fleet is only a partial capacity subset. Independently check the full generation supply scope and validate EIA-923 technology definitions before comparing dispatch. **Historical PyPSA calibration: NOT CERTIFIED.**
