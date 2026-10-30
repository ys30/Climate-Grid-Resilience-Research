# Research V2: Independent paper C — Compound climate extremes and electricity adequacy

**Status:** preregistered-style analysis plan; **not** a calibrated reliability study or confirmed manuscript findings.

## Central question

How do compound climate hazards interact with generation availability and constrained interregional transfers to amplify power-system adequacy risk in selected western U.S. balancing authorities?

### Identifiable hypotheses

- H1. Modeled climate stress raises unserved load relative to a weather-matched baseline, conditional on modeled network assumptions.
- H2. Joint heat and wind-availability shocks exhibit an interaction that can be separated from additive single-hazard effects **only after a complete factorial scenario is implemented**.
- H3. The response to climate shocks changes with intertie and thermal capacity assumptions; use matched scenario-by-capacity configurations to test the interaction.
- H4. Results generalize to independent extreme-event windows and years **only after temporal holdout validation**.

## Reuse / do not conflate with paper B

B's historical demand/fuel/capacity alignment, BA reporting rules and validation methodology can be reused **as the common data foundation**. C's outcomes are unserved-load risk, shortage duration and transfer-vulnerability interactions—not storage investment economics or long-term optimal decarbonization trajectories. Report cross-project shared methods explicitly.

## Data and evidence gates

1. **Baseline period:** 2019–2023 for calibration; 2024 reserved as a temporal validation holdout where possible. Use 2025 only if input-year completeness and source revisions are documented. These years are proposed, not completed.
2. **Geography:** begin with CISO, AZPS, BPAT, SRP, but do not claim representative WECC coverage. Verify load, interchanges, generator fleet, and actual BA topology and transfer constraints before physical grid conclusions.
3. **Weather:** sample historical compound events with a reproducible heat/wind/hydro trigger, multi-BA spatial coherence, and separate non-extreme controls. Compare matching hours/days; avoid selecting on outcome shortage.
4. **Calibration:** minimize historical observed-vs-modeled BA/technology generation and interchange discrepancies with explicitly controlled parameters and identification bounds; retain observation-only, withheld/ambiguous EIA-923 records separately. Document model fit on holdout years.
5. **Factorial shocks:** full baseline, heat-only, wind-only, and heat+wind under the SAME load/network/capacity assumptions. Calculate interaction = compound - heat - wind + baseline. Never interpret current three-scenario model as such a decomposition.
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
