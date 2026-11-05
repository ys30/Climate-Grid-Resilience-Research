# EPA local-July 744-hour ERA5 completion: strict August-boundary admission gate (2026-11-04)

## Status and scope

The original EPA Part75 **July local-standard time** clock corresponds to 2024-07-01 07:00 through 2024-08-01 06:00 UTC (744 hours). The independent *UTC July only* ERA5 file provides **737 exact source hours per EPA Unit ID**, as established by [CI 41926491544](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41926491544). It leaves seven real **2024-08-01 00:00–06:00 UTC** weather hours unavailable. **No August source values have been claimed or fabricated in this development.**

## New reproducible gate

- Implementation: [strict observed-source completion module](../src/grid_resilience/srp_epa_era5_august_boundary_completion.py).
- Regression tests: [August boundary tests](../tests/test_srp_epa_era5_august_boundary_completion.py).
- Input 1: original CI-verified `epa_source_july_lstd_era5_utc_hourly.csv` with 744 EPA rows per unit and exactly 737 temperature matches.
- Input 2: **independently obtained real ERA5** site-hour CSV with columns `plant_id,timestamp_utc,temperature_2m_c` for all three plants and all seven timestamps on August 1 UTC. An actual dataset source URL and its content SHA-256 are mandatory.
- An exact site/hour many-to-one join, 7/7 observed August hours for each unit, 744/744 total hours for each unit, no overlap and no interpolation are enforced. Reject incomplete/duplicated/weather-filled inputs.
- Output: `epa_local_july_744h_observed_era5.csv`, `epa_local_july_744h_observed_summary.csv`, and a scope/provenance manifest, **only after the actual August observations have been admitted**.

Example CLI after independently downloading and verifying genuine August ERA5:

```bash
python -m grid_resilience.srp_epa_era5_august_boundary_completion \
  --july-panel verified_july_panel.csv \
  --august-weather actual_aug1_utc_era5_sites.csv \
  --august-source-url 'SOURCE_DATASET_URL' \
  --august-sha256 'ACTUAL_SHA256_HEX' \
  --output outputs/epa_era5_full_local_july
```

The URL must identify an actual source dataset, not a placeholder; the expected SHA-256 must be calculated independently from that downloaded source. These files are **not** claimed to exist now.

## Remaining scientific limitations

The ability to join full weather source hours is an **exposure-data completeness upgrade** only. The observational EPA gross load and Operating Time fields do **not** establish electrical net generator MW, forced outages, temperature-driven availability losses, dispatch-independent derating, GT generator mappings, or observed EENS. In particular, multiple EPA units at one plant share a single weather series and must not be counted as independent climatic replicates.

## Next acquisition action

Retrieve and archive the true Aug 1 2024 00–06 UTC ERA5 source with original coordinate/site metadata and source checksums; verify the 3 × 7 source-unique plant-hour rows before running this gate. After successful execution, record full workflow run SHA, weather provenance, output artifact and summary counts here. **Do not overwrite the earlier 737-hour certified result**; retain both as separate provenance stages.


## 2026-11-04 executed source completion — CI verified

The independent [source-fetch and completion workflow](../.github/workflows/srp-epa-july744-real-august-era5.yml) has now **SUCCEEDED**: [GitHub Actions run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085) on commit `59b03c67257e1d6ef6e3b08fe8f7241db27adba6`. Its Python regression tests, retrieval of the previous certified July artifacts, actual ERA5 August 2024 site-point requests, source provenance checks, exact 21 plant-weather-hour extraction, and strict 744-hour join assertions all completed successfully.

The [uploaded artifact 13385277887](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085/artifacts/13385277887) is named `srp-epa-local-july744-real-august-era5`. It includes `observed_aug1_utc_7h_by_site.csv`, the request/response provenance manifest, the completed unit-hour panel and the summary/manifest. The CI asserted exactly **10 source EPA units × 744 fully matched hours = 7,440 unit-hours** across the same three sites: **737 prior July-UTC source hours plus 7 genuinely observed August-UTC source hours per unit**. The 21 August source site-hours correspond to **three sites × seven UTC hours**; they are shared across colocated EPA units, not 70 independent weather samples.

This confirms hourly **meteorological exposure coverage**, not an independent audit of equipment availability or dispatch. It does not verify EPA–EIA unit identity, net electric output, causal thermal derating, EENS or outages. The original 737-hour result and the new 744-hour result remain separately archived for provenance.
