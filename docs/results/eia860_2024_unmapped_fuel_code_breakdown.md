# Four-BA EIA-860 2024 unmapped primary energy source breakdown

Verified by [successful BPAT July workflow 41273367264](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41273367264), and [research methods CI 41273568967](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41273568967).

These rows are **unmapped** primary fuel codes among the four balancing authorities, following hierarchical exclusion of secondary-fuel and explicit storage-technology records. Positive nameplate totals are **not** guaranteed dispatchable MW.

| Primary energy code | Generator records | Sum positive nameplate (MW) |
|---|---:|---:|
| MWH | 251 | 13,450.1 |
| LFG | 122 | 279.4 |
| PG | 23 | 2.3 |
| OBG | 23 | 31.5 |
| WDS | 22 | 385.6 |
| WH | 3 | 44.7 |
| OG | 3 | 37.7 |
| AB | 2 | 33.1 |
| PUR | 2 | 8.0 |
| OTH | 1 | 1.0 |
| **TOTAL** | **452** | **14,273.4** |

Of these, **201 non-MWH records / 823.3 MW** are candidates for further individually validated fuel/technology mapping, not immediate additions to available generation.

| BA | All unmapped records | Sum positive nameplate (MW) |
|---|---:|---:|
| AZPS | 16 | 614.2 |
| BPAT | 41 | 133.0 |
| CISO | 386 | 12,393.2 |
| SRP | 9 | 1,133.0 |

**Decision:** Keep storage-related MWH separate from unconstrained generators. Before adding storage to PyPSA, independently source and audit rated discharge MW, usable energy MWh, charging MW, efficiency and dispatch limits, initial state-of-charge, and BA mapping. Confirm physical technology classifications for non-storage fuels and hourly/annual resource constraints prior to adding them to capacity. Avoid conflating EIA-860 nameplate capacity with dependable BA supply.

**Caveat:** The additional 38 generator rows excluded earlier by explicit storage-technology labels do not overlap the 251 MWH-code rows under this hierarchical audit. Do not treat either category as a complete census of storage units.

Full-fleet capacity calibration: **not certified**. Historical shortfall reliability calibration: **not certified**.
