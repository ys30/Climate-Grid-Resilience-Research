# Paper C — Cross-year summer heat-active conditional four-BA factorial, 2023 versus 2024

## Independently sourced and verified workflow

**Successful 2023 source intake, activation gate and solver:** [GitHub Actions 42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209), commit `35ba7bf2`, with [full model/input/artifact archive 13592962046](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209/artifacts/13592962046). **Research methods CI 42419233985** also passed.

The comparison uses real original **EIA-930 2023 July–December BA hourly demand**, normalized from UTC hour-ending to hour-start, and actual **Open-Meteo ERA5** four *representative points* (not verified BA-wide polygons). These are matched within 2023-07-10–16 (168 hourly observations per BA). The comparison period 2024-07-01–07 uses the previously independently admitted corrected-source EIA-930 and ERA5 inputs. All 4 BAs (AZPS, BPAT, CISO, SRP) have full observation grids for both candidate periods, with no missing-hour fabrication.

**Heat activation diagnosis:** Highest 2023 July ERA5 representative-point temperature across the four BAs and seven days: **47.3°C**. **509 of 672 BA-hours** activate the specified `+4°C` heat response at a hypothetical `30°C` load threshold. This contrasts with the prior winter February 2024 negative-control (maximum 23.0°C; 0 of 672 active BA-hours), so the cross-year summer test does not suffer the winter thermal-response nonactivation.

## Results: source-observed inputs, *conditionally modeled* outcomes

| Metric (MWh, seven days across four BAs) | July 2023 (10–16) | July 2024 (1–7) |
|---|---:|---:|
| Baseline, isolated four-BA model supply gap | **417,730.627847** | **440,029.150992** |
| Baseline, frozen hypothetical links model supply gap | **238,300.278102** | **292,031.962482** |
| Compound heat–wind model factorial interaction, isolated | **+12,968.975027** | **+14,630.333329** |
| Compound heat–wind model factorial interaction, frozen links | **+12,886.902774** | **+22,515.997901** |

The factorial interaction is `U(heat+wind) - U(heat only) - U(wind only) + U(baseline)`, where `U` is unserved energy **in the incomplete-fleet deterministic screening model**. Both summer source-input weeks show a **positive** second difference with and without hypothetical links; however its magnitude and link sensitivity change materially across years. This is cross-year **model-input robustness**, not a demonstrated real grid risk estimate or climate causal interaction.

**Critical cross-year design limit:** Both periods deliberately use the **same frozen, partial 2024 EIA-860 generic thermal/wind proxy fleet** and **same illustrative three-link ratings fixed from the first week of 2024**. This is a controlled model sensitivity, **not an authentic 2023 generator roster or actual BA intertie capacities**. These periods were not matched for comparable extreme-event severity, baseline load level, resource mix or meteorological spatial patterns; no statistical replication claim is justified by two weeks alone.

## Manuscript implications

1. The original July 2024 positive factorial effect is not unique to the 2024 input window: a second distinct-year summer source window likewise yields positive, assumption-conditional interactions.
2. The February 2024 structural zero remains a **negative control on the hot-weather demand-response function**, not a result that real winter compound risks are zero.
3. The 2023 and 2024 summer linked-network interactions are different; no inference about actual grid interconnection value is warranted while physical line ratings, dispatch and availability are uncalibrated.
4. Place this subsection after the intra-July four-week interaction analysis, with the cross-year figure and a transparent observed-versus-synthetic data inventory. Avoid using “independent extreme-event validation” without preselected weather event definitions or event-severity matching.

### Remaining gates

- Repeat with **year-specific** EIA-860 fleet mappings, technology-level EIA-930 generation and verifiable transfer ratings before quantitative adequacy inference.
- Predefine and source-audit heat/wind extreme-event criteria and matched cross-year baseline exposures, ideally several nonoverlapping years; no pseudo-independent hourly p-values.
- Conduct physical validation of HY/PS operations and transmission; model shortage is not observed or expected energy not served (EENS).
