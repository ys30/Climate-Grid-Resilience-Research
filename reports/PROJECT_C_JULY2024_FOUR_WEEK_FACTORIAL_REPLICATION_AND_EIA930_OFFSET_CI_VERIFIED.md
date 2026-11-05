# Four distinct source-observed July 2024 weekly matched four-scenario PyPSA analyses — CI verified

**Original-source, newly acquired 28-day weather and official demand CI:** [42103762531](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42103762531) **SUCCESS**; [results artifact 13450498593](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42103762531/artifacts/13450498593). A reproducibility-enhanced rerun [42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361) **SUCCESS** and includes the **exact source-hour demand and weather inputs for all four weeks**. Capacity and model code use the existing 2024 EIA860 partial gas/wind proxy, not a calibrated multi-technology fleet. Both new workflow runs used a fixed 2024 annual partial fleet and a single hypothetical link rating derived from **first-week 10% of the smaller BA's peak demand**, applied unchanged to all weeks.

**Input vintage warning:** original 168-hour EIA930 API label and the official July CSV hour convention were **NOT identical**. The first new week's modeled interaction is +22,515.998 MWh, not the historic +23,306.937 MWh. **This is not a bitwise or exact-input reproduction of the old result**; see the source reconciliation below.

## Study design: four genuine disjoint observed windows

Actual source provenance:
- Official original July 2024 EIA930 H1/H2 joined raw balancing-authority hourly demand, previously source-verified in [41325415594](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41325415594). The documented CSV field `UTC Time at End of Hour` was converted to UTC **start** hour by subtracting one hour.
- A newly acquired Open-Meteo ERA5 2024 July 1–28 UTC record, representative-point temperatures and derived **hypothetical** wind availability, at CISO, AZPS, BPAT and SRP (four *points*, not full BA spatial domains or observed wind generation). Validated exact **672 distinct UTC hourly timestamps × 4 BAs = 2,688 BA-hours** with no fabricated/missing hour.
- Source inventory: 2024 EIA860 **partial** generic gas/thermal + wind capacity proxy, held fixed for all scenarios and weeks. **No observed generator available net MW**, real intertie ratings, storage SOC, all-fuel supply accounting or historical outage evidence.
- Four nonoverlapping 168h windows: **July 1–7**, **July 8–14**, **July 15–21**, **July 22–28** UTC. Each is a separate source-observed weekly window, **not an independent year, season or statistically independent heat-wave event**.
- At each week, all four cases baseline, heat-only, wind-only, heat+wind are solved with **exact same inputs/assumptions** aside from hypothetical shock changes; each week is also solved with isolated BAs and with exactly the same illustrative three-link network. **4 weeks × 2 network assumptions × 4 cases × 4 BAs = 128 BA-scenario output records**, i.e. 32 optimization runs.

Factorial nonadditivity is **I = U(heat+wind) − U(heat-only) − U(wind-only) + U(baseline)** where U is **modeled** unserved energy. I need not be monotone with network rating or positive at every BA; this is not a causal observed real-world interaction.

## Empirical-input, structurally assumed PyPSA simulation results

**System-level week-specific nonadditivity (MWh)**:

| Source UTC week (2024 July) | Isolated BAs | Hypothetical frozen 10%-peak links | Hypothetical links − isolated |
|---|---:|---:|---:|
| Week 1 / July 1–7 | +14,630.333 | **+22,515.998** | +7,885.665 |
| Week 2 / July 8–14 | +15,338.708 | **+16,204.695** | +865.987 |
| Week 3 / July 15–21 | +14,697.753 | **+25,211.030** | +10,513.277 |
| Week 4 / July 22–28 | +8,575.179 | **+15,177.070** | +6,601.890 |

All four week-level **system** interactions are positive under **both** held-fixed structural variants. The hypothetical link case varies by approximately **1.66×** across weeks (25,211/15,177). The assumed-link minus isolated second difference ranges from **+865.987** to **+10,513.277 MWh**. This reflects week-specific input and nonlinear assumed network response, **not observed inter-BA transfer causation**. The adjacent weekly windows are temporally related; do not attach independently replicated p-values or confidence intervals to four weeks.

**Important counterexamples at individual BAs:** despite positive system-wide contrasts, **CISO in week 1 under hypothetical links has approximately −5,763.7 MWh** of modeled interaction; **BPAT week 3 under hypothetical links is approximately −5,918.4 MWh**; **AZPS week 4 under hypothetical links is approximately −3,663.8 MWh**. These negative local contrasts disprove any simplistic claim that assumed heat–wind synergy is uniformly positive over BAs or weeks.

