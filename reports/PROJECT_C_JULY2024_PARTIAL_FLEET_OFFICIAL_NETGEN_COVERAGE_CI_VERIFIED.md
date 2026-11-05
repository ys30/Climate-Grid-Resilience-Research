# Project C — July 2024 four-week partial-fleet versus official EIA930 BA net generation: source-audited coverage

**Source-backed CI:** [GitHub Actions 42112872434](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42112872434) **SUCCESS**; [CSV and manifest artifact 13455238702](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42112872434/artifacts/13455238702). Reuses the original 2024 July official EIA930 raw balance artifact [run 41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594) and corrected-hour four-week PyPSA demand, 2024 partial-fleet EIA860 proxy and deterministic solver results [run 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361). The strict source gate checks **672 distinct UTC start hours × 4 BAs = 2,688 BA-hour model demand records**, exact official `UTC Time at End of Hour − 1h` demand equality, 2024 EIA860 capacity-source identity, all 16 BA-week isolated baseline runs, and no incomplete source hours.

## Main observation: partial source supply proxy cannot represent the full reported BA net generation footprint

| BA | Partial gas nameplate MW | Partial wind nameplate MW | Sum partial MW | Official BA net-gen above sum partial MW / 672 source hours | Four-week official BA reported net generation MWh | Isolated baseline PyPSA modeled unserved MWh |
|---|---:|---:|---:|---:|---:|---:|
| AZPS | 4,818.8 | 628.5 | **5,447.3** | **0** | 2,314,568 | **656,558.753** |
| BPAT | 3,177.9 | 3,617.1 | **6,795.0** | **672** | 7,027,805 | **795,413.712** |
| CISO | 32,934.6 | 6,334.7 | **39,269.3** | **54** | 19,471,802 | **655,272.502** |
| SRP | 9,263.9 | 226.0 | **9,489.9** | **133** | 5,681,573 | **0** |

This is **a reporting-scope incompatibility / structural incompleteness indicator**, not a verified nameplate-versus-actual-capacity violation. The official EIA930 BA net generation comprises a **different generating-unit scope** than the limited EIA860 gas/wind proxy, and BA net interchange can be substantial. In particular BPAT's strong hourly reported net generation reflects a broader system and likely other resources than this original gas/wind proxy. Do **not** convert the reported excess into missing *installed MW*, physical guaranteed MW, ownership-specific output, actual blackout observations, or firm renewable capacity.

## Lower bounds on the current *isolated partial-model* baseline deficits

The current isolated source optimization uses capacity fixed every hour: gas generation at most its partial nameplate, wind production at most its partial nameplate and the assumed ERA5 wind-availability proxy. At any UTC hour and BA, the deterministic mathematical bound

`u_partial,BA,h >= max(0, demand_official,BA,h - (gas_partial_nameplate,BA + wind_partial_nameplate,BA))`

holds for **modeled no-link partial supply** only (no storage, all other generation, imports, fuel/ramp/commitment constraints). This lower bound is **NOT a bound on real-world loss of load**. It is an indicator that the source gas/wind supply universe cannot meet all source demand hours *even if each included generator were at its own full nameplate*. If the same model admits omitted fuel technologies, imports, storage, and real flow constraints, both its baseline shortage and its factorial interaction could change substantially.

| BA | Source demand MWh over 672h | Model isolated partial-nameplate minimum deficit MWh | Actual simulated isolated baseline deficit MWh | Excess simulated deficit above simple partial-nameplate floor MWh |
|---|---:|---:|---:|---:|
| AZPS | 4,056,921 | **533,059.3** | **656,558.753** | 123,499.453 |
| BPAT | 4,593,934 | **289,924.0** | **795,413.712** | 505,489.712 |
| CISO | 21,704,731 | **172,413.3** | **655,272.502** | 482,859.202 |
| SRP | 4,070,663 | **0** | **0** | 0 |

At BPAT, the official reported BA net generation exceeds the current partial gas+wind nameplate **every hour**, while the same *isolated model* reports approximately 795 GWh of hypothetical baseline shortage. This strongly indicates a **severe source/reporting-scope mismatch**, not a climate-driven or measured historical supply failure. The source-reported official generation does not automatically determine when or where it could be dispatched to specific loads, and the official generation-versus-BA demand difference includes BA interchanges and reporting differences. These are therefore **diagnostic contradictions for treating the partial proxy as a historical BA adequacy model**, rather than a complete balanced energy-accounting reconciliation.

## Scientific impact

1. **Model adequacy interpretation requires downgrade**: positive assumed heat×wind second differences across four July weeks are still legitimate *within-model factorial interactions* but cannot represent observed system-wide resilience loss, historical EENS/LOLE, nor verified physical capacity derating.
2. The high *baseline* source modeled unserved energy must not be attributed solely to temperature/wind. It already arises before either hypothetical shock and is sensitive to excluded resource categories, missing imports/storage, wind-proxy assumptions and network constraints. The nameplate lower-bound check reinforces this structural point.
3. **BA production and capacity represent different grains**. The site/BA/fuel EIA860 and EIA923 physical-unit crosswalk, dispatchable versus nondispatchable resource representation, BA boundary assignment, and official EIA930 interchange reconciliation are prerequisites to expanding the model responsibly.
4. Updating charts: mark any baseline, heat-only, wind-only and compound shortage panels explicitly **`PARTIAL FLEET; HYPOTHETICAL NETWORK; MODEL SHORTAGE NOT MEASURED EENS`**. Do not replace published original results without traceable corrected-hour reruns.
5. **Paper C new findings:** a source-admission counterexample helps motivate methodological distinction between *weather-exposure scenario sensitivity* and *validated grid reliability*. It is not a calibrated climate impact conclusion.

## Next engineering step

Rank BA/technology coverage gaps using the existing [unmapped EIA860 generator fuel-code audit](../docs/results/eia860_2024_unmapped_fuel_code_breakdown.md), [EIA923 cross-sheet observation work](EIA923_PAGE1_PAGE4_PLANT_COVERAGE_2024.md), [storage SOC evidence gate](../src/grid_resilience/eia860_storage_field_evidence_gate.py) and true EIA930 BA generation/interchange sources. Prioritize BPAT hydro and technology categories, but do not directly map BA-level net generation to EIA860 named installed capacity without proper crosswalk; some categories contain negative net generation, pump charging and storage and require specialized dispatch models.

**Reproducible implementation:** [source-verified BA net-generation coverage code](../src/grid_resilience/july2024_partial_fleet_official_generation_audit.py), [strict source tests](../tests/test_july2024_partial_fleet_official_generation_audit.py), [GitHub Actions workflow](../.github/workflows/july2024-partial-fleet-official-netgen-audit.yml).

**Historical reliability calibration certified: NO. Generator net capacity matched: NO. Physical transfer ratings verified: NO.**
