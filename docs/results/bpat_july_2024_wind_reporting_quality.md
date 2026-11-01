# July 2024 BPAT EIA-930 wind reporting quality gate

**Verified CI evidence:** [run 41249650972](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41249650972).

July ERA5 plant weather coverage is **744/744 hours**; matched EIA-930 wind observation coverage is **737/744 hours** (99.06%). Missing UTC hours are July 1 00:00 through 06:00.

For all **737** matched BPAT wind rows, the official archive supplies a value in **Net Generation (MW) from Wind without Integrated Battery Storage (Adjusted)**; the field **Net Generation (MW) from Wind with Integrated Battery Storage**, including its alternate versions, is blank. The former is 737 reported values; the latter is **737 missing category values**, **not 737 observed zeros**.

The EIA-930 reporting codes distinguish WND (wind without integrated storage) and WNB (wind with integrated storage). The documentation does not establish that blank WNB means zero for this BA. See [EIA data description](https://www.eia.gov/electricity/930-content/about.html) and [EIA-930 reporting instructions (WNB/WND categories)](https://catalystcoop-pudl.readthedocs.io/en/v2025.7.0/_downloads/2297feef7fae5877a95f4a67bdc3cab2/eia930_instructions_2026-07-31.pdf).

The earlier provisional July wind subtotal computes 737 hours from the reported WND adjusted column and implicitly contributes zero for unavailable WNB. This is a **reported-category subtotal under a missing-category assumption**, *not a certified full wind fleet net-generation series*. Its historical comparison metrics (r=0.864359, MAE=10.249 pp, RMSE=13.328 pp and bias=-9.568 pp) are **provisional**. The code must not label these metrics as publication-ready total-wind validation or calibrated operational forecasting.

**Release gate:** obtain a source-grounded determination that WNB is genuinely not applicable/zero for BPAT in July 2024, or reconstruct reported total from independently verified official aggregation; otherwise keep July metrics and derived three-month comparisons explicitly provisional. February and March diagnostics are unaffected by this July category issue.

Additional limitations: WND net generation can differ from raw weather-dependent potential due to curtailment, outages and grid conditions; neither correlation nor PyPSA scenario shortfalls establish observed historical outages.
