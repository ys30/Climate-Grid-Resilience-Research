# Official SRP 2024 January EIA-923 Page1 HY/PS monthly observations

**CI verified:** [run 41409931415](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41409931415), implementation commit `3dbef36fee7ce0195932423229fba6c1d8193a41`. Extractor: `src/grid_resilience/eia923_page1_hy_ps.py`.

Official EIA-923 `Schedules_2_3_4_5` 2024 workbook, `Page 1 Generation and Fuel Data`; header row 6 checked against reported prime mover at zero-index column 13, balancing-authority code at column 16 and monthly net generation January–December at columns 79–90. Includes source rows with BA code `SRP`, reported prime mover `HY` or `PS`, and reporting year 2024. Negative net generation values and source provenance are retained; missing never silently set to zero.

| Source | January observed rows | January net generation MWh |
|---|---:|---:|
| Page1 HY | 5 | 1,015 |
| Page1 PS | 2 | −132 |
| **Page1 HY + PS** | **7** | **883** |

Reported missing HY/PS monthly cells for 2024 = **0**. The signed PS value must be retained; it can reflect pumping energy in the source net-generation accounting and should not be interpreted as an observed outage or loss-of-load.

**IMPORTANT:** Page1 records have different granularity (plant × fuel × prime mover × month) than Page4 generator × month. This ledger is an independent observation, not a proof of non-overlap or directly additive BA electricity supply. Never blindly sum it with Page4 MWh or compare to EIA-930 demand as if system balancing components have been fully reconciled. There is no water reservoir/time-of-day dispatch profile or PS charge/discharge state in the PyPSA SRP monthly screen yet.

Next: confirm overlap and reporting conventions between Page1 HY/PS and Page4, obtain independent net interchange from EIA-930, and add source-aware hydro energy constraints rather than a single nameplate-based flat generator.

**Historical calibration certified: NO.**
