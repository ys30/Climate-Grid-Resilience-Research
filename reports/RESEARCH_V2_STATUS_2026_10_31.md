# Research C v2 — engineering and manuscript gate status (2026-10-31)

Project-management estimates (not mechanically computed): **engineering ~75%** toward a defensible research pipeline; **manuscript ~35%** toward submission. Neither is a claim of empirical historical reliability calibration.

## Verified engineering evidence

- [Research CI 41265718914](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41265718914): success on the full-month HY/PS model output adapter.
- [Official EIA-923 2024 intake 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401): success; 2,940 observed HY plant-month records and 120 PS plant-month records; 72/96 target BA/technology/month source slots have reported observations. AZPS HY/PS slots are **missing source rows, not zero generation**.
- [Official EIA-923 2024 intake 41261608309](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41261608309): 245 reported HY plant/BA source rows, all WAT, no duplicate plant/BA pair in the filtered source.
- [Research CI 41263169972](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263169972): monthly modeled-vs-observed diagnostics unit tests pass; real historical PyPSA month-to-month comparisons are **not yet produced**.
- The [full-calendar-month PyPSA workflow](../.github/workflows/full-month-pypsa-integration.yml) remains a **synthetic** February integration test. Its dispatch generation and analytical-reference match are not historical fit.
- [Wind temporal validation notes](../docs/results/bpat_era5_feb_march_july_2024.md) report separately checked BPAT ERA5-vs-EIA-930 wind-proxy timing correlation; observed net generation is not meteorological potential.

## Work remaining before a publishable claim

1. Historical EIA-860/923 BA and generator-fleet completeness, source equivalence and PS pumping convention checks.
2. Actual full-calendar-month PyPSA solution with historical demand, appropriate plant/BA capacity, dispatch treatment, and unambiguous modeled **net** generation definition, rather than the current synthetic integration.
3. Report both source coverage and signed Bias/MAE/RMSE for matched BA/technology/month series, with temporal holdout where feasible.
4. Verify transmission assumptions and EIA-930 interchange accounting separately from line capacities; analyze sensitivity to the unverified limits rather than presenting them as actual transmission ratings.
5. Execute and archive matched baseline, heat-only, wind-only, heat+wind factorial results, per independent event window, with the interaction computed as compound − heat − wind + baseline.
6. Uncertainty/negative controls, event selection reproducibility, figures, Results/Discussion and final full manuscript drafting.

## Manuscript status

- Research question, hypotheses, candidate BA scope, methods outline, initial source audits and selected screening results exist.
- No defensible paper-level calibrated historical reliability performance metrics or full independent factorial event inference currently documented.
- A portfolio-ready screening project exists separately; the research V2 is **not submission-ready**.
- Newly added `hydro_calibration_readiness.py` reports which provenance checks remain absent and always keeps historical **adequacy** certification separate from generation-fit eligibility.

This status note must be updated only after a traceable CI run or specific reproducible result, not based on code commits alone.
