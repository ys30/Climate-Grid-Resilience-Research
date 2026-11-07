# Project C — Grand Coulee July 2024 independent HY/PS energy-accounting verification

## Source and verification

The [Grand Coulee 672-hour model and independent exported SOC audit, GitHub Actions run 42397840448](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42397840448), commit `7dfce21cb9`, completed successfully, including real source-input retrieval, 16 PyPSA/HiGHS optimizations, an independently executed audit of the saved hourly PS/HY trajectories, and artifact upload. The independent checker explicitly printed **16 audited groups**, each with 672 consecutive hours (10,752 exported hourly observations). Its report and original model outputs are preserved in [artifact 13583689177](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42397840448/artifacts/13583689177). This is **post-solver numerical conservation verification**, not independent empirical calibration.

The EIA-860 2024 Grand Coulee six reversible generating-unit nameplates sum to **314 MW**. Hypothetical access fractions 0/25/50/100%, each at an *assumed* four-hour energy duration and *assumed* 80% roundtrip efficiency (except the zero-power control), are model inputs. The four-BA network is isolated and includes an incomplete supply fleet and additional **hypothetical HY 2,000 MW / 598,947.6 MWh** budget over 28 days. All simulated shortage totals are **modeled supply gaps, not real historical EENS, blackout records or avoided damages**.

## Actual 672-hour factorial output (MWh; rounded from CI logs)

| Assumed PS access | Baseline modeled gap | Heat-only | Wind-only | Heat + wind | Compound interaction |
|---|---:|---:|---:|---:|---:|
| 0%: 0 MW / 0 MWh | 1,508,297 | 2,114,325 | 2,071,102 | 2,730,371 | +53,241.973 |
| 25%: 78.5 MW / 314 MWh | 1,500,630 | 2,106,664 | 2,067,439 | 2,726,708 | +53,236.025 |
| 50%: 157 MW / 628 MWh | 1,493,498 | 2,099,187 | 2,064,643 | 2,723,913 | +53,579.909 |
| 100%: 314 MW / 1,256 MWh | 1,480,656 | 2,084,540 | 2,061,116 | 2,720,385 | +55,385.708 |

The interaction is defined exactly as **(heat + wind) − heat-only − wind-only + baseline**, under the *same assumed PS settings*. Positive values here indicate **superadditivity in the screening model objective**, not identified physical climate causality. The modeled baseline gap reduction at 100% access relative to the 0% case is **27,641.637 MWh** (not a measured avoided outage).

### What the additional independent audit adds

- Verifies all four factorial cases at all four assumed PS settings, each on the contiguous July 1–28, 2024 UTC calendar; no missing or duplicate exported hours.
- Checks hourly `SOC[t] − SOC[t−1] = sqrt(eta_roundtrip)*charge[t] − discharge_delivered[t]/sqrt(eta_roundtrip)`, with one-hour steps.
- Checks nonnegative SOC, assumed PS power/energy maxima, zero final SOC, and full-horizon closed-cycle input/output accounting.
- Checks HY dispatch power and a **single 28-day** HY energy budget; budget is not reset between weeks.
- Preserves `historically_calibrated=false` and refuses to interpret project-wide real Banks Lake pumping as the six generators' PS charging.

**Important distinction:** Numerical energy conservation is a necessary condition for a well-posed model but does not supply hourly PG7–PG12 charge/discharge measurements, irrigation disaggregation, hydraulic head/volume or verified transmission and full generation fleet.

## Manuscript Results integration

Suggested subsection: *Intertemporal storage constraints and non-identification of historical pumped-storage dispatch*. Report the complete 0–100% assumed-availability factorial sensitivity and source-verified 31-day USACE pumping as **separate layers**, supported by the independent audit. Pair with the previously generated three original-observation figures. Do not present this as an empirical storage-benefit curve or a physically calibrated hydropower dispatch response.

## Remaining necessary scientific gates

1. Source-admitted PG7–PG12 operating schedules, independently reported dedicated irrigation pump demand, stage–volume and compatible head measurements to constrain PS physics.
2. Full fleet and link-rate calibration, and non-overlapping independent-year/season event validation before historical adequacy claims.
3. Private paper Results/Discussion/Methods integration with a transparent observed-versus-hypothetical data table and uncertainty assumptions.
