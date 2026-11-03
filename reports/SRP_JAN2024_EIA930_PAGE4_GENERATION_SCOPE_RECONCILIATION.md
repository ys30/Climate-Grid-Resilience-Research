# SRP January 2024: EIA-930 versus EIA-923 Page 4 generation-scope reconciliation

**Status: source-scope accounting only; not historical dispatch or reliability calibration.**

## Provenance
2024-01, 744 UTC hours. Source artifact: [successful full workflow 41718037295](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037295), commit `055b8a18b47ae98e39352453bbeb806999fe51f7`, [artifact 13269759289](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037295/artifacts/13269759289). Values from `eia930_balance_metrics.json`, `page4_month_scope_manifest.json`, `srp_generator_monthly_identity_audit.json`, `fuel_descriptive_noncali_comparison.csv`, and `explicit_exchange/explicit_import_export_manifest.json`.

| Scope | January MWh | Important caveat |
|---|---:|---|
| EIA-930 SRP BA reported generation | 5,098,927 | BA-level EIA-930 hourly source |
| EIA-923 Page 4 matched generator net generation | 2,160,272 | Limited matched Page 4 identities, 40 rows |
| EIA-930 minus selected Page 4 | 2,938,655 | **Coverage/reporting-scope difference, not unexplained physical power** |
| Page 4 NG matched net generation | 1,889,999 | 35 included identities |
| Page 4 SUB matched net generation | 270,273 | 2 included identities |
| Page 4 excluded matched identities | 0 | 3 excluded NG identities; zero reported *monthly net generation* does not establish physical unavailability |
| PyPSA partial-fleet hypothetical model generation | 4,625,935.045 | 37 eligible generators, assumed hourly availability and dispatch, fixed boundary |
| PyPSA minus matched Page 4 | 2,465,663.045 | **Not** a calibrated error metric |

Selected EIA-923 matched Page 4 monthly net generation is **42.367%** of EIA-930's BA generation, leaving a **57.633%** numerical difference between two non-equivalent source populations. Neither percentage is whole-BA generator capacity coverage or a validated dispatch reconciliation.

## BA-wide EIA-930 accounting check

EIA-930 demand: **2,455,626 MWh**. EIA-930 reported net interchange: **+2,643,306 MWh**, using the extracted convention that BA generation minus net interchange minus demand should be zero. 5,098,927 − 2,643,306 − 2,455,626 = **−5 MWh**; the maximum absolute hourly residual is **1 MW**, over five hours. The signed net interchange should not be confused with gross directional transfers, contractual supply, or transmission limits.

## Partial-fleet PyPSA model check

The explicit-boundary optimization has 0 scheduled imports, **2,643,306 MWh** scheduled exports, **4,625,935.045 MWh** modeled generation, **472,996.955 MWh** modeled unmet load-equivalent requirement across **601** hours. The internal optimization balance closes within floating point tolerance. The external observed export sink is imposed, not optimized by real interties. The modeled gap is **not** measured outages, EENS/LOLE, or proof of real SRP reserve shortfalls.

## Methodological finding

Current Page 4 source extract is a *selected monthly generator subset*, not a full BA-wide generation ledger; a comparison to EIA-930 cannot yet isolate omissions from source coverage, plant/BA scope, generator-level reporting, net versus gross concepts, hydro/PS Page 1, behind-the-meter generation, generator dispatch rights, or geographic boundary differences. Nor can a hypothetical NG/SUB-only PyPSA dispatch total be used as an empirical generation forecast without hourly technology availability and observed full-fleet source matching.

**Next verification gates:** (1) obtain documented EIA source definitions and exact Page 1/Page 4 reporting coverage; (2) expand 2024 monthly generation coverage by technology/plant while preventing duplicate accounting; (3) assign crosswalk confidence and explicit unmatched MWh rather than filling missing as zero; (4) re-run hourly supply screens with measured resource limits and observed physical boundary constraints; (5) compare independent months/years before making climate-change or grid-reliability claims.

**Reproducibility:** all source file names, official-run commit and artifact link are retained above. This report is a deterministic reconciliation of stored manifests, **not** a new official EIA download or new simulation.
