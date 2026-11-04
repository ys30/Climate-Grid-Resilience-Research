# SRP Plant 6177 ST/DFO source-code audit: all six EIA-860 source fields

**Evidence:** successful [real EIA-860 / EIA-923 audit run 41743878231](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743878231) and successful [Research Methods CI run 41743878130](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743878130). Source code commit `273da109638843ee5597e79cec346bc59f14de7e`, [artifact 13281678734](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41743878231/artifacts/13281678734). The artifact preserves the raw EIA-923 Page 1 selected fuel row, EIA-860 Operable source-field roster extract, the SHA-256 source manifests, and `eia860_full_fuel_field_probe.json`.

## Findings

The official EIA-860 2024 generator workbook `3_1_Generator_Y2024.xlsx`, Operable sheet, provides the fields **Energy Source 1, 2, 3, 4, 5, and 6**. Exactly **two** operable generator identities appear for Plant ID **6177** (CO1 and CO2). None of these six reported generator energy-source codes equals **DFO**.

EIA-923 Page 1 separately reports exactly **one** January 2024 SRP `ST/DFO` entry for that plant, with **+160.391 MWh** signed net generation. The `ST/SUB` entry remains a distinct **270,112.610 MWh** source observation.

The mismatch is **not** an artifact of the prior parser reading only the first two EIA-860 fuel columns: a complete six-column probe still has zero same-fuel candidates.

## Limits

An EIA-923 fuel-associated net-generation observation is not automatically generator-level production under that same fuel, and an EIA-860 generator fuel-code list can exclude occasional auxiliary/startup fuels. Neither an error in official source data nor a specific operational interpretation is established. Do **not** reassign the 160.391 MWh to SUB, deduplicate the source rows, or use this fuel discrepancy to alter PyPSA capacity or infer outages.

## Remaining scientific checks

1. Verify EIA-923 Page 1 fuel allocation and its net generation definitions from official instructions and investigate whether DFO is a startup/auxiliary fuel at Plant 6177.
2. Check Plant 6177 EIA-923 fuel receipts/consumption and reporting notes rather than assuming an implicit mapping to CO1/CO2.
3. Reconcile Plant BA versus operating dispatch, and compare EIA-930 Coal on the correct BA-wide basis before validating an hourly generator dispatch model.

**Fuel-to-generator attribution certified: NO. Historical grid reliability calibration certified: NO.**
