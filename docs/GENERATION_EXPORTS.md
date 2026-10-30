# PyPSA generation exports and observation-comparison boundary

The four matched scenario solves now additionally write:

- `factorial_generation_hourly.csv`: modeled hourly MWh for each event, network variant, scenario, BA and generation technology.
- `baseline_generation_event_partial_fleet.csv`: baseline-only generation summed across the **exact solved event window**, labeled with a start/end event identifier.

Technologies are explicitly named `generic_thermal_proxy` and `wind`. The thermal proxy is not observed natural gas production; omitted solar, hydro, nuclear, storage, etc. are not represented as zero. The load-shedding slack generator is excluded from generation exports, because slack is unserved demand, not real electricity supply.

**Crucial period restriction:** the existing 2024-07-01–07 experiment covers seven days, not the full July 2024 calendar month. Its event-window aggregates **must not** be compared directly with EIA-923 July monthly generation. An EIA-923 comparison requires a full matching month or a separately justified daily/hourly observed generation source, as well as an independently audited plant-to-BA crosswalk, net/gross convention and technology map. The `generation_calibration` command enforces exact labels, but cannot assess whether the data source really covers the claimed period.

The existing factorial shortage output and interaction calculation remain unchanged. These exports are diagnostic, not calibrated energy-system evidence. Run the PyPSA workflow and tests before relying on newly generated artifacts.
