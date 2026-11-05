# SRP 2024 EPA–EIA source-unit physical identity evidence gate (CI verified)

**Status (2026-11-04):** The [real-source 2024 EPA–EIA identity audit, GitHub Actions run 41962810547](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41962810547), **SUCCESS**, at commit `e2d9a277fac12a4518b9dbfc006ccd6d9a6ca8f7`. The immutable source was the previously verified full-year 2024 archived EPA Unit ID operation profile and pinned static EPA–EIA crosswalk bridge from [CI 41889477040](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41889477040). [Audit artifact 13385863379](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41962810547/artifacts/13385863379) includes the unit-specific review queue and explicit admission manifest.

## Verified findings

- **10** real EPA source units, all with the previously verified **8,784 calendar-hour records per unit in 2024**.
- **6/10** source units possess a pinned *historical static* EPA/EIA relationship; **4/10** do not.
- Priority P0, no static link: `141/7`, `141/8`, `55129/DBG4`, `55129/DBG5`.
- The remaining six source units have linked EIA identifiers but the relationships may be one-to-many, and **none directly establishes a valid physical mapping to one of the ten targeted EIA GT generators**.
- **0** units admitted to 2024 ECMPS-monitoring-plan verified status; **0** units admitted to verified physical generator mapping; **0** generator-level net-MW calibrations authorized.

These zeros are **evidence-admission statuses, not assertions that such historical records do not exist or that the plants are not operating**.

## Evidentiary distinction

EPA states that ECMPS's official submitted monitoring plans are publicly viewable, including unit–stack/pipe configurations. These confirm a reported emissions monitoring arrangement, **not automatically a unique EIA electricity generator identity**. Separately EPA publishes static unit crosswalk material used to bridge power-sector data sources.

Official references:
- [EPA ECMPS User Guide](https://www.epa.gov/power-sector/ecmps-user-guide)
- [EPA CAM API Portal](https://www.epa.gov/power-sector/cam-api-portal)
- [EPA Monitoring Plan Reporting Instructions (December 2024)](https://www.epa.gov/system/files/documents/2024-12/ecmps-2.0-mp-reporting-instructions_2024-12.pdf)
- [EPA Power Sector Data](https://www.epa.gov/power-sector/power-sector-data)

## Reproducible gate

Implementation: [source EPA–EIA identity audit](../src/grid_resilience/srp_epa_2024_identity_evidence_gate.py); [7 regression tests](../tests/test_srp_epa_2024_identity_evidence_gate.py); [source-backed GitHub Actions workflow](../.github/workflows/srp-epa-2024-identity-evidence-audit.yml).

The gate refuses incomplete/duplicated source-unit rosters, invalid calendar hours, inconsistent static link counts and any unsupported assertion of verified 2024 ECMPS plans, direct GT generator mapping or electrical net MW. It emits a provenance-labelled priority queue for source documents to collect; it **does not** itself retrieve ECMPS monitoring plans or establish unique equipment wiring.

## Next gate before physical modeling

For each unit, obtain publicly submitted **2024-effective** ECMPS monitoring plan (effective dates, unit and stack/pipe configuration, monitoring location); separately obtain independent contemporaneous EIA generator/boiler mapping or verified engineering documentation. Audit many-to-many associations and avoid any allocation of an EPA source's entire gross load to multiple generators. Without both chains of evidence, keep EPA gross-load weather correlations as descriptive source-level operating indicators; do not estimate generator thermal derating or observed EENS.
