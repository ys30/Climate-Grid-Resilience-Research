# ECMPS 2024 monitoring-plan evidence gate — validation stage

## Verified previous findings
- The complete 2024 local-July EPA source-hour × ERA5 source-hour panel is independently verified at **10 EPA units × 744 hours**, [source workflow 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085).
- Ten EPA units at three SRP-context facilities appear in the 2024 CAMPD source, but **four lack a static EPA–EIA association:** 141/7, 141/8, 55129/DBG4, 55129/DBG5. The static crosswalk does **not** directly certify any of the ten target EIA860 GT generators. See [earlier evidence](SRP_EPA_2024_HOURLY_OPERATION_AND_CROSSWALK_CI_VERIFIED.md).
- EPA's ECMPS 2.0 public monitoring plans expose unit/stack/pipe configurations and time-specific relationships. Documentation: https://www.epa.gov/power-sector/cam-api-portal and production OpenAPI https://api.epa.gov/easey/monitor-plan-mgmt/swagger. The public website is https://easey.epa.gov/ecmps. **Do not use EPA dev/perf environments as production research evidence.**

## New admission check

The implementation [srp_ecmps_2024_plan_evidence_gate.py](../src/grid_resilience/srp_ecmps_2024_plan_evidence_gate.py) accepts a carefully normalized extract of original EPA monitoring-plan *unit-to-stack/pipe* relationships. Required columns: `facility_id, epa_unit_id, stack_pipe_id, begin_date, end_date, source_plan_id, source_url, source_sha256`.

It checks:
1. The ten already-seen EPA source Unit IDs only; aliases resembling EIA generator IDs are not accepted.
2. Positive provenance: HTTPS original plan source URI, SHA-256 format, plan identity and no duplicate relationships.
3. Explicit overlap with the target **2024-07-01 through July 31 local-standard month** using monitoring-plan effective start/end dates.
4. A source-unit-by-source-unit coverage table retaining missing historical plan relationship evidence as missing rather than treating it as outage or assuming a generator.
5. A separate manifest declaring that unit–stack relationship does not establish EIA generator correspondence, electrical net output or thermal derating.

The associated [synthetic regression tests](../tests/test_srp_ecmps_2024_plan_evidence_gate.py) exercise date validity, source-provenance rejection, name collision and duplicate rejection. [Research CI 41962771283](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41962771283) verified that the full test suite passed.

## Empirical status / blocker

**Monitoring-plan records have not yet been retrieved and source-admitted through this gate.** This milestone adds defensible analysis and tests only; it is not a successful source download or a resolved four-unit identity match. Importantly, even once genuine 2024 monitoring plans are obtained, they certify monitoring unit–stack configurations, **not automatically the generator-to-unit electrical relationship**. To admit GT generator-specific net MW or availability, additional source-linked, historically applicable EIA / plant engineering documentation is necessary.

## Next executable step

Export production ECMPS monitoring plans for plants 141, 55129 and 147, preserving original plan IDs, file bytes, content digests and active date intervals. Normalize the documented unit/stack relationships and execute:

```bash
python -m grid_resilience.srp_ecmps_2024_plan_evidence_gate \
  --normalized-plan verified_2024_ecmps_unit_stack_relationships.csv \
  --output outputs/ecmps_2024_evidence
```

Do not replace the missing source file with a fabricated fixture or promote historical crosswalk labels to validated generator identities.
