# SRP GT 2024: EPA production facility API access and monitoring-plan admission gate

## Source verification

EPA's [Clean Air Markets API Portal](https://www.epa.gov/power-sector/cam-api-portal) documents production facility management and emissions interfaces, distinct from public archived CSV crosswalk snapshots. EPA's [Power Sector Data](https://www.epa.gov/power-sector/power-sector-data) distinguishes CAMPD program/apportioned unit hourly emissions data from raw ECMPS reported monitoring plans. This project's independent [live facility admission CI 41875589498](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41875589498) **SUCCESS** with [artifact 13344944977](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41875589498/artifacts/13344944977) recording the exact query endpoint, source HTTP status, response size and SHA256 per site. Associated source admissions and unit-output flags are deliberately conservative.

| Requested ORIS code | Queried endpoint | HTTP response | Facility source identity admitted | 2024 monitored unit mapping admitted |
|---|---|---|---|---|
| 141 | EPA production /facilities-mgmt/facilities/141 | **403** | **No** | **No** |
| 55129 | EPA production /facilities-mgmt/facilities/55129 | **403** | **No** | **No** |
| 147 | EPA production /facilities-mgmt/facilities/147 | **403** | **No** | **No** |

A 403 is an **API access and/or authorization denial** for the request configuration; it is NOT evidence that a facility is absent from EPA's database, that a turbine lacks monitoring data, or that a generating unit was not operating. Furthermore the `/facilities/{id}` path's resource key may represent an internal facility ID rather than the EIA ORIS code. A returned HTTP 200 alone would therefore not prove identity: the parser requires an explicit matching ORIS identifier in the source payload before source admission.

**No actual 2024 hourly EPA electricity, emissions, heat input, gross load or monitoring-plan dataset has been downloaded or validated by this workflow**. The positive CI result confirms the gate correctly fails closed, not that the underlying API provided data.

## Distinct static crosswalk evidence

The pinned [USEPA/camd-eia-crosswalk](https://github.com/USEPA/camd-eia-crosswalk) source contains **3, 4 and 2** EIA plant-level crosswalk rows respectively for Plant 141, 55129 and 147. However zero of the **10 EIA860 2024 annual GT generator identities** has a direct CAMD combustion-unit mapping. Those 9 preexisting plant source records must be inspected at their original EIA-generator, CAMD-unit and match-method grain separately; they are not evidence of GT unit equivalence.

Original independent source-backed crosswalk run: [41874622794](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41874622794). The newer workflow also writes `target_plant_epa_all_source_relationships.csv` to make all 9 plant-level original crosswalk rows auditable without fabricating missing generator mappings.

## Reproducibility constraints and next best sources

1. Obtain authorized EPA CAM facility/ECMPS production API access or use EPA's publicly accessible [CAMPD bulk-data downloads](https://campd.epa.gov/data/bulk-data-files) and [ECMPS monitoring plan interface](https://easey.epa.gov/ecmps), explicitly retaining the original resource identifier, API/bulk vintage, reporting dates and facility-unit IDs. The 403 check must not be 'fixed' by assuming an unsupported endpoint or inventing an API key.
2. Inspect all available CAMD combustion unit versus EIA electricity generator relationships, including boiler-generator mapping, common stacks and gas/steam combined-cycle topology, before making plant-to-unit assignments. Many-to-many relationships require physical/documentation validation.
3. For any 2024 EPA hourly raw or apportioned data, verify the **metric** and units: emissions, heat input, operating time or gross load are not independently measured **net electrical MW** for an EIA generator. Never use them as monthly EIA923 net MWh or as heat-related derating calibration without a validated allocation/basis.
4. Retain existing independently validated ERA5 site-hour exposure and EIA860/Page1/Page4 source data; they do not on their own establish thermal MW loss, generator outage, climate causality or electric energy not served.

**Research gate: EPA live facility retrieval — ACCESS DENIED (HTTP 403); 2024 EPA monitoring-unit mapping — NOT VERIFIED; 2024 hourly electrical unit net MW — NOT VERIFIED.**
