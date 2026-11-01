# February 2024: observed BA interchange vs. isolated screening adequacy

**Verified CI:** [EIA-930 interchange/import audit and full-month PyPSA screening, run 41267409804](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41267409804) (success).

These are EIA-930 **reported hourly observations aggregated across the complete 696-hour February 2024 UTC month**. Negative net interchange denotes net imports under the source convention; the table below converts this into positive net-import energy.

| BA | Reported demand (MWh) | Reported net imports (MWh; positive = imports) | Net-import/demand ratio | Monthly generation–demand accounting discrepancy (MWh) | Monthly identity passes 1 MWh tolerance |
|---|---:|---:|---:|---:|---|
| AZPS | 2,209,947 | +524,093 | +23.715% | 0 | Yes |
| BPAT | 5,063,536 | −4,513,569 | −89.139% | −3,152,089 | **No** |
| CISO | 15,932,523 | +2,432,049 | +15.265% | −213,709 | **No** |
| SRP | 2,139,896 | −2,456,564 | −114.798% | 0 | Yes |

**Interpretation:** AZPS has a documented net-import direction and substantial monthly net-import energy in this period. The isolated, no-transfer PyPSA capacity screening at 100%, 70%, and 40% uniform availability yielded AZPS modeled unserved energy of 0, 3,553.52 and 601,098.08 MWh respectively. It does **not** demonstrate actual loss-of-load, actual inability to import, or a physical import limit. Other BA accounting inconsistencies are explicitly flagged, not silently calibrated away.

**Important scientific limits:**
- Observed 2024 exchange MWh is an **energy accounting** result, not MW intertie capacity, available import flexibility during stress hours, bilateral flow distribution, or network topology.
- The EIA-860 based screening fleet includes only eligible single-fuel operable units; it excludes some real resources. Dispatch uses identical constant 100%/70%/40% hypothetical availability across selected generation technology categories, illustrative costs and no transfers.
- AZPS's apparent threshold of approximately 78.7% follows peak observed load / included nameplate; it is a property of the assumed screening fleet, **not** an operational reserve requirement.
- The BPAT monthly discrepancy and the CISO discrepancy block source identity certification even if those areas show zero screening shortfalls.
- Demand and interchange use historical observations, while the supply-side constraints and modeled results are not historically calibrated.
- Published paper-level results must demonstrate audited BA/generator mapping, historical technology availability, power balance, matched factorial climate shocks, and uncertainty before attributing modeled shortage to compound weather effects.

**Next test design:** introduce *explicitly hypothetical* import-capacity scenarios with documented scenario parameters and avoid using the observed monthly net-import MWh as a firm MW rating. Compare the matched no-transfer control. Independently audit EIA-930 bilateral interchange and externally grounded intertie limits before making physical network statements.

**Historical generation fit certified: false. Historical adequacy validation certified: false.**
