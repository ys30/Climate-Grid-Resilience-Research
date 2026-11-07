# Paper C: First source-admitted cross-season four-BA factorial comparison (Feb vs July 2024)

## Verified runs and source provenance

- [2024 February 5–11 official EIA-930 + ERA5 168h four-BA source admission: CI 42414968609](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42414968609): **SUCCESS**, [original-source input artifact 13591157332](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42414968609/artifacts/13591157332).
- [Winter four-case, two-network PyPSA and summer first-week matched-design comparison: CI 42415608060](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42415608060): **SUCCESS**, [results, solver files and activation diagnostic artifact 13590484205](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42415608060/artifacts/13590484205). Earlier [CI 42415478119](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42415478119) had already successfully solved both model configurations; 42415608060 additionally verified the temperature mechanism.

The February window is a **different meteorological season**, not a different calendar year: February 5–11, 2024 UTC versus July 1–7, 2024 UTC, each 168 consecutive hourly observations × 4 BAs (CISO, AZPS, BPAT, SRP). The winter demand is from the **official original EIA-930 2024 Jan-Jun balance CSV**, the hour-ending labels mapped to model hour-start; winter temperature is Open-Meteo ERA5 **representative-point** weather, not BA-wide weather, and wind availability is a hypothetical power-curve transformation, not measured output. The same EIA-860 **partial generic thermal+wind capacity** snapshot is frozen and the same illustrative **July-first-week 10%-peak intertie rating** (or isolated BA variant) is used. These are *model structure controls*, not verified historical intertie ratings, observed hourly available MW, or a full fleet.

## CI-verified model outputs (MWh per 168-hour window)

| Model statistic | February 2024 (winter) | July 2024 (summer week 1) |
|---|---:|---:|
| Isolated BAs: baseline modeled shortage | 478,743.014486 | 440,029.150992 |
| Hypothetical 10%-peak links: baseline modeled shortage | 354,271.417441 | 292,031.962482 |
| Isolated BAs: heat–wind second difference | **0.000000** | **+14,630.333329** |
| Hypothetical links: heat–wind second difference | **0.000000** | **+22,515.997901** |

The interaction is defined as `U(heat+wind) - U(heat_only) - U(wind_only) + U(baseline)`, where U is **model-optimized unmet load from the incomplete modeled fleet**, not observed EENS or blackout data.

## Diagnostic: exact source of the winter zero

The additional [source-weather activation check in CI 42415608060](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42415608060) found:

- **Maximum of all 672 February ERA5 four-BA representative-point hours: 23.0°C.**
- **Zero of 672 BA-hours** cross the assumed thermal load-response threshold under the experiment's hypothetical `+4°C` heat perturbation: `max(T+4−30,0)−max(T−30,0)=0` throughout.
- Therefore the **heat-only and baseline model demand inputs coincide exactly** in this winter case, and the heat+wind and wind-only demand increments also coincide. The second difference is structurally forced to **zero**, not independently estimated to be zero with sampling uncertainty.

**Scientific interpretation:** This is a **useful falsification/negative-control of season-invariant positive model interaction**, but it does **not** provide an independent test of the physical summer heat–wind mechanism: winter input temperatures never activate the code's heat-response function. Claiming that real winter compound grid hazards disappear would be unsupported. The winter baseline modeled deficits are also large because the partial-fleet supply representation omits major resources; physical adequacy and historical EENS remain uncalibrated.

## Revised independent validation design

1. **Next material validation** should select a temporally independent, source-observed year/season with **actual representative temperatures exceeding the experiment's activation threshold** after the shock, and predefine the hazard window without selecting on modeled shortfall; compare events conditional on observed threshold exposure.
2. Separate a **cold-season negative-control stratum** from **active-heat stress strata**. Do not treat February's 0 MWh interaction as an unbiased winter-versus-summer causal seasonal contrast.
3. Add controls using a more physically justified, calibrated temperature-demand response (including seasonality and cold-related load if supported by data), rather than adopting `30°C` as a universal demand-response threshold.
4. Complete generators, dispatch/availability, source-grounded interties and hydro/PS unit-specific operations before describing modeled gaps as realistic unserved electricity.

**Current milestone:** First reproducible **source-admitted winter versus summer model run completed**, with mechanism-attributed winter zero; **cross-year holdout, active-heat-season generalization and calibrated physical reliability remain open**.

The private paper's Results subsection should report this as a **model-threshold negative control and extrapolation limitation**, not as a strong external validation of compound heat effects.
