# EIA-923 2024 Page 1 vs Page 4 plant coverage audit

## Source

Actual CSVs from successful [official EIA-923 intake run 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401), artifact `13065659112` (SHA-256 `6bdb4d084fa7034257c784b26816003e25757b757534624b8822310d9780edc6`).

The extracted source files are `eia923_generator_month_net_mwh.csv` (Page 4, generator-month) and `page1_hy_plant_month_net_mwh.csv` plus `eia923_page1_ps_plant_month_net_mwh.csv` (Page 1, plant-month). Analysis keyed on normalized plant ID after stripping leading zeroes and whitespace; no BA topology or EIA-860 identity certification is implied.

## Coverage checks

| Check | Actual audit result |
|---|---:|
| Page 4 distinct plant identifiers | 123 |
| Page 1 HY + PS distinct plant identifiers | 250 |
| Page 1 HY/PS plant identifiers also appearing on Page 4 | 1 |
| Page 4 duplicate plant/generator/month keys | 0 |
| Page 4 plants associated with multiple reported BAs in extract | 0 |
| Page 1 plants associated with multiple reported BAs in extract | 0 |
| Page 1 plant IDs appearing in both HY and PS categories | 5 |
| Page 4 HY/PS prime-mover records | 0 |

**Interpretation:** The Page 4 extraction does **not** provide adequate direct coverage for Page 1 HY/PS records. Missing Page 4 HY/PS keys must not be treated as zero measured production. Page 1 HY/PS must remain a separately identified observational source. The five plant IDs appearing in both HY and PS are *not* duplicates by default: technology and source sheet differ.

## Limits and subsequent gate

This is a *cross-sheet coverage audit*, not yet an EIA-860 generator crosswalk. To carry out EIA-860 matching safely, download the official matching-year generator/plant inventory, normalize plant and generator identifiers with vintage-aware BA attribution, and compare plant/technology coverage before any summation. Hydro Page 1 uses plant-month aggregation, while Page 4 uses generator-month rows; never infer a one-to-one generator mapping from a plant ID alone. Distinct source-sheet records must not be summed across Page 1 and Page 4 for the same physical generation without verified reconciliation.

The current 168-hour SRP stress-test output remains an **assumption-driven screening result**. No full calendar-month simulated generation output or independent-year observational calibration is certified.