**Structural inadequacy caution:** the model's linked-network **baseline** unserved load is already approximately **292,032, 480,493, 317,924 and 412,467 MWh** in the four weeks, respectively, and isolated baseline gaps are even larger. These very large *baseline* modeled shortages confirm that the partial-fleet hypothetical supply representation is highly incomplete. The result is **only an engineering/stylized screening sensitivity**, not modeled EENS in the probabilistic reliability sense and emphatically not real-world unserved energy or blackouts. SRP has zero or near-zero simulated shortage in many cases despite missing plant/BA electrical mapping, which illustrates heterogeneous structural model artifacts, not verified real SRP resilience.

## Critical old-versus-new input convention finding

The new original-to-refetched first-week comparison is audited in **[CI 42104382649](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104382649)**, [source comparison artifact 13450349373](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104382649/artifacts/13450349373), followed by independent one-hour lag search **[CI 42104639488](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104639488)**, [lag artifact 13451056369](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104639488/artifacts/13451056369).

- **Original and refreshed BA-hour weather records are exactly identical** for all **4 BA × 168 actual hours**, for both ERA5 `temperature_c` and the computed wind resource proxy.
- **Old and new EIA930 demand at the same timestamp differ** in 167–168 of 168 hours per BA, with some substantial instantaneous deviations.
- Shifting the **old API demand time labels one hour earlier** gives **167/167 exact numeric source matches for each of CISO, AZPS, BPAT, SRP (all absolute errors exactly zero)** against the new official EIA930 CSV series. That is strong evidence of **an old/new hour-label convention discrepancy**, *not* different weather, fluctuating EIA source revisions, or changed BA demand magnitudes. The official July CSV calls its timestamp `UTC Time at End of Hour`; the new pipeline subtracts one hour to align hourly input at the start of the interval. The older API input code retained the source `period` directly as a UTC timestamp. Before using the legacy run as a time-matched comparator, the original API time convention must be verified and harmonized.
- At the first and last observation, a one-hour shift necessarily has one unmatched endpoint in each source. **Never fill or wrap these endpoints to manufacture an exact 168/168 overlap**.
- Therefore the older **+23,306.937 MWh** interaction and the newly computed **+22,515.998 MWh** interaction are outputs of **different hourly demand↔weather alignment**. Their difference should not be attributed to the scientific climate mechanism, physical reliability or pure optimizer nondeterminism.

## Methods and manuscript significance

Four independent *calendar-week windows in a single July month* now exist, so the earlier single-week factorial result can be discussed as **within-month input-window structural sensitivity**. However, the inclusion of real EIA930/ERA5 inputs **does not validate the modeled extreme-demand shocks, hypothetical wind derating response, annual generator capacity availability, real BA intertie deliverability, or actual adequacy**. No causal, historically calibrated, climatologically generalizable or probabilistically inferred grid-risk claim is justified.

This supports a private manuscript Results subsection on (i) within-month week-to-week heterogeneity, (ii) network assumptions and spatial redistribution of modeled nonadditivity, and (iii) time-interval provenance. The old V2 plan's factorial-complete-but-multi-event-incomplete label must now be refined: **four July real observed weekly windows completed**, but **independent-season/year robustness and physical calibration remain incomplete**. These four adjacent weeks should not be called four independent extreme-weather events without event separation or clustering evidence.

### Remaining gates

1. **Official EIA930 API-versus-CSV hour convention audit** in the original intake and unit test, and prospective cross-version time reconciliation. Freeze the corrected **start-hour** interpretation across old and new workflows.
2. True extra **months/years and independently screened compound events** (not merely adjacent weeks) with comparable source-hour coverage and a held-fixed cross-period fleet/availability formulation.
3. Include complete technology categories and constrained storage SOC, justify/obtain actual BA electrical topology and intertie ratings, benchmark EIA923 monthly generation and EIA930 technology production against model outputs. The baseline artificial gaps should materially improve before any adequacy conclusion.
4. Integrate complete and private manuscript figures, uncertainty and references; the current study is **not publication ready as a calibrated reliability assessment**.

Scripts: [four-week authentic source admissions](../src/grid_resilience/july2024_four_week_factorial_inputs.py), [four-week PyPSA scenario runner](../src/grid_resilience/july2024_four_week_factorial_replication.py), [first-week source version comparison](../src/grid_resilience/july2024_four_week_source_version_reconciliation.py), [actual EIA930 time-offset diagnosis](../src/grid_resilience/july2024_eia930_demand_hour_lag_diagnostic.py), CI workflows in `.github/workflows/july2024-four-week-factorial-replication.yml`, `july-four-ba-input-version-reconciliation.yml` and `july-eia930-old-new-hour-lag-audit.yml`.
