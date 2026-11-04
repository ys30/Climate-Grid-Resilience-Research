# SRP January 2024: natural-gas generator identifiability audit

**Verified official-data workflow:** [41752121163](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752121163) and [Research Methods CI 41752121236](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752121236), both successful at source commit `3d4aeab2dfae1ad6e11717238171b9980dd4699b`. [Artifact 13286301502](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752121163/artifacts/13286301502) includes 32 files, notably `ng_identifiability_source_rows.csv`, `ng_identifiability_buckets.csv`, `ng_identifiability_plant_buckets.csv`, and `ng_identifiability_manifest.json`.

## Source-grain identity evidence

The verified EIA-923 Page 1 January SRP natural-gas records contain **24 plant/fuel/prime-mover source rows** at **11 distinct plants** totaling **1,902,868.304 MWh** of signed reported NG net generation.

| Candidate-generator count based on EIA-860 Plant BA / prime mover / source 1–2 | Page 1 rows | Signed Page 1 NG MWh |
|---|---:|---:|
| 0 candidates | 0 | 0 |
| Exactly 1 candidate | 8 | 569,886.000 |
| 2 or more candidates | **16** | **1,332,982.304** |
| Total | **24** | **1,902,868.304** |

**70.0512%** of the source-reported NG generation falls into the **multiple-candidate** bucket. These records cannot be assigned uniquely to one generator from the available source keys. Even an exactly-one candidate is only a candidate match, not a validated generator-level monthly dispatch or ownership allocation.

## Largest plant-specific candidate ambiguity

| Page 1 NG plant | Plant NG MWh | Multi-candidate source MWh |
|---|---:|---:|
| 8068 | 422,911 | 422,911 |
| 58557 | 332,589 | 189,184 |
| 55129 | 324,002 | 194,362 |
| 60768 | 312,798 | 200,240 |
| 59338 | 197,225 | 118,631 |
| 55455 | 140,432 | 140,432 |
| 56948 | 11,807 | 11,807 |

These observations are not hourly generator dispatch. The EIA-923 reported-BA plant/fuel/prime-mover granularity and EIA-860 annual generator attributes are distinct, as are EIA-930 BA-wide hourly net fuel generation and any contractual dispatch rights.

## Model implication

- Do **not** distribute the 1,332,982.304 MWh equally among candidate generators, or assert observed 744-hour generator availability.
- Keep source-month generation at original plant/fuel/prime-mover grain in source reconciliation.
- A physically constrained hourly PyPSA model needs independent hourly plant dispatch, capacity factors, operational BA attribution and transfer constraints, or an explicit sensitivity-only allocation.
- The previously observed **+477,752.304 MWh** EIA-923 Page 1 NG versus EIA-930 Natural Gas difference is not resolved by candidate identity matching, and must not be treated as additional missing physical generation.

**Generator dispatch attribution certified: NO. Historical grid reliability calibration certified: NO. Observed outages inferred: NO.**
