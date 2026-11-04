# SRP gas turbine candidates: EPA CAMD / EIA crosswalk admission result (2024 inventory)

## Independent evidence and verified runs

- **2024 EIA-860 Operable** GT candidate unit identities, officially extracted and checked: [run 41873051184](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41873051184).
- **EPA / EIA unit crosswalk**: source repository [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk); pinned **master SHA `3c7d6724cddee38dfb6a06debca732c33a227ed6`** CSV, source URL and downloaded SHA256 recorded, not assumed to reflect 2024 active monitoring plans.
- **Completed source-backed admission and plant-level crosswalk diagnostics**: [GitHub Actions 41874622794](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41874622794) **SUCCESS**; accompanying [Research Methods CI 41874622169](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41874622169) **SUCCESS**. [Evidence artifact 13345458248](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41874622794/artifacts/13345458248) includes pinned source provenance, 10-generator relationship ledger, crosswalk site-row counts, raw candidate joins and conservative source-admission flags.

## EIA 2024 GT candidate inventory vs EPA crosswalk

| EIA Plant ID | EIA 2024 GT candidates | Eligible 2024 GT IDs | Pinned crosswalk rows at EIA plant ID | Pinned crosswalk rows at same numeric CAMD plant ID | GT IDs matched to CAMD unit |
|---|---:|---|---:|---:|---:|
| **141** | **5** | AF4, AF5, AF6, AF7, AF8 | **3** | **3** | **0** |
| **55129** | **2** | CTG4, CTG5 | **4** | **4** | **0** |
| **147** | **3** | KY4, KY5, KY6 | **2** | **2** | **0** |
| **TOTAL** | **10** | | **9** source site rows | **9** | **0** GT unit mappings |

**Interpretation:** All three plants are represented in the *pinned public crosswalk's plant-level rows*, but **none of the ten target annual EIA-860 GT generator IDs occurs as a direct EIA generator-ID-to-CAMD unit relationship in that crosswalk**. There may be EPA emissions records or different boiler/unit relationships not captured by these exact 2024 GT generator IDs. Absence from the crosswalk cannot establish that a generating unit is not monitored, retired, shut down, non-emitting, or physically unavailable.

The official source notes that EPA/CAMD identifies emissions-generating combustion units, whereas EIA names electricity-producing generators; multiple combustion units may feed one electrical generator, and identifiers may require manually validated/fuzzy crosswalks. Historical crosswalk vintages and monitoring-plan changes must also be considered.

## Admission gate: what may and may not be claimed

- Accepted: official 2024 EIA Operable target generator IDs, normalized plant and generator keys, official-source pinned EPA-EIA crosswalk source provenance, **site presence vs direct generator-unit match explicitly separated**, automated duplicate-key and many-to-many protections.
- NOT accepted: an *actual 2024 EPA unit-level operating-hours dataset*, a verified 2024 CAMD emissions-to-EIA GT mapping, a turbine-specific gross-load or net-load telemetry series, unit dispatch rights, heat-related equipment derating or generator outage hours.
- Even when EPA CEMS hourly `grossLoad` is available, it is **not necessarily EIA net electrical power** and can be missing or not meaningful for non-applicable configurations. EPA monitoring and emissions may be apportioned across units; do not presume a 1-to-1 mapping or treat `heatInput` or CO2 emissions as measured net electric production.
- The existing EIA-923 Page1 NG/GT plant-month output **has no individual generator ID**. EPA crosswalk absence does not resolve its unit allocation.

## Next independent verification

Targeted query of EPA CAMD/CAMPD **2024 facility/unit inventory** and **ECMPS monitoring plans** for ORIS 141, 55129, 147, paired with published EIA-860 environmental association or boiler-generator worksheets, is the next necessary step. Explicitly quantify unique unit identifiers and any valid generator links; distinguish unit-level operating/emissions evidence from independent electrical output. If no valid electrical power ground truth exists, maintain a research-gate failure rather than invent a thermal derating coefficient.

**Weather-to-generator MW derating empirically calibrated: NO. Observed SRP historical shortages, EENS, forced outages, or causal climate impacts: NOT VERIFIED.**
