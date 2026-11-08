# Paper C — Four-BA technology-by-technology reporting-roster nameplate coverage (2023/2024 EIA-930A vs cited 2025 EIA-860M)

## Verified execution and primary source lineage

- [Exact-source annual EIA-930A × cited February/August 2025 EIA-860M identity audit — SUCCESS #42455881405](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455881405).
- [Four BA × 13 technology categories × 2023/2024 original-generator matched-nameplate audit — SUCCESS #42460680310](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42460680310), with five regression tests, original download SHA256, 104 BA/category/year rows, source identity-classification tables and unmatched-source-row CSV. [Download source tables and manifests (artifact 13609079899)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42460680310/artifacts/13609079899).
- [Reproducible supplementary BA × technology matching-fraction heatmap — SUCCESS #42460821029](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42460821029), using identical archived CI inputs with missing-denominator guard and provenance-validated source totals. [Download publication PDF/PNG and full matrix CSV (artifact 13609294270)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42460821029/artifacts/13609294270).

**Important source-year distinction:** EIA-930A *data year* **2023** cites the **February 2025 EIA-860M** preliminary generator inventory. EIA-930A data year **2024** cites the **August 2025 EIA-860M** inventory. These are two **different 2025 inventory snapshots**, not measured 2023 versus 2024 generator nameplate or 2023/2024 hourly operating levels. Changes across the table cannot be interpreted as the 2023–2024 physical buildout rate.

For each BA + technology, the:
- **Denominator** is the sum of *nonmissing* nameplate MW for generators in the given cited **2025 EIA-860M Operating** inventory, using **the BA code assigned within that monthly file**.
- **Numerator** is the sum of those exact-month generator nameplates that match **unique, formally recognized EIA-930A Schedule 2 Plant ID + Generator ID and the same BA**, with no duplicated source generator identity.
- **Matched fraction** = numerator / positive denominator; if denominator is zero, percentage is **N/A**, not 0%. Missing monthly nameplate records are tracked in the denominator validity count, and cannot be silently assigned zero MW.

This is *strict source reporting-population nameplate matching*. An unmapped EIA-930A row is **not** a verified absent generator. A BA mismatch is **not** evidence that a physically connected tie-line is missing. Neither monthly nameplate ratio nor annual EIA-930A Schedule 2 appearance identifies **available hourly MW, dispatch, import deliverability, storage energy state, actual reliability, blackouts or EENS**.

## Whole four-BA source roster totals

| Cohort | Preliminary 2025 EIA-860M monthly Operating nameplate across four BAs (MW) | Uniquely same-BA EIA-930A identity matched monthly nameplate (MW) | Matched row count | Original 930A rows not included in unique same-BA matching |
|---|---:|---:|---:|---:|
| 2023 EIA-930A cohort, Feb 2025 inventory | **143,211.9** | **116,984.7** | **1,869** | 275 |
| 2024 EIA-930A cohort, Aug 2025 inventory | **149,420.7** | **126,851.0** | **1,692** | 268 |

These are **nameplate inventories** of equipment, some of which cannot generate simultaneously; storage nameplate MW is a power rating, not available MWh. No availability-factor, outage-rate, capacity-factor or firm capacity assumption is applied. The unmatched raw-source-row counts retain no-ID entries, other BA assignments, undetected annual-vintage counterparts and ambiguous duplicates without adding invented MW.

## Key 2024 EIA-930A cohort — source-month **August 2025** technology examples

| BA | Technology | Monthly Operating nameplate (MW) | Unique EIA-930A same-BA ID matched nameplate (MW) | Source-roster nameplate match share |
|---|---|---:|---:|---:|
| CISO | Natural gas | 32,259.3 | 29,064.4 | 90.1% |
| CISO | Solar | 24,164.4 | 21,394.8 | 88.5% |
| CISO | Battery storage | 14,484.6 | 11,306.5 | 78.1% |
| CISO | Wind | 6,394.7 | 5,552.4 | 86.8% |
| CISO | Conventional hydro | 6,728.0 | 5,167.1 | 76.8% |
| BPAT | Conventional hydro | 21,686.6 | 20,419.7 | 94.2% |
| BPAT | Natural gas | 2,179.0 | 1,281.2 | 58.8% |
| AZPS | Solar | 2,489.6 | 1,195.7 | 48.0% |
| AZPS | Battery storage | 2,236.8 | 548.0 | 24.5% |
| SRP | Natural gas | 8,563.4 | 7,323.3 | 85.5% |

All **13 class** results per BA and year, including pumped hydro, nuclear, coal, petroleum, geothermal, other storage, other and unknown, are in the CI source artifact. The classifications are a transparent **technology/source-fuel screening crosswalk**; they are not an EIA-approved technology redefinition. For code review, see [classification and source-audited nameplate calculation](../src/grid_resilience/paperc_eia930a_technology_nameplate.py).

## Consequences for the existing PyPSA baseline

The current Paper C four-BA simulation represents generic thermal (gas-like) and wind, with hypothetical BA exchange capability and ERA5 single-point weather proxies. The audited *reporting-population nameplate inventory* contains **substantial solar, conventional hydro, nuclear, batteries and pumped hydro** (different by BA) that the simplified model has not reconstructed in the actual hourly baseline.

Therefore a large simulated shortfall under the partial thermal+wind resource representation must be described as **a model-bound supply-representation artifact and a conditional stress-test result**, *not observed grid shortage*. This audit does **not quantify how much real hourly unmet load would disappear** if these technologies were added: hydro operational constraints, wind/solar profiles, storage SOC and dispatch, power plant outages and transmission bottlenecks are not identified by the nameplate roster.

## Publication positioning and next data checks

This source-audited matched-fleet figure and inventory table can be included in **Supplementary Data / data provenance and resource coverage limitations** of Paper C. If the paper aims for a system-level adequacy claim, the next defensible gate is to reconstruct BA-specific **168-hour source fuel generation profiles**, respecting EIA-930 split-year schema (previously verified), and compare to technology-resolved PyPSA baseline with source-coherent fuel/technology populations. Report energy-balance incompleteness and interchange reciprocity discrepancies separately. Physical generator availability, transmission ratings and real shortfalls remain uncalibrated.

Before interpreting any 2023 vs 2024 apparent nameplate change, compare truly **same-calendar historical monthly inventories** with consistent EIA-930A reporting definitions; the cited February and August 2025 snapshots cannot substitute for that.
