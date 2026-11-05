# SRP 2024 EPA–ERA5–EIA930 multi-day moving-block sensitivity — source CI verified

## Verification and provenance

Real original-source [GitHub Actions run 42068799659](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42068799659) **SUCCESS** on commit `ed7eca5cc5f92c8aa969e93eac2ac83c3c632739`; [machine-readable 60-row source artifact 13435475654](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42068799659/artifacts/13435475654). Unit and source tests, official upstream artifact downloads, model calculations, scope gates and file upload all passed.

Inputs are the verified **2024 local-July** EPA–ERA5 source panel ([CI 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085)) and **official July 2024 EIA-930 SRP BA demand** ([CI 41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594)). Exact source-hour intersection: **737 hours for each of 10 EPA source units**, 31 Arizona MST dates (30 complete days, then 17 hours of the final local date). Do not invent the seven UTC-August demand hours outside the July EIA file.

## Experimental design

For each source EPA unit, the original **temperature** slope from an exploratory linear probability model for *reported Operating Time >0* and exploratory OLS for *source Gross Load (MW) conditional on positive reported operation* is recomputed under three resampling rules:

- Draw **2 consecutive local-standard calendar dates** at a time, with replacement, until 31 date-occurrences have been selected.
- Repeat using **3 consecutive dates**.
- Repeat using **5 consecutive dates**.

There are **120 draws for each width** (2, 3, 5). Blocks never wrap across month end; only actually observed source dates can be drawn, preserving existing partial-day observation counts. Each sampled source date-occurrence receives its own day-fixed-effect label. SRP BA reported demand and MST hour fixed effects remain in the model. The date-within transformation was already independently checked against the original OLS dummy-variable fit in the previous day-bootstrap CI. The output preserves both admissible and failed resample counts and reports percentile spans only when at least 90% of 120 draws identify the model.

**Important:** percentile ranges here are sensitivity diagnostics, **not statistically validated confidence intervals**. Dates within a heatwave may be correlated for more than five days; only one calendar month is available, and consecutive-block resampling near the month edge has sampling-composition effects. Observed source Gross Load is selected by plant dispatch and **is not available net electrical capacity**.

## Illustrative results

### Reported Operating Time > 0 (temperature coefficient in percentage points per °C)

| EPA unit | Original OLS estimate | 2-day 2.5–97.5% sensitivity span | 3-day span | 5-day span |
|---|---:|---|---|---|
| 141/1 | −3.49 | [−10.08, +1.71] | [−10.79, +2.69] | [−10.73, +2.11] |
| 147/K-7 | +2.70 | [+0.04, +5.98] | [+0.13, +5.97] | [+1.51, +6.22] |
| 55129/DBG1 | +0.19 | [−1.14, +2.03] | [−1.44, +1.65] | [−1.44, +0.74] |
| 55129/DBG4 | −1.15 | [−4.25, 0.00] | [−4.11, +0.001] | [−3.28, 0.00] |

### Source Gross Load, *conditional on positive reported operation* (MW per °C)

| EPA unit | Original OLS estimate | 2-day 2.5–97.5% sensitivity span | 3-day span | 5-day span |
|---|---:|---|---|---|
| 141/1 | −2.63 | [−7.03, +2.37] | [−6.18, +1.67] | [−5.58, +0.63] |
| 147/K-7 | +7.14 | [+1.15, +14.90] | [−0.37, +14.28] | [+1.45, +15.39] |
| 55129/DBG1 | +0.27 | [−3.04, +2.94] | [−3.64, +3.35] | [−4.71, +3.36] |
| 55129/DBG4 | Not estimable (18 valid source rows) | Withheld | Withheld | Withheld |

These are data-derived source model coefficients from execution logs and the uploaded verified artifact. The 3-day K-7 *gross load* sensitivity span **crosses zero**, although the 2-day and 5-day spans do not; this is a meaningful warning against claiming stable inferential significance or physical heat enhancement. Contrasts across resampling widths should not be interpreted as a formal block-length selection criterion.

## Evidence and next scientific gates

1. The fact that some source EPA units exhibit opposite conditional associations after demand/date/hour controls demonstrates heterogeneity but does **not** establish turbine-specific physical behavior.
2. Only descriptive source operating indicators and conditional source gross load have been analyzed. Dispatch, unobserved equipment availability, unit-stack-to-EIA generator identity, cooling design, heat-input anomalies and net output are not calibrated.
3. Earlier [single-day bootstrap](SRP_2024_EPA_EIA930_DAY_BLOCK_BOOTSTRAP_ROBUSTNESS_CI_VERIFIED.md) and [leave-one-day-out](SRP_2024_EPA_EIA930_LODO_ROBUSTNESS_CI_VERIFIED.md) provide complementary diagnostics but not independent validation.
4. A defensible future results section should prioritize independent-year/season holdouts and physically documented EIA/CAMD generator associations before using any temperature parameter as a PyPSA derating curve. **No observed EENS, outages, or causally identified heat-driven generation shortfall is established.**
