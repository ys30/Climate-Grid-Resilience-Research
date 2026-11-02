# SRP EIA-923 Page1 HY/PS versus Page4 plant-identity scope — artifact audit

Source: [successful Actions run 41409931415](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41409931415), artifact **13124389927**. Independently read `page1_hy_ps_monthly_observations.csv` and `eia923_page4_full_observation_ledger.csv` from this run.

**Source-specific review:** For reported BA `SRP`, the 2024 Page1 HY/PS table has five distinct plant codes: **100, 145, 148, 149, 150**. The extracted Page4 SRP generator-month source has plant codes **141, 147, 6177, 8068, 55129, 55306, 55455, 55481, 58557, 59338, 60768**. **The sets are disjoint in the source-derived extract**, for both January and the 2024 full-year rows. Therefore none of those Page1 hydro/PS plant identities is present among the SRP-labeled Page4 generator-month rows in this artifact.

January Page1, source-described prime-mover split:
| Plant | HY Jan MWh | PS Jan MWh |
|---|---:|---:|
| 100 | 0 | n/a |
| 145 | 380 | -89 |
| 148 | 192 | -43 |
| 149 | 458 | n/a |
| 150 | -15 | n/a |
| **Totals** | **1,015** | **-132** |

In January these represent seven Page1 plant/prime-mover/fuel source rows, but only five unique plant IDs. Negative values are preserved; n/a means no HY/PS row at that plant in the observed source, **not zero**. Both HY and PS have observed rows in all 12 months during 2024.

Page4 observed SRP January net generation for its selected generator-month rows is **2,160,272 MWh**, from 40 rows. This is **not BA-wide gross/net generation**. EIA-930 separately reports SRP **5,098,927 MWh** January BA net generation with **2,643,306 MWh** outbound net interchange. These distinct products have different scope; **do not directly add Page1 to Page4 and treat the result as BA-wide validated supply**, nor infer the difference as unmodeled renewable power.

**Research impact:** The Page4-only candidate inventory excluded plants with source-labeled HY and PS January observations. This is a concrete potential technology-inventory expansion target, but first requires EIA-860 generator identity/capacity and plant ownership/capability crosswalk with correct storage modeling. These observations alone are not an hourly capacity factor, reservoir, energy budget, or calibrated model input.

**Verification status:** prior source CI successful; plant-set intersection and January values recomputed independently from downloaded artifact. Latest GitHub workflow change `22f5a7f` and all-fuel Page1 CI have **not been confirmed green**. Historical calibration **NOT CERTIFIED**.
