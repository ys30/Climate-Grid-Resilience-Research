# Paper C — Cross-year and within-July paper figures: 2024 shared-anchor crosscheck (CI VERIFIED)

## Verification and artifacts

[New cross-archive source-data CI run #42879516949 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42879516949) compares the two **independently archived output bundles** using [cross-year/four-week bridge code](../src/grid_resilience/paperc_crossyear_fourweek_bridge.py), [six regression tests](../tests/test_paperc_crossyear_fourweek_bridge.py) (6 passed), and [strict reproducibility workflow](../.github/workflows/paperc-crossyear-fourweek-anchor.yml). [Reconciled 2024 common-anchor CSV and scope artifact #13793406477](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42879516949/artifacts/13793406477).

Original CI evidence:
- [2023-versus-2024 source-admitted heat-active model run #42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209), and [already successful cross-year publication figure #42441181359](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441181359), [figure artifact #13601059992](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441181359/artifacts/13601059992).
- [Source-admitted 2024 four consecutive July model-week run #42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361), and [layout-clean source-recomputed main figure #42878609152](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42878609152), [figure artifact #13791309521](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42878609152/artifacts/13791309521).

## Strict model-anchor agreement

Two panel families reuse **the identical 2024 July 1–7 (UTC) original demand and representative-point ERA5 input, the same frozen partial 2024 EIA-860 proxy fleet, identical assumed heat/wind response, and identical frozen hypothetical 10%-peak network definition**. The 2023 comparator is **2023 July 10–16**, a different window with the deliberately frozen **2024, not observed 2023**, capacity formulation.

| Network variant | 2023 Jul 10–16 modeled heat×wind interaction (MWh) | 2024 shared Jul 1–7 modeled interaction in both figure sources (MWh) | 2024 shared baseline modeled gap (MWh) | Difference in 2024 interaction across archives (MWh) | Difference in 2024 baseline gap across archives (MWh) |
|---|---:|---:|---:|---:|---:|
| Isolated BAs | +12,968.975027 | +14,630.333329 | 440,029.150992 | **0** | **0** |
| Illustrative frozen links | +12,886.902774 | +22,515.997901 | 292,031.962482 | **0** | **0** |

The CI checks **actual original archive numerical output**, not copied README text; it rejects missing years, unexpected BA/week identifiers, duplicate original model keys, a changed 2024 model baseline or interaction, and any source scope that falsely claims physical grid calibration or historical EENS. Agreement tolerance was 0.001 MWh; **observed CSV discrepancies are exactly 0 MWh**.

## Paper implications

1. The already published intra-July 2024 four-week figure and 2023/2024 two-summer-window figure **share one 2024 Week 1 model result**. This is a **single reused model anchor**, not a second independent replication of 2024.
2. The **2023 July 10–16** result represents a distinct-year real weather/load input period and generates a positive conditional interaction; the distinct periods were **not matched for extreme event magnitude, generator mix, year-specific fuel availability or spatial extremes**.
3. Their output numerical agreement confirms **cross-figure reproducibility under one frozen partial model configuration**, not external validation of generator availability, interregional power-transfer capacity, battery or pumped-storage state, probabilistic resource adequacy, or true observed electricity shortages.
4. The legacy first-week 2024 model with uncorrected EIA930 hour-label convention is **not** part of this cross-archive anchor. Only corrected official EIA930 hour-ending → start-hour input convention is admitted.
5. Both figures can be used together in the manuscript under **Results: conditional weather-interaction sensitivity** and **Results: cross-year input robustness**, with an explicit figure-legend statement that 2024 July 1–7 is shared, not statistically independent.

## Editorial evidence caption

**Source consistency across model figures.** The matched 2023–2024 model-input comparison and the July 2024 four-week analysis reuse the same 2024 July 1–7 four-BA PyPSA scenario set. Numerical verification against the independently archived summary tables confirms exact agreement of the 2024 isolated and illustrative-link heat × wind second differences and modeled baseline supply gaps. The additional 2023 summer window supplies a distinct-year conditional source-input test, but the comparison is not a physically calibrated historical adequacy reconstruction and does not identify actual outages or EENS.

**Status:** common-anchor consistency: VERIFIED. Historical physical grid calibration: NOT VERIFIED. Independent event-severity-matched climate replication: NOT VERIFIED. Manuscript figures: two already CI generated; final human visual review remains appropriate.
