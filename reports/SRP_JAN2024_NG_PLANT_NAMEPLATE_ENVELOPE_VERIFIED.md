# SRP January 2024: verified plant-level NG monthly nameplate-energy envelopes

**Official source:** successful [SRP EIA-923/EIA-860 audit workflow 41752738613](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752738613) and successful [Research Methods CI 41752738649](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752738649), source commit `e6277312cd6e6231e7097252340bc75967a3ee4c`. [Artifact 13287356313](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41752738613/artifacts/13287356313) contains 34 files including `ng_plant_nameplate_energy_envelope.csv` and its JSON manifest. The audited input files are official EIA-923 January 2024 plant/fuel/prime-mover records and official EIA-860 2024 Plant BA operable nameplate capacity.

## Necessary, not sufficient, physical energy condition

For each Page 1 NG plant `p`, take the **union** of EIA-860 generator IDs that match the plant, prime mover, and either primary or secondary EIA-860 energy-source field for **at least one** NG record at that plant. Sum each such generator's EIA-860 nameplate MW **once**. Define an idealized maximum January energy `E_max,p = 744 h × sum_g C_nameplate,g`; `r_p = E_Page1,NG,p / E_max,p`. This is not a capacity-factor estimate from verified actual January capability, nor a dispatch allocation or an estimate of available reserve margin.

| Plant ID | NG source MWh | Unique candidate generators | Nameplate MW (union) | Fraction of theoretical January ceiling |
|---|---:|---:|---:|---:|
| 8068 | 422,911 | 9 | 1,326.0 | 0.4287 |
| 58557 | 332,589 | 3 | 691.6 | 0.6464 |
| 55129 | 324,002 | 5 | 745.1 | 0.5845 |
| 60768 | 312,798 | 3 | 619.0 | 0.6792 |
| 59338 | 197,225 | 3 | 619.0 | 0.4283 |
| 55455 | 140,432 | 6 | 1,127.0 | 0.1675 |
| 147 | 71,464.304 | 5 | 465.7 | 0.2063 |
| 55306 | 57,763 | 3 | 619.0 | 0.1254 |
| 55481 | 31,503 | 3 | 691.6 | 0.0612 |
| 56948 | 11,807 | 12 | 726.0 | 0.0219 |
| 141 | 374 | 8 | 712.3 | 0.0007 |

The source total is **1,902,868.304 MWh** over **24** Page 1 records at **11** plants. Signed net-generation source conservation checks pass. **No plant exceeds** the idealized nameplate x 744-hour ceiling, and **no plant has zero source-matched candidate nameplate**. The largest observed-to-ceiling ratio is **67.9204%** at Plant 60768.

## Acceptance and exclusion

This screen is a *necessary upper-bound feasibility check* only. It does **not** show plant actual capacity factors, season-specific forced outages, an hour-by-hour feasible dispatch, unique generator MWh attribution, BA dispatch rights, operational transmission limits, or historical calibration. The annual inventory can include candidate generator attributes that are not representative of each 2024-01 hour. Source fuel code NG is evaluated separately from other fuels; monthly net generation is not a guaranteed physical dispatch profile.

**Next modeling gate:** introduce source-preserving monthly plant/technology energy budgets or bounds into an explicit sensitivity model, retaining the unresolved NG Page 1 versus EIA-930 BA-wide difference (**+477,752.304 MWh**) and candidate-identity uncertainty. Document observed versus assumed resources and avoid double-counting shared generators across source rows or physical BA boundaries.

**Historical reliability calibration certified: NO. Actual 744-hour source-driven plant dispatch certified: NO.**
