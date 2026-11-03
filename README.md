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

## Verified January 2024 SRP real-input screening workflow (2026-11-03)

The [full SRP January 2024 GitHub Actions run 41718037295](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037295) completed **successfully** at commit `055b8a18b47ae98e39352453bbeb806999fe51f7`. Its 29 workflow steps include the 744-hour EIA-930 demand/boundary screen, EIA-860/923 generator-identity checks, PyPSA solves, source-scope sensitivity diagnostics, a firm-capacity frontier, and synthetic signed-import/export regression. GitHub uploaded the [run artifact](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037295/artifacts/13269759289) (`srp-jan2024-real-load-partial-supply-screen`). The [research methods CI](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037303) and [exchange boundary regression](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41718037235) also passed at the same commit.

**Interpretation:** workflow completion verifies execution and artifact upload, not independent verification of every artifact value, full-fleet capacity assignment, transmission deliverability, out-of-year calibration, or observed outages. All January shortfalls and firm-capacity frontiers remain *conditional partial-fleet model screens*, not historical reliability estimates. Do not transfer numerical results into the paper without separately auditing artifact rows and their provenance.

## EIA-923 2024 observed-source audit (not historical calibration)

The [verified HY/PS audit](reports/EIA923_2024_HYDRO_PS_OBSERVATION_AUDIT.md) records 245 conventional hydro Page 1 plant/BA source rows and 120 pumped-storage measured plant-month net-generation rows. **HY monthly reported-source MWh are now extracted** for BPAT, CISO and SRP (12 months each) in [official intake run 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401); AZPS HY/PS source slots remain missing, not zero. Full-fleet mapping, hourly availability and historical reliability calibration remain unverified. These observations must not be interpreted as modeled outage validation.

## SRP hourly adequacy diagnostics (model-based, validation pending)

The [SRP multi-technology workflow](.github/workflows/azps-srp-multitech-envelope.yml)
generates 16 refined gas/coal/nuclear availability cases for an illustrative
168-hour window. Per-case modeled shortfall is compared with demand and an
**assumed** solar availability profile; this does not represent observed power
outages or a historically calibrated reliability model.

On a successful run it should emit:

- `fine_gas_derating_threshold.csv` and `fine_gas_shortfall_hours.csv`;
- `fine_gas_hourly_demand_solar_context.csv` and
  `fine_gas_hourly_vulnerability_summary.csv`;
- `srp_hourly_figure_data.csv` (16 × 168 expected rows) and
  `srp_diurnal_figure_data.csv` (16 × 24 expected rows);
- `figures/` containing 16 hourly and 16 UTC-hour-of-day PNG diagnostics;
- `manifest.json` retaining explicit non-calibration flags.

The [lightweight SRP figure quality workflow](.github/workflows/srp-figure-quality.yml)
checks data integrity and synthetic figure rendering independently of expensive
PyPSA solves. The full workflow also runs these tests before optimization and
checks output counts, energies, and figure files afterward.

**Verification gate:** code commits and workflow configuration are **not**
evidence of a successful run. Record the exact GitHub Actions run URL and
commit SHA, verify the run conclusion and artifact contents, and only then
transfer numerical findings or images into the manuscript. EIA-923/930
reconciliation, transmission assumptions, and out-of-year validation remain
outstanding. See
[SRP hourly context methods](reports/SRP_SHORTFALL_HOURLY_CONTEXT_METHODS.md).
