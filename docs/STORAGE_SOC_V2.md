# Optional SOC-constrained storage in V2 multi-technology dispatch

The isolated multi-technology solver now accepts `--storage storage.csv`, with one row per BA and fields `ba,power_mw,energy_mwh,efficiency_store,efficiency_dispatch,initial_soc_fraction`. The matched four-scenario orchestrator also accepts the same `--storage` argument. Every scenario receives **identical** storage capacity, energy, charge/discharge efficiencies and initial SOC; only climate-forcing inputs differ.

PyPSA `StorageUnit` enforces within-event intertemporal state of charge. The initial SOC is explicit, energy/power duration is `energy_mwh/power_mw`, and `cyclic_state_of_charge=False`. Storage SOC trajectories are exported to `storage_soc_mwh.csv` for each solve. An energy-limited unit cannot deliver its nameplate power indefinitely.

```bash
python -m grid_resilience.multi_technology_factorial \
  --demand INPUT_DEMAND.csv --weather INPUT_WEATHER.csv \
  --capacity INPUT_CAPACITY.csv --availability INPUT_AVAILABILITY.csv \
  --storage INPUT_STORAGE.csv --output outputs/multi_factorial_soc
```

**Scientific limitations:** storage capacities/efficiencies/initial SOC remain upstream assumptions, no observed charging records or independently verified battery siting are claimed; no forced outages, unit commitment, hydropower reservoirs, or end-of-event SOC reserve constraint are modeled. A positive result from synthetic CI demonstrates solver functionality only, not historical calibration.
