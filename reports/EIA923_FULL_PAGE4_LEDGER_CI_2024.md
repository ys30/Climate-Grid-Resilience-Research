# 2024 EIA-923 Page-4 full extracted observation ledger: CI-verified

**Official-source workflow:** [run 41400664393](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41400664393) (success), code commit `4b6aa325f997bfb380b61ea3c0805774be7f49b2`, [artifact 13120623806](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41400664393/artifacts/13120623806).

## Audited source-scope results

| Test | Actual workflow output |
|---|---:|
| EIA-923 Page-4 generator-month rows in targeted extraction | 3,392 |
| Exact identity present in 2024 EIA-860 Operable list | 3,324 |
| Outside that selected Operable list | 68 |
| Observed reported net generation summed over all extracted rows | 123,780,484.277 MWh |

The 68 unmatched generator-month records are **retained**, not imputed or deleted. They contribute 262,307 MWh to the reported-source total, as confirmed by the separate EIA-860 retired-status observation ledger. Some of these generator identities appear in EIA-860 2024's Retired and Canceled sheet; in-year energy reporting and status dates require independent reconciliation.

These figures describe the **limited Page-4 source extraction** and cannot be presented as complete four-BA electricity generation: Page-1 hydro/PS uses a distinct observational sheet/grain, no full 2024 BA fleet crosswalk is certified, and time-varying fleet membership has not been established. Combining Page-1 and Page-4 totals without verified non-overlap risks double counting.

## Next validation gates

1. Build a source-specific BA–technology–month observational coverage table with explicit missingness and prime-mover/multifuel exclusions.
2. Establish EIA-860 2024 year-scoped plant/BA and generator active-status coverage; reconcile retired-source reported MWh independently.
3. Create actual full-calendar-month PyPSA generation by matched BA and technology. The existing 168-hour adequacy screen is not a substitute for monthly modeled electricity generation.
4. Report observed-versus-modeled training and withheld-year metrics only after equivalent annual series exist.

**Historical calibration certified: NO.**
