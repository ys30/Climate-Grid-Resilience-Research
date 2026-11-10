# Paper C E1 — Final 2024 EIA-860 generator-keyed admission and 643-row exclusion audit (CI VERIFIED)

## Evidence and provenance

**Successful final source CI:** [#42921601170](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42921601170); original [raw-data-backed generator-level results artifact #13811412833](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42921601170/artifacts/13811412833). CI re-downloaded **official EIA-860 2024 annual ZIP** and parsed its original Operable and Plant worksheets. Official ZIP SHA256: `0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b`. Each BA association is the original reported annual Plant BA, **not reconstructed electric topology**. The source implementation requires unique (plant ID, generator ID) keys and a disjoint, explicit exclusion reason for each source record.

Source file: [generator-keyed census](../src/grid_resilience/paperc_e1_2024_generator_keyed_census.py); [unit tests](../tests/test_paperc_e1_2024_generator_keyed_census.py); [CI workflow](../.github/workflows/paperc-e1-2024-generator-keyed-census.yml). Exact original EIA860 annual E1 versus model-proxy population scope was already [audited successfully](PROJECT_C_E1_2024_EIA860_ANNUAL_VS_ORIGINAL_PARTIAL_PROXY_CI_VERIFIED.md).

## Every 2024 four-BA original Operable row has an exclusive outcome

| Exclusive source-screen outcome | Generator rows | Positive reported nameplate (MW) |
|---|---:|---:|
| Admitted single-fuel nonstorage technology candidate | **2,625** | **121,270.9** |
| Excluded: multi-fuel or secondary-fuel use | 153 | 3,900.7 |
| Excluded: storage including reported batteries or pumped storage | **289** | **16,805.8** |
| Excluded: other / unsupported predominant fuel under original candidate map | 201 | 823.3 |
| **Total 2024 reported four BA Operable population** | **3,268** | **142,800.7** |

**Excluded = 643 source rows and 21,529.8 MW of positive reported nameplate, NOT "missing available firm generation".** The excluded storage includes batteries (annual power capacity only, no verified energy content or available SOC) and pumped-storage generators (no verified charge/discharge time or dispatchable water energy). No excluded generator is assumed absent from the real grid.

### Four-BA source census and exclusion categories (generator rows)

| BA | Admitted | Multi-fuel | Storage | Unsupported primary fuel | Total |
|---|---:|---:|---:|---:|---:|
| AZPS | 97 | 6 | 15 | 3 | 121 |
| BPAT | 331 | 16 | 11 | 36 | 394 |
| CISO | 2,111 | 120 | 252 | 162 | 2,645 |
| SRP | 86 | 11 | 11 | 0 | 108 |
| **Total** | **2,625** | **153** | **289** | **201** | **3,268** |

## Important classification correction from the original original-schema audit

The EIA-860 `Technology` field uses **"Batteries"** (plural), while its energy source code is `MWH` and prime mover code is `BA`. A legacy substring check of singular `Battery` did not classify these as storage and instead incorrectly labeled **251 MWH/BA batteries totaling 13,450.1 MW** as "unmapped fuel". The source-corrected E1 census explicitly recognizes `Batter(?:y|ies)`, prime mover `BA`/`PS`, and source fuel code `MWH`. The final correction changes only **excluded-category attribution**, not the previously independently verified 2,625 admitted candidates or 643 excluded total.

The original gas/wind-only PyPSA `gas_mw` is an **EIA923-selected generic thermal proxy**, not natural-gas-only installed nameplate. Annual candidate totals, excluded generator nameplates and original proxy MW cannot be subtracted or simply added as independently missing *firm* capacity.

## E1 stopping rule and E2/E3 admission

**E1 Source identity/census phase: COMPLETE and frozen.** Exactly 3,268 BA generator identities, annual source status, prime mover, fuel, nameplate fields, admission flags and mutually exclusive classification are archived; four BA/technology and exclusion totals reconcile. EIA930A-vintage same-BA generator matching and unresolved fallback/BA conflicts remain separately archived in [source-vintage audit](PROJECT_C_EIA930A_CITED_2025_EIA860M_VINTAGE_ID_MATCH_CI_VERIFIED.md).

**Physical hourly capacity reconstruction: NOT COMPLETE; not achievable by mere EIA860 nameplate census.** Original BAs' hourly available thermal, renewable, hydro and storage resources and physical intertie exchange are not identifiable from this admission audit; EIA930A has unresolved same-ID/BA cases. In particular, storage power nameplate is not 672h energy.

**E2** may be a explicitly conditional model-screening structural robustness comparison only. Do not claim actual historical EENS/LOLE, capacity need, or geographic reliability ranking. **E3** should use a distinct source-time cohort under a predeclared, consistent surrogate resource definition, not the repeated 2024 first-week anchor as an independent validation. **No more E1 ad hoc source screens or arbitrary capacity-grid expansion** are required for the paper's present screening-study scope.

The complete source-key classification is preserved as a downloadable Actions artifact, not committed as a potentially source-licensed public data CSV. No new PyPSA solves were executed in this E1 admission step.
