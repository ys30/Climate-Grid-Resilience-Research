# SRP January 2024 Page4 versus PyPSA fuel descriptive comparison

**Provenance of numeric values:** Previously successful [real source CI Run 41480406930](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41480406930), archived artifact 13158429326. Files: `page4_month_scope_rows.csv`, `ba_capacity_identity_review.csv`, `interchange_case/modeled_generation_with_net_exchange.csv`. The **newly added comparison module and workflow have not yet been independently CI-verified**.

| Fuel code | Matched EIA-923 Page4 2024-01 net generation MWh | Modeled scenario 2024-01 generation MWh |
|---|---:|---:|
| NG | 1,889,999 | 4,190,803.39 |
| SUB | 270,273 | 435,131.655 |
| Total | 2,160,272 | 4,625,935.045 |

The observed column represents 37 exact-identity-selected Page4 generator-month records, **not total BA electric output**. Three additional Page4 observed AF1/AF2/AF3 generator records have zero January reported MWh and were excluded as multifuel candidates. The scenario column represents modeled dispatch from the partial candidate fleet under a fixed official EIA-930 demand + net export requirement, with **hypothetical static capacity derates and cost ordering**, not observed plant dispatch. The model also includes 472,996.955 MWh of **counterfactual unmet requirement**, not real-world outages.

**Never compute MAE, RMSE, relative percent difference, model bias, or a claim of fuel-specific validation using these unmatched reporting populations.** The fact that modeled generation exceeds this Page4 selected subset in NG and SUB is not proof of a historically exaggerated BA generation level. Use it only to expose model structure and investigate missing independent observed BA supply, EIA-923 source grain and EIA-930 hourly net generation.

For follow-up source checks: EIA-930 BA net generation during the same month was 5,098,927 MWh, separately verified in [CI Run 41410208607](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41410208607). Actual system net exports in EIA-930 were +2,643,306 MWh under the published positive-outbound sign convention. Do not subtract Page4 from EIA-930 and classify the difference as a particular missing technology without source reconciliation.

New script: `src/grid_resilience/page4_fuel_descriptive_comparison.py`; workflow patch: `a6355333c0af2671a123cb002f895bed42ce44ad`. **New CI verification: PENDING / NOT CONFIRMED**.

Historical calibration and full BA fleet completeness: **NOT CERTIFIED**.
