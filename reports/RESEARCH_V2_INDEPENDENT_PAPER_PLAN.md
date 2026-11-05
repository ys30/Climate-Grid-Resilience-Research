# Research V2: Independent paper C — Compound climate extremes and electricity adequacy

## Verified progress correction — 5 November 2026

The initial Gate 1 milestone in this plan was written before later CI-verified research. **The full baseline/heat-only/wind-only/heat+wind four-case PyPSA experiment HAS BEEN COMPLETED for one 168-hour July 2024 observed-input window across CISO, AZPS, BPAT, SRP**, including explicit nonadditivity (**+23,306.936668 MWh**, hypothetical 10%-peak linked network), isolated/no-link comparison and 5/10/20% assumed rating sensitivity. These are uncalibrated screening outcomes, not true physical loss or measured outage energy. See [completed factorial analysis](../docs/results/july2024_factorial_interaction_by_ba.md), [paired network analysis](../docs/results/july2024_paired_network_factorial_interaction.md), and [network-rating sensitivity](../docs/results/july2024_network_rating_factorial_sensitivity.md). A separate SRP-only January 744-hour assumed six-technology four-case experiment was completed and produced **zero shortage in all four scenarios**; it is NOT a matched independent replica of July's four-BA partial-fleet analysis.

**Updated four-week real July coverage:** The original archived input [source-count CI 42103046067](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42103046067) contained just **one** 168h four-BA event (672 BA-hour rows). We subsequently acquired the **full real July 1–28 four-BA weather and official EIA930 source sequence** and successfully completed **four actual disjoint 168h windows × four matched scenarios × isolated/frozen illustrative links**, [4-week solver CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361) **SUCCESS**. Under hypothetical 10%-peak links, modeled second differences were **+22,516, +16,205, +25,211, +15,177 MWh** for the four weeks. BA-specific interactions can be negative. Full source-qualified report: [4-week factorial and EIA930 hour label reconciliation](PROJECT_C_JULY2024_FOUR_WEEK_FACTORIAL_REPLICATION_AND_EIA930_OFFSET_CI_VERIFIED.md). **Thus the Gate 1 factorial plus within-July four-window replication is COMPLETE, but distinct-season/year independent event validation is STILL MISSING.** The four consecutive weeks are not four statistically independent heatwaves.

**Critical source time audit:** [original versus refreshed input CI 42104382649](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104382649), [lag CI 42104639488](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104639488) showed all four BA first-week ERA5 and wind proxies **exactly matched** old and new inputs. EIA930 demand required shifting **old API timestamp labels back one hour** to match **167 of 167** overlapping hours in every BA with the official CSV `UTC Time at End of Hour` shifted to UTC hour-start. **The legacy +23,306.937 MWh first-week interaction and corrected-source +22,515.998 MWh are not exact-input replications.** This is a source alignment quality finding, not a physical-weather phenomenon.

**Observed source diagnostics:** separately verified Arizona source-unit EPA/ERA5/EIA930 June↔July common-support and month-transfer assessments, including the finding that observed ERA5 temperature did not consistently improve held-out month forecast skill. These cannot be used to calibrate available generator MW or convert the modeled gaps into actual EENS. See [month transfer](SRP_2024_EPA_JUNE_JULY_OBSERVED_COVARIATE_TRANSFER_CI_VERIFIED.md) and [longer-block robustness](SRP_2024_JUNE_JULY_COMMON_CELL_MULTIDAY_DIFFERENCE_CI_VERIFIED.md).

**Revised execution order:** (i) resolve/standardize EIA930 API and CSV hour-ending conventions; (ii) additional *independent months and years* with weather hazard selection, not just adjacent July weeks; (iii) feasible all-technology/storage assumptions and genuine transmission ratings; (iv) independent generator dispatch/availability calibration; (v) integrated private manuscript, uncertainty, figures. The current same-July four-week experiment is within-month structural scenario sensitivity and is not cross-year generalization.


**Status:** preregistered-style analysis plan; **not** a calibrated reliability study or confirmed manuscript findings.

## Central question

How do compound climate hazards interact with generation availability and constrained interregional transfers to amplify power-system adequacy risk in selected western U.S. balancing authorities?

### Identifiable hypotheses

