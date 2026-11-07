# Project C: independent-event evidence admission — executable gate and next source acquisition

## Current verified source scope

The July 2024 study spans **four adjacent 168-hour windows**, with four BAs and source-audited hourly EIA-930 load and representative-point ERA5 inputs. Although each July week has complete observational timestamps, all four share **meteorological summer 2024** and a fixed **partial EIA-860 fleet**. They are within-month structural sensitivities, **not** independent-season or independent-year validation. The source-vintage demand hour convention was reconciled to **UTC start of hour**; historical first-week results using the prior API label are not exact-input replicas.

The dedicated [fail-closed source-period gate](../src/grid_resilience/paperc_independent_period_gate.py) checks 168 consecutive UTC hourly timestamps × four source BAs; complete BA-hours in both weather and demand; explicit source-date, weather-provenance, hour-start and frozen-capacity assertions; duplicate/missing timestamps; distinct meteorological seasons/years; and no overlapping windows. It distinguishes calendar coverage from event independence and **never** claims physical network calibration or statistical independence. The [automated July cohort CI](../.github/workflows/paperc-independent-period-gate.yml) checks the original source archive and must record that **no cross-season/year holdout is admitted**.

## Prioritized non-overlapping validation design

1. **First independent period:** Select a genuinely different season (e.g., January 2024), but only after matching **all four** CISO/AZPS/BPAT/SRP official EIA-930 UTC start-hour demand and ERA5 source windows for an exact contiguous 168-hour interval. Existing January **SRP-only** analyses do not satisfy this four-BA gate. Dates are candidate design choices, not completed source acquisitions.
2. **Second independent year:** Acquire an analogous 2023 or 2025 nonoverlapping 168-hour period, documenting EIA-930 source vintages and ERA5 data, and re-auditing generator roster and BA definitions. Do not silently reuse the 2024 annual fleet as historically valid in another year.
3. **Hazard selection:** Predefine temperature and wind availability trigger quantiles against a source-grounded reference climatology, retain matched non-extreme controls, and prevent outcome-based event selection. Seven-day candidate windows should not be selected for high *modeled* shortage.
4. **Model evaluation:** Freeze or explicitly rerun sensitivity for the available fleet and link assumptions; preserve the full baseline/heat-only/wind-only/heat+wind design within each holdout, and compare directional second differences without pretending event-hour samples are independent.
5. **Reporting limits:** A source-admitted extra period supports a cross-period *conditional model* robustness comparison only. Physical transfer ratings, hourly available MW, actual PG7–PG12 energy inventories and hydro operation, actual blackouts, and probabilistic EENS remain separate, currently unmet admission gates.

## Paper-ready decision

**Current designation:** complete intra-July source-backed scenario sensitivity, **cross-season/year external validity not established**, physical adequacy calibration not established. Subsequent writing must label results as conditional screening-model outcomes. The independent-event CI is a quality barrier, not itself evidence of new historical events or a completed PyPSA validation run.
