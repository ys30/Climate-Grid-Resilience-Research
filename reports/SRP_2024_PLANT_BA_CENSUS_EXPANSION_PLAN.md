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

## November 3, 2026 — source-shape and scope robustness

The implementation now validates the actual Plant workbook layout assumption with a synthetic ZIP/XLSX fixture and explicitly records `nationwide_operable_records_without_plant_join`. Input capacity validity is checked **after selecting the target BA**; otherwise an unrelated nationwide row with blank capacity could invalidate the SRP-specific audit despite not being in its population. Invalid or missing target-BA capacities still fail closed.

Tests cover malformed official headers, target-BA nonnumeric capacities, unrelated missing plant joins, and unrelated nonnumeric capacities. These are source-contract checks, not evidence that the *real* new expanded census has finished successfully.

Remaining critical acceptance criteria: execute the expanded census on the actual 2024 official ZIP; report the target Plant-BA count/installed nameplate; reconcile any target BA mismatches with Page4; classify renewable/hydro/storage and avoid treating those resources as unconditional hourly firm supply. Current CI success remains **unconfirmed**.

## Independent archived Plant BA fuel reference (2024)

An earlier successfully stored GitHub Actions artifact, `github-actions-artifact-13097269172.zip`, contains `eia860_plant_ba_capacity_candidates.csv` and `eia860_plant_ba_capacity_manifest.json` from an independently constructed EIA-860 Plant-to-Operable crosswalk. Its SRP **eligible single-fuel** aggregates are:

| Fuel group | Operable generator identities | Nameplate MW |
|---|---:|---:|
| Gas | 53 | 7655.1 |
| Coal | 2 | 821.8 |
| Nuclear | 3 | 4209.6 |
| Hydro | 8 | 94.1 |
| Solar | 18 | 1674.9 |
| Wind | 2 | 226.0 |
| **Total eligible** | **86** | **14681.5** |

The same artifact has `azps_srp_excluded_generator_capacity.csv` showing **22 excluded SRP generator rows** with **2,182.1 MW** positive nameplate: 11 secondary/multifuel NG (895.0 MW), 2 excluded pumped-storage WAT (154.1 MW), and 9 MWH (1,133.0 MW). This is **not** a claim that excluded capacity is firm, dispatchable, available, or additive without double-counting.

New machine-readable reference: `references/srp_2024_eia860_plant_ba_eligible_aggregate.csv`, derived from the archived artifact. `src/grid_resilience/srp_plant_ba_technology_crosscheck.py` classifies the newly generated official SRP Plant BA roster into transparent fuel and exclusion categories, then writes per-fuel differences compared with the prior independent artifact. Mismatches remain visible and must be reviewed; the existing 37-screened-generator Page4 model is **not** automatically replaced. The new end-to-end CI has **not yet been verified as passing**.

**Caution:** The EIA-860 Plant BA annual assignment and EIA-923 Page4 monthly reported BA do not necessarily define identical generator populations. The 86 eligible entries should not be interpreted as 86 fully available resources, and the prior model's hourly unmet requirement is not observed historical load shedding.

## Source-level exclusion category correction (2026-11-03)

The archived artifact `github-actions-artifact-13097269172.zip`, file `azps_srp_excluded_generator_capacity.csv`, identifies the following **SRP-only** source-attribution exclusions:

| Category | Primary EIA fuel | Generator records | Nameplate MW |
|---|---|---:|---:|
| Multifuel / secondary-fuel | NG | 11 | 895.0 |
| Pumped storage | WAT (PS mover) | 2 | 154.1 |
| Unmapped primary energy source | MWH | 9 | 1,133.0 |
| **Total exclusions** | | **22** | **2,182.1** |

The initial new crosscheck grouped all `MWH` energy-source records under `storage_excluded` despite the archived classification calling them `unmapped_primary_energy_source`. This classification was fixed in `srp_plant_ba_technology_crosscheck.py`, with corresponding regression expectations updated. **The eligible single-fuel roster (86 identities, 14,681.5 MW) is unaffected**, but the reason codes now stay faithful to the previously verified source audit. This classification correction does not imply a conclusion about the actual operational technology or dispatchability of those nine MWH records; further source review is necessary.

The public GitHub Actions API could not be read in this session, so new workflow execution remains **unconfirmed**, not passing by assertion.

## Source-verified acceptance gate for expanded SRP Plant BA roster

The prior 2024 EIA-860 artifact was inspected again at the original CSV level. Its source manifest reports 16,132 plants with BA assignments, 26,855 US operable generator rows, and one nationwide unmatched generator-plant identity. The six SRP eligible single-fuel categories sum to **86 units and 14,681.5 MW**; the detailed SRP attrition table shows **11 secondary/multifuel + 2 pumped-storage + 9 unmapped = 22 excluded**, totaling **2,182.1 MW**. These are counts from an independently archived source-data pipeline and are not observed dispatch.

The complete SRP GitHub workflow now checks the new Plant BA census against the independently archived **108-unit source roster**, including generator counts and MW for the six eligible fuel categories and the three exclusion category counts. A mismatch **fails CI with a specific reason**, rather than silently returning a successful run. Diagnostic CSVs are included in the workflow's always-uploaded artifacts. The large workflow's latest execution remains unverified; this defines an acceptance criterion, not a claim it has passed.

The isolated fast contract workflow `.github/workflows/eia860-plant-ba-contract.yml` tests ZIP parsing and roster classification without downloading large government archives or running PyPSA.

## November 3 — strict BA provenance control

The new `srp_plant_ba_technology_crosscheck.py` originally aggregated any input roster without independently enforcing `plant_reported_ba == SRP`. That could contaminate SRP totals if an upstream CSV accidentally mixed records from multiple balancing authorities. Commit `536c579` requires explicit target-BA identity checks on every input generator and on the archived reference CSV, and normalizes leading zeros in plant IDs before detecting duplicates. Commit `db5efaa` adds tests for cross-BA contamination, wrong-reference BA, normalized duplicate IDs and blank BA identity. A small pandas 2.2.3 smoke check of those Boolean/normalization contracts passed locally; complete GitHub CI and 2024 source ZIP execution remain unverified. No supply capacities or original model outputs were changed by this guard.
