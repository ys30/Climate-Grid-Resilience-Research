# SRP Page1 hydro / pumped storage — EIA-860 generator crosswalk (archival artifact)

**Data source:** Prior successful official-source GitHub Actions artifact `13097269172`, file `eia860_2024_operable_generators.csv`, cross-matched by normalised numeric plant ID to independently recovered EIA-923 Page1 HY/PS plant codes 100, 145, 148, 149, 150. **Recomputed from archived source in this session**, not from a newly green CI. Source period is 2024, EIA-860 status OP.

| Plant ID | Generator ID | EIA-860 prime mover | Primary fuel | Nameplate MW |
|---|---|---|---|---:|
|100|SC1|HY|WAT|1.4|
|145|HM1|HY|WAT|9.9|
|145|HM2|HY|WAT|9.9|
|145|HM3|HY|WAT|11.7|
|145|HM4|PS|WAT|99.8|
|148|MF1|HY|WAT|9.2|
|148|MF2|PS|WAT|54.3|
|149|ROOS|HY|WAT|36.0|
|150|SM|HY|WAT|13.0|
| **Total** | **9 units** | **HY 7 / PS 2** | | **245.2** |

Breakdown: **HY 91.1 MW; PS 154.1 MW**. Both plant and prime mover match the reported EIA-923 Page1 categories at these five plant codes. It is a plant/mover-based crosswalk, **NOT proof that each unit generated the reported Page1 MWh**, nor that the five plants exhaust SRP's balancing-authority operating supply.

Previously source-verified January Page1 net MWh: HY **1,015**, PS **−132**. Negative pumping storage net output is valid as a reporting category. The Page1 observed energy is plant/mover/fuel-level, not directly generator-month-level.

**Strict modeling caveat:** EIA-860 nameplate alone does not provide reservoir energy, inflow, chronology, pumped storage roundtrip efficiency, state of charge, actual dispatch, or BA transmission topology. No historical calibration claim. In particular, **do not assign 154.1 MW PS as an unconstrained 744-hour generator**. Obtain independent storage energy limits before adding PS to any adequacy screen.

Source provenance: this session's new crosswalk program `src/grid_resilience/page1_hy_ps_eia860_crosswalk.py` and workflow `eia860-unmatched-status-real.yml` are committed but their latest CI outcome remains unconfirmed. The numbers above were computed independently from *older verified EIA-860 artifact*.

**Historical calibration: NOT CERTIFIED.**
