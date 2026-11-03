# SRP January 2024 — hourly firm capacity sensitivity (partial-fleet scenario)

## Source and analysis status

This is a **counterfactual supply-screening result**, not recorded electricity shortage or a historical capacity adequacy finding. Source: genuine successfully uploaded [GitHub Actions run 41542019155](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155) [artifact 13186838868](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155/artifacts/13186838868), `hy_ps_case/baseline_hourly_diagnostics.csv`. The capacity-limited partial EIA-860/EIA-923 inventory has **6,294.045 MW** of illustrative static available output and an imputed **472,996.955 MWh** of unserved *model requirement*, occurring over **601 hours**.

For each of 744 observed-demand/observed-net-exchange hours, with modeled baseline gap `u_t >= 0` and incremental *perfectly firm* capacity `k`, the best-case remaining gap is:

```
U_remaining(k) = sum_t max(u_t - k, 0)
Best-case gap avoided(k) = U_baseline - U_remaining(k)
```

This correctly accounts for **hourly** deficit timing instead of the overly loose bound `k * 744`.

| Extra perfectly firm MW | Remaining modeled gap MWh | Positive-gap hours | Avoided share |
|---:|---:|---:|---:|
| 0 | 472,996.955 | 601 | 0% |
| 100 | 413,827.900 | 580 | 12.509% |
| 250 | 331,693.825 | 515 | 29.874% |
| **390.4** | **263,003.965** | **463** | **44.396%** |
| 500 | 215,083.505 | 411 | 54.528% |
| 1,000 | 60,770.820 | 204 | 87.152% |
| 1,500 | 6,986.065 | 43 | 98.523% |
| 2,025.955 | 0 | 0 | 100% |

### Reinterpretation of excluded 390.4 MW

The existing `excluded_capacity_maximum_contribution.json` identified **three excluded generator identities totaling 390.4 MW nameplate**. The prior monthly upper bound of `390.4 × 744 = 290,457.6 MWh` was deliberately loose. Hourly deficit alignment tightens their **maximum possible** avoided model gap to **209,992.99 MWh**, leaving at least **263,003.965 MWh** of the same *counterfactual modeled gap* if *only these three* were added and all were assumed perfectly available with no transmission limitations.

This does **not** mean the excluded generators are eligible, were running, or could deliver that much electricity. Annual inventory, seasonal resource availability, fuel, hydro energy limits, storage, unit commitment and internal transmission constraints are unmodeled.

### Reproducibility

`src/grid_resilience/srp_firm_capacity_frontier.py` now computes the frontier directly from complete verified hourly baseline diagnostics and fails on malformed timestamps, nonfinite values or nonconservation. `tests/test_srp_firm_capacity_frontier.py` tests its numerical contracts. Both dedicated and full SRP GitHub workflows now include it; **new CI has not yet been confirmed successful**. Source-artifact scenario numbers above were independently calculated in the working session.

**Historical calibration certified: NO. Historical outages inferred: NO.**
