# V2 partial-fleet screening quality gate

This is a diagnostic disclosure check, **not an adequacy validation**. It checks that the matched four-scenario matrix is complete, and compares omitted generation nameplate to the included thermal/wind projection. It refuses to label the model historically calibrated under any configuration.

## Usage

After EIA-860 adaptation and a completed four-scenario dispatch:

```bash
python -m grid_resilience.screening_gate \
  --dispatch outputs/solved/factorial_dispatch.csv \
  --capacity outputs/eia860_projection/capacity.csv \
  --excluded outputs/eia860_projection/excluded_technologies.csv \
  --demand outputs/prepared/demand.csv \
  --output outputs/screening_gate.json
```

The result includes baseline modeled unserved energy, capacity coverage, an explicit list of blockers, and `pass_for_historical_reliability_claims: false`. The default 5% omitted-nameplate threshold is a *user-configurable diagnostic screen*, not an industry reliability criterion. Nameplate coverage alone cannot establish dependable capacity.

When `--demand` supplies a complete consecutive BA-hour panel, the gate computes `baseline_energy_fraction` as modeled baseline shortfall MWh divided by total modeled demand MWh (one-hour snapshots). If demand is omitted, the value remains null. Never divide modeled shortage MWh by nameplate MW and interpret it as an energy fraction. EIA-923 generation calibration, hourly supply mix, availability factors, transfer rating provenance, historical load comparison, and independent-period holdout testing remain future work.

Run tests with `python -m pytest -q`.
