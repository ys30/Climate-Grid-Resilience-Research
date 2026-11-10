# Paper C — hourwise 7/8-category EIA-930 source reconciliation (implementation; CI pending)

## Research question and evidence status

Does the originally reported EIA-930 **Other Fuel Sources** category, and **All Petroleum Products** where separately numeric, account arithmetically for the signed BA-net-minus-six-fuel discrepancy within the **161 original 2024 Jul–Dec modern-taxonomy UTC hours**? This tests source reporting arithmetic only. It does **not** assert generation accounting completeness, actual generation deficit, plant capacity, physical interchange, historical blackout, deterministic loss of load, EENS, or climate causation.

**Code added:** [hourwise source reconciliation](../src/grid_resilience/paperc_2024_seven_eight_fuel_reconciliation.py), with [synthetic missingness and duplicate-key regression tests](../tests/test_paperc_2024_seven_eight_fuel_reconciliation.py). New source-data execution and CI results are **not yet verified**. Do not assign results to the new hourly outputs until an actual source-backed run has passed.

## Verified upstream evidence

The original [16-category source audit](PROJECT_C_2024_ALL_16_FUEL_SOURCE_COMPLETENESS_CI_VERIFIED.md) succeeded in [GitHub Actions #42716078830](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42716078830). Every one of the 644 BA-hours has at least one original source-category blank. Previous 161-hour six-category BA-net signed weekly differences were **AZPS +14,487**, **CISO −25,937**, **SRP −3,986 MWh**; BPAT Coal was blank in all 161 original hours. Original Other Fuel weekly signed sums are AZPS **+14,487**, CISO **−36,109**, SRP **−3,986 MWh**. CISO original Petroleum totals **+10,183 MWh**. CISO therefore has an arithmetic **−11 MWh** six-plus-Other-plus-Petroleum aggregate difference, which must not be attributed to rounding, storage, line loss, or a physical mechanism without separate evidence.

## Strict hourly design

For each (BA, UTC hour), using the *same original-source keys*:

- Define **six-component signed difference** `R6_t = NG_t - S6_t` **only if all six original source components and BA net generation are numeric**.
- Define **seven-component signed difference** `R7_t = R6_t - Other_t` **only if Other is originally numeric**.
- Define **eight-component signed difference** `R8_t = R7_t - Petroleum_t` **only if Petroleum is originally numeric**.
- Preserve the original source category sign, including negative `Other` values; never cap negative values at zero.
- A blank Petroleum cell leaves `R8` null even when `R7` can be calculated. Blank Coal leaves all three source differences null.
- Report both the **sum of signed residuals** and **sum of absolute hourly residuals** over separately declared admitted hour cohorts. A zero signed weekly total need not imply hourly agreement because errors may cancel.
- Do not fill blank source values with zero; do not stitch the first seven legacy-taxonomy hours into this modern 161-hour analysis; do not claim complete 16-category source accounting even when R7 or R8 is exactly zero.

## Required CI evidence before publication

1. Run `python -m pytest -q tests/test_paperc_2024_seven_eight_fuel_reconciliation.py`.
2. Reuse the original **source-backed** 16-fuel BA-hour CSV and same-key six-fuel CSV from the audited upstream CI artifact, not synthetic test data.
3. Execute `python -m grid_resilience.paperc_2024_seven_eight_fuel_reconciliation --fuel <original-full-16-long-csv> --six <verified-six-fuel-hourly-csv> --output <artifact-directory>`.
4. Verify output coverage: 161 hours × 4 BAs, AZPS/CISO/SRP admitted for R7, BPAT inadmissible for R7, and no missing-as-zero values. R8 admission is dependent on **original Petroleum field completeness**, which must be verified from actual hourly output.
5. Audit whether the source-observed **−11 MWh** CISO aggregate difference is distributed over one or several source hours, and distinguish signed cancellation from absolute misfit. Preserve original source SHA-256, run URL, commit, and archived CSV artifacts.
6. Require existing physical EENS/historical calibration gate to stay **false** in the manifest and manuscript.

## Publication placement

Appendix or Supplementary Methods / Source Data Integrity. The main paper should emphasize differences between **reported hourly generation categories**, **partial fleet model supply**, and **historical physical availability** rather than present incomplete-fleet simulated shortages as observed electricity outages.
