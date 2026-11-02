# SRP 2024-01 observed net interchange in partial-supply PyPSA

**CI:** [success run 41410684104](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41410684104), commit `34224bbe2ad3c97584c3741c08b9373fb8a94702`.

Full 744-hour official EIA-930 demand and Total Interchange fields (including the seven UTC boundary hours from 2023H2) are reconciled before use. Positive reported total interchange is treated as an **exogenous hourly export sink**. This is **not a physical multizone power network, not an endogenous import/export optimization and not a dispatch-calibrated case**.

| Item | MWh |
|---|---:|
| EIA-930 observed SRP demand | 2,455,626 |
| EIA-930 observed net interchange, exports positive | 2,643,306 |
| Imposed demand + signed net export schedule | 5,098,932 |
| Modeled partial-fleet generation | 4,625,935.045 |
| **Modeled unmet requirement** | **472,996.955** |

The modeled energy balance closes: **4,625,935.045 + 472,996.955 = 5,098,932 MWh**. The EIA-930 published within-source generation is 5,098,927 MWh, differing by −5 MWh from demand + interchange due to observed source reconciliation residual (previously reported, cause not certified). The new model's shortage is a counterfactual artifact of **incomplete EIA-923 Page-4→EIA-860 generator BA identification**, simplified fixed hourly availability, fuel-specific illustrative costs, and omitted hydro, PS, solar, wind, imports and neighboring BA network representation. **Do not describe the shortage as historical unserved energy or infer actual SRP failures.**

Important engineering risk: the new implementation rejects any hour with demand + signed net interchange below zero rather than simulating negative export schedules as actual imports. For SRP January this gate passed. Generalization to other BAs and months will require explicit imports and bidirectional external-bus treatment, not silent clipping.

Next focus: complete BA supply inventory and separate hydro/PS source reconciliation; then implement imports/transfers as actual links or boundary injections and compare with observed EIA-930 generation, before EIA-923 fuel calibration.

**Historical calibration certified: NO.**
