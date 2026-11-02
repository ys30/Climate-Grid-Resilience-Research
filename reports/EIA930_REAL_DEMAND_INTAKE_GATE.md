# EIA-930 actual-hourly-data intake gate (November 2026)

## Implemented

- `src/grid_resilience/eia930_monthly_demand.py` fetches EIA API v2 RTO region demand (`type=D`) for one BA and checks exact UTC-hour timestamp coverage, duplicates, nonnegative values, and complete month.
- `tests/test_eia930_monthly_demand.py` includes a 744-hour January fixture and fail-closed tests for missing/duplicate hours or wrong BA.
- `.github/workflows/eia930-real-hourly-demand.yml` attempts to retrieve **actual SRP January 2024** demand (not hypothetical).

## Verified blocker

[EIA-930 specific GitHub Actions run 41402148202](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41402148202) failed at **Retrieve official full January 2024 EIA-930 demand** with `urllib.error.HTTPError: HTTP Error 403: Forbidden`. This is not a PyPSA numerical failure; it occurred during public API download. No verified hourly demand CSV was created from this run. Passing local UTC-month tests should **not** be described as successful real-data ingestion.

EIA documentation describes API authentication, access, and official CSV downloads; see [EIA API technical documentation](https://www.eia.gov/opendata/documentation.php) and [EIA-930 source data instructions](https://www.eia.gov/electricity/930-content/about.html). An alternative is to ingest official EIA-930 semiannual balance CSVs (or preserved source archive from [PUDL EIA-930 raw data](https://docs.catalyst.coop/pudl/en/v2026.4.0/data_sources/eia930.html)), with original archive URL/version/checksum and strict UTC coverage checks. **No alternative archive has yet been parsed or CI-verified in this repository.**

## Remaining full-month empirical gate

1. Confirm a reproducible authorized EIA-930 source and verify 744 UTC hourly observations for January 2024 SRP.
2. Independently establish EIA-860 BA-specific, technology-specific 2024 capacities and effective availability; do not imply EIA-923 observation ledger supplies capacity.
3. Run real-input January PyPSA screening with stated simplifications and preserve both demand and supply provenance.
4. Independently validate EIA-923 monthly technology observations and availability of 2019–2024 years before calibration/holdout metrics.

**Empirical PyPSA calibration certified: NO.**


## Alternative archive access test (run 41402367603)

A specific versioned source was identified: [Catalyst Cooperative / PUDL raw EIA-930 Zenodo record 18366739](https://zenodo.org/records/18366739) with `eia930-2024half1.zip`, advertised MD5 `b8cc4d16ee54724d94ca3df4f8f1bb3a` (the source version is pinned because newer archived snapshots can have different content/checksums). EIA's [EIA-930 source documentation](https://www.eia.gov/electricity/930-content/about.html) confirms official six-month balance CSV availability.

An [actual GitHub Actions archive acquisition run 41402367603](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41402367603) **failed** at the public Zenodo download with `urllib.error.HTTPError: HTTP Error 403: Forbidden`. This is an independent 403 block affecting the second source domain in the CI runner environment, not a checksum mismatch. The archive never downloaded, so its internal schema and observed 744 SRP hours remain **unverified**; do not claim real data ingestion or monthly empirical simulation.

Recommended next path: acquire the official EIA-930 six-month balance CSV from the EIA Grid Monitor interface and pass it into a reviewed importer (or use a source-supported GitHub release / artifact mirror with provenance and checksum); diagnose CI outbound HTTP filtering and access policies. Avoid bypassing access controls. Until actual file bytes and hourly completeness are verified, leave the model's real-data gate closed.

**Current state:** 744-hour *hypothetical* PyPSA screen has a passing CI; real EIA-930 → PyPSA solve not executed.
