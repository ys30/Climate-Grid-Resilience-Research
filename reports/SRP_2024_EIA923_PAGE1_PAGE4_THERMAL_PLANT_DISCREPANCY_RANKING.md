# SRP EIA-923 2024 Jan/Jul thermal source disagreement: audited plant-level attribution

**Official-source cross-sheet extraction:** [GitHub Actions 41862581130](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41862581130), SUCCESS at `f7956d42c995744c82daec4536fd4880d10ec514`, [source evidence artifact 13340152664](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41862581130/artifacts/13340152664).

**Verified supplementary discrepancy ranking:** [GitHub Actions 41869332600](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41869332600), SUCCESS at `eae44ffc24094a15dc6d88e4b348a90a48b1e6f7`, with passing [Research Methods CI 41869332753](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41869332753) and [source evidence artifact 13344111822](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41869332600/artifacts/13344111822).

## Population, statistical grains and safe comparison

The eligible EIA-860 2024 SRP *annual Plant BA* source cohort is 12 gas sites (8,550.1 MW nameplate) plus one coal site (821.8 MW). Official EIA-923 Page1 records **plant/fuel/prime-mover** monthly reported net MWh and Page4 records **generator** monthly reported net MWh; this audit crosswalks at **plant and month** after filtering Page1 to matching NG-compatible movers or SUB/ST coal and Page4 to reported BA=SRP. Duplicate coarse Page1 fuel/mover keys are permitted when source rows legitimately repeat; generator/month duplicates in Page4 are rejected.

Page1 and Page4 are overlapping reporting views, so their reported MWh **must not be added**. A difference is a *source-reconciliation issue*, not independently measured missing energy. Negative signed values and true Page4 source zeros are retained; an absent Page4 month remains NaN and is not converted to 0.

## Audited matching and net source differences

| Month | Class | Annual source sites | Page1 reported sites | Page4 reported sites | Matched both | Matched Page1 net MWh | Matched Page4 net MWh | Page1 − Page4 MWh |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Jan 2024 | Gas | 12 | 11 | 10 | 10 | 1,891,061.304 | 1,889,999 | **+1,062.304** |
| Jul 2024 | Gas | 12 | 12 | 10 | 10 | 3,611,429.474 | 3,588,016 | **+23,413.474** |
| Jan 2024 | Coal | 1 | 1 | 1 | 1 | 270,112.610 | 270,273 | **−160.390** |
| Jul 2024 | Coal | 1 | 1 | 1 | 1 | 321,275.430 | 321,634 | **−358.570** |

There are **7 gas plants** with exactly equal Page1 and Page4 reported net MWh in January and in July, and **3 gas plants** with a nonzero difference in each month. The apparent gas net-source disagreement in the July matched cohort is **0.6525%** of Page4 same-cohort signed net MWh; this is not a generator capacity error or a reliability estimate.

### Largest gas source differences — rank by absolute Page1–Page4 discrepancy

| Plant ID | January difference MWh | July difference MWh | Fraction of July absolute gas discrepancy |
|---|---:|---:|---:|
| **141** | +374.000 | **+22,050.000** | **94.1765%** |
| **55129** | +504.000 | +1,323.000 | 5.6506% |
| **147** | +184.304 | +40.474 | 0.1729% |

Every other common-reporting gas plant had exact matching signed monthly MWh in both target months. The Page1 source for plant 141 reports **97,026** MWh in July versus **74,976** in Page4. This is an observed *difference between reporting scopes*, **not independently validated missing generation**. The 2024 annual Plant BA population under investigation is not a guarantee of operational BA dispatch ownership.

### Explicitly unmatched source plants

| Plant | Annual candidate gas nameplate | January reporting | July reporting |
|---|---:|---|---|
| 56948 | 726.0 MW | Page1 only | Page1 only |
| 58413 | 99.8 MW | Neither | Page1 only |

These **825.8 MW** are unrepresented in the Page4 filtered reported-BA monthly source cohort, not observed zero-MWh generation or a weather-driven outage. Both plants have valid official source plant coordinates and independently retrieved January/July ERA5 2m air temperature exposure. Absence of Page4 records may reflect source population/reporting choices, not plant unavailability.

## Acceptance gate and recommended next work

**Accepted:** genuine official source archive SHA-256 provenance, 12+1 eligible annual Plant-BA site scope, explicit 26 plant-month source cells, missing-reporting classification, exact per-plant differences, separate signed vs absolute-discrepancy conservation, and all automated tests.

**Not accepted:** interpreting Page1–Page4 source differences as unit operating losses, actual outages, heat-related derating, or measurement error. Monthly 2024 output cannot isolate hour-of-day ambient temperature effects from commitment, dispatch, demand, maintenance, fuel, cooling conditions or equipment characteristics.

The highest-value *targeted* next step is to investigate Plant **141** EIA923 Page1 underlying fuel/mover rows and Page4 generator identities, including whether subunits or fuel reporting categories differ; then investigate Plant 55129 and the two Page4-unreported sites. Do not distribute the 23,413 MWh July discrepancy across the entire gas fleet as a model correction. Obtain independently measured **hourly unit net output and dispatch/availability context**, plus turbine OEM/cooling documentation, before pursuing weather-conditioned derating calibration.

**Model status:** climatic *exposure* measurements can be used for descriptive risk mapping and assumed sensitivity experiments. Empirically calibrated heat derating, climate-attributable outages, system EENS or predictive adequacy remain **not established**.
