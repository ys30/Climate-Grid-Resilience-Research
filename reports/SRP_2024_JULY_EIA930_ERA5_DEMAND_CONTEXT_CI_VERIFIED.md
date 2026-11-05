# SRP EIA-930 July 2024 demand context linked to EPA–ERA5 heat exposure — CI verified

## Evidence and source scope

[Executed GitHub Actions run 41965387798](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41965387798) completed **SUCCESS** after fixing the legacy EIA-930 manifest's literal escaped-newline trailer in source admission. [Uploaded artifact 13387905060](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41965387798/artifacts/13387905060) includes exact joined site-hour source rows, nine site/temperature-bin summaries and scope manifest.

Upstream inputs:
- Verified full 744-hour EPA–ERA5 *local July* weather panel: [run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085), 10 EPA units at 3 sites.
- Original official EIA-930 July 2024 H1/H2 balance source merge: [run 41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594), 744 unique UTC hourly SRP BA rows.
- [Exact UTC source-hour algorithm](../src/grid_resilience/srp_epa_era5_eia930_demand_context.py) and [regression tests](../tests/test_srp_epa_era5_eia930_demand_context.py).

**Time conventions:** EIA-930 'UTC Time at End of Hour' is converted to *start-of-hour* by subtracting exactly one hour. Original EPA July local-standard time is UTC−07 and therefore includes August 1 UTC 00:00–06:00. The EIA source is UTC **July only**, giving 737 verified overlapping source hours/site and leaving exactly 7 August UTC EIA demand hours/site unmatched. No values are imputed or inferred; weather shared by multiple units is counted once per site.

## Observed same-hour SRP BA demand by local weather exposure

These are **the same SRP balancing-authority demand series** grouped three different ways using co-located ERA5 plant temperatures. They are not three separate plant demand measurements or independent BA-demand replicates.

| Plant ERA5 site | Temperature bin | Unique UTC-July hours | Mean SRP BA demand MW | Median SRP BA demand MW | Range MW |
|---|---|---:|---:|---:|---:|
| 141 | below 35°C | 262 | 4,739.80 | 4,700.5 | 4,074–6,246 |
| 141 | 35–below 40°C | 237 | 6,040.93 | 6,033.0 | 4,807–7,508 |
| 141 | at least 40°C | 238 | **7,416.59** | 7,450.0 | 6,118–8,267 |
| 55129 | below 35°C | 312 | 4,871.16 | 4,787.5 | 4,074–7,247 |
| 55129 | 35–below 40°C | 239 | 6,369.33 | 6,368.0 | 5,045–7,685 |
| 55129 | at least 40°C | 186 | **7,508.63** | 7,553.0 | 6,500–8,267 |
| 147 | below 35°C | 279 | 4,785.28 | 4,715.0 | 4,074–6,246 |
| 147 | 35–below 40°C | 225 | 6,115.44 | 6,091.0 | 4,807–7,508 |
| 147 | at least 40°C | 233 | **7,414.64** | 7,461.0 | 6,352–8,267 |

**Descriptive contrast:** For the Plant 141 weather stratification, mean SRP demand is 2,676.79 MW greater in source hours with at least 40°C than below 35°C (7,416.59 − 4,739.80 MW). For Plant 55129 the contrast is 2,637.48 MW; for Plant 147 it is 2,629.36 MW. These are **differences in observed conditional means**, not causal heat coefficients and not forecasts.

## Validation and limitations

1. Each plant has exactly **737 EIA-matched** and **7 unmatched** source site-hours; the full EPA weather source itself retains 744 distinct site-hours per plant.
2. No 2024-Aug-01 EIA-930 demand values were included in the July-only official source, and none were filled.
3. SRP EIA-930 demand represents total balancing-authority operations. Plant BA affiliation from EIA-860 does not independently certify an EPA-monitored unit's ownership, contractual dispatch or generator-level load assignment.
4. EIA-930 demand can explain why EPA unit operations are demand-selected, but this **descriptive join does not control for hourly dispatch decisions, equipment availability, hour-of-day, temporal autocorrelation, outage status, or generator-specific net MW**.
5. This is not physical thermal derating, causal meteorological inference, empirical unserved load, LOLE, EENS or a historically calibrated PyPSA reliability estimate.

## Run provenance / diagnosis

The initial [CI 41965287463](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41965287463) failed when parsing an already archived source-manifest file that had a **literal \\n trailer**. [Commit 2253b353](https://github.com/ys30/Climate-Grid-Resilience-Research/commit/2253b35344a294465a8cd96792b788aa7c2dfbf3) added a restricted JSON decoder that rejects any non-whitespace or nonliteral newline trailer other than the known source defect, while leaving all original EIA source values unchanged. The following run succeeded and uploaded the real source-joined output.

## Next empirical controls

Obtain UTC-August EIA demand for full local-July overlap; then construct hour-of-day and calendar-day demand comparisons, with appropriate temporal clustering and separate per-site analyses. Before any physical heat-derating calibration, independently verify EPA/EIA electrical generator identities and access credible equipment/dispatch/availability data.
