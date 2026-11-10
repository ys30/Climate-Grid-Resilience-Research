# Paper C — Grand Coulee model sensitivity vs observed pumping context, CI verified

## Reproducibility

The [Grand Coulee source-separated figure CI #42882357268](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42882357268) **SUCCESS** ran six integrity tests, restored two previous CI-audited original artifacts, and generated a 250-dpi PNG and PDF: [figure artifact #13793534312](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42882357268/artifacts/13793534312).

Source materials:
- [Original 16-case / 672h hypothetical PS operating-access PyPSA solve #42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635); [scientific assumptions and 314MW nameplate source report](PROJECT_C_GRAND_COULEE_BPAT_PS_IRRIGATION_OPERATIONS_SOURCE_AND_672H_CI_VERIFIED.md).
- [Source-audited July 31-day USACE/USBR/USGS pump + reservoir observations #42332073470](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42332073470); [original pumping source reporting scope](PROJECT_C_GRAND_COULEE_JULY2024_USACE_REAL_PUMP_MWH_KCFS_DUAL_RESERVOIR_CI_VERIFIED.md).
- [Figure code](../src/grid_resilience/paperc_grand_coulee_model_observation_figure.py), [regression tests](../tests/test_paperc_grand_coulee_model_observation_figure.py), and [GitHub Action](../.github/workflows/paperc-grand-coulee-model-observed-figure.yml).

## Two distinct evidence types — do not combine into inferred measured PS operations

**Panel A — conditional model.** From original 672-hour four-BA isolated incomplete-fleet PyPSA solves, the modeled baseline gap reduction relative to 0% assumed PS availability is:

| Assumed share of 314MW reversible-generator nameplate | Modeled reduction (MWh) |
|---:|---:|
| 0% | 0 |
| 25% | 7,667.105766 |
| 50% | 14,799.651676 |
| 100% | 27,641.637424 |

Assumed access share simultaneously scales symmetric charge/discharge model power and **4h assumed energy capacity**; model 80% roundtrip efficiency, zero initial/terminal SOC, hypothetical 2,000MW / 598,947.6 MWh conventional BPAT HY budget, and incomplete partial thermal/wind fleet are **not physical 2024 plant dispatch measurements**. 314MW is the **original EIA-860 generator nameplate for six reversible PG7–PG12 units**; not a metered charging-power rating.

**Panel B — reported observation.** The official USACE Banks Lake **whole pumping installation** records **169,160 MWh in July 1–28** (corresponding to the model input calendar) and **175,641 MWh in July 1–31**. It includes separate dedicated irrigation pumping equipment and the reversible pump-generator installation: original USACE project pumping cannot be disaggregated to PG7–PG12 or turned into usable PS electrical MWh, generator availability, historical irrigation fractions, annual water energy or storage SOC. The source originally reports 31 complete dated observations; the figure's original inputs are independently checked for that exact calendar, completeness, nonnegativity and both cumulative totals.

## Proposed manuscript caption

**Figure 4. Hypothetical pumped-storage operating-access sensitivity and observed multiuse-water pumping context at Grand Coulee.** (A) Change in the modeled July 1–28, 2024, four-balancing-authority baseline supply gap, relative to a zero-PS model variant, as constant *assumed* available fractions of six EIA-860 source-identified 314MW reversible-generator nameplate are varied (0%, 25%, 50%, 100%). The simulations use an incomplete thermal/wind resource representation, isolated BA network, and assumed 4h storage energy and 80% roundtrip efficiency; they are **not** historical loss-of-load or grid-adequacy estimates. (B) Original USACE daily reported electricity consumption by the **entire** Banks Lake pumping installation, separately identifying July 1–28 corresponding to the model input dates and July 29–31 outside that window. Whole-installation pumping includes distinct irrigation pumps and must not be identified with six reversible PG7–PG12 units, their observed charging, historical state of charge or available electrical energy. Model and observed panels have different reporting units, source populations and inferential scope and do not constitute a physically calibrated model-to-data validation.

## Technical CI correction

The first figure workflow [#42882235506](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42882235506) failed **before real input downloads** because a newly added scenario-label regular expression incorrectly escaped `\\d` as a literal backslash. The parser was corrected in commit [4b892884](https://github.com/ys30/Climate-Grid-Resilience-Research/commit/4b8928846aa2d00fd37c6671e4f6ec618f19d591). Successful run #42882357268 executes the full real-source CI path and uploads the finished figure. This was a code regression, not an empirical model-data discrepancy.

## Remaining scientific admission gates

No actual PG7–PG12 machine-level pumping generation time series, pump curve, irrigation allocation fraction, historical pump head and reservoir stage–volume rating, PS usable storage-energy inventory, complete BA generating fleet, calibrated physical interties, or observed grid EENS has been obtained. This exhibit supports a cautious model-sensitivity and observational-context distinction; it does **not** validate physical historical resilience.
