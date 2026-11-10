# Paper C — Original EIA-930 July 2024 seven-/eight-fuel hourly reconciliation (CI verified)

## Exact reproducible evidence

- **Fixed syntax at commit** [a4c0456](https://github.com/ys30/Climate-Grid-Resilience-Research/commit/a4c0456c8d80135f38a296d7f30eaed208a1f9e3).
- [**Original source-backed 161h seven-/eight-category workflow #42855419578 — SUCCESS**](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419578).
- [**Research methods CI #42855419812 — SUCCESS**](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419812).
- [Archived full hourly, summary, and SHA256 source-manifest artifact #13782427218](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419578/artifacts/13782427218).
- Original upstream source cohorts: [16-category original EIA-930 audit](PROJECT_C_2024_ALL_16_FUEL_SOURCE_COMPLETENESS_CI_VERIFIED.md) and [six-category modern-taxonomy accounting](PROJECT_C_2024_161H_ORIGINAL_SIX_FUEL_ACCOUNTING_SCOPE_CI_VERIFIED.md).

## Observed-source results

The exact common cohort contains 2024 July 1 07:00 UTC through July 8 00:00 UTC, **161 hours per BA × four BAs = 644 BA-hour keys**, all from the original modern EIA-930 Jul–Dec source taxonomy. Source blanks are never converted to zero. Seven-component and eight-component reconciliation are separate *conditional accounting* checks, not exhaustive fuel generation reconstruction.

| BA | Six reported | Seven reported | Eight reported | Signed R7 (MWh) | Absolute R7 (MWh) | Nonzero R7 hours | Signed R8 (MWh) | Absolute R8 (MWh) | Nonzero R8 hours | Max single-hour abs R8 (MWh) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AZPS | 161 | 161 | 161 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| BPAT | 0 | 0 | 0 | — | — | — | — | — | — | — |
| CISO | 161 | 161 | 161 | +10,172 | 10,172 | 161 | **−11** | **85** | **78** | **2** |
| SRP | 161 | 161 | 0 | 0 | 0 | 0 | — | — | — | — |

Here R7 = original net generation − (six original numeric reported fuel labels + Other Fuel Sources), and R8 = R7 − originally reported All Petroleum Products. CISO's 161-hour petroleum source is **+10,183 MWh**, reducing signed R7 +10,172 to R8 −11. The absolute hourly R8 sum is **85 MWh**, despite the much smaller signed weekly total: **78** hours have nonzero original reporting differences. The largest single-hour absolute difference is **2 MWh**. AZPS and SRP match the *selected seven-component reporting arithmetic* in every admitted hour. BPAT's original Coal blanks prevent any source-approved six/seven/eight calculation; SRP has no source-admitted original Petroleum cells in this partition.

## Scientific conclusion and restrictions

For AZPS and SRP the selected seven reported components close the BA-net arithmetic at hourly resolution **under the source-category definition used**, while for CISO including reported Petroleum reduces the difference to small but nonzero hourly mismatches. **Neither outcome certifies all 16 original fuel reporting categories complete**: all 644 BA-hours have at least one missing original fuel-category cell. No evidence identifies the remaining CISO small differences with a specific reporting convention, rounding mechanism or physical effect. The source arithmetic is **not** generator-level metered output, firm capacity, storage energy/SOC, line rating, observed load curtailment, historical outage, deterministic simulated shortage, or EENS. All historical physical-adequacy admission gates remain closed.

## Manuscript placement

Suitable for Supplementary Results / Source data reporting consistency, with a clearly labeled plot contrasting signed and absolute hourly differences and a per-hour nonzero indicator. Do **not** position source-category closure as validation of the four-BA PyPSA physical baseline. Keep the main scientific results as clearly identified conditional matched factorial model sensitivities.

## CI validation correction

Earlier workflows at [#42854260139](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42854260139) and [#42854259903](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42854259903) failed on a Python `SyntaxError: unmatched ')'` at line 105 in the new reconciliation module, **before original data analysis**. The syntax was corrected in commit a4c0456 and the two successful runs above confirm both complete test and original-data execution. The previous failures are engineering, not source evidence.
