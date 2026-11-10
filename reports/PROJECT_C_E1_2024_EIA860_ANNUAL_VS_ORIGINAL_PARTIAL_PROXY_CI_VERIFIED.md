# Paper C E1 — Annual EIA-860 technology-candidate census versus original generic-thermal PyPSA proxy (CI VERIFIED)

## Verified archive-to-archive source inventory reconciliation

The original-source comparison was completed by [GitHub Actions #42920485954 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42920485954) with **5 regression tests** and the [four-BA CSV plus fail-closed scope manifest artifact #13812165455](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42920485954/artifacts/13812165455). Reproducible implementation: [paperc_e1_original_proxy_vs_eia860_annual.py](../src/grid_resilience/paperc_e1_original_proxy_vs_eia860_annual.py); [CI workflow](../.github/workflows/paperc-e1-annual-inventory-vs-original-proxy.yml); [tests](../tests/test_paperc_e1_original_proxy_vs_eia860_annual.py).

The CI independently retrieved all **three original, previously source-audited artifacts**:
1. [2023/2024 official annual EIA-860 four-BA Operable technology-candidate inventory #42441328634](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441328634);
2. [2024 EIA-930A versus its cited 2025-August preliminary EIA-860M identity reconciliation #42455881405](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42455881405);
3. [Original July 2024 source/model four-week partial capacity file #42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361).

## Source census versus modeled proxy — different populations, DO NOT subtract as missing firm MW

| BA | 2024 EIA-860 selected single-fuel nonstorage technology candidate nameplate (MW) | EIA-860 natural-gas-only nameplate (MW) | Original PyPSA `gas_mw` = generic thermal proxy (MW) | Annual EIA-860 wind nameplate (MW) | Original wind proxy (MW) |
|---|---:|---:|---:|---:|---:|
| AZPS | 5,779.2 | 2,471.2 | 4,818.8 | 628.5 | 628.5 |
| BPAT | 29,653.4 | 2,171.5 | 3,177.9 | 3,617.1 | 3,617.1 |
| CISO | 71,156.8 | 31,186.2 | 32,934.6 | 6,352.2 | 6,334.7 |
| SRP | 14,681.5 | 7,655.1 | 9,263.9 | 226.0 | 226.0 |

The annual candidate **total** spans selected coal, gas, oil, nuclear, hydro, solar, wind and geothermal technology populations, and includes neither excluded multi-fuel/storage records nor proof of physical BA dispatch connectivity. It is **NOT** the amount of firm capacity to put into the model. The original `gas_mw` is **not gas-only capacity**, despite its column name: it comes from a different generator-identity/technology-selection workflow and is used in PyPSA as one idealized always-available generic thermal generator per BA. These are **different statistical and operational populations**. An arithmetic difference `EIA860 gas MW - model gas_mw`, `EIA860 total MW - model gas_mw`, or `EIA860 wind MW - original wind_mw` is **NOT an independently identified shortage of installable firm MW**.

Annual 2024 original EIA-860 Operable source includes **3,268 generator rows** for the four BAs; the strict single-fuel positive-nameplate non-storage technological candidate screen admits **2,625**, and **643 are explicitly excluded, not assigned zero capacity**. Same-vintage identity audit of the 2024 EIA-930A raw Schedule 2 population (1,960 records) against its cited August 2025 EIA-860M still has **231 no-verified-ID records**, **10 unmatched** and **27 BA conflicts**. These are **source-row/identity counts**, not MW, not independently distinct physical generators and not measures of true hourly availability. CISO accounts for 225 of the no-verified-ID original EIA-930A rows.

## Strict frozen-E1 work remaining

The **annual candidate inventory and original proxy comparison are done**, not a fully reconstructed physical BA capacity model. In order to close E1 for source-grounded model substitution, the bounded remaining work is:

1. Build a **mutually exclusive generator-keyed technology crosswalk** in the exact 2024 EIA-860 vintage, recording each source ID, BA provenance, prime mover, fuel, nameplate, operative/retired/pending classification and exclusion reason. Do **not** double count EIA-923-seen generators against EIA-860 Operable candidates.
2. Report **included / excluded / ambiguous** nameplate MW separately by BA and technology; distinguish annual installed nameplate, nameplate confidence and assumed hourly dispatchable MW. Never silently label annual nameplate as observed availability.
3. Explicitly audit the **643 annual excluded** rows and EIA-930A conflicting/fallback identities as unknown scope rather than fabricating a completed fleet. Build one documented **source-aligned technology model scenario** only if source identity and operational meaning can be justified.
4. If unresolved topology, hydro/storage energy availability, generator operational status or BA sourcing still preclude true model substitution, **close E1 at inventory-admission level** and record physical-model calibration as unavailable. Under the frozen publication plan, E2 and E3 must be interpreted as model-screening tests or narrowed, not endlessly expanded.

**E1 partial progress:** exact source-audited technology candidate census, historical model proxy, and EIA-930A source-vintage identity constraints verified in one CI. **Not yet done:** unique physical fleet/usable-hourly MW calibration. **E2/E3 not run by this workflow; zero new PyPSA solves here.** No new E4/E5 work was started.
