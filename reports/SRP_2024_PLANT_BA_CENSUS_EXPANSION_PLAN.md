# EIA-860 Plant BA census: expand the SRP supply inventory (2024)

## Research gap found

The existing SRP baseline derives its candidate generator population from the generators appearing in EIA-923 Page4 for the selected BA and month. Only **40 generator identities** entered the source join; **37** were screened in. That is **not** a complete SRP balancing-authority fleet.

The annual EIA-860 2024 archive contains a separate **Plant** workbook with a plant-reported **Balancing Authority Code**, and an **Operable** generator inventory. These permit an independent plant-assignment census without first requiring a generator to appear in January 2024 Page4. EIA documents the Plant dataset and its BA field: https://www.eia.gov/electricity/data/eia860/

## New reproducible validation

`src/grid_resilience/eia860_plant_ba_census.py` now reads the official Plant workbook, joins its plant BA assignment to all Operable generators, and reports:

- Number and nameplate MW of all **plant-assigned SRP operable generators**.
- Count of those identities that appear in the selected EIA-923 Page4 2024-01 SRP subset.
- Count and nameplate MW of **additional plant-assigned operable generators absent from that Page4 subset**.

The new CI stage runs this after the existing official ZIP extraction and saves `plant_ba_operable_generator_census.csv` plus `plant_ba_generator_census_manifest.json`. These data are **not** silently injected into the old PyPSA model; the historical partial-fleet analysis is preserved for comparison.

**Important:** plant-reported BA assignment is not proof that its generators were available, dispatched in January, locally delivering electricity to SRP, or part of the same EIA-930 accounting boundary. The scope and physical topology still need source-level reconciliation. No historical outage is inferred from the partial fleet model.

## Status

The earlier source-verified subset is 40 Page4 identities, 37 screened eligible, 7,453.1 MW eligible *nameplate*, and 6,294.045 MW under illustrative fuel deratings. **The expanded Plant BA population count and MW remain pending a successfully executed new workflow. Do not report an invented expanded count.**

Next research steps: inspect the new crosswalk; reconcile year/BA codes and hydro/solar/storage fuels; identify independently supported BA-level energy accounting; verify hourly resource constraints and only then construct a more complete dispatchable fleet and constrained power network.

**Calibration certified:** NO.
