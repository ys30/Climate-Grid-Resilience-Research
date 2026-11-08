# Paper C — Official EIA-930 2023/2024 source-native seven-day hourly generation and stable-fuel admission

## Reproducible source evidence

Two successfully executed CI pipelines independently reconstruct and audit the original **EIA-930 4-BA 168-hour** records:

1. [Original full fuel taxonomy / source completeness — SUCCESS #42462457999](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42462457999), [full 2023/2024 hourly fuel evidence CSV and three original CSV SHA256 manifest (artifact 13610670717)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42462457999/artifacts/13610670717).
2. [Strict stable-label original coal/natural gas/nuclear hourly admission — SUCCESS #42462843256](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42462843256), [24 BA × year × original category summary and 4,032 source hourly category entries (artifact 13610780244)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42462843256/artifacts/13610780244).

All source timestamps are EIA `UTC Time at End of Hour` **converted to UTC hour start**, and hourly mean MW is integrated over 1 hour when called MWh. The cohorts are **July 10–16, 2023 UTC** and **July 1–7, 2024 UTC**; they are *not the same week*, so differences cannot be interpreted as a controlled interannual climate effect.

### Original-source completeness vs fuel-category missingness

- 2023 source: **672 of 672** expected BA-hours from the original EIA-930 `2023 Jul–Dec` file, **9 original fuel categories**.
- 2024 source: **672 of 672** BA-hours from the original `2024 Jan–Jun` and `2024 Jul–Dec` files, **7 + 161 UTC hours per BA**, original schema comprises **19 unique fuel labels across the two source partitions**.
- The 2024 first-seven-hour legacy source and final-161-hour modern source use **different classifications** for hydro/pumped storage, wind/integrated storage and solar/integrated storage. No direct same-category 168h summation of these renamed groups is certified.
- Full BA-hour presence **does not establish fuel reporting completeness**. Original-source fuel-category blank field counts:

| BA | 2023 blanks across 9 original category fields × 168 hours | 2024 blanks across both schema partitions |
|---|---:|---:|
| AZPS | 168 | 1,295 |
| BPAT | 504 | 1,470 |
| CISO | 168 | 1,295 |
| SRP | 336 | 1,463 |

These counts are **blank fuel-category cells**, not empty total BA hours, not missing MWh, not physical unserved load and not zeros.

## CI-admitted 168-hour source-reported Coal/Natural Gas/Nuclear totals

Three original source fuel labels persist unchanged across the 2023 cohort and both 2024 half-year partitions. All **24 year × BA × category** records are source-hour complete, but BPAT's **Coal** field is **blank for all 168 hours** in both years. Thus **22/24** complete numeric 168h fuel sums are admitted. Every other admitted full-week value below has **168 actual reported hourly values**; source zero measurements are valid and distinct from missing cells.

| BA | Stable fuel | 2023 Jul 10–16 reported MWh | 2024 Jul 1–7 reported MWh |
|---|---|---:|---:|
| AZPS | Coal | 227,639 | 194,642 |
| AZPS | Natural Gas | 234,657 | 203,967 |
| AZPS | Nuclear | 0 | 0 |
| BPAT | Coal | **N/A: all 168 blank** | **N/A: all 168 blank** |
| BPAT | Natural Gas | 152,510 | 116,528 |
| BPAT | Nuclear | 185,610 | 190,591 |
| CISO | Coal | 436 | 0 |
| CISO | Natural Gas | 2,090,547 | 2,076,666 |
| CISO | Nuclear | 380,436 | 381,468 |
| SRP | Coal | 97,931 | 90,859 |
| SRP | Natural Gas | 594,397 | 492,311 |
| SRP | Nuclear | 661,774 | 659,960 |

These are EIA-930 original **reported BA generation-by-fuel totals**, NOT generator-identity-level metered data. They are not technology nameplate, dependable MW, comparable climate-treatment estimates, hourly unserved energy or observed blackouts. Blank BPAT coal records cannot be treated as zero output, even though independent monthly source inventory may identify coal capacity assigned to BPAT.

### Implications for the current PyPSA screening model

The source-admitted stable series permits a transparent **reported natural gas versus model generic thermal proxy** diagnostic using exact BA-hour keys, but this is **not a model calibration error** because the resource populations differ. The preceding [CI-reverified 2024 original gas-vs-PyPSA proxy audit](PROJECT_C_EIA930_2024_SOURCE_NATIVE_FUEL_BRIDGE_AND_GAS_MODEL_SCOPE_CI_VERIFIED.md) already established the mismatch. A legitimate full-fuel model baseline still needs realistic solar, hydro, nuclear, battery, coal and other technologies, storage state-of-charge/efficiency, plant operational constraints, weather-driven capacity factor profiles and defensible BA import/export accounting and transmission ratings.

2024 month-source [EIA-930A × EIA-860M reporting-inventory and technology nameplate audit](PROJECT_C_EIA930A_EIA860M_BA_TECH_NAMEPLATE_SCREENING_CI_VERIFIED.md) shows the breadth of equipment omitted by the **generic thermal + wind-only** screening simulation, but the **August 2025 source roster** is not a July 2024 historical operational generator portfolio. It cannot directly be used as true observed 2024 operating capacity.

### Next methodological gate

1. **Keep strict source-native original fuel labels for wind/solar/hydro**, including 7h legacy and 161h modern categories, and report them side by side with their reporting completeness — not as a fabricated harmonized 2024 full-week fuel total.
2. If reconstructing a new model baseline, obtain actual 2023/24 technology-appropriate plant/source vintages and hourly profiles rather than substitute 2025 inventory MW or arbitrarily reuse current thermal proxy output.
3. Preserve EIA-930 reporting imbalance (BPAT and CISO), CISO missing Total Interchange and bilateral reciprocity differences as **independent accounting/source-quality limitations**, not events of actual energy shortage.

**Publication status:** The 2023/2024 original BA fuel reporting panel and 22 source-admitted full-week stable-fuel totals are reproducible, source-hash versioned and independently regression-tested. Source-level reporting coverage is stronger; historical system adequacy and causal resilience claims remain uncalibrated.
