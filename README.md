# Climate–Grid Resilience Research | Manuscript Development

**Research V2 — independent climate and power-system adequacy paper.** This repository is separate from the [portfolio V1 demonstration](https://github.com/ys30/Climate-Grid-Resilience-PyPSA). Results in the portfolio remain versioned and are not presented as historically calibrated grid reliability forecasts.

## Main research question

How do compound climate stresses interact with generation availability and constrained interregional transfers to affect electricity adequacy across selected Western U.S. balancing authorities?

See the [preanalysis roadmap](reports/RESEARCH_V2_INDEPENDENT_PAPER_PLAN.md).

## First reproducible module: factorial nonadditivity

Four *matched* scenario results must exist for every event, BA and network variant: `baseline`, `heat_only`, `wind_only`, `heat_wind`. Then calculate

`interaction = U(heat_wind) - U(heat_only) - U(wind_only) + U(baseline)`.

This identifies a modeled nonadditive contrast conditional on the specified assumptions; it is **not by itself causal identification**. The previous portfolio's third scenario additionally derated interties, so its three scenarios **cannot** be used to estimate this interaction.

### Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m grid_resilience.factorial_interactions --input examples/factorial_synthetic.csv --output outputs/factorial_interactions.csv
```

The example fixture is **synthetic unit-test input**, not observed or simulated study evidence. New multi-year EIA/ERA5/PyPSA results will require separate execution, QA and historical validation before any paper claims.

## Historical input validation gate (implemented)

The [historical input harmonizer](src/grid_resilience/historical_inputs.py) takes **upstream-provided** demand and weather BA-hour CSVs, plus a capacity projection with source year and provenance, checks hourly completeness and ranges, and writes strictly validated `demand.csv`, `weather.csv`, `capacity.csv`, and `input_provenance.json`. It **does not download EIA/ERA5**, validate original agency reports, estimate transmission capacities, or silently fill missing hours. Use it before the [PyPSA matched factorial dispatch](src/grid_resilience/factorial_dispatch.py). Do not call this historical calibration until EIA-860/923/930 comparisons and independent-year checks are performed.

## Scope / boundaries

- Historical EIA-860/923/930 and ERA5 inputs must be reconciled before calibration.
- Transfer ratings and BA service geometries are not established by historical interchange flows.
- Deterministic unserved energy is not probabilistic EENS/LOLE; modeled shortfalls are not observed outages.
- Paper B's storage investment economics is deliberately outside this paper's main contribution.

[Source Portfolio C](https://github.com/ys30/Climate-Grid-Resilience-PyPSA) · [Technical summary of completed demonstration](https://github.com/ys30/Climate-Grid-Resilience-PyPSA/blob/main/reports/FINAL_TECHNICAL_SUMMARY.md)
