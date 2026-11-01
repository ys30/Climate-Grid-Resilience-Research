# Official EIA-923 acquisition and 2024 historical validation checklist

## Confirmed source and verified CI intake

The U.S. EIA publishes its 2024 final Form EIA-923 archive at
https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip
(official landing page: https://www.eia.gov/electricity/data/eia923/).

**Status, 2026-10-31:** the repository's official intake workflow **successfully downloaded and inspected the actual 2024 archive**, calculated a source checksum and inventory, probed workbook schemas, extracted generator-month net generation, audited BA/prime-mover monthly totals, and produced separate hydro/pumped-storage evidence and a Page 1 schema probe. These files are **CI artifacts**, not versioned raw inputs or certified historical calibration. Evidence: [successful intake run 41257620031](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41257620031), commit `abc511bd29d763b9f02d61e6c6c6d2616b2807ae`; [methods tests also passed](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41257619976).

The associated `eia923-2024-intake-manifests` artifact contains the source manifest, structural/schema probes, generator-month extraction, prime-mover audit, hydro/pumped-storage evidence, and Page 1 probe. Do not interpret successful extraction as an independent historical accuracy check.

## Verified engineering steps

1. Retrieve official EIA-923 archive, recording URL, ZIP SHA256, inventory and source layout. **Completed in CI.**
2. Inspect real worksheets, preserve generator/plant identity and classify monthly generation without manufacturing absent records. **Source extraction and structural probes completed; completeness and classification remain under audit.**
3. Compare hydro (HY) and pumped storage (PS) as distinct technologies, explicitly preserving negative PS net generation and reporting absent source coverage as missing, not zero. **Checks implemented and passing; see CI artifacts for actual coverage.**
4. Independently verify historic plant/generator-to-BA assignments, expected fleet/key inventory, and source definitions (net/gross, monthly reporting, fuel/prime-mover). **Not certified.**
5. Match complete calendar-month BA/technology observations to a corresponding PyPSA model solution and report bias, errors, coverage and withheld periods. **Not certified.**
6. Validate historic hourly demand, climate-driven generator availability and independently defensible transfer capacities; run out-of-period evaluation and sensitivity analysis. **Outstanding for end-to-end empirical validation.**

## Non-negotiable scientific boundaries

- Successful CI tests or an official data download do **not** establish a calibrated electricity adequacy model.
- No verified, complete year-scoped plant-to-BA/technology crosswalk or full-fleet EIA-923 calibration is asserted.
- A prior 7-day scenario is not interchangeable with a full-month generation benchmark.
- Inflow/outflow measurements are not transmission thermal ratings; power shortfalls produced by deterministic dispatch are not observed historical outages.
- The repository's historical-calibration flag must remain `false` until independently checked empirical coverage and comparison gates pass.

Related documentation: [empirical readiness](EMPIRICAL_INPUT_READINESS.md), [calibration pipeline](EIA923_CALIBRATION_PIPELINE.md), [BA crosswalk](PLANT_BA_CROSSWALK_AUDIT.md).
