# SRP hourly shortage context: analysis protocol

Status: **code committed; new CI results not yet independently verified**.

## Research question

For the selected 168-hour July 2024 modeled window, how does the spatially
isolated SRP shortfall under assumed coal, nuclear and gas deratings coincide
with the input demand profile and an *illustrative*, non-observed solar
availability schedule?

## Reproducible outputs

The workflow `.github/workflows/azps-srp-multitech-envelope.yml` writes:

- `fine_gas_derating_threshold.csv`: gas-availability grid and corresponding
  modeled shortfall MWh, shortfall hours, and peak shortfall MW.
- `fine_gas_shortfall_hours.csv`: affected UTC timestamp records only.
- `fine_gas_hourly_demand_solar_context.csv`: **all** 168 UTC hours for each
  of 16 cases, including zero-shortfall hours.
- `fine_gas_hourly_vulnerability_summary.csv`: per-case demand and solar
  contrasts, case-level top-quartile load threshold and associated shortage MWh.

## Interpretation

The case-specific 75th percentile of demand is computed using *all* 168
hours and defines high-demand hours. The percentage of shortage hours that
are high-demand is compared to the percentage of all hours that are
high-demand. Solar-zero intervals use the explicitly assumed solar profile
and must not be described as measured generation, an empirical solar drought,
or a causal driver of shortages. Separate shortage-hour averages from
non-shortage-hour controls. Cases with no shortfalls produce null conditional
means/fractions, not zeros.

The dispatch excludes transmission and storage and should not be treated as
a BA-wide calibrated historical reliability reconstruction. The generation
capacity mapping is based on EIA-860 source-candidate rows, while fuel
availability and the hydro 48-full-load-hour budget are model assumptions.
EIA-923 and EIA-930 reconciliation and external-year validation remain open.

## Quality checks

- Exactly 16 refined combinations, each with 168 hourly records.
- Unique (case, timestamp) pairs.
- Each case's shortage and non-shortage hours partition 168 hours.
- Sum of hourly shortages equals each summary's total shortage MWh.
- Shortage MWh in a subset never exceeds total shortage MWh.
- Weakly monotone shortage MWh as assumed gas availability increases.

## Next validation gate

Inspect the new GitHub Actions run, capture its run ID, conclusion,
full artifact provenance and numeric results, then use those *verified*
outputs for plots and manuscript findings. Do not infer new empirical
results from a successful code commit alone.
