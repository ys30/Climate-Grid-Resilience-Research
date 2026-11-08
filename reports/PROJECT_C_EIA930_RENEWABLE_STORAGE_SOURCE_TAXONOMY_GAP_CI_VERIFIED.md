# Paper C — Original EIA-930 renewable, hydro and storage reporting taxonomy transition

**Study windows:** July 10–16, 2023 UTC; July 1–7, 2024 UTC. Four target balancing authorities: AZPS, BPAT, CISO and SRP.

## CI-verified deliverables and provenance

- [Original two-year, full source-native fuel-hour panel #42462457999](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42462457999), each cohort has **672/672 BA-hours**, original EIA-930 source file SHA256 preserved.
- [Original wind/solar/hydro/storage halfyear-category and blank-status audit #42464011904](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42464011904), five tests passed. [Download 2023/2024 original fuel hourly records, 52 partition–BA–category reporting rows and source audit JSON (artifact 13609799976)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42464011904/artifacts/13609799976).
- [Publication source-reporting completeness heatmap #42464152906](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42464152906), four tests and real-source assertions passed. [Download PDF, PNG, numeric 7 × 4 matrix and scope manifest (artifact 13610836529)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42464152906/artifacts/13610836529).

These are original EIA-930 *source-reported net generation category* cells, not a plant-level measured dispatch or reliable physical adequacy series. An hourly average power report over one hour can be described as MWh but does not identify available MW or the storage state-of-charge. *Absent reported values remain null; no zeros are fabricated.*

## What actually changes at the 2024 halfyear boundary

All four BAs have complete original BA-hour keys. **2024 July 1 UTC 00:00–06:00** (seven hours) comes from EIA-930 `2024 Jan–Jun`, while **2024 July 1 UTC 07:00 through July 7 23:00** (161 hours) comes from `2024 Jul–Dec`. The original source fuel fields change by publication partition:

| Reporting family only | First 7 hours (2024 Jan–Jun source) | Following 161 hours (2024 Jul–Dec source) | Admission |
|---|---|---|---|
| Wind | `Wind` | `Wind without Integrated Battery Storage`; `Wind with Integrated Battery Storage` | Do not assume 168h equivalence |
| Solar | `Solar` | `Solar without Integrated Battery Storage`; `Solar with Integrated Battery Storage` | Do not assume 168h equivalence |
| Hydro | `Hydropower and Pumped Storage` | `Hydropower Excluding Pumped Storage`; `Pumped Storage` | Do not sum different reporting definitions |
| Battery | No comparable legacy stand-alone `Battery Storage` label | `Battery Storage` | Not a 168h energy/SOC record |

The 2023 July 10–16 source has **168 reported values per BA for Wind, Solar and Hydropower and Pumped Storage**, in their unsplit original taxonomy. All four 2024 first-seven-hour legacy categories likewise have seven reported values for these categories. These are true source values, but neither 2023 versus 2024 window nor 2024 old/new taxonomy can be treated as exchangeable without external definition validation.

## Key result: modern 2024 161-hour cell counts

| Original Jul–Dec fuel category | AZPS | BPAT | CISO | SRP |
|---|---:|---:|---:|---:|
| Wind without integrated battery | 161/161 | 161/161 | 161/161 | 161/161 |
| Wind with integrated battery | **0/161** | **0/161** | **0/161** | **0/161** |
| Solar without integrated battery | 161/161 | 161/161 | 161/161 | 161/161 |
| Solar with integrated battery | **0/161** | **161/161** | **0/161** | **0/161** |
| Hydro excluding pumped storage | 161/161 | 161/161 | 161/161 | 161/161 |
| Pumped storage | **0/161** | **0/161** | **0/161** | **0/161** |
| Battery storage | **0/161** | **0/161** | **0/161** | **0/161** |

The empty fields for all four BAs' standalone battery and pumped storage **are not observations of zero output or zero installed capacity**. BPAT has complete original Solar with Integrated Battery Storage reports in the modern 161-hour partition; the other three have no reported readings in that column. Wind with Integrated Battery Storage is entirely blank for all four BAs during the same 161h source period.

### Original reported source MWh (partition-specific, never a 168h harmonized sum)

| BA | Legacy wind first 7h | Modern wind excluding integrated storage next 161h | Legacy solar first 7h | Modern solar excluding integrated storage next 161h | Legacy hydro + pumped first 7h | Modern hydro excluding pumped next 161h |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 1,940 | 29,834 | 336 | 75,377 | 0 | 0 |
| BPAT | 12,616 | 97,446 | 291 | 7,024 | 57,635 | 1,251,752 |
| CISO | 26,458 | 403,508 | 39,846 | 1,201,550 | 24,580 | 503,966 |
| SRP | 447 | 12,581 | 1,819 | 88,442 | 753 | 10,251 |

The above MWh are only the *specific numeric reported category and source partition*. For modern BPAT Solar with Integrated Battery Storage, 161-hour category total is **4,848 MWh**, separately reported and not silently combined with legacy solar. The differences in taxonomy and substantial source-null categories block any claim that these six columns form complete contemporaneous energy-source totals for the 168h window.

## Relation to the capacity reporting-population audit

The earlier [EIA-930A and cited 2025 EIA-860M BA × technology nameplate audit](PROJECT_C_EIA930A_EIA860M_BA_TECH_NAMEPLATE_SCREENING_CI_VERIFIED.md) reports large CISO battery storage nameplate and BPAT conventional hydropower nameplate in **preliminary 2025 inventory files**. The lack of original EIA-930 category observations during this 2024 July 161-hour window **does not negate those annual equipment records**. Conversely, annual 2025 installed nameplate cannot recover historical 2024 battery power, SOC, duration, dispatch, firm capacity, available hydro, or physical adequacy.

This demonstrates an important **nonidentifiability**: the current paper's partial-fleet PyPSA generic-thermal + wind screening model cannot be corrected simply by adding EIA-930 original battery or pumped-storage columns as zeros. A physically credible resource expansion requires independently dated generator technology, hourly renewable/hydro profiles, storage energy and SOC, operations, and independently validated interchange/transfer limits.

## Admissibility for paper and next steps

- **Admitted to supplementary source-quality results:** original reported BA fuel-by-hour records, blank proportions, the exact seven-hour/161-hour archive split, per-category partial-period numeric reports, and the reporting-coverage heatmap.
- **Not admitted:** full 2024 168h harmonized wind/solar/hydro output, July 2024 battery SOC/charge-discharge reconstructed from blank cells, observed shortage/EENS, or original EIA-930 nameplate-equivalent plant capacities.
- **Next scientific gate:** investigate officially documented label definitions for integrated-storage wind/solar and pumped/battery reporting, and separately locate **historically contemporaneous** time-varying renewable/hydro/storage source measurements. If unavailable, retain technology outputs as incompletely observed and restrict physical reliability claims. Preserve the earlier BPAT/CISO balance and bilateral reciprocity source limitations.

**Bottom line:** The two-year BA fuel panel is now complete at the BA-hour key level and source-hash reproducible; reporting completeness is not identical to a complete physical generation baseline. The new evidence supports a publishable *source-quality and model-boundary* supplement, not a validated electricity shortfall study.
