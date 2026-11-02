# CI-verified SRP refined gas-availability sensitivity (model-only)

## Reproduction record

- Workflow: `.github/workflows/azps-srp-multitech-envelope.yml`
- Successful run: [41386883075](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075)
- Commit: `568f52f17b6d0aa287353793d1be01feecc5cd7f`
- Artifact: [AZPS-SRP-2024-OFFICIAL-MULTITECH-ENVELOPE](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075/artifacts/13115548069)
- Artifact SHA-256: `784e93871ded9cd109e428c5bae05c3041c8200dd3c490b5394bb4a4fe10746a`
- Validated: 16 cases, 2,688 hourly rows, 384 UTC-hour-of-day rows, 32 PNG figures, four cases with nonzero shortfall.
- Upstream input artifact runs: `41285853425` (screening); `41341668303` (EIA-860 schema).
- Source of numbers below: numerical validation step in the successful Actions job log.
 
## Refined gas sensitivity

All MWh are deterministic **modeled unserved energy over the 168-hour window**, not historical observed outages. Gas, coal, nuclear availability are *assumed constant multipliers* in the indicated scenarios. Values printed as `-0.000` in solver output are shown as `0.000` here (floating-point numerical tolerance).

| Scenario | Coal availability | Nuclear availability | Gas availability | SRP modeled shortfall (MWh) |
|---|---:|---:|---:|---:|
| baseline | 100% | 100% | 30% | 450.880 |
| baseline | 100% | 100% | 35% | 0.000 |
| baseline | 100% | 100% | 40% | 0.000 |
| baseline | 100% | 100% | 45% | 0.000 |
| baseline | 50% | 75% | 55% | 0.000 |
| baseline | 50% | 75% | 60% | 0.000 |
| baseline | 50% | 75% | 65% | 0.000 |
| baseline | 50% | 75% | 70% | 0.000 |
| heat_wind | 100% | 100% | 30% | 4342.666 |
| heat_wind | 100% | 100% | 35% | 635.731 |
| heat_wind | 100% | 100% | 40% | 0.000 |
| heat_wind | 100% | 100% | 45% | 0.000 |
| heat_wind | 50% | 75% | 55% | 352.485 |
| heat_wind | 50% | 75% | 60% | 0.000 |
| heat_wind | 50% | 75% | 65% | 0.000 |
| heat_wind | 50% | 75% | 70% | 0.000 |

The first **tested gas-availability points** with positive modeled shortfall are 30% in the baseline and heat/wind cases with full assumed coal/nuclear availability, and 55% in heat/wind with coal/nuclear at 50%/75%. These are grid points, **not continuously optimized critical thresholds**.

For the full coal/nuclear case at gas 30%, the heat/wind case yields 4,342.666 MWh versus 450.880 MWh at baseline, a difference of 3,891.786 MWh **conditional on this model**. This is a matched modeled scenario difference, not a real-world outage estimate or a causal climate attribution.

## Validation and interpretation boundaries

Successful workflow steps included the synthetic figure tests, optimization, post-solve consistency checks and artifact upload. The scenario set excludes verified transmission, storage dispatch, historical plant-hourly availability, EIA-923/930 historical reconciliation, and independent-year calibration. The solar availability profile and hydro 48-full-load-hour budget are illustrative assumptions. Do **not** call these observed reliability estimates or use these numbers as empirical out-of-sample model skill.

## Next study steps

1. Review rendered figures and the per-case hourly CSVs for counterintuitive artifacts.
2. Compare shortage hours with input demand and assumed solar profiles; report the **actual**, not inferred, observed-input contrasts.
3. Add historically reconciled generation/availability and network transfer evidence before extending claims to calibrated multi-BA reliability.
4. Integrate these numbers into a clearly marked *model sensitivity* subsection of Results; postpone historical/causal claims.
