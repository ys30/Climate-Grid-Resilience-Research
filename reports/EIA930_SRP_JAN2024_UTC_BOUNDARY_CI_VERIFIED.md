# EIA-930 SRP January 2024 UTC calendar-month reconciliation

**VERIFIED:** [GitHub Actions run 41407182014](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407182014), source implementation commit `e69dacdb51560fe7a1d277fcc27090d313bd4431`, [artifact 13124031945](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407182014/artifacts/13124031945).

## Verified underlying issue

The EIA-930 official 2024 Jan–Jun Balance CSV contains only **737** of the **744** hours within the strict **January 2024 UTC** calendar window. Missing are January 1, 2024 00:00–06:00 UTC (seven hours, corresponding to Dec 31 2023 17:00–23:00 MST). They were **not randomly missing observations**; the adjacent official **2023 Jul–Dec** CSV contains exactly those seven rows. Both are original official observations: **no interpolation, no zero-fill, no duplicate hour**.

| Original official source | January 2024 UTC hours |
|---|---:|
| `EIA930_BALANCE_2023_Jul_Dec.csv` | 7 |
| `EIA930_BALANCE_2024_Jan_Jun.csv` | 737 |
| **Combined uniquely validated** | **744** |

**Measured SRP January 2024 monthly hourly demand aggregate:** **2,455,626 MWh**, obtained by integrating 744 reported hourly MW values with one-hour interval weights. This is a balancing-authority demand series, **not EIA-923 generation or verified modeled dispatch**.

The workflow records exact original official source URLs and SHA256 in `source_manifest.json`, generates the original-row-recombined CSV and the hourly `srp_2024_jan_utc_744.csv` file in the artifact. `eia930_balance_archive_import` rejects any incomplete/duplicated UTC month.

**Important methodological detail:** Official Balance `UTC Time at End of Hour` is normalized by subtracting one hour so that PyPSA snapshots represent hour starts, not hour ends.

## Next gate

Run the genuine 744-hour SRP demand profile through the monthly PyPSA solver with explicitly documented, BA-specific 2024 EIA-860 capacity inputs and availability assumptions. Do **not** declare empirical model calibration until observed EIA-923 BA/technology/month generation is independently reconciled, modeled generation is compared using matching definitions, and independent-year holdout is verified.
