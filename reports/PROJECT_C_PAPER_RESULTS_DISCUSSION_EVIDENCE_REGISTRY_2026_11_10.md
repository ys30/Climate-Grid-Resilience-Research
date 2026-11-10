# Paper C — Results/Discussion evidence registry and non-comparability rules (10 Nov 2026)

This is a PUBLIC **evidence-index only** document, not the private manuscript.

## Study modules and admissible claims

| Module | Source run / figure CI | Unit of analysis | Allowed result | Non-comparability guard |
|---|---|---|---|---|
| July 2024 matched factorial | [source solver 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361); [layout-corrected main figure 42878609152](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42878609152) | Four consecutive nonoverlapping 168h windows, four BAs; 2 modeled network variants, 4 scenarios | System second differences (links): +22,515.998 / +16,204.695 / +25,211.030 / +15,177.070 MWh; isolated +14,630.333 / +15,338.708 / +14,697.753 / +8,575.179 MWh | Frozen incomplete 2024 EIA860 gas/wind proxy, assumed heat and wind responses, 10%-peak illustrative links; weekly windows are adjacent, not independent extremes |
| 2023 versus 2024 summer-source robustness | [source solver 42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209); [figure 42441181359](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441181359) | 2023 Jul 10–16 vs 2024 Jul 1–7, each 168h, four BAs | Isolated interactions +12,968.975 vs +14,630.333 MWh; linked +12,886.903 vs +22,515.998 MWh | **Both years use frozen 2024 partial-fleet proxy; not two authentic annual dispatch inventories; years are not event-severity matched** |
| Common 2024 anchor check | [source comparison 42879516949](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42879516949) | Exact July 1–7 2024 cohort present in both analyses | Both 2024 interaction and baseline modeled gap differ **0 MWh** across archived figures in both variants | This is the *same reused scenario result*, not an independent 2024 replication |
| Grand Coulee 672h hypothetical PS stress | [original 16-case solver 42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635); [source-separated figure 42882357268](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42882357268) | July 1–28 672h, four BAs isolated; 0/25/50/100% assumed access | Modeled baseline gap reductions +0 / +7,667.106 / +14,799.652 / +27,641.637 MWh | **Different resource scenario**: hypothetical conventional BPAT HY 2,000MW/598,947.6MWh plus modeled PS 4h/80% and *incomplete* fleet; not equivalent in configuration or modeled outcome to four-week factorial |
| Original Grand Coulee observation | [original USACE/USBR/USGS join 42332073470](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42332073470) | July 1–31 daily original facility-wide pump electricity and stage | Whole Banks Lake pump installation 175,641 MWh in full month; 169,160 MWh July 1–28 | **Whole station ≠ six reversible PG7–PG12 units**; 314MW is rated generator nameplate, not actual measured charging MW. Do not infer SOC/energy storage or compare to model PS charging |
| Original EIA930 7/8 fuel source arithmetic | [original source 42855419578](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419578); [supplemental figure 42857085092](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42857085092) | 161 Jul-Dec modern-taxonomy hours each, four BA (644 keys) | AZPS and SRP seven-category zero hourly absolute mismatch; CISO after petroleum −11 MWh signed, 85 MWh absolute, 78 nonzero hours, max 2 MWh/h | Every original 16-category BA-hour has at least one source blank; source accounting closure is not available generation/capacity or validated dispatch |

## Results and Discussion assembly gates

**R1**: Every figure's quantitative claim must be tied to its **specific original solver artifact**, not copied between incompatible partial fleet/network/HY/PS scenarios. Cite exact time labels (UTC hour-start vs end), BA membership, capacity vintage, threshold, and modeled outcome.

**R2**: Never sum Grand Coulee scenario benefit with the four-week factorial interactions or treat its cumulative 672h model as a straightforward 4-week replication: the energy budgets and optimization horizons differ.

**R3**: Never frame the 2024 first week from crossyear and within-year figures as two independent tests: the exact source-model result is intentionally reused and crosschecked with 0 MWh discrepancy.

**R4**: Describe four positive system-level factorial terms as finite sample conditional model nonadditivity, not an estimated physical interaction, transmission benefit, causal synergy, measured blackout or probabilistic EENS. Individual BA second differences may be negative.

**R5**: Distinguish original observed operating electricity (USACE whole installation) from model assumptions (unit-access fraction, 4h storage energy, symmetric charge/discharge, efficiency, reservoir SOC) and from model optimized unserved load.

**R6**: Original category missingness stays null, never zero; the EIA930 arithmetic sample is 161h modern taxonomy, not a consistently labeled 168h cross-taxonomy fuel population. An accounting identity alone does not imply a calibrated physical grid model.

**R7**: Because initial modeled supply gaps are large from incomplete capacity representation, all modeled deficits must be called *modeled screening shortfalls* or *model supply gaps*, never historical outages, loss-of-load observations, actual EENS/LOLE, or avoided blackout energy.

**R8**: The current evidence supports a manuscript section on *source-audited structural screening sensitivity*. Physical adequacy, causal reliability and extrapolation claims remain blocked until full historical eligible fleet, technology dispatch, calibrated transmission, storage/hydrological constraints and independent-event design are available.

## Suggested manuscript order (private text kept outside public repository)

Results 3.1 source cohort and admission limitations; 3.2 within-July modeled heat-wind interactions; 3.3 crossyear source-input robustness and common anchor; 3.4 hypothetical Grand Coulee PS accessibility and real observational context; 3.5 original fuel-reporting consistency, supplement. Discussion 4.1 nonlinear mathematical/model interaction; 4.2 network assumption sensitivity; 4.3 multiuse water and partial identification; 4.4 source reporting and non-identifiability; 4.5 external validity and bounded conclusions.

The complete narrative draft should stay private until editorial review; this file is restricted to public-safe audit facts and methods.
