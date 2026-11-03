# SRP January 2024 EIA source-scope decomposition

Verified source: [successful run 41718037295](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037295), commit `055b8a18b47ae98e39352453bbeb806999fe51f7`, artifact 13269759289. Reaggregated `plant_ba_technology_scope_rows.csv` (108 unique generator identities); reconciled against `plant_ba_generator_census_manifest.json` and `srp_generator_monthly_identity_audit.json`.

| Source scope | Generators | Nameplate MW |
|---|---:|---:|
| EIA-860 Plant BA roster | 108 | 16,863.6 |
| Appearing in selected January EIA-923 Page 4 | 40 | 7,843.5 |
| Selected partial NG/SUB model | 37 | 7,453.1 |
| Page 4 matched, excluded multifuel | 3 | 390.4 |
| Not in selected Page 4 BA/month | 68 | 9,020.1 |

Non-Page-4 technical categories (nameplate MW): gas 1,528.4; nuclear 4,209.6; solar 1,674.9; hydro 248.2; wind 226.0; primary fuel not mapped 1,133.0. These sum to 9,020.1 MW.

Among the 68 non-Page-4 identities: 49 fall in the source technology candidate class (7,228.4 MW), 8 are flagged multifuel or secondary fuel (504.6 MW), 2 are excluded storage (154.1 MW), and 9 have unmapped primary source (1,133.0 MW). Source inventory status codes: OP 64 / 8,899.1 MW; OS 4 / 121.0 MW. Status codes are **not** interpreted as January hourly availability.

The 9,020.1 MW missing from this Page 4 *reporting population* must **not** be added as available output or firm capacity in the dispatch model. EIA-860 plant BA assignment, EIA-923 Page 4 reporting, and EIA-930 BA-wide generation have distinct scopes. Ownership/contract entitlement, transmission deliverability, technology-specific hourly limits and source reconciliation remain unverified.

**Historical reliability calibration: NO. Recorded outages inferred: NO.** The 744-hour partial-fleet deterministic gap remains a diagnostic only.
