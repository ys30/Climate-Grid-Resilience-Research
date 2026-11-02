# SRP 2024-01 EIA-923 Page-4 versus PyPSA source-scope audit

**Verified:** [CI run 41408882466](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41408882466), commit `896aaa145fd47ac4dd9e28a84300c53cd8cf405f`. Source implementation: `src/grid_resilience/srp_source_scope_gap.py`.

| Quantity | Verified value |
|---|---:|
| EIA-930 SRP 2024-01 demand, 744 UTC hourly values | 2,455,626 MWh |
| Extracted EIA-923 Page-4 generator-month source reported as SRP, January | 2,160,272 MWh |
| Extracted EIA-923 Page-4 generator-month records | 40 |
| Source rows associated with modeled fuel codes NG/SUB | 40 |
| Source fuel codes absent from model (within selected Page-4 rows) | None |

The numeric difference of **295,354 MWh** is **not measured loss-of-load, imports or a verified residual**. EIA-930 demand is a balancing-authority load accounting quantity, whereas these EIA-923 records are generator-level net electric MWh from a **partial** Page-4 source. They do not cover the complete operational/BA supply mix, including Page-1 hydro and pumped storage, interchange and other resources. An EIA-923 BA field is a reported mapping, not proof that the full BA operational footprint was enumerated.

A classification of `fuel_present_in_model` means merely fuel-code overlap between a source record and one of the modeled primary fuel keys; it is **not** a generator-identity coverage certification or an exact modeled-observed comparison. Thus: **do not calculate MAE/RMSE or claim historical calibration based on these two totals**.

Next: source-aware EIA-923 Page-1 HY/PS monthly provenance, revise generator identity accounting, and reconcile EIA-930 net interchange and independent capacity composition. `Page-4 missing` never means zero generation.

**Historical calibration certified: NO.**
