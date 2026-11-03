# SRP January 2024: official EIA-923 Page 1 to EIA-860 Plant BA fuel candidates

## Verified source and scope
Successful [GitHub Actions run 41742692552](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41742692552) and successful [research methods CI 41742692598](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41742692598), code commit `05d6a874963a88b0b60bd06b8ed81bfa60f0e52f`. Official EIA-923 2024, EIA-860 2024 and EIA-930 January source files were independently downloaded in that workflow with SHA-256 provenance; [artifact 13281159163](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41742692552/artifacts/13281159163) contains the source-specific evidence and `page1_eia860_fuel_candidate_manifest.json`.

**Purpose:** identify plausible *plant/prime-mover/fuel* candidates, not allocate reported EIA-923 Page 1 net-generation MWh to a particular EIA-860 Generator ID or certify hourly deliverability.

| Verified January SRP metric | Value |
|---|---:|
| EIA-923 Page 1 original source rows | 61 |
| Unique Page 1 plant IDs | 35 |
| EIA-860 2024 Plant BA operable generator IDs | 108 |
| Page 1 source rows whose plant is absent from EIA-860 SRP Plant BA | 0 |
| Page 1 rows with same-plant same-prime-mover fuel-code candidate in EIA-860 Energy Source 1/2 | 60 |
| Rows with same plant and prime mover but no corresponding Energy Source 1/2 code | 1 |
| Signed Page 1 source generation total | 5,306,052.001 MWh |
| Source rows with candidate match, signed total | 5,305,891.610 MWh |
| Source rows without Energy Source 1/2 match, signed total | 160.391 MWh |

The one fuel-code mismatch is **Plant 6177, ST/DFO, +160.391 MWh**. EIA-860 2024 lists its two operable ST units CO1/CO2 as primary source SUB with no second energy source recorded. This is an *audit flag*, not proof that the DFO amount was incorrectly reported or that it should be reassigned to coal. EIA-860 may not represent every supplemental/startup fuel in the first two energy-source fields, and EIA-923 Page 1 has a different aggregation grain. Investigate official fuel-code definitions and complete EIA-860 source columns before any definitive fuel reconciliation.

For context, the larger cross-source differences remain: **EIA-923 Page 1 natural gas +477,752.304 MWh versus EIA-930 Natural Gas**, and **Page 1 ST/SUB −266,720.390 MWh versus EIA-930 Coal**. These are numerical comparisons of non-equivalent reporting scopes, not model fit errors or proof of missing production. The current candidate crosswalk does **not** resolve those differences merely because most Page 1 rows find a possible generator fuel-code match.

## Scientific acceptance gates
1. Keep all 61 Page 1 rows, including three repeated coarse ST/NUC keys at Plant 6008, as separate valid reported-source observations. No generator-level allocations are certified.
2. Read Page 1 fuel information and EIA-860 generator energy sources as source evidence; a candidate generator list may contain several generators, and source MWh cannot be distributed between them without a validated allocation rule.
3. Review Plant 6177's DFO reporting and EIA-860's additional fuel/source fields, plus the other plants with major apparent NG/coal scope differences.
4. Diagnose contractual dispatch and BA operational boundary differences across EIA-923 and EIA-930 before fitting plant-level dispatch or adding EIA-860 nameplate capacities to modeled available supply.
5. Retain explicit flags: `unique_generator_assignment_certified=false`, `physical_ba_entitlement_certified=false`, and `historical_calibration_certified=false`.

**No historical outage inference, probabilistic EENS/LOLE estimate, or climate-attributable causal conclusion is supported by this accounting audit.**
