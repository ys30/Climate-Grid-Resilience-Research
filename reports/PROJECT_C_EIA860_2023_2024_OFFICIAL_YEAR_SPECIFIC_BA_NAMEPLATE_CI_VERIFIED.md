# Paper C — Official 2023 vs 2024 EIA-860 year-specific four-BA nameplate inventory

**Source-verified workflow:** [GitHub Actions 42441328634](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441328634), SUCCESS. [Annual-source SHA256 records, 2023/2024 four-BA year-specific nameplate candidate CSV and attrition scope artifact](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441328634/artifacts/13601444011). [Parser](../src/grid_resilience/paperc_year_specific_eia860_inventory.py). Source: official U.S. EIA EIA-860 annual generator and plant archives (2023 and 2024), Operable tab, Plant BA annual mapping. The original downloaded archives are not stored in this compact result artifact; source URLs and exact hashes are stored.

## Evidence scope

The source audit recovered **3,132 four-BA Operable generator records for 2023** versus **3,268 for 2024**. Strict single-fuel, positive-nameplate, supported-technology and non-storage screens selected **2,546** (2023) versus **2,625** (2024). **586 / 643** four-BA rows respectively were excluded from the candidate screen; these are explicitly **not** zero-capacity, zero-output or absent electrical resources. Plant-level BA codes and generator nameplate ratings do not identify electrical topology, unit hourly availability, DER/reporting completeness, retirement dates within the event, physical transfers or real shortfall. These candidate annual nameplates must **not** be described as full BA firm capacity.

### Source-audited gas and wind candidates (nameplate MW)

| BA | 2023 gas | 2024 gas | 2023 wind | 2024 wind |
|---|---:|---:|---:|---:|
| AZPS | 2,290.6 | 2,471.2 | 412.5 | 628.5 |
| BPAT | 2,166.0 | 2,171.5 | 3,617.1 | 3,617.1 |
| CISO | 31,140.3 | 31,186.2 | 6,179.6 | 6,352.2 |
| SRP | 7,568.6 | 7,655.1 | 63.0 | 226.0 |

Annual source candidates are materially different in some BAs. For example, AZPS wind increases by **216.0 MW**, SRP wind by **163.0 MW**, and AZPS gas by **180.6 MW** from the 2023 to 2024 roster, within the strict mapping. Therefore the previous 2023/2024 factorial comparison which *deliberately froze a 2024 partial generator proxy* is a **fixed-structural-assumptions simulation**, not a year-specific empirical fleet replay. That distinction is now supported by *independent official annual rosters*, rather than merely a caveat.

Other supported technology candidates are retained in the source CSV. Solar changes also matter, but are **omitted** from the previous gas/wind-only factorial model, as are many other resources. Do not infer full-fleet adequacy from the gas/wind comparison.

## Manuscript implications and remaining work

1. Keep the previously passed [source-year model sensitivity figure 42441181359](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441181359) labeled as *controlled annual-fleet-frozen sensitivity*. It is not invalid as a model experiment; it is **not** a year-specific physical forecast.
2. A future second sensitivity may substitute the distinct 2023 and 2024 annual BA gas/wind nameplate candidate scenarios, **while holding the same counterfactual thermal-load and wind derating specification**, with transparent results and an omitted-fleet diagnostic. Do not silently overwrite the prior fixed-fleet experiment.
3. Before any physical adequacy claim, validate BA generator identity and status, multi-fuel/storage and excluded resources, monthly generation against EIA-923, actual hourly fuel dispatch from EIA-930, intertie deliverability and generation outages; estimate actual **available**, not merely nameplate, MW.

The correct conclusions remain: observed BA load and representative-point weather source periods are real; heat–wind response and unserved load are hypothetical model outputs; neither model outcomes nor nameplate inventory establish historical EENS or actual outages.
