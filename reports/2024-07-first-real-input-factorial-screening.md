# First observed-input four-scenario screening result (2024-07-01–07 UTC)

**Provenance:** successful [GitHub Actions run #41111007548](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41111007548); values transcribed from its `Verify matching, numerical completeness, and nonadditivity` step. This run passed 16 BA × scenario row checks and the input provenance gate.

**Model scope:** EIA-930 observed BA hourly demand; ERA5 representative-point meteorology; 2024 EIA-860 year-end nameplate projected to **generic thermal and wind only**; omitted generation categories (e.g., hydro/solar/nuclear) not dispatched; hypothetical 10%-of-smaller-BA-peak links on three assumed edges. Heat and wind responses are stipulated shock functions. No EIA-923 validation, observed line-rating constraints, storage dispatch, historical calibration or out-of-sample adequacy test.

## Modeled unserved energy (system sum; MWh)

| Weather scenario | Modeled EENS (MWh) |
|---|---:|
| Baseline | 271,730.350393 |
| Heat only | 397,760.110130 |
| Low wind only | 391,034.531561 |
| Heat + low wind | 540,371.227966 |

The modeled factorial interaction equals
`540371.227966 - 397760.110130 - 391034.531561 + 271730.350393 = +23306.936668 MWh`.
This **positive interaction is superadditive within the specified model**, not evidence of a physical causal interaction in the real grid. Joint shock modeled EENS is 98.863% above baseline. The baseline has 271.7 GWh of hypothetical unserved demand, indicating severe structural incompleteness in this partial-generation screening setup. In particular, this is **not observed outages** and should **not** be used to estimate real western US reliability or costs.

**Next calibration gate:** include all material supply technologies and storage SOC, verify EIA-860 temporal generation availability, benchmark modeled generation against EIA-923 and EIA-930 reported generation, and justify spatial transfers from independently sourced power-system data. Re-solve and assess holdout periods before interpreting regional climate impacts.
