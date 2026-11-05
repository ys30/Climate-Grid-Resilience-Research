# SRP 2024 full local-July 744-hour EPA–ERA5 descriptive heat strata — CI verified

**Evidence:** [real-source GitHub Actions run 41961614671](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961614671) completed **SUCCESS** at commit `e380be1c15ac70b409bb24d5cfc2417aefc3650a`. Artifact [13385079259](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961614671/artifacts/13385079259) contains the unit-level descriptive heat strata CSV, deduplicated plant-weather-hour CSV, and noncausal scope manifest. The upstream fully observed source panel is [run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085).

The first attempt [41961536880](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961536880) failed due to a wrong **artifact subdirectory path**; source data itself was downloaded and regression tests passed. Commit `e380be1c` corrected this path and reran successfully. Preserve this provenance instead of obscuring the failure.

## Independently counted ERA5 weather hours — three site-hour series

| Plant | Below 35 °C | 35–below 40 °C | At least 40 °C | Full local-July hours |
|---|---:|---:|---:|---:|
| 141 | 266 | 240 | 238 | **744** |
| 55129 | 318 | 240 | 186 | **744** |
| 147 | 283 | 228 | 233 | **744** |
| **Distinct site-hour total** | **867** | **708** | **657** | **2,232** |

The additional seven UTC-August weather source hours corrected the earlier 737-hour accounting. Only 21 new site-weather hour records were added, not 70 independent meteorological observations. Note that these are **ERA5 reanalysis point samples**, not on-site thermometers.

## Example observed EPA operating diagnostics

Source EPA unit 141 / 1 has `Operating Time > 0` counts of **48/266 = 18.0%** below 35 °C, **112/240 = 46.7%** at 35–below 40 °C, and **173/238 = 72.7%** at least 40 °C. Conditional mean source-reported gross load for positive-operation records is approximately **31.44**, **40.85**, and **84.92 MW**, respectively. These differences illustrate why dispatch selection and contemporaneous demand are critical: **they must not be described as a positive physical causal effect of heat on generating capacity**.

EPA source unit 147 / K-7 has corresponding positive-operation counts **232/283**, **188/228**, and **199/233**, with mean *gross load conditional on operation* approximately **213.16**, **216.12**, and **215.35 MW**. Their apparent stability does not establish the absence of derating, because load dispatch and equipment availability are unidentified.

The full artifact contains all three temperature bins for each of ten source EPA units. Numerical values above were extracted from the completed GitHub Actions job logs, not inferred from a theoretical weather curve.

## Research interpretation and limitations

1. **Historical observation:** verified EPA source combustion-unit operating reports, joined to original ERA5 site-hour exposure by Part75 local-standard-to-UTC conversion.
2. **Descriptive analysis:** unit-hour conditional operating shares and reported gross load by concurrent site weather bins, with 744 hour conservation for all ten units.
3. **Not demonstrated:** EPA source unit correspondence to any specific target EIA860 GT generator; independent operating availability; grid dispatch control; generator net MW; forced outages; temperature-induced derating; observed EENS; causal effects.
4. **No inferential precision claimed:** three sites' weather histories and multiple colocated EPA units do not supply independent causal replicates. There are no confidence intervals, p-values, regression controls or independent-year validation yet.

## Next verification gates

- Retrieve original ECMPS monitoring-plan unit/source-to-generator documentation and confirm 2024 applicability, especially the four units missing static crosswalk links.
- Add actual EIA-930 hourly demand and contemporaneous BA source context with validated time zones and plant-to-BA attribution before any control-rich observational regression.
- Assess external temperature/operation years and equipment-specific physical ratings before transferring weather effect coefficients into PyPSA availability or reliability calibration.
