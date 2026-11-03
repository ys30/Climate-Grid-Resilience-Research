# SRP 2024-01 — source-matched zero-output capacity sensitivity

## Why this scenario matters

In the successful archived [run 41542019155](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155), EIA-860 and EIA-923 Page4 matched at the exact **plant + generator** identity level. Of **40** matched units, **37** were screened into the partial supply inventory; **3** were excluded. Among the screened units, **3 additional NG units** at a single plant (55455: CT1A, CT1B, ST1) reported **zero 2024 January net output** in the matched monthly Page4 extract, representing **559.8 MW** of nameplate capacity.

The original model assumed a constant **85% NG availability** and **80% SUB availability** for its matched screened fleet: **5,636.605 MW NG + 657.440 MW SUB = 6,294.045 MW**. The identified zero-observed-output units contribute **559.8 * 0.85 = 475.830 MW** of this assumed constant NG supply.

## Counterfactual (not a historical availability estimate)

Remove **only this 475.830 MW** of assumed constant screened NG supply from the same 744-hour model:

| Quantity | Baseline partial inventory | Hypothetical zero-output removal |
|---|---:|---:|
| Firm modeled supply capability | 6,294.045 MW | 5,818.215 MW |
| Modeled unmet scheduled supply requirement | 472,996.955 MWh | **780,033.435 MWh** |
| Hours with positive modeled gap | 601 | **691** |
| Largest hourly modeled gap | 2,025.955 MW | **2,501.785 MW** |

The hypothetical scenario **increases** the screened model gap by **307,036.480 MWh**. Values are independently recomputed using the original successful artifact's complete 744 hourly demand / exchange schedule.

**Important:** Zero source-reported monthly net generation does **NOT** prove that these units were unavailable, retired, curtailed, economically noncompetitive, or offline in every hour. The scenario is an *availability stress case*, not a reconstructed dispatch history. It does not mean SRP suffered historical load shedding; the inventory is partial and excludes other actual and external generation resources.

## Implementation

`src/grid_resilience/srp_generator_monthly_identity_audit.py` now provides per-fuel exact-match counts and reports the screened zero-output nameplate. `src/grid_resilience/srp_zero_observed_capacity_sensitivity.py` joins reviewed and observed identities, reuses source-reported capacity assumptions, and recalculates a marked hypothetical 744-hour shortfall sensitivity. CI now writes `outputs/srp_real_screen/zero_observed_availability_sensitivity.json` and tests the source identity join, but **the newly modified GitHub CI has not yet been confirmed passing**.

## Required scientific work before historical interpretation

Full BA fleet coverage / reconciliation, observed hourly generation by technology, source-consistent interchanges, and physically grounded transmission and storage constraints. The EIA-923 Page4 40-generator subset is not a substitute for a complete BA census.

**Historical calibration certified: NO.**
