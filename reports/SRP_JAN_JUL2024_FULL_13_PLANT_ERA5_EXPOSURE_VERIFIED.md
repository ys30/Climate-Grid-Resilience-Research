# SRP Jan–Jul 2024: full matched thermal-plant ERA5 temperature and exposed-nameplate hours

**Verified official-source full Jan:** [run 41775332025](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775332025), [artifact 13296393799](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775332025/artifacts/13296393799).

**Verified official-source full Jul:** [run 41773763147](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147), [artifact 13296450727](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147/artifacts/13296450727).

**Verified immutable-source matched comparison:** [run 41775606409](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775606409), [artifact 13296393961](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775606409/artifacts/13296393961), code commit `2436195a7b41b11cc6b367bb47c713dcfbfb767d` and independently tested analysis code `6735f84e678738192459fd6914e2b29075c72063`.

## Design and provenance

For both full 744-hour UTC months (2024-01 and 2024-07), ERA5 2m temperature came from the Open-Meteo archive API queried using **official 2024 EIA-860 plant coordinates**. Exactly the same **12 gas plants (8,550.1 MW)** and **one coal plant (821.8 MW)** are present in both months. No site imputation. Every source weather request and source archive has provenance metadata and downloaded-byte SHA256 in the respective month artifacts.

The new [same-site analysis code](../src/grid_resilience/srp_matched_thermal_seasonal_exposure.py) rechecks each plant identity, nameplate equality across months, no duplicate hours, exactly 744 UTC hours, nonfinite readings and plausible units. The matched-site comparison is now **100% of this EIA860 annual Plant-BA SRP eligible gas/coal nameplate**, not the entire physical SRP fleet or verified dispatch rights.

## Verified exposure results

| Exposure metric | January 2024 | July 2024 | Difference |
|---|---:|---:|---:|
| Gas: 12 matched plants, 8,550.1 MW, capacity-weighted mean 2m air temperature | **12.014947°C** | **37.078063°C** | **+25.063116°C** |
| Coal: 1 matched plant, 821.8 MW, mean 2m air temperature | **2.088844°C** | **26.259409°C** | **+24.170565°C** |
| Gas fleet-*weighted mean* 2m temperature ≥35°C hours | 0 | **465** | descriptive exposure |
| Gas fleet-*weighted mean* 2m temperature ≥40°C hours | 0 | **231** | descriptive exposure |
| Gas **individual-site source nameplate exposure** ≥35°C (MW × hours) | 0 | **4,021,180.2 MW·h** | **63.2134%** of source capacity-hours |
| Gas **individual-site source nameplate exposure** ≥40°C (MW × hours) | 0 | **2,002,298.5 MW·h** | **31.4764%** of source capacity-hours |
| Coal individual-site ≥35°C source nameplate exposure | 0 | **7,396.2 MW·h** | **1.2097%** of capacity-hours |
| Coal individual-site ≥40°C source nameplate exposure | 0 | **0** | 0% |

For **12 individual gas site exposures** in July, plant-specific >=40°C counts vary from **158 to 262 hours**, with source plant coordinates assigned to their respective ERA5 grid cells. Several neighboring EIA-860 plants have **identical reanalysis temperature series** because they map to the same ERA5 grid cell. Those are **distinct generator/plant source identities**, **not independent meteorological samples**.

The nameplate-weighted mean **individual-site degree-hours above 35°C** is **2,292.7918 °C·h** in July; above 40°C it is **537.551708 °C·h**. These integrate positive deviations above each descriptive weather threshold and differ from simple hours that the **fleet-average** temperature exceeds that threshold.

**Interpretation of units is critical:** `site_exposed_nameplate_mwh_ge_35_c` and `site_exposed_nameplate_mwh_ge_40_c` are exposure denominators, expressed as **nameplate MW × weather hours**, not electrical generation MWh, lost energy, power derating, EENS or outage observations. No temperature-to-MW conversion, efficiency loss factor, heat-outage model or causal climate-change trend was estimated.

## Scientific advance and remaining uncertainties

Compared to the previous [8-gas-site seasonal analysis](SRP_JAN_JUL2024_MATCHED_THERMAL_ERA5_CI_VERIFIED.md), this new matched analysis covers **all 12 eligible gas plant sites** in both source months and gives a more internally comparable meteorological contrast. The January/July differences describe normal monthly atmospheric variation within one year, **not a trend**.

The high-temperature thresholds 35°C and 40°C are **descriptive** and deliberately not labeled technology-specific critical points. Actual gas turbine ambient-temperature curves, cooling technologies, relative humidity/wet bulb, on-site microclimate, actual plant dispatch and transfer capacity, fuel conditions, and event-specific generation availability are unobserved or unvalidated in this source set.

Recommended next independent scientific step: acquire validated **technology-/equipment-specific performance evidence** and, if such evidence is unavailable, test temperature-derating functions as explicitly hypothetical sensitivities only, keeping the weather point-source/plant-grain differentiation transparent. Additional out-of-year heat episodes are essential for external validity. Keep separate the completed source verification from not-yet-completed reliability calibration.

**EIA860 location and full eligible annual BA cohort: verified. Weather-to-plant output calibration: NOT verified. Actual lost MWh or EENS: NOT estimated.**
