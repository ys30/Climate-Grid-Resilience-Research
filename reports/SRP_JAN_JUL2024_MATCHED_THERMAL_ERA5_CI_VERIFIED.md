# SRP 2024 January versus July — verified matched-plant ERA5 analysis

**Independent reproducible verification:** [matched source-artifact CI workflow 41774526697](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41774526697) **SUCCESS**, code commit `8d86e4e30185e294873973ec82c4f0166aa4f3b9`. [Artifact 13296233186](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41774526697/artifacts/13296233186) contains the machine-generated matched source summaries, per-plant summaries, paired hourly category aggregates, monthly differences and a caution manifest.

## Input source and reproducibility chain

The CI downloads **immutable outputs from two previously successful official-source workflows** through GitHub's artifact service:

- [January 2024 SRP thermal ERA5 workflow 41772449116](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41772449116): 8 gas sites, 1 coal site, 9 × 744 validated point weather rows.
- [July 2024 SRP full-fleet thermal ERA5 workflow 41773763147](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41773763147): 12 gas sites, 1 coal site, 13 × 744 validated point weather rows, 100% EIA860 annual Plant BA SRP eligible source capacity.
- The [matching implementation](../src/grid_resilience/srp_matched_thermal_seasonal_exposure.py) validates unique plant-hour source identities, exact UTC monthly coverage, finite plausible temperatures, constant source nameplate within each month, and matching EIA860 nameplate across seasons. The July-only four gas sites are **excluded** from the seasonally matched comparison, not filled with estimated January values.

All results below are from the **identity-matched 8-gas + 1-coal subset**, not a comparison of unequal seasonal samples.

| Source exposure metric | January 2024 | July 2024 | July − January |
|---|---:|---:|---:|
| 8 gas plant locations / 6,638.6 MW nameplate: mean hourly fleet-weighted 2m temperature | **11.902894°C** | **37.001422°C** | **+25.098528°C** |
| Same coal plant 6177 / 821.8 MW: mean 2m temperature | **2.088844°C** | **26.259409°C** | **+24.170565°C** |
| Gas fleet-weighted hourly temperature ≥ 35°C | **0 / 744** | **461 / 744** | descriptive hours only |
| Gas fleet-weighted hourly temperature ≥ 40°C | **0 / 744** | **226 / 744** | descriptive hours only |
| Coal plant temperature ≥ 35°C | **0 / 744** | **9 / 744** | descriptive hours only |

The hourly *fleet-weighted mean* threshold count is not equal to the total number of generator-level exposure hours, since each plant's 2m temperature can differ. The table does not establish thermal equipment derating, forced outages or any causal climate effect.

## Scientific interpretation

This milestone removes a composition artifact: July's full 12-gas-site population has mean **37.078063°C**, whereas January's 8-site population has mean **11.902894°C**. Comparing those different populations directly would mix seasonal weather and site selection. With identical sites and EIA860 nameplate weights, the July mean is **37.001422°C**; the paired descriptive exposure change is **25.098528°C**.

The full July 12-gas-site nameplate population is useful for documenting where weather data are available, but the matched 8-site sample is the comparable one for the January/July exposure contrast. Annual Plant-BA classification **is not dispatch ownership**.

## Next highest-value scientific tasks

1. Obtain January ERA5 at the remaining four July gas sites and rerun the full identical 12-site matched comparison; avoid imputation or undocumented mixing.
2. Acquire calibrated equipment-specific ambient temperature versus delivered-MW relationships (or independently observed operating deratings) before reporting heat-induced capacity losses.
3. Repeat across independent summer events/years, with full provenance. Distinguish temperature exposure, natural weather variability and causal climate-change attribution.
4. Continue separating wind-curve model-form uncertainty from actual observed plant wind output, and avoid naming any simulated gap EENS or historical outages.

**Verified:** source-matched site identity, 744h UTC complete months, source-consistent nameplate, ERA5 exposure. **Not verified:** plant thermal derating, physical dispatch rights, real outage risk, climate causality or historical reliability calibration.
