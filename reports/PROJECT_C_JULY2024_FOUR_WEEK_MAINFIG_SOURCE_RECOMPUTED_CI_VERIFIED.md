# Paper C — Main Figure: July 2024 four-week matched heat × wind factorial study (CI verified)

## Reproducibility source

- [Successful source-recomputed plotting workflow #42876964432](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42876964432) **SUCCESS**.
- [Archived original-derived PNG, vector PDF, model contrasts and scope artifact #13790878917](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42876964432/artifacts/13790878917).
- The source was the already independently verified **32-PyPSA-solve, 128 BA-scenario record** [four observed July-week study #42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361); [original report](PROJECT_C_JULY2024_FOUR_WEEK_FACTORIAL_REPLICATION_AND_EIA930_OFFSET_CI_VERIFIED.md).
- [Figure generator](../src/grid_resilience/paperc_2024_four_week_mainfigure.py), [tests](../tests/test_paperc_2024_four_week_mainfigure.py), [CI](../.github/workflows/paperc-july2024-four-week-mainfigure.yml). No new solver runs are implied: original archived solver records are parsed and all four scenarios' interaction recomputed and matched against original archived BA and system summaries.

## Cohort and exact results

The model uses original-sourced July 1–28 2024 EIA-930 demand (official end-of-hour adjusted to UTC start) and ERA5 weather at four representative BA points, a **partial generic EIA860 annual thermal/wind proxy fleet**, and frozen hypothetical BA links set to 10% of the smaller endpoint BA peak demand as defined for the first week. The links are **not independently calibrated physical transmission limits**. Scenario heat and wind sensitivities are assumed, not observed causal generator deratings. Week 1 legacy hour-lagged results are excluded from this corrected source cohort.

The system factorial second difference `I = U(heat+wind) - U(heat) - U(wind) + U(baseline)` (modeled MWh only):

| 2024 UTC window | Isolated four BA | Frozen illustrative links | Linked minus isolated |
|---|---:|---:|---:|
| July 1–7 | +14,630.333 | +22,515.998 | +7,885.665 |
| July 8–14 | +15,338.708 | +16,204.695 | +865.987 |
| July 15–21 | +14,697.753 | +25,211.030 | +10,513.277 |
| July 22–28 | +8,575.179 | +15,177.070 | +6,601.890 |

The first panel plots paired model variants per week. The second panel plots each AZPS/BPAT/CISO/SRP contribution under the same frozen hypothetical link capacity and preserves **negative BA-specific interactions**. All 40 original model summary keys are cross-checked against the 128 original solver BA-scenario values, with exact 4-week and 2-network scope checks; missing scenarios, altered sums, or claiming historical EENS fail closed.

## Proposed manuscript caption

**Figure 2. Within-July variation and spatial heterogeneity in the modeled heat–wind factorial interaction under frozen, illustrative Western-US balancing-authority network configurations.** (A) Four sequential, nonoverlapping 168-hour source-observed July 2024 windows under isolated-BA and fixed hypothetical 10%-peak intertie configurations. (B) BA-level factorial interactions under illustrative links, retaining negative responses. The interaction is calculated from four matched PyPSA scenarios as combined heat-plus-wind modeled unserved energy minus heat-only minus wind-only plus baseline. Original EIA-930 demand and ERA5 representative-point weather inform scenario inputs; available capacity is approximated by an incomplete EIA-860 technology proxy fleet and the intertie network and climatic generator responses are assumed rather than physically calibrated. The four adjacent calendar weeks are **not four independent extreme-weather events**. The MWh numbers characterize deterministic model second differences and cannot be interpreted as observed grid failures, physical power shortages, blackout attribution or probabilistic expected energy not served.

## Manuscript interpretation and remaining barriers

All four system second differences are positive under both structural configurations, but BA contributions can be negative. The linked-minus-isolated model contrast varies substantially by week and is not empirical evidence that adding real transmission increases weather risk. Model baseline shortages are already very large due to the incomplete proxy fleet. This supports a source-audited *conditional interaction screening* narrative, not a validated adequacy estimate. Independent weather-event/year replication, plant-level available capacity, physical tie-line limits, hydro/PS energy constraints and full original fuel source completeness remain open.

**Visual QC note:** A matplotlib tight-layout warning was emitted in a synthetic figure test although CI passed and PNG/PDF files were generated. Manually inspect final manuscript placement, tick/label clipping, legends and panel footnotes before final submission. The run proves file creation and numeric integrity, not subjective print layout quality.
