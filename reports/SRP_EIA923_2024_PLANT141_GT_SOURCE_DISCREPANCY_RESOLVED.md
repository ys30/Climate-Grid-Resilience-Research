# SRP EIA-923 2024: targeted plant-level GT reporting-grain discrepancy resolved

## Official 2024 original-source evidence and accepted CI

Successful [raw source audit run 41871741828](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41871741828) and [Research Methods CI 41871741784](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41871741784). The [immutable artifact 13344647439](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41871741828/artifacts/13344647439) contains all Page1 original source fuel/mover rows and Page4 original generator rows with worksheet row numbers, their month values, exact mover decomposition, and original archive SHA256. The implementation validates original EIA-923 workbook positions, signed values, identity, source year, BA reporting field and Jan/Jul net-generation columns.

The official Page1 and Page4 are **not independent additive generation measurements**. Page1 is recorded at plant/fuel/prime-mover row grain; Page4 at generator/month row grain. This audit identifies the exact classification-level mismatch; it does not certify unit allocation or infer lost electricity.

## Primary finding: all targeted original cross-sheet discrepancies are accounted for by Page1 NG/GT reporting

| SRP reported plant | Month | Page1 NG / GT net MWh | Page1 non-GT NG net MWh | Page4 non-GT generator net MWh | Page1 − Page4 net MWh | Residual after excluding unmatched GT |
|---|---|---:|---:|---:|---:|---:|
| **141** | January 2024 | **374.000** | **0.000** | **0.000** | **+374.000** | **0.000** |
| **141** | July 2024 | **22,050.000** | **74,976.000** | **74,976.000** | **+22,050.000** | **0.000** |
| **55129** | January 2024 | **504.000** | **323,498.000** | **323,498.000** | **+504.000** | **0.000** |
| **55129** | July 2024 | **1,323.000** | **365,848.000** | **365,848.000** | **+1,323.000** | **0.000** |
| **147** | January 2024 | **184.304** | **71,280.000** | **71,280.000** | **+184.304** | **0.000** |
| **147** | July 2024 | **40.474** | **129,447.000** | **129,447.000** | **+40.474** | **0.000** |

For all six plant-month checks, Page4 has **no GT prime mover row**, whereas Page1 has an NG/GT row. After excluding Page1 GT, Page1 non-GT reported NG net MWh **matches exactly** the Page4 listed non-GT generator net MWh. This exact arithmetic passes the CI gate and explains the previously identified **+23,413.474 MWh July** and **+1,062.304 MWh January** net differences across these three plants.

### Plant 141 original source identities

- Page1 row 130: GT/NG reported **374 MWh (Jan)**, **22,050 MWh (Jul)**.
- Page1 row 133: ST/NG reported **0 MWh (Jan)**, **74,976 MWh (Jul)**.
- Page4 ST generator IDs AF1, AF2, AF3; July net MWh respectively **19,476**, **19,278**, **36,222**, totaling **74,976**. January all three are reported **0**.
- Other Page1 rows include auxiliary/non-target reporting codes BA/MWH, GT/DFO, PV/SUN and ST/DFO, but none is assigned to the NG-only source reconciliation.

### Other plants

- Plant 55129: Page1 CA/NG and CT/NG sum to precisely the Page4 CA/STG plus CT/CTG1 and CT/CTG2 generator totals, while Page1 GT/NG contributes the full extra 504 MWh (Jan) and 1,323 MWh (Jul).
- Plant 147: Page1 CA/NG and CT/NG exactly match Page4 KY7A (CA) and KY7 (CT); Page1 GT/NG contributes the full +184.304 MWh (Jan) and +40.474 MWh (Jul).

**Interpretation:** This is an accounting *source scope/prime-mover coverage explanation*, **not evidence** that the GT source record is physically absent from operations, lost due to weather, overstated, or included in a particular unreported Page4 generator. The reason certain NG/GT rows are not represented at the Page4 generator grain needs independent source-level reporting/documentation verification.

## Scientific consequence for Project C

The earlier EIA923 Page1–Page4 discrepancies must not be used as weather derating calibration targets or distributed across annual EIA860 gas nameplate. In fact, the exact non-GT identity match reinforces the importance of distinguishing reported fuel/prime-mover subsets from generator records. The 2024 Plant BA SRP cohort remains a source population, not independently verified operator-controlled physical fleet. The total reported BA generation scope is still not equivalent to observed EIA930 BA hourly gas supply.

A rigorous next calibration attempt requires actual hourly **unit-level** electrical production, unit-specific ambient temperature/performance specifications, unit availability and dispatch context, cooling system constraints, and independently checked weather series. Until then, retain ERA5 meteorological exposure and PyPSA weather-proxy comparisons as descriptive or conditional scenario analysis, **not** observed EENS, real forced outages or climate-attributable shortages.

**Source discrepancy decomposition: verified. GT subunit physical mapping and performance calibration: not established.**
