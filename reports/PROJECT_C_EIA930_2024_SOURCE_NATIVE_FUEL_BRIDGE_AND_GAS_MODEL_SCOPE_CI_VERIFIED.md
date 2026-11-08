# Paper C — 2024 source-preserving EIA-930 fuel-schema bridge and hourly model scope diagnosis

## Verified workflow chain

**2024 source-native split/unsplit original fuel columns:** [GitHub Actions CI 42444317594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42444317594), [source checksums, 672 BA-hour CSV, original-schema BA fuel totals and manifest artifact 13602574292](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42444317594/artifacts/13602574292).

**Same-hour observed gas versus deliberately incomplete PyPSA thermal proxy:** [CI 42444496460](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42444496460), [672 matched-hour descriptive CSV, BA table and non-equivalence manifest artifact 13602434894](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42444496460/artifacts/13602434894). Both successful. Original 2024 EIA-930 Jan–Jun and Jul–Dec source archive hashes are recorded, original CSV row values are parsed as **raw** (not adjusted or imputed) data, with UTC hour-ending labels converted to hour starts.

## Source-audited official BA net/gas and separate native wind columns

The four BAs (AZPS, BPAT, CISO, SRP) each have **7 BA-hours in Jan–Jun**, **161 in Jul–Dec**, covering 2024 July 1–7 UTC. The unchanged original category `Natural Gas` has all 168 reporting hours, so an entire-week raw signed gas total is admitted. `Wind` from the **old unsplit schema** is a distinct field from `Wind without Integrated Battery Storage` and `Wind with Integrated Battery Storage` under the new schema. The last category was blank for all BA-hours in this week and is **not zero**.

| BA | Observed BA net generation, all 168h (MWh) | Observed raw natural gas, all 168h (MWh) | Old unseparated wind, first 7h (MWh) | New wind without battery, remaining 161h (MWh) |
|---|---:|---:|---:|---:|
| AZPS | 522,280 | 203,967 | 1,940 | 29,834 |
| BPAT | 1,763,554 | 116,528 | 12,616 | 97,446 |
| CISO | 4,653,684 | 2,076,666 | 26,458 | 403,508 |
| SRP | 1,355,280 | 492,311 | 447 | 12,581 |

**Do not add the two wind columns and present the result as a single validated 168-hour observed wind category**. Their source definitions differ and integrated-battery wind is explicitly unknown, not necessarily zero. Raw BA net generation is also not interchangeable with total available plant capacity, scheduled supply or balance between BA demand, interchange, imports and storage.

## Hour-key exact descriptive model-population mismatch

The independent 2024 EIA-860 candidate experiment models only hypothetical **generic thermal + wind**, and its `generic_thermal_proxy` dispatch is **not a source-matched EIA-930 natural-gas technology or unit fleet**. The archival comparison joins all **672 exact BA-hour records** for the July baseline, checks no duplicate or missing hour keys, and explicitly retains `generator_population_equivalent=false`.

| BA | Source observed natural gas (MWh / week) | PyPSA generic thermal proxy (MWh / week, approximate CI printed values) |
|---|---:|---:|
| AZPS | 203,967 | ~415,162 |
| BPAT | 116,528 | ~355,808 |
| CISO | 2,076,666 | ~4,673,489 |
| SRP | 492,311 | ~979,763 |

The numerical mismatch is **substantial**. It is **not** a model forecast error, a calibration statistic, missing electricity, an estimated resource coverage fraction, physical generator ramp shortfall, a climate effect, an observed blackout, or probabilistic EENS. The output intentionally records the mismatch under different equipment/technology scopes as **a representational diagnostic**. Do not report the total of these proxy differences as a physical BA supply accounting residual.

## Methodological and manuscript implications

1. The old/new schema bridge and net/gas source coverage are now **reproducible, CI-verified and original-hour aligned**, removing the earlier 28-hour false missingness.
2. The baseline supply model has a **large generator population/technology representation mismatch**; historic adequacy claims must be held until a consistent full-fleet and hour-by-hour available-supply reconstruction is complete.
3. The user's existing source-input conditional heat/wind interaction sensitivity can remain in a well-labeled **screening-model section**, while the EIA-930 provenance and fleet-scope results should feature prominently in **Methods, Supplementary Tables, Limitations, and model calibration roadmap**.
4. Next scientific priority: compare plant-BA technology coverage and source EIA-923 monthly generation to available EIA-930 fuel categories; validate actual interties. Treat unit-level pumped storage and unreported solar/wind-battery values as distinct gaps rather than inventing observations.

This is strong **reproducible data lineage and model-specification auditing**, not evidence of actual grid resilience or identified reliable capacity.
