# SRP January 2024 generator identity audit — recovered measured results

**Provenance:** [successful historical CI run 41480406930](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41480406930), Artifact **13158429326**, files `page4_month_scope_rows.csv` and `ba_capacity_identity_review.csv`. This report's exact-ID matching statistics were **independently recomputed from the archived source files** after the run; they were not generated or verified by the newer `exact_generator_scope_audit.py` CI, whose current run status is not established.

Normalize plant IDs by stripping leading zeroes; match on exact `(plant_id, generator_id)`, preserve all observed 2024-01 rows and signed net MWh. `screening_candidate` is the actual eligibility flag exported by the EIA-860/Page4 join, not a fuel-class proxy.

| Classification | Generator rows | Observed net MWh | 2024 EIA-860 nameplate MW |
|---|---:|---:|---:|
| Exact screened NG | 35 | 1,889,999 | included in below total |
| Exact screened SUB | 2 | 270,273 | included in below total |
| **All exact screened** | **37** | **2,160,272** | **7,453.1** |
| Reviewed but excluded multi-fuel NG (AF1/AF2/AF3, plant 141) | **3** | **0** | **390.4** |
| Missing from identity review | **0** | **0** | n/a |
| **Page4 source total** | **40** | **2,160,272** | **7,843.5** |

Exact screened generator-row share: **37/40 = 92.5%**. Exact screened observed net MWh share: **2,160,272/2,160,272 = 100%**; this is also 100% of *absolute signed Page4 source MWh* because none of these 40 observations contributes negative January energy.

The three excluded multi-fuel units each report zero January generation in the **selected Page4 sample**. Their excluded **390.4 MW nameplate** nonetheless matters for capacity adequacy counterfactuals and does not imply these units could all generate at that output continuously.

**Crucial bounds:** Page4 generator-month data are only a partial observed source population. **100% source-selected observed MWh coverage does not mean 100% BA generation, capacity, dispatch, renewable, storage or import/export coverage.** In the distinct EIA-930 BA accounting report, January net generation sums to 5,098,927 MWh. Do not interpret difference with Page4 2,160,272 MWh as certain missing physical generation or infer its fuel type without a reconciled reporting crosswalk. EIA-923 Page1 HY + PS source contributes +883 MWh net but at a different reporting grain and should not be silently added to Page4.

**Research implication:** Prioritize BA operational supply population and EIA-930/EIA-923 reconciliation over repeatedly inventing capacity derates. The 472,996.955 MWh model supply gap under exogenous observed exports is not historical unserved energy.

**Verification statuses:** exact matching arithmetic from downloaded previously green artifact: **CHECKED**; new GitHub exact generator CI: **NOT CONFIRMED**; full BA fleet completeness and historical PyPSA calibration: **NOT CERTIFIED**.