- H1. Modeled climate stress raises unserved load relative to a weather-matched baseline, conditional on modeled network assumptions.
- H2. Joint heat and wind-availability shocks exhibit an interaction that can be separated from additive single-hazard effects **using the completed four-scenario contrast, while preserving its uncalibrated status**.
- H3. The response to climate shocks changes with intertie and thermal capacity assumptions; use matched scenario-by-capacity configurations to test the interaction.
- H4. Results generalize to independent extreme-event windows and years **only after temporal holdout validation**.

## Reuse / do not conflate with paper B

B's historical demand/fuel/capacity alignment, BA reporting rules and validation methodology can be reused **as the common data foundation**. C's outcomes are unserved-load risk, shortage duration and transfer-vulnerability interactions—not storage investment economics or long-term optimal decarbonization trajectories. Report cross-project shared methods explicitly.

## Data and evidence gates

1. **Baseline period:** 2019–2023 for calibration; 2024 reserved as a temporal validation holdout where possible. Use 2025 only if input-year completeness and source revisions are documented. These years are proposed, not completed.
2. **Geography:** begin with CISO, AZPS, BPAT, SRP, but do not claim representative WECC coverage. Verify load, interchanges, generator fleet, and actual BA topology and transfer constraints before physical grid conclusions.
3. **Weather:** sample historical compound events with a reproducible heat/wind/hydro trigger, multi-BA spatial coherence, and separate non-extreme controls. Compare matching hours/days; avoid selecting on outcome shortage.
4. **Calibration:** minimize historical observed-vs-modeled BA/technology generation and interchange discrepancies with explicitly controlled parameters and identification bounds; retain observation-only, withheld/ambiguous EIA-923 records separately. Document model fit on holdout years.
5. **Factorial shocks:** full baseline, heat-only, wind-only, and heat+wind under the SAME load/network/capacity assumptions. Calculate interaction = compound - heat - wind + baseline. The earlier three-scenario-only limitation has now been resolved for the July screening cases, not for physical climate causality.
6. **Transmission interaction:** repeat factorial shocks over plausible documented actual transfer limits (if verified) and separately hypothetical stress-test intervals; identify scenario×constraint differences, distinguishing observed flows from transfer ratings.
7. **Outcomes:** modeled unserved energy (MWh), shortage hours, peak MW, normalized unserved-load share, and event-level distributions. Do **not** call deterministic shortfall probabilistic EENS/LOLE without a probabilistic sampling design.
8. **Uncertainty:** sensitivity across availability, thermal capacity, intertie assumptions and weather inputs; cluster inference or resampling at independent event or year levels, not treating adjacent hours as independent.
9. **Validation:** do not claim reliable forecasts without out-of-sample observed dispatch/BA flows and defensible nameplate/availability inputs; actual historical blackouts alone need not match an inadequately specified screening model.
10. **Publication:** expose all scenario scripts, source dates, BA crosswalks, calibration losses, held-out metrics, and alternative definitions. Separate historical EIA-930 measurements from PyPSA model outcomes.

## Existing evidence (descriptive, not calibrated)

Four 168-hour sampled weeks in 2024 have been solved for three stylized scenarios. AZPS summer simulated unserved energy: baseline **22,168.29 MWh**, heat +4°C **45,640.99 MWh**, compound heat/wind derating **90,343.96 MWh**. These show screening-model sensitivity but **cannot** alone establish a calibrated climate mechanism or the additive interaction, because a wind-only scenario is missing.

Intertie and thermal-capacity sensitivity sweeps strongly change shortage. Report results as structural model uncertainty rather than calibrated transmission risk. EIA-930 bilateral interchange data have separately been cross-checked by partner and season, but historical flows do not identify line capacities.

## Next execution milestones

**Gate 1:** Generate a reproducible **factorial four-scenario** model for multiple independent event windows; add the missing wind-only scenario without changing baseline parameters.

**Gate 2:** Match and validate EIA-860/923/930 historical inputs under explicit BA/fuel coverage and holdout rules; log observed/model discrepancies, with and without calibration.

**Gate 3:** Link observed weather extremes to constrained supply under verified regional-transfer assumptions; separately run transparent hypothetical link sensitivity.

**Gate 4:** Quantify event-level heterogeneity, interactions, structural sensitivity, and negative controls; publish uncertainty-aware tables and figures.

**Gate 5:** Draft paper after the preceding gates and select journal based on scientific novelty and validated geographic scope.

### Publication readiness decision

Current portfolio V1 is complete as a reproducible **screening demonstration**. **Research V2 has been scoped and initiated but is not submission-ready.** No evidence of true 2024 BA polygon boundaries or calibrated line ratings has been produced.
