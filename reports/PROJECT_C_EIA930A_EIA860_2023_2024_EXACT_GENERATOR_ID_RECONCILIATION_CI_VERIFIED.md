# Paper C — Official 2023/2024 EIA-930A Schedule 2 × annual EIA-860 Operable exact generator-ID reconciliation

## Reproducible evidence and scope

The actual original-source identity audit succeeded: [GitHub Actions #42455058537](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455058537); [download full year-level generator-row CSVs, four-BA match summary and official SHA256 provenance (artifact 13606884233)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455058537/artifacts/13606884233). Six regression tests cover exact joins, BA inconsistencies, repeated EIA-930A BA-ID rows, fallback IDs, official annual-source bounds and EIA-860 duplicate keys. The [CI source code](../src/grid_resilience/paperc_eia930a_eia860_generator_match.py) does not guess identities from names, technology or similar capacities.

Sources: EIA official original `EIA_930A_2023_with layout.xlsx` and `EIA_930A_2024_with layout.xlsx` Schedule 2, combined on official EIA Plant ID and EIA Generator ID with **the corresponding original EIA-860 2023/2024 annual `Operable` generator roster** and official Plant-to-BA coding. Unrecognized EIA-930A fallback Plant/Generator IDs are intentionally **not accepted as certified EIA-860 identities** even if a string happens to match. Identical within-BA source keys are **retained as ambiguous raw rows**, not dropped, summed as independent installed capacity, or classified as unique matched generators.

EIA-930A's own workbook `Layout Details` identifies **preliminary February 2025 EIA-860 monthly source** as its generator information source for data-year 2023, and **preliminary August 2025 monthly source** for 2024. Therefore this strictly defined same-*data-year* comparison to annual EIA-860 has **unmatched vintage differences**; residual discrepancies do not by themselves demonstrate missing physical equipment or actual availability.

## CI-verified category reconciliation (record counts, not distinct physical generators)

| BA | EIA-930A 2023 records | 2023 exact ID + same BA | 2023 ID match / BA conflict | 2023 not in annual Operable | 2023 no formally recognized ID | 2023 duplicate same-BA/ID rows |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 131 | 114 | 12 | 0 | 5 | 0 |
| BPAT | 300 | 294 | 5 | 0 | 1 | 0 |
| CISO | 1,619 | 1,348 | 11 | 58 | 111 | **91** |
| SRP | 94 | 94 | 0 | 0 | 0 | 0 |
| **Total** | **2,144** | **1,850** | **28** | **58** | **117** | **91** |

| BA | EIA-930A 2024 records | 2024 exact ID + same BA | 2024 ID match / BA conflict | 2024 not in annual Operable | 2024 no formally recognized ID | 2024 duplicate same-BA/ID rows |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 133 | 117 | 12 | 0 | 4 | 0 |
| BPAT | 298 | 292 | 6 | 0 | 0 | 0 |
| CISO | 1,434 | 1,165 | 9 | 35 | **225** | 0 |
| SRP | 95 | 93 | 0 | 0 | 2 | 0 |
| **Total** | **1,960** | **1,667** | **27** | **35** | **231** | **0** |

Category totals per BA sum exactly to the source-record denominators. These are **raw EIA-930A annual Schedule 2 rows** classified by conservative same-year annual EIA-860 identifier and BA checks; they are **not** unique nationwide generators, MW of resource availability, hourly operating units, measured generation, verified transmission capacity or actual electricity shortages.

The 2023 CISO schedule contains **91 raw row occurrences with repeated same BA/Plant ID/Generator ID combinations**. The module preserves the source but **does not certify a unique generator identity/capacity contribution for those rows**. EIA-930A 2024 CISO has **225 source records without a formally recognized EIA-860 ID** and another **35 EIA-860-ID-recognized records not found in the 2024 annual Operable population**; both groups require an original source identity/vintage investigation before assigning physical resources.

## Why the annual capacity sums cannot yet be 'calibrated'

- EIA-930A Schedule 2 is an **annual BA-reporting population**, not an hourly dispatch or outage data source.
- BA coding can differ between the EIA-930A reporting BA and EIA-860's plant location/control BA, especially where dynamic and pseudo-tied resources are involved. A **BA conflict is an observation**, not proof one institution misreported the resource.
- EIA-930A generators represented by nameplate fields in the official workbook may use EIA-860 **preliminary monthly vintages that differ from the independent annual EIA-860 extraction**. Exact ID mismatches or annual MW differences cannot be treated as actual physical discrepancies until vintage-matched.
- Natural gas, coal, wind, hydro, solar, batteries and pumped storage require source-technology/fuel and availability crosswalks. Simply summing the original same-year annual EIA-860 Operable roster and comparing to EIA-930A reported capacity would conflate unmatched source definitions and BA report scope.
- The current PyPSA screening model with generic thermal and wind proxies, hypothetical BA links and an incomplete fleet remains **not calibrated to real hourly supply adequacy, outages or EENS**.

## Immediate next scientific gate

1. **Source-vintage-matched identity check:** where available, obtain the original **February 2025 EIA-860 preliminary monthly** inventory for EIA-930A 2023 and **August 2025 preliminary monthly** for EIA-930A 2024, or prove their absence. This distinguishes official vintage differences from genuine source-population differences.
2. **Duplicate and missing-ID follow-up:** inspect CISO 2023's 91 same-BA/ID repeated entries and CISO 2024's 225 unrecognized-ID entries for source patterns. Do not silently de-duplicate or invent IDs.
3. **Technology inventory by matched confidence level:** report verified matched-identity technology/nameplate in each BA separately from BA conflicts, fallback IDs and older-vintage unmatched sources. Any MW ratio must state its exact numerator/denominator and whether the technologies and BA source populations are comparable.
4. **Physical model calibration (not yet complete):** obtain BA-appropriate hourly available generation, observed balancing energy, storage energy state, actual interchange deliverability and transmission limits, then rebuild baseline before asserting physical climate impact or blackout/shortage outcomes.

**Current publication classification:** Source-data provenance and annual roster identity reconciliation are CI verified; they support a stronger supplementary data section and model coverage limitations, but do not validate observed system reliability.
