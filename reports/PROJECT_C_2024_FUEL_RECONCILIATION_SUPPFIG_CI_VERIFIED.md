# Paper C — 2024 original EIA-930 fuel-accounting supplementary figure (CI verified)

## Archived provenance and reproducibility

- [Successful original-data figure workflow #42857085092](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42857085092)
- [PNG, PDF and numeric-summary artifact #13782014354](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42857085092/artifacts/13782014354)
- [Verified upstream hourwise fuel arithmetic #42855419578](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419578) and [full data interpretation](PROJECT_C_2024_161H_SEVEN_EIGHT_FUEL_HOURLY_RECONCILIATION_CI_VERIFIED.md)
- [Figure code](../src/grid_resilience/paperc_2024_fuel_reconciliation_suppfigure.py), [figure tests](../tests/test_paperc_2024_fuel_reconciliation_suppfigure.py), [workflow](../.github/workflows/paperc-2024-fuel-reconciliation-suppfigure.yml)

The figure artifact contains the rendered 250-dpi PNG and vector PDF, source summary CSV and source scope manifest. The CI successfully checked 644 original BA-hour records, verified the summary against source hourly data, and rendered both formats. This figure **does not use synthetic unit-test values as research results**.

## Figure interpretation

**Panel A:** sum of *absolute* hourly arithmetic differences (MWh) in original-source selected seven-fuel (six original categories plus Other Fuel Sources) and eight-fuel (plus original All Petroleum Products) categories for AZPS, BPAT, CISO and SRP. Hatched N/A means original fields were blank and the particular source accounting check was not admitted—not observed physical zero.

**Panel B:** source-reported signed CISO per-hour residual after including the original numeric Petroleum field. Exactly **78 of 161 hours** have nonzero values, signed sum **−11 MWh**, sum of absolute hourly differences **85 MWh**, maximum single-hour absolute difference **2 MWh**. AZPS closes at every hour for both checks. SRP closes at every hour for its seven-category check, but its original Petroleum cell is blank. BPAT's Coal cell is blank and disallows complete six/seven/eight-source-category checks.

The original 16-category source reporting census still contains one or more missing original fuel-category cells in **all 644 BA-hours**. Seven/eight-component bookkeeping reconciliation is thus not exhaustive physical generating supply, generator dispatch, capacity, real interchange, simulated shortage, observed blackout or historical EENS.

## Proposed supplementary figure caption

**Figure S — Hourly consistency of original EIA-930 fuel reporting for four balancing authorities, July 2024.** (A) Sum of absolute hourly differences between reported balancing-authority net generation and selected numeric original-source fuel components (six specified categories plus Other Fuel Sources; with an eighth category, All Petroleum Products, where reported). Missing source category values render the corresponding series unavailable rather than being interpreted as zero. (B) Signed hourly source reporting arithmetic differences for CISO after including reported Petroleum. Data use the original 2024 July–December modern fuel taxonomy for the 161 UTC hours from July 1 07:00 through July 8 00:00 and preserve the missingness semantics of the source. These comparisons characterize original-source accounting consistency only; they neither establish exhaustive technology generation or operating availability nor quantify physical electricity shortfalls or historical expected energy not served.

## Limitations before paper submission

The figure can be included in Supplementary Results / Data QA. Do not elevate its BA-net source arithmetic to independently validated four-BA physical PyPSA history. Actual generator availability, energy-constrained storage, validated interties, BA source boundary inconsistency, and historical adequacy calibration remain unresolved. The research manuscript itself stays private.
