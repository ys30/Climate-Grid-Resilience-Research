# Official EIA-923 acquisition and 2024 historical validation checklist

## Confirmed primary source

EIA publishes original Form EIA-923 detailed ZIP files, including **2024 (final)**, at:
https://www.eia.gov/electricity/data/eia923/

Source checked 2026-10-30. EIA describes plant/prime-mover-level electricity generation and fuel consumption, including Schedule 3A/5A. Its 2024 ZIP is final as of the date checked. The public dataset is **not yet acquired or loaded by this repository**. This note must not be interpreted as a completed empirical validation.

## Ingestion requirements

1. Download and retain the original official 2024 ZIP, its official URL, retrieval timestamp, SHA256 checksum and release/revision identification. Do not commit large raw data or confidential credentials.
2. Inspect the workbook sheets and headers from the downloaded version. Explicitly identify plant ID, generator/fuel or prime-mover technology, Jan–Dec net generation columns, reporting units, suppressed/missing indicators and any special reporting rows. Do not assume a fixed workbook layout.
3. Build a source-audited monthly long table retaining `plant_id` **as a string**, `technology`, `period`, `generation_mwh`, `source_file`, `reporting_basis`. Preserve reported zero separately from missing; document conversion of any units.
4. Construct an independent expected-key inventory and a **year-scoped BA assignment**. Evidence for BA attribution must be checked against historic generator/operator/BA information; geographic proximity is insufficient.
5. Run `observation_coverage` then `year_scoped_plant_ba`. Compare with a **full-calendar-month** PyPSA generation solution using `observed_to_model_pipeline`.
6. Audit all major generation technologies, storage behavior, cross-BA transfer ratings and fuel availability before calling any power-adequacy result historically calibrated. Hold out an independent period.

## Known blockers

- No authoritative generator/plant-to-BA crosswalk has yet been independently verified here.
- The prior July 1–7 simulation does **not** cover a full month and remains only screening evidence.
- No source-authenticated EIA-923 generation comparison has been run.
- Technical CI tests use synthetic fixtures and do not substitute for historical calibration.

Official description / data download: https://www.eia.gov/electricity/data/eia923/
EIA API v2 notes: https://www.eia.gov/opendata/documentation.php
