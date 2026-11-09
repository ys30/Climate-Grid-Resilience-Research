# Paper C — CAISO 2023/2024 observed battery power envelopes and explicitly counterfactual PyPSA storage input bridge

## Source admission and reproducible status

**Observed 5-minute CAISO battery telemetry: [GitHub Actions #42674867012 SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42674867012)**, five regression tests. [Download real-source 2023/2024 5-minute charge/discharge power distribution, all 168 UTC hourly envelope rows per technology scope, UTC-day summaries, and source-scope manifest (artifact 13699562779)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42674867012/artifacts/13699562779).

The source is the already independently reconciled [CAISO five-minute Today's Outlook batteries source #42672045610](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42672045610). It contains **2,016 contiguous 5-minute observations per study window (168h)** in each of these three reported series:
- `Total batteries`
- `Stand-alone batteries`
- `Hybrid batteries`

Original `Total batteries` matches the source's contemporaneous `fuelsource.csv` Battery field for each original 5-minute UTC key; neither `Total` nor `Standalone` is certified to equal a set of physical EIA-930A generator IDs. **Original source telemetry may include hybrids, and the series are not assumed strictly additive**.

The source 2023 study period is **July 10–16 UTC**; 2024 is **July 1–7 UTC**. These are **different weeks**, so changes cannot identify a climate treatment, a normalized growth trend or operating response to a common shock. All results below are *historical observed output behavior*, not a rated technical resource capability.

## Source-grounded signed 5-minute operating distributions

Positive `MW` denotes discharging into the system in Today's Outlook; negative denotes charging. The report divides observations into positive-only discharging and absolute-value negative-only charging before calculating percentiles. Charging and discharging sample populations can have different sizes.

| Original total batteries metrics | 2023 July 10–16 | 2024 July 1–7 |
|---|---:|---:|
| Original source points | **2,016 / 2,016** | **2,016 / 2,016** |
| Maximum reported positive discharge MW | **4,178** | **7,298** |
| Maximum reported negative charge magnitude MW | **3,281** | **6,233** |
| Positive-only discharge P50 | **792 MW** | **998 MW** |
| Positive-only discharge P95 | **3,573 MW** | **6,073 MW** |
| Negative-charge magnitude P95 | **2,577.85 MW** | **4,930 MW** |
| Positive-only discharge P99 | **3,935.40 MW** | **6,466.26 MW** |
| Negative-charge magnitude P99 | **3,089.68 MW** | **5,793.80 MW** |
| Five-minute samples with discharge / charge / exact 0 | **881 / 1,134 / 1** | **875 / 1,141 / 0** |
| Longest uninterrupted positive discharge run | **550 min** | **450 min** |
| Longest uninterrupted negative charge run | **480 min** | **555 min** |
| Descriptive positive-signed 5min power integrated over week | **95,767 MWh** | **153,962.75 MWh** |
| Descriptive negative-charge magnitude integrated over week | **91,026.58 MWh** | **169,379 MWh** |

The source-integrated MWh is an arithmetic integral of the *informational* 5-min average power series, **not the battery's usable capacity, energy SOC, standalone/hybrid plant-level metered energy or an energy-storage reservoir budget**. The maximum observed consecutive charge/discharge run likewise is **not installed storage duration**.

All 2023/24 total, stand-alone and hybrid source distributions, five-minute and hourly profiles and individual UTC-day totals are archived. This phase does not derive or certify charging efficiency, discharge efficiency, battery's total available MWh, battery generator ID, resource uptime or initial SOC.

## PyPSA linkage — *only explicit counterfactual scenarios*

[Source-gated StorageUnit input matrix and 32 per-scenario CSVs: GitHub Actions #42675256298 SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42675256298), five tests, source-bound original 5-minute cohorts and explicit no-SOC/no-EENS assertions. [Download 32 CISO counterfactual StorageUnit inputs, scenario matrix and assumption manifest (artifact 13699253814)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42675256298/artifacts/13699253814).

The existing [PyPSA `multi_technology_dispatch.solve`](../src/grid_resilience/multi_technology_dispatch.py) interface accepts a BA-level `StorageUnit` configuration with `ba`, `power_mw`, `energy_mwh`, `efficiency_store`, `efficiency_dispatch` and `initial_soc_fraction`. The source-to-scenario bridge uses the **smaller of the positive-only discharge quantile and negative-charge-magnitude quantile** to form an *assumed symmetric power scale* for each source series. This is an implementation compatibility choice, not a measured physical upper bound.

| Original cohort | Source subset | Symmetric scenario power from P95 (MW) | From P99 (MW) |
|---|---|---:|---:|
| 2023 | All source batteries | 2,577.85 | 3,089.68 |
| 2023 | Stand-alone only | 2,339.60 | 2,925.28 |
| 2024 | All source batteries | 4,930.00 | 5,793.80 |
| 2024 | Stand-alone only | 4,607.00 | 5,502.00 |

The **32** explicitly declared counterfactual configurations use:
- Four original year × population combinations × **two empirical quantile power scales (P95/P99)** × **two entirely hypothetical energy-duration choices (2 and 4 h)** × **two entirely hypothetical initial SOC fractions (0.25 and 0.75)**.
- Per-direction charge/discharge efficiencies are **0.90 assumed**, implying approximate `0.90 × 0.90 = 0.81` round-trip storage efficiency under the simplified StorageUnit model.
- For each chosen configuration, `energy_mwh = power_mw × assumed duration`. That `energy_mwh` **does not come from actual CAISO generator energy capacity or SOC measurements**.

The source and scenario CSV deliberately retain `observed_quantile_is_not_technical_power_rating`, `energy_mwh_assumed_not_source_measured`, `historical_dispatch_reconstructed=False`, and `observed_EENS_inferred=False` metadata. They are **candidate sensitivity inputs**. No actual historical adequacy response, restoration event or shortage reduction is claimed.

## Physical-model and publication boundaries

At this stage the study has independently validated **CISO's available source-time battery power pattern**, but has *not* built a physically consistent combined-source CISO PyPSA historical system. The EIA-930A generator inventory and 2025 preliminary EIA-860M capacity sources are not July 2024 unit-level operational power/SOC measurements. The four BA study still has incomplete source fuel generation categories, BPAT generation-energy accounting nonclosure, CISO original Total Interchange missingness, unvalidated transfer limits and incomplete hydro/storage energy budgets.

**Publication recommendation:** Present the observed five-minute envelope as a robust, data-driven *historical source analysis*, and the StorageUnit grid as a clearly hypothetical *model sensitivity design*. Do not describe the 32 generated input files as 32 completed PyPSA historical runs; the pipeline has only generated and verified configuration inputs. Any synthetic solver smoke test should be explicitly isolated from the paper's real 2023/24 adequacy outcome.

## Reproducibility

- [Original five-minute signed-power envelope extraction](../src/grid_resilience/paperc_caiso_battery_observed_envelope.py) and [source validation tests](../tests/test_paperc_caiso_battery_observed_envelope.py)
- [CISO StorageUnit counterfactual scenario generator](../src/grid_resilience/paperc_caiso_battery_counterfactual_bridge.py) and [assumption integrity tests](../tests/test_paperc_caiso_battery_counterfactual_bridge.py)
- [Synthetic-only solver integration smoke](../src/grid_resilience/paperc_ciso_battery_synthetic_integration.py); this is a separate CI and **does not establish historic physical validation**.
