# EPA ECMPS production monitoring-plan source access: observed HTTP 403 (2026-11-04)

## Executed source checks

The [documented production ECMPS monitor-plan configurations endpoint](https://api.epa.gov/easey/monitor-plan-mgmt/swagger) was queried by a source-provenanced GitHub Actions workflow with the documented `orisCodes` filter for plants **141, 55129 and 147**. The filter name and pipe-separated format were checked against the public US-EPA-CAMD `easey-monitor-plan-api` source controller and DTO.

- [New source-probe CI 41963785485](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41963785485): workflow **SUCCESS**, actual production response **HTTP 403**, `data_admitted=false`, `http_access_blocked=true`. Unit tests passed.
- [Independent production export-probe CI 41963781341](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41963781341): workflow **SUCCESS**, source access for **all three** target plants returned **HTTP 403**. These are access/authorization outcomes, not evidence of missing monitoring plans.
- Code: [public monitoring-plan probe](../src/grid_resilience/srp_ecmps_public_monitor_plan_probe.py); [7 response-validation tests](../tests/test_srp_ecmps_public_monitor_plan_probe.py); [Actions workflow](../.github/workflows/srp-ecmps-2024-public-monitor-plan-probe.yml).

The **successful CI status refers only to reproducible execution and honest recording of the blocked access condition**, not successful acquisition of regulatory plan documents. No actual 2024 effective-date monitor-plan or unit–stack relationship has been admitted, and no EPA–EIA physical generator mapping has been established.

## Alternative verified official access channel

EPA's [ECMPS production public Global View](https://easey.epa.gov/ecmps) and [ECMPS User Guide](https://www.epa.gov/power-sector/ecmps-user-guide) state that official monitoring-plan records are publicly viewable without logging in. This does **not** guarantee that programmatic requests from GitHub Actions to the production API can succeed without credentials or against network access controls. The retired FACT API and Monitoring Plan Viewer must not be mistaken for live replacements (see [EPA legacy-tool notice](https://www.epa.gov/power-sector/monitoring-plan-part-75-sources)).

## Next accepted evidence

1. Acquire each target facility's **official submitted monitor-plan JSON** via the EPA public Global View or an explicitly permitted, documented data export. Preserve source URL, extraction date, effective reporting periods, plan/configuration IDs, full original content, and its checksum.
2. Independently validate reported unit and stack/pipe configurations against EPA original source EPA Unit IDs (especially 141/7, 141/8, 55129/DBG4, 55129/DBG5).
3. Obtain separate EIA generator/engineering association evidence; emissions monitoring relationships alone do not identify net electric generator power paths.
4. Only then evaluate whether any generator-specific 2024 weather–operation calibration is admissible. Maintain net-MW, physical heat-derating and observed outage/EENS claims as unverified in the meantime.

**Evidence status:** 10 source units, 6 historical static links, 4 without static links; 0 admitted dated ECMPS plans; 0 confirmed physical EIA GT mappings. Zero means *no verified evidence admitted*, not zero existing equipment or no operations.
