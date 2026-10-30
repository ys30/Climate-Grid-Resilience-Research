# V2 capacity source integration gate

This repository's current four-scenario PyPSA solver only has a generic firm `gas_mw` dispatch component and wind. The new adapter accepts the **audited BA/technology totals** exported by the Portfolio V1 EIA-860 workflow, not arbitrary raw EIA spreadsheets. It maps `thermal` to a clearly disclosed **generic dispatchable thermal proxy**, and `wind` to wind nameplate. It saves separate omitted capacities (solar, hydro, nuclear, geothermal, storage and other) and a provenance manifest.

## Preparing a limited screening run

1. Download a validated `eia860_ba_technology_capacity.csv` from the original generator inventory workflow. Check its source-year and BA crosswalk independently; year-end nameplate does not establish summertime dependable availability.
2. Run `python -m grid_resilience.eia860_adapter --source PATH_TO_AUDITED_CAPACITY.csv --output outputs/eia860_projection --year 2024`.
3. Check `excluded_technologies.csv` and `capacity_mapping_manifest.json` before using `capacity.csv` in `historical_inputs` or `research_run`.
4. Treat any resulting PyPSA solve as **partial-fleet sensitivity**, not historical validation. Capacity mapping uses an explicitly assumed all-thermal dispatch proxy, with no technology-specific marginal costs or minimum generation. A publishable paper needs technology-resolved operation and EIA-923 comparison.

**Next scientific integration task:** extend the solver to technology-resolved gas/coal/nuclear/hydro/solar with observed or independently justified hourly availability, fuel costs, maintenance/forced outage factors, and storage state-of-charge dynamics where material. Do not back-fit unknown transfer ratings from EIA-930 measured interchange.
