# EIA-923 2024 Page-4 technology-month coverage — verified CI result

Source: official-data [GitHub Actions run 41400977425](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41400977425), commit `260a0d4881123f503c807f4c9380156b4fc84ee7`. The workflow downloads official EIA-860 and EIA-923 2024 ZIPs, retains every extracted EIA-923 Page-4 generator-month record, and joins exact generator IDs to the EIA-860 Operable identity table.

## Reproduced classification counts

| Classification (Page-4 source rows) | Rows |
|---|---:|
| single_source_candidate | 2,673 |
| multifuel_ambiguous | 651 |
| not_in_operable_inventory | 68 |
| **Total** | **3,392** |

Across four target BAs, 2024 calendar months, and 7 distinct EIA-860 primary energy-source codes found among single-source candidates, the audit generated **336** possible BA–fuel–month cells and found **144** cells with at least one selected source row. The remaining **192** cells are marked `missing_selected_source_rows`, **not measured zero generation**. This grid is a *source-candidate coverage inventory*, not an independently established set of all technologies present within each BA.

Outputs in the run artifact: `eia923_technology_classification_audit.csv`, `eia923_month_technology_coverage.csv`, and `eia923_multifuel_exclusions.csv`.

## Gates before monthly calibration

1. Exclude 651 ambiguous/multi-source rows from single-fuel totals unless manually justified, but **retain their measured energy** in the full observational ledger.
2. Keep 68 outside-Operable records and their signed measured MWh in the observational ledger, with status flags.
3. Reconcile hydro/PS Page-1 plant-month evidence separately; no duplicate contribution from Page 4 without a documented cross-sheet crosswalk.
4. Verify EIA-860 plant/BA assignments, generator status and historical revisions before calling this complete fleet coverage.
5. Produce **actual complete-calendar-month PyPSA generation** and train/holdout year series before calculating empirical calibration skill; the SRP 168-hour stress simulation is not a substitute.

**Historical calibration certified: NO.**
