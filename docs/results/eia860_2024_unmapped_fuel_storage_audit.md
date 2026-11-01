# EIA-860 2024 four-BA roster: unmapped primary fuel audit

Verified detailed classifications in [BPAT July CI 41273139765](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41273139765), success. The observed classification comes from official EIA-860 2024 plant-reported BA assignments and generator nameplate fields, following the conservative single-fuel mapping of `eia860_plant_ba_capacity.py`.

Of **3,268** operable generator roster records for AZPS, BPAT, CISO and SRP, **2,625** records (**121,270.9 MW** of eligible nameplate) were selected; **643** records were excluded: **452** unmapped primary energy source, **153** multi-/secondary fuel, **38** explicit storage. These are *record counts*, not verified nameplate coverage or reliable dispatch capacity.

## Unmapped MWH energy-source records — storage-related, NOT firm generation

| BA | Generator rows | Nameplate MW |
|---|---:|---:|
| AZPS | 13 | 608.0 |
| BPAT | 5 | 34.0 |
| CISO | 224 | 11,675.1 |
| SRP | 9 | 1,133.0 |
| **Total** | **251** | **13,450.1** |

The EIA-860 primary energy code `MWH` is related to electricity storage energy input and cannot legitimately be reassigned as an unlimited fuel-fired generator. The exclusion categories are hierarchical: records with secondary fuel or explicit storage technology were classified before the unmatched-primary-code category. **Thus the 38 explicitly storage-excluded records and these 251 MWH-code unmapped records are separate in this audit, not evidence that only 38 storage generators exist.**

Other unmapped records include landfill gas (LFG), wood waste (WDS), other biogas (OBG), and several minor codes. These must be audited individually for technology compatibility, separate from storage. Do not indiscriminately add their nameplate to reliability/firm generation.

## Model decision

1. Maintain existing four-scenario partial-fleet figures explicitly as screening results; no historical reliability calibration.
2. For storage, require charger/discharger power limits, energy capacity (MWh), round-trip efficiency, initial state-of-charge, intertemporal energy balance and site/BA assignment; an EIA-860 generator nameplate alone is insufficient.
3. For non-storage excluded fuels, map using source-defined energy code, generator technology, data completeness and hourly availability; distinguish records from MW.
4. Before assessing capacity coverage, establish the denominator from a BA-consistent, technology-appropriate full roster and separate physical (capacity) from operational (hourly dispatch) comparisons.

**Current full BA generation fleet certified: false. Storage dispatch calibrated: false. Actual line ratings verified: false.**
