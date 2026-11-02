# SRP 2024 January partial-capacity sensitivity — verified real-load run

**Verified run:** [GitHub Actions 41407961683](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407961683), commit `0fea206ad226bcc8a6459cfbb170fd100f6c56f5`, [artifact 13124470929](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407961683/artifacts/13124470929).

The 744-hour SRP demand is official EIA-930: **2,455,626 MWh** January 2024 UTC. Supply is **only 7,453.1 MW** of generator nameplate from 2024 EIA-860 Operable records matched to the partial EIA-923 Page-4 reported BA SRP identities. This is **not a complete BA fleet or validated hourly availability**. Scenarios uniformly scale the partial candidate nameplate by hypothetical factors 1, 0.75, 0.5 and 0.35, with no time-varying outages, transmission interchange, storage chronology, or documented variable costs. All optimization cases passed monthly supply + unserved = demand energy-balance assertions.

| Uniform hypothetical capacity multiplier | Modeled supply MWh | Modeled unserved MWh | Unserved share |
|---|---:|---:|---:|
| 1.00 | 2,455,626.00 | 0.00 | 0.0000% |
| 0.75 | 2,455,626.00 | 0.00 | 0.0000% |
| 0.50 | 2,426,133.55 | 29,492.45 | 1.2010% |
| 0.35 | 1,940,183.39 | 515,442.61 | 20.9903% |

**Interpretation:** Scenario-dependent partial nameplate reduction first produces simulated shortages by the 50% case. Zero shortage in the 75% case is **not** proof of an actual SRP resource-adequacy threshold or no historical unserved load. Generation by fuel cannot be treated as historical dispatch validation; all selected technologies currently use a common hypothetical marginal cost of 50, and the isolated-BA assumption excludes imports and exports.

Artifact outputs: `availability_sensitivity_summary.csv`, `availability_sensitivity_generation.csv`, `availability_sensitivity_manifest.json` plus source hash provenance and January modeled outputs. No EIA-923 modeled-versus-observed test or withheld-year validation was run.

**Historical calibration certified: NO.**
