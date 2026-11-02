# EIA-923 2024 hydro and pumped-storage observed source audit

## Reproducible source evidence (2026-10-31)

**Official intake workflow run:** [41261608309](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41261608309), success on commit `a067a393869f83b4de22d8ff1be348ca4aca4679`.

The run downloads the official 2024 final EIA-923 Schedules 2/3/4/5 workbook and publishes its audit and extraction artifacts. The numbers below are **observed source rows, not dispatch capacity or electricity MWh**.

### Page 1 conventional hydro (HY) inventory

| Reported balancing authority | HY source rows | Distinct plant/BA pairs |
|---|---:|---:|
| AZPS | 0 | 0 |
| BPAT | 55 | 55 |
| CISO | 185 | 185 |
| SRP | 5 | 5 |
| **All four target BAs** | **245** | **245** |

All 245 qualifying HY rows report fuel code `WAT`. No repeated `plant_id + reported_ba` pairs and no plant with multiple reported BAs were found *among these extracted HY rows*. This is **not** an independent historic BA crosswalk certification.

**Important:** HY source coverage is demonstrated, but monthly net generation for HY has **not** been extracted or independently reconciled. Page 1 Generation and Fuel fuel quantities must never be represented as MWh. The Page 4 generator-month slice did not include HY/PS for these target BAs; this does not imply zero hydro production.

### Page 1 energy storage (PS) measured monthly net generation

**Source runs:** [41260615850](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41260615850) and [41261259000](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41261259000), successful.

- 10 PS source rows: BPAT 1, CISO 7, SRP 2, AZPS 0.
- 120 observed PS plant-month net-generation rows, including 67 negative and 22 zero monthly net-energy rows. No absent monthly net-generation cells in the 10 extracted source rows.
- Of the 48 possible target-BA/month slots, 36 have at least one source record (12 each BPAT, CISO, SRP). AZPS has no PS source records in this extraction. **Missing does not equal zero.**

PS monthly signed net generation is not pumping consumption, state of charge, installed capacity or hourly storage availability.

## Calibration gates not yet passed

1. Obtain and validate **independent HY monthly electricity generation** at an appropriate plant/BA reporting basis, with source and temporal identification. Do not equate EIA-923 fuel quantity to electric energy.
2. Independently audit EIA-860 plant/generator mapping and completeness of the expected fleet, year-scoped BA assignments and any changed affiliations.
3. Verify month-by-month measurement definitions for HY and PS (net vs gross, pumping treatment, and duplicates across reporting schedules).
4. Only then compare complete calendar-month PyPSA generation with matched observed BA/technology/month totals and report signed bias, MAE, RMSE and withheld-period performance.
5. Keep transmission rating, weather availability, demand and full reliability-model historical validation separate from the EIA-923 generation calibration gate.

**Historical calibration certified: NO.** These are source-audit results, not a historically calibrated grid-reliability forecast or observed outage statistics.

Reproduce the technical extraction through `.github/workflows/eia923-official-intake.yml`. The generated CSV and JSON files are retained as GitHub workflow artifacts, not silently treated as committed historical datasets.


## Updated verified HY/PS month-generation evidence (run 41263007401)

**This section supersedes the earlier statement that HY monthly MWh had not been extracted.** The successfully completed [EIA-923 official intake run 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401) on commit `01898fa1c034b0d95a328851998eec34d5706653` published artifact `13065659112` (SHA-256 `6bdb4d084fa7034257c784b26816003e25757b757534624b8822310d9780edc6`). Inspection of its CSVs and manifests confirms 2,940 measured HY plant-month net-generation rows and 120 PS plant-month rows.

| BA | HY observed months | HY 2024 net MWh | PS observed months | PS 2024 signed net MWh |
|---|---:|---:|---:|---:|
| AZPS | 0 | missing | 0 | missing |
| BPAT | 12 | 60,869,517 | 12 | 1,691 |
| CISO | 12 | 21,483,685 | 12 | -138,986 |
| SRP | 12 | 217,124 | 12 | 82,975 |

There are **72 observed BA/technology/month slots of 96** expected slots; the missing 24 are AZPS HY and PS and must **not** be interpreted as measured zero generation. Signed PS totals can be negative; this is not a storage discharge-only metric. These are reported-source totals, not proof of complete fleet coverage, reconciled BA mapping, independent weather availability or historical model calibration.

A separate `hydro_ps_coverage_manifest.json` using the Page-4 prime-mover audit contains zero observed slots; that manifest reflects a **different source extraction path** and must not supersede the independently extracted Page-1 HY/PS records above.

**Revised gate:** HY monthly MWh extraction is achieved for reported-source rows in BPAT/CISO/SRP. Next reconcile reported BA assignment and full-fleet completeness, compare actual complete-month model generation (not the existing 168-hour screen) with observed month totals, and carry out year-held-out validation. Historical calibration certified: **NO**.
