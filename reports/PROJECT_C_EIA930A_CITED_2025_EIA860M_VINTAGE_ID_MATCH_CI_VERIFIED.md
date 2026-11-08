# Paper C — EIA-930A cited EIA-860M 2025 source-vintage matching versus annual EIA-860

## Verified sources and scope

**Successful CI [#42455881405](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455881405)** independently obtained the original monthly source inventory for **February 2025** and **August 2025**, corresponding to the original-source vintages cited by the EIA-930A data-year 2023 and data-year 2024 workbooks, respectively. [Download full matched generator-level classification transitions, BA summaries, source hashes and CSVs (artifact 13607119851)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455881405/artifacts/13607119851). [Reproducible source code](../src/grid_resilience/paperc_eia860m_vintage_identity.py).

Original EIA sources, with SHA256 archived in the CI results:
- [February 2025 EIA-860M Operating inventory](https://www.eia.gov/electricity/data/eia860m/archive/xls/february_generator2025.xlsx), preliminary month-level roster.
- [August 2025 EIA-860M Operating inventory](https://www.eia.gov/electricity/data/eia860m/archive/xls/august_generator2025.xlsx), preliminary month-level roster.
- Original EIA-930A 2023 and 2024 annual source workbooks as archived in [prior EIA-930A extractor CI](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42451161661).
- Year-specific 2023 and 2024 **annual** EIA-860 Operable reference is the previous [successful original-source census](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455170263).

The official monthly EIA-860M Operating sheet includes Plant ID, Generator ID, Balancing Authority Code, Technology, energy source, prime mover, nameplate capacity, and monthly status. Both original monthly workbooks were source-hash validated and downloaded, not assumed from annual EIA-860 records.

## Source-verified identity reconciliation

For every original EIA-930A Schedule 2 row, the program compares two independent classification outcomes using the **same strict official plant/generator IDs and BA-name comparison rules**:

1. EIA-930A versus the **corresponding annual EIA-860 Operable** (previous audit).
2. EIA-930A versus the **explicitly cited preliminary 2025 EIA-860M Operating monthly vintage** (new audit).

The program preserves all EIA-930A rows, including fallback/unrecognized IDs and 2023 duplicated same-BA/ID entries. It does not deduplicate ambiguous identities into capacity or treat a matched row as a unit physically available during the 2023/2024 extreme-weather window.

| EIA-930A data year | EIA-930A source rows, four BAs | Cited EIA-860M monthly vintage | Original rows whose identity/BA match classification changes |
|---|---:|---|---:|
| 2023 | 2,144 | February 2025 | **53** |
| 2024 | 1,960 | August 2025 | **29** |

### BA-specific new monthly results

| EIA-930A data year | BA | Original annual same-BA matches | Cited monthly same-BA matches | Monthly-vs-annual changed-category rows | Cited monthly still unmatched | Monthly fallback/no verified identity | Duplicate same-BA identity rows |
|---|---|---:|---:|---:|---:|---:|---:|
| 2023 | AZPS | 114 | 114 | 0 | 0 | 5 | 0 |
| 2023 | BPAT | 294 | 294 | 0 | 0 | 1 | 0 |
| 2023 | CISO | 1,348 | **1,367** | **53** | **39** | **111** | **91** |
| 2023 | SRP | 94 | 94 | 0 | 0 | 0 | 0 |
| 2024 | AZPS | 117 | **115** | 2 | **2** | 4 | 0 |
| 2024 | BPAT | 292 | 292 | 0 | 0 | 0 | 0 |
| 2024 | CISO | 1,165 | **1,192** | **27** | **8** | **225** | 0 |
| 2024 | SRP | 93 | 93 | 0 | 0 | 2 | 0 |

The **same-BA exact-match CISO improvement**, alongside unresolved CISO fallback identities and 2023 duplicate EIA-930A rows, indicates that **source inventory version is a measurable contributor to previous unmatched classification differences**. The 2024 AZPS case illustrates why monthly-source matching is not guaranteed to improve every BA. Do not infer that the changed categories reflect generator construction, retirement, maintenance state or available capacity in the July climate windows.

## Scientific implications and manuscript placement

**Admitted:** EIA-930A original Schedule 2 generator identities can now be independently checked against the exact-month preliminary EIA-860M inventory cited by the workbooks. Annual-vintage mismatch is quantitatively real: 53 and 29 row classifications change, primarily in CISO.

**Not admitted:** That the sources identify a complete physical generating fleet, correctly assign all pseudo-tie resources to a physical BA, measure hour-by-hour generation availability, capture behind-the-meter generation, reveal the true transfer capability of transmission lines, or validate the PyPSA screening-model simulated unmet energy as observed shortages.

EIA expressly states that preliminary monthly capacities are estimates, may be revised without specific acknowledgment, and **are not firm capacity commitments**. [Official EIA-860M methodology](https://www.eia.gov/electricity/data/eia860m/).

This result is suitable as a **Data Provenance and Reporting-Fleet Identity Sensitivity** supplement to the Paper C study, and as a prerequisite for developing technology-level BA resource categories.

## Next gate

1. For CISO's **225** EIA-930A 2024 fallback-ID records, preserve raw plant name/unit and compare to official source descriptions; do not infer missing generating capacity from unrecognized IDs.
2. Identify 2023 CISO's **91 duplicate same-BA/ID row occurrences** by plant and technology; check whether the rows represent ambiguous source roster entries or an unsupported repeated identifier scheme.
3. Compute **matched-only nameplate by technology and BA** for both source-vintage alternatives, with the *same* EIA-930A row cohort denominator and explicit exclusion of non-unique IDs. Do not use such sums as available supply in July.
4. Only after a technology-complete and source-coherent actual-supply model exists should EIA-930 hourly generation/interchange be used for physical baseline calibration and resilience comparison.
