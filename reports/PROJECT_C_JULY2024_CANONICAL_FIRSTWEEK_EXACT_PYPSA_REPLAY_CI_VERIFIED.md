# July 2024 first-week factorial: exact corrected-hour original-weather replay (CI verified)

**Independent observed-source PyPSA replay:** [GitHub Actions 42111352630](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42111352630) **SUCCESS**, [source-checked model parity artifact 13454107084](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42111352630/artifacts/13454107084). All source-admission tests and optimization steps succeeded, including both isolated and frozen hypothetical three-edge network configurations.

## What was replayed

The replay independently restores the **original archived EIA930/ERA5 first-week ERA5 source weather** from [run 41102363806](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41102363806) and the **corrected official EIA930 first-week hour-start demand, partial EIA860 annual generator capacities, hypothetical links and canonical source-scenario outputs** from the later real four-week source experiment [42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361). It checks exact UTC hour keys from 2024-07-01 00:00 to 2024-07-07 23:00, at AZPS, BPAT, CISO and SRP; **672 BA×hour records per weather/demand dataset (168 true UTC hours × 4 BA)**.

A source-level comparison had already proven that the legacy and canonical first-week ERA5 temperatures and assumed wind-availability proxies are identical, while the originally API-labeled BA demand was **one hour offset** relative to official EIA930 CSV interval-start conversion. [Clock-convention integrity report](PROJECT_C_EIA930_CANONICAL_HOUR_START_AND_JANUARY_BOUNDARY_CI_VERIFIED.md) and [canonical source CI 42107809174](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42107809174) document **668 genuine common-source demand hours precisely matching after the one-hour conversion**, without inventing either endpoint.

The independent replay uses **the original exact weather source**, the **corrected official demand**, the **identical frozen partial fleet** and **identical network assumptions**, so this is a test of code reproducibility and input-domain integrity, *not a new source dataset* or a causal model validation.

## Verified model agreement

| Measure | Observed result |
|---|---:|
| Original vs canonical first-week weather/BA-hour exact source pairs | **672/672** |
| Corrected official BA demand rows admitted for the seven-day window | **672/672** |
| PyPSA first-week case solves rerun | **8** (4 factorial cases × 2 networks) |
| Scenario-by-BA model output records compared | **32/32** |
| Maximum absolute difference in modeled unserved energy | **0.000000 MWh** |
| Allowed replay discrepancy threshold | 0.01 MWh |
| All source/optimization/consistency checks | **PASS** |

The corrected first-week linked hypothetical-network model's heat×wind second difference is approximately **+22,515.998 MWh**; the original legacy source-time-misaligned analysis had **+23,306.937 MWh**. The present source-matched rerun establishes that the corrected first-week output is computationally reproducible and **the legacy result must not be misrepresented as a direct identical-source reproduction**.

## How this changes Paper C status

- **Corrected first-week scenario reference:** [four genuine July weeks](PROJECT_C_JULY2024_FOUR_WEEK_FACTORIAL_REPLICATION_AND_EIA930_OFFSET_CI_VERIFIED.md) produced corrected-input hypothetical linked-network interaction estimates of ~**+22,516, +16,205, +25,211, +15,177 MWh** for weeks 1–4. The **exact replay** validates week 1 against its original weather source and correct source-clock demand, *not* cross-season or cross-year effect stability.
- **Provenance / testing:** a single shared EIA930 hour-ending-to-start conversion is implemented and tested in the API and official CSV ingestion paths; January SRP official H1 CSV remains source-audited **737 hours, not 744**, with seven unavailable first-UTC-month hours excluded rather than imputed.
- **Structural restrictions unchanged:** the capacity file is an **incomplete annual EIA860 gas/wind proxy**; meteorology is at representative BA points; demand and wind shocks are hypothetical; three BA links use synthetic ratings. The very large baseline **modeled** unserved energy is **not observed blackouts, true EENS, physical derating or independent causal attribution**.
- **Remaining tasks:** assess other historical charts that consumed hour-end-labeled demand, add independent months/years and actual heat-event selection, assess EIA923 net generation and complete generating capacity/storage, reconcile BA transfer limits, and privately integrate all paper figures/methods/results/discussion.

## Reproducibility assets

- [Exact original-weather canonical-demand replay](../src/grid_resilience/july2024_firstweek_canonical_replay.py)
- [Source-coverage and no-imputation tests](../tests/test_july2024_firstweek_canonical_replay.py)
- [Original-source archived workflow](../.github/workflows/july2024-canonical-firstweek-factorial-replay.yml)
- [Source CI and downloadable result artifact](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42111352630)

This report is about **reproducibility of an explicitly stylized screening model**, not about empirical adequacy calibration.
