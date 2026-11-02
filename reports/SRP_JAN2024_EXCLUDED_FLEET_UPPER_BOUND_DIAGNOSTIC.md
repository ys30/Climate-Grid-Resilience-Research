# SRP January 2024 excluded generator nameplate upper-bound sensitivity

**Provenance:** Previously successful [real-input CI run 41480406930](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41480406930), artifact 13158429326. Independently reproduced the arithmetic from `ba_capacity_identity_review.csv` and `bidirectional_case/bidirectional_boundary_screen.json` in this session.

| Quantity | Result |
|---|---:|
| Excluded multi-fuel generator IDs | 3 (AF1, AF2, AF3) |
| Sum EIA-860 nameplate | 390.4 MW |
| January duration | 744 hours |
| Extreme maximal contribution at 100% nameplate output 24/7 | 290,457.6 MWh |
| Prior modeled counterfactual unmet energy, real demand+net exports | 472,996.955 MWh |
| **Minimum residual unmet requirement with these additions alone** | **182,539.355 MWh** |

This is an *upper-bound/counterfactual arithmetic diagnosis*, **not observed hydro/gas capacity utilization**. It assumes the missing 390.4 MW can serve every hour continuously, which ignores scheduled/forced outages, fuel constraints, ramping, dispatch, network constraints and multi-fuel handling. Accordingly the actual incremental contribution could be less. The existing partial-screening model was never calibrated to historical plant dispatch.

Implemented reusable `src/grid_resilience/excluded_capacity_upper_bound.py` and wired it to the existing full-month source CI on commit `5fe9457fe47361234219a98653737b0868a96fa3`. The new workflow run has **not been confirmed**; the calculations above were independently reproduced from a **previously successful archival artifact**, not by asserting the new CI is green.

**Interpretation:** Reinstating only AF1/AF2/AF3 cannot independently close the model gap under the fixed observed net export schedule. The next major task is source-defined full BA supply inventory, renewable/hydro storage/interchange representation and generator availability profiling. No historical loss-of-load conclusion is justified.

**Historical calibration certified: NO.**
