# EPA production ECMPS historical monitor plan access probe — source blocked (2026-11-04)

## Independently executed result

[GitHub Actions run 41963781341](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41963781341) **SUCCESS** at commit `11f4d83a366e65d3473df38a794338ba361ccafc`. This success means the **access probe** completed with status reporting and tests passed, **not that any historical plans were downloaded**. [Archived probe artifact 13386456952](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41963781341/artifacts/13386456952).

The **production** EPA URL was `https://api.epa.gov/easey/monitor-plan-mgmt/plans/export`, with `orisCode` as the query argument. The CI environment did not provide an `EPA_CAM_API_KEY`. The source responses were:

| Requested EIA ORIS code | HTTP response | Classification | Historical plan admitted |
|---|---:|---|---:|
| 141 | **403** | Authorization/access blocker | **0** |
| 55129 | **403** | Authorization/access blocker | **0** |
| 147 | **403** | Authorization/access blocker | **0** |

EPA's production [Monitor Plan OpenAPI](https://api.epa.gov/easey/monitor-plan-mgmt/swagger) documents the `/plans/export` operation. Public application access and API authentication are different mechanisms; the [public ECMPS web interface](https://easey.epa.gov/ecmps) says monitoring plan information can be viewed without login. The API specification declares an `x-api-key` header. This test cannot distinguish missing key from a permission block before request-parameter validation. **Neither 403 nor empty query output constitutes evidence that a plant or unit lacks a monitoring plan.**

## Implemented reproducible evidence

- [Source access probe](../src/grid_resilience/srp_ecmps_production_access_probe.py): only the three specified plant ORIS codes, production-only HTTPS requests, optional key via secret/environment, bounded payloads, HTTP classification and no credential printing.
- [Regression tests](../tests/test_srp_ecmps_production_access_probe.py): ensure successful JSON transport is **not** equivalent to historical-plan evidence admission; reject fabricated plant identifiers and never misreport 403/400 as no units.
- [CI source workflow](../.github/workflows/srp-ecmps-production-monitor-plan-access.yml): exposes `EPA_CAM_API_KEY` only through an optional GitHub Actions secret, without printing it; status manifest uploaded even on access block.

## Scientific gate

The prior verified **10 source EPA units**, **6 static EPA–EIA associations**, **4 missing static associations**, **0 verified EIA GT-generator physical power mappings** remain unchanged. No original plan files, time-valid unit/stack relationship rows, generator-level net MW, outage labels or physical derating coefficients were acquired in this run. The 744h meteorological panel remains verified separately.

## Next acquisition decision

Use EPA's public ECMPS monitoring-plan page to obtain/inspect original plant configuration records or provide an authorized API key **through normal secure GitHub secret management**, not in source code, chat, or logs. Independently retain original plan IDs, raw byte hashes, dated location relationships and source URLs; validate against [ECMPS historical relationship admission gate](../src/grid_resilience/srp_ecmps_2024_plan_evidence_gate.py). A monitoring-unit-to-stack link is not a verified EIA electrical generator-to-unit map; confirm physical power identity separately using source-dated EIA or plant engineering documentation.

**Do not publish a claim that these four units have been matched or that the project has physically calibrated heat derating.**
