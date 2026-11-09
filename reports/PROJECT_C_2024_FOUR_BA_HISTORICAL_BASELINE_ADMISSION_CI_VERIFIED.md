# Paper C — July 2024 four-BA historical PyPSA baseline source admission and physical-calibration blockers

## Verified original-source cohort and source provenance

The exact original EIA-930 2024 first/second half-year raw BA hourly records, source-native hourly fuel data and independent CAISO five-minute storage-power provenance are now jointly audited by BA and UTC-hour key: [four-BA source-joined admission CI #42688934228 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42688934228), with four regression checks. [Download source-joined historical baseline eligibility CSV, 32 category-completeness records, source scope and EIA-930 SHA256 (artifact 13705614098)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42688934228/artifacts/13705614098).

The [audit implementation](../src/grid_resilience/paperc_2024_baseline_admission.py) performs:
1. Exact **168 UTC start-hour × 4 BA = 672** joined original EIA-930 raw demand, net generation and interchange record keys, preserving 2024 July's **seven Jan–Jun + 161 Jul–Dec** original source partitions per BA.
2. Exact 2024 original fuel label-and-hour keys from the previous [source-native EIA-930 original fuel audit](PROJECT_C_EIA930_2023_2024_SOURCE_NATIVE_HOURLY_GENERATION_CI_VERIFIED.md), retaining original blanks and **modern-versus-legacy** 2024 category noncomparability.
3. A separate conditional **CISO informational 2,016-point battery power envelope**, already verified against original CAISO source CSV, **without** inserting inferred battery SOC or energy capacity.
4. BA-specific physical-model **fail-shut gates**: source balance completeness, fuel-category comparability, plant-level energy availability, hydro/battery state, physical intertie ratings and historical EENS identification.

## Historical baseline eligibility result (actual original 2024 source rows)

| BA | Original hourly demand source | Original hourly net generation source | Original Total Interchange nonblank | Total Interchange missing | Raw accounting incomplete or nonclosing (of 168h) | Full numeric groups among eight reviewed fuel categories | CAISO five-minute battery information source | Physically calibrated historical PyPSA/EENS admitted |
|---|---:|---:|---:|---:|---:|---:|---|---|
| AZPS | 168 | 168 | 168 | **0** | **0** | **6/8** | No | **No** |
| BPAT | 168 | 168 | 168 | **0** | **168** | **5/8** | No | **No** |
| CISO | 168 | 168 | 24 | **144** | **163** | **6/8** | Yes, 2,016 observed 5min records | **No** |
| SRP | 168 | 168 | 168 | **0** | **0** | **6/8** | No | **No** |

CISO's 163 unavailable/nonclosing arithmetic hours consist of **144 hours with missing original total interchange** and **19 originally complete but nonclosing** hours. BPAT raw net generation, demand and interchange reported for each hour but **fails closing arithmetic for all 168** under the audit's documented source balance rule. AZPS and SRP **pass the stated source accounting arithmetic criterion**, but this does **not** certify generator availability, storage constraints, physically valid intertie transfer limits, adequate technology coverage or observed reliability.

The eight reviewed fuel categories are original Coal, Natural Gas and Nuclear over all 168 hours, and original modern Solar without Integrated Battery Storage, Wind without Integrated Battery Storage, Hydropower Excluding Pumped Storage, Battery Storage and Pumped Storage **over their 161-hour modern source partition only**. Complete numeric group here means the *defined source partition* has no blank values, **not** that a full old/new-schema consistent 168-hour technology output was recovered. In particular, the original **Battery Storage** modern field has zero reported values for all four BA cohorts; it **does not mean zero actual storage output**.

## Why this blocks a historical physical adequacy result

The source accounting test `raw NG - demand - interchange` is a **reported-data arithmetic check**, not evidence of actual network constraints or losses. Its success for AZPS/SRP does not imply physical calibration, and its failure for BPAT/CISO must not automatically be interpreted as actual shortages.

A real four-BA 168h historical network adequacy model additionally needs:

- Source-matched historical technology-complete actual generating populations and relevant hourly operating availability/constraints, rather than a generic gas-like thermal/wind approximation and 2025 preliminary monthly source roster treated as 2024 operating capacity.
- Hydro inflow, water/energy budget, pumped-storage energy and operating constraints, and battery energy capacity/efficiencies/initial SOC. CAISO's historical five-minute battery power is an observed source operating signal **only for CISO**, not an MWh reservoir or SOC measurement.
- Independently documented physically deliverable BA exchange edges and transfer limits, not bilateral EIA-930 interchanges interpreted as available link ratings, and resolution of the existing CISO missing Total Interchange, BPAT nonclosure, and directional reciprocity source issues.
- Distinction between modeled counterfactual shortfall and measured, attributed real-world load curtailment. No actual historical EENS, outage or blackout count was inferred.

## Paper manuscript placement and defensible new claim

**Supplementary Methods — Empirical Source Admission and Rejection:** This source-joined table demonstrates an auditable, reproducible *model-readiness audit* that distinguishes original hourly data coverage from technology report completeness and physical system identification. The next main-text claim can say that CISO five-minute historical storage operation and stable EIA-930 fuel components provide **partial empirical baseline evidence**, while an unverified four-BA physical reliability baseline remains outside the supported data scope.

**Do not state:** "2024 historical extreme-weather conditions caused X MW of physical shortage or EENS", "completing source BA-hour data proves adequacy", "the 2025 EIA-860M nameplate is historical hourly available supply", "CAISO battery telemetry provides actual SOC", or "EIA-930 reported exchange equals a validated AC transmission limit."

The cited workflow is a source-validation gate and **does not run an actual 168h physically calibrated four-BA PyPSA model**. It also does not replace the separately CI-proven three-hour synthetic-only StorageUnit interface test.
