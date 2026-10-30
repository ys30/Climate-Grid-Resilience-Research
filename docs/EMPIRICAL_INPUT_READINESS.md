# Empirical input readiness and remaining calibration blockers

Run `python -m grid_resilience.empirical_input_readiness --provenance inputs/empirical_sources.csv --output outputs/readiness`.

Required source manifest rows: `demand_hourly`, `capacity_technology`, `availability_hourly`, `observed_generation_monthly`, `ba_transfer_capacity`. Each must declare `source_url,source_year,measurement_basis,status` with status from `official_observed, independently_audited, assumed, synthetic, missing`.

The check rejects missing fields and marks any assumed/synthetic/missing core model inputs as empirically unready. It **does not** authenticate source labels or certify actual full-fleet BA/technology coverage.

**Current project limitations:** the real 2024 EIA generator-month input has been downloaded and mapped into a conservative partial-fleet candidate set, but verified historical hourly BA demand, generator availability and actual transfer capacity parameters have not been demonstrated for this end-to-end model. The 696-hour February dispatch is synthetic. The CI success confirms reproducibility and mechanics, not historical calibration. EIA-923 BA report associations and EIA-860 predominant fuel assignments still require observational and fleet-basis scrutiny.

Do not interpret the success of this quality gate as a research validation result.
