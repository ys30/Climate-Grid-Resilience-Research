# SRP January 2024: NG/SUB source-contribution and EIA-930 fuel-heading audit

**Verified execution:** [official source run 41743236601](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743236601) and [Research methods CI 41743234998](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743234998), both successful at commit `49b3adf00d8122c15a1429329d307db5cee3c10f`. Underlying [artifact 13281608251](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743236601/artifacts/13281608251) contains 24 evidence files, including `page1_ng_sub_plant_attribution.csv`, `ng_coal_cross_source_differences.csv`, and `ng_coal_source_diagnostic_manifest.json`. Source downloads preserve EIA-860, EIA-923 and EIA-930 provenance checksums.

## Measured-source totals, not model error

| Source code / descriptive heading | EIA-923 Page 1 reported net MWh | EIA-930 BA-wide reported MWh | Page 1 − EIA-930 MWh | EIA-923 Page 1 plants |
|---|---:|---:|---:|---:|
| NG / Natural Gas | 1,902,868.304 | 1,425,116 | +477,752.304 | 11 |
| SUB / Coal | 270,112.610 | 536,833 | −266,720.390 | 1 |

Both EIA-930 headings have nonblank reported values in all 744 January UTC hours. **Complete reporting for a fuel heading is not equivalent to compatible cross-source plant membership, BA boundary, dispatch rights or fuel classification.** The signed differences are descriptive scope differences, *not* model errors, missing power, or actual shortages.

## Plant-level contributors

EIA-923 Page 1 NG (24 original source rows): Plant 8068, **422,911 MWh** (22.225%); 58557, **332,589 MWh** (17.478%); 55129, **324,002 MWh** (17.027%); 60768, **312,798 MWh** (16.438%); 59338, **197,225 MWh** (10.365%); 55455, **140,432 MWh**; 147, **71,464.304 MWh**; 55306, **57,763 MWh**; 55481, **31,503 MWh**; 56948, **11,807 MWh**; 141, **374 MWh**. The three largest plants account for **56.73%** of the NG Page 1 total. These are source-attributed plant contributions; no EIA-930 per-plant allocation has been inferred.

The sole Page 1 SUB entry is **Plant 6177: 270,112.610 MWh**. The same plant has a distinct **ST/DFO Page 1 entry of +160.391 MWh**. The 2024 EIA-860 Operable roster shows CO1 and CO2 as ST/SUB, with no DFO in Energy Source 1 or Energy Source 2; this is an explicit fuel-code reconciliation flag, *not* evidence of bad production data or proof that the DFO entry is coal output. Check all EIA-860 energy-source fields and EIA-923 fuel reporting definitions before reclassification.

## Decision gate for the PyPSA model

Do not add the +477,752 MWh NG discrepancy or −266,720 MWh SUB discrepancy as new generator output/capacity. Instead:
1. Investigate the five most-contributing NG plants and Plant 6177 against official Plant BA fields, reported fuel/prime mover, and EIA-930's BA-wide boundary.
2. Retain multiple EIA-923 Page 1 plant/fuel records without deduplication, preserve signed storage/pumping and oil outputs, and avoid Page 1 + Page 4 double counting.
3. Establish documented attribution of ownership/BA contract and technology dispatch eligibility before using EIA-860 nameplate MW as available supply.
4. Revisit the 744-hour PyPSA gap *only after* source boundaries and hourly resource limits are independently checked.

**No claims supported yet:** historically calibrated reliability; measured power outages; inferred historical plant failures; a causal climate effect; EENS/LOLE estimates.
