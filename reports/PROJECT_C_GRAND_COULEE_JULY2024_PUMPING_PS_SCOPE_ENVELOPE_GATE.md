# Grand Coulee July 2024: observed project pumping versus hypothetical PG7–PG12 charging envelope

## Scope and reproducibility

The authentic USACE July 2024 daily Banks Lake Pump MWh field reports **whole-project pumping electricity**, not an isolated PG7–PG12 electrical charging meter. Independently verified original-source monthly total: **175,641 MWh** over July 1–31; **169,160 MWh** over July 1–28; maximum single project day **10,735 MWh**. Six PG7–PG12 EIA-860 2024 generating nameplates sum to **314 MW**, which is **not** a verified charging rating.

The optional, explicitly **hypothetical** symmetrical charging limit of 314 MW implies no more than **314 MW × 24 h = 7,536 MWh** per day, regardless of efficiency or water balance. The observed whole-project maximum is **3,199 MWh** higher (factor ~1.425). Consequently the project-wide daily meter cannot be used as a validated 314 MW PG7–PG12-only charger series under this assumed envelope.

This mismatch **does not** identify the dedicated irrigation-pump share, nor establish a PG7–PG12 pumping rating, physical head, charge/discharge cycle, water-volume balance, efficiency, operating SOC, or recoverable stored MWh. The dates above concern source-reported daily electricity, not hourly equipment dispatch. On days falling below the assumed envelope, device-level attribution remains entirely unverified.

## Automatically enforced scope gate

- `grid_resilience.grand_coulee_pumping_scope_gate.pumping_scope_diagnostic` checks observed nonnegative daily MWh against an **assumed** power × 24-hour energy ceiling; never promotes project-level observations into generator-level data.
- `grid_resilience.grand_coulee_2024_july_pump_hydro_source_reconciliation.audit` now appends `hypothetical_314mw_ps_scope_diagnostic` to its existing 31-day original-source JSON manifest.
- Unit tests assert the 10,735-MWh evidence-based peak comparison; integration tests use **synthetic fixture values** (not the observed day-by-day July profile) and test that the manifest flags remain non-calibrated.
- Source provenance, flow-statistic ambiguity, differences in reservoir reporting clocks/datums, and the 31-day/28-day alignment are documented in [the actual-source audit](PROJECT_C_GRAND_COULEE_JULY2024_USACE_REAL_PUMP_MWH_KCFS_DUAL_RESERVOIR_CI_VERIFIED.md).

## Manuscript-safe language

> The 2024 USACE Grand Coulee daily project report independently documents 175,641 MWh of July Banks Lake pumping electricity, including 169,160 MWh in the 28 days overlapping our hypothetical dispatch horizon. However, it aggregates a multipurpose pumping installation, including equipment outside the six reversible generator records. One observed project day exceeded 10,735 MWh, whereas a hypothetical 314-MW symmetrical PG7–PG12 charger could consume at most 7,536 MWh per day. This source-scope discrepancy excludes a direct identification of the aggregate meter as unit-specific storage charging; no physically calibrated pump-storage dispatch or reservoir energy balance is claimed.

For the empirical paper, use this as **a negative identification result** and design constraint, not as observed avoided shortages or a measured climate effect. The existing 672-hour PyPSA four-BA results remain assumption-conditional screening sensitivities.
