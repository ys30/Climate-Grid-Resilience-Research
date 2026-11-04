# SRP: exact EIA-860 annual unit crosswalk for EIA-923 NG/GT reporting discrepancies

## Verified source evidence

Official 2024 EIA-860 Operable archive downloaded independently with SHA256 audit; original 2024 EIA-923 Page1/4 January/July source rows reused by immutable [previous verified run 41871741828](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41871741828). **New crosswalk workflow [41873051184](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41873051184) SUCCESS**; associated **Research Methods CI [41873052421](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41873052421) SUCCESS**. Evidence artifact: [13346345165](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41873051184/artifacts/13346345165). Reports source-nameplate from EIA-860 annual Operable roster, exact EIA-923 Page4 generator IDs and Page1 reported fuel/prime-mover source categories.

## Grounded plant-generator identity

| Plant ID | Annual operable generator count | Annual GT candidates (EIA-860 generator IDs) | GT candidate nameplate | Page4 reported generator IDs matching EIA-860 | Page4 mover agreement |
|---|---:|---|---:|---:|---|
| **141** | 10 | **AF4, AF5, AF6, AF7, AF8** (5) | **321.9 MW** | **3 / 3** | **3 / 3** |
| **55129** | 5 | **CTG4, CTG5** (2) | **99.0 MW** | **3 / 3** | **3 / 3** |
| **147** | 7 | **KY4, KY5, KY6** (3) | **173.7 MW** | **2 / 2** | **2 / 2** |

The exact matching of the Page4 reported generator IDs and annual EIA-860 reported prime mover validates that those **reported Page4 records** correspond to named generator identities in the 2024 Operable inventory. It **does not** establish full Page4 completeness, all operational generators, or BA dispatch rights.

All targeted January and July Page4 reported records have **zero GT generator rows**. Conversely, each targeted plant has an EIA-923 Page1 NG/GT monthly reported row and multiple EIA-860 annual GT candidates:

| Plant ID | EIA-923 Page1 GT/NG January net MWh | EIA-923 Page1 GT/NG July net MWh | Page4 GT reported MWh | Non-GT Page1 − Page4 residual |
|---|---:|---:|---:|---:|
| 141 | **374.000** | **22,050.000** | **0 in matched Page4 source rows** | **0 both months** |
| 55129 | **504.000** | **1,323.000** | **0 in matched Page4 source rows** | **0 both months** |
| 147 | **184.304** | **40.474** | **0 in matched Page4 source rows** | **0 both months** |

**Important:** “0 in matched Page4 source rows” here means no *reported Page4 GT generator row*, **not an observed zero GT generator output**. There is no justification to divide an aggregated Page1 GT/NG MWh value across EIA-860 annual candidates, even if they are co-located and classified as GT; the missing per-unit assignment must remain **unidentified**.

## Why this matters for climate-grid calibration

The source-scope discrepancy is now explained to the reporting-category level and the annual candidate GT inventory has been identified. This supports reproducible accounting and selection of follow-up equipment records but does **not** create true generator-month GT net output, thermal derating coefficients, hourly generation, or historical capacity-unavailability evidence.

Annual EIA-860 GT nameplate can be used as an inventory denominator or candidate identity, but not as proof of unit dispatch or to convert Page1 monthly generation to each GT unit's observed capacity factor. Likewise, ERA5 2m air temperature at the plant coordinate is a weather exposure, not turbine inlet temperature or a heat-induced unit outage.

Highest-value next steps: obtain EIA-860 source generator details needed to distinguish the GT units and check their operating/reporting status; locate independent public turbine-level dispatch or emissions/CEMS hourly telemetry where admissible, validate generator/unit mapping and operating hours before regression, and identify relevant gas-turbine performance documentation. CEMS electrical generation may be unavailable even when operating/emissions telemetry exists; never infer measured net MW from an unrelated unit without validation.

**Verified:** full target plant annual Operable generator identities, GT candidate count/capacity, exact reported Page4 generator ID/mover matches, source GT reporting asymmetry. **Not verified:** Page1 GT monthly generation assignment to one or more exact EIA-860 units, physically available capacity, hourly electrical output, high-temperature performance and reliability outcomes.
