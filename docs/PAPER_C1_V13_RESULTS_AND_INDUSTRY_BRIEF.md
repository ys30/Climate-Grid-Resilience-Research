# Paper C-1 — Industry-facing results and provenance brief

**Study (solo author: Yu Song):** *Modeled compound heat and low-wind stress depends on resource representation: a reserve-margin explanation for four western US balancing authorities*. Current sole-author manuscript v13, updated title and reserve-margin framing; research preparation, **not yet published**.

**Purpose:** Test whether climate-driven stress interactions are robust to partial generation-resource coverage, rather than assuming outputs of a simplified power model represent actual outages. Designed for climate-risk analytics, grid scenario evaluation, data engineering, and model-risk communication.

## At a glance

| Demonstrated capability | Audited value or scope |
|---|---|
| Balancing authorities | AZPS, BPAT, CISO, SRP |
| Historical model-input windows | Four non-overlapping 168-hour windows in July 2024 (672 hours per BA) |
| Matched climate-stress cases | Baseline; +4°C heat; −30% model wind availability; combined |
| Capacity-sensitivity experiment E2 | 96 PyPSA/HiGHS optimizations; +0%/+25%/+50% hypothetical firm thermal additions relative to BA Week-1 peak |
| Without added capacity | Positive SYSTEM interaction in all eight week × network cases, 8.575–25.211 GWh |
| Sensitivity result | Absolute SYSTEM interaction fell in 7 of 8 cases from +0 to +25%, but Week 2 illustrated links increased 16.205 → 18.602 GWh |
| Relative metric | Rose in all eight cases from +0 to +25%; unstable when denominator approaches zero, undefined when exactly zero |
| Distinct-year check E3 | July 2023 positive SYSTEM interaction (12.969 GWh isolated; 12.887 GWh links) under the same 2024 partial fleet model; 2024 Week-1 reused anchor |
| E1 agency inventory audit | 3,268 EIA-860 Operable generator records, 2,625 admitted strict single-fuel non-storage candidates, 643 excluded |
| Grand Coulee sensitivity (separate model) | Hypothetical full 314 MW PG7–PG12 access lowered modeled baseline gap by 27.642 GWh relative to zero PS access |

## Reproduction evidence

- Main factorial: [factorial_dispatch.py](../src/grid_resilience/factorial_dispatch.py).
- Weather/wind proxy with 3/12/25 m/s rule: [era5_proxy.py](../src/grid_resilience/era5_proxy.py).
- EIA-923 2024 generator-month extraction: [eia923_generator_extract.py](../src/grid_resilience/eia923_generator_extract.py).
- EIA-860 / EIA-923 model-input partial fleet: [eia860_partial_fleet_capacity.py](../src/grid_resilience/eia860_partial_fleet_capacity.py).
- Source/audit and preserved frozen commit: [PAPER_C1_ARCHIVE.md](PAPER_C1_ARCHIVE.md).
- E2 results report: [PROJECT_C_E2_FOUR_WEEK_CAPACITY_INTERACTION_STABILITY_96_SOLVES_CI_VERIFIED.md](../reports/PROJECT_C_E2_FOUR_WEEK_CAPACITY_INTERACTION_STABILITY_96_SOLVES_CI_VERIFIED.md).
- E3 results report: [PROJECT_C_E3_CROSSYEAR_FROZEN_RESOURCE_SHARED_2024_ANCHOR_FINAL_SOURCE_AUDIT.md](../reports/PROJECT_C_E3_CROSSYEAR_FROZEN_RESOURCE_SHARED_2024_ANCHOR_FINAL_SOURCE_AUDIT.md).

## What the model does **not** establish

The main four-week model intentionally includes aggregated **generic thermal and wind** proxies rather than a complete physical fleet. It has no separately modeled hydro, solar, nuclear or storage resources. Interties and load/weather sensitivities are stipulated. BPAT is especially exposed to this omission of hydropower. **Results are conditional screening metrics, not observed outages, EENS/LOLE, historically calibrated grid adequacy, or future climate-impact forecasts.**

The 672-hour Grand Coulee example is a **separate** isolated-BA, energy-limited hydro and pumped-storage formulation. Its 80% round-trip efficiency and usable power/energy are hypothetical. Real USACE whole-installation daily energy use and RISE monthly unit data do not provide the 672-hour unit-level SOC trajectory.

## Links

- [Industry-facing portfolio case study](https://ys30.github.io/projects/climate-grid-resilience-pypsa.html) (re-plots manuscript Table 3 as an accessible figure, does not publish manuscript pages).
- [Main public repository](https://github.com/ys30/Climate-Grid-Resilience-Research).
- [Frozen source commit](https://github.com/ys30/Climate-Grid-Resilience-Research/tree/6b549a6612f280646389f87bfc35453dd0e5d7dc).
- Zenodo dataset **reserved** DOI `10.5281/zenodo.24212503`: **do not claim availability until publication**. No software DOI currently published.

## Industry-facing takeaway

The project demonstrates auditable source-to-simulation pipelines, factorial scenario design, optimization-backed sensitivity testing, and explicit model governance. Its highest-confidence finding is a **structural modeling sensitivity**: the same weather shocks can appear more or less nonadditive as the represented resource margin moves. It does not quantify real Western US outage risk.

*Latest source of record: author-uploaded v13 submission package with its final title, sole-author declaration, four main tables and five main figures. The manuscript and cover letter name Yu Song as sole author, University of New Mexico as the affiliated institution. Numerical results remain unchanged and E1–E3 are frozen. No new experiments were run for this overview.*
