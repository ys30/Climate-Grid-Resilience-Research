# EIA-versus-model comparison key coverage

Use `python -m grid_resilience.eia_model_key_coverage --observed <BA_technology_month.csv> --modeled <BA_technology_month.csv> --output <directory>` before calculating comparative generation errors.

The output `comparison_key_coverage.csv` uses an **outer join** and labels matched, modeled-only and observed-only BA/technology/month combinations. Missing observed groups are left null; they are never changed to zero. `comparison_complete` means only that the two supplied key sets match and does not establish actual plant-fleet completeness or historical calibration.

**2024 real-data finding:** seven of eight BA/technology groups in the single-fuel candidate coverage matrix had twelve recorded months. CISO/coal had **zero observed groups after candidate filtering**. This must not be interpreted as an observed zero MWh of coal generation. The apparent absence could reflect excluded generators, plant status, reporting behavior, or data-mapping definitions and requires separate review.

The module is a quality gate and does not itself run a full-month PyPSA solve.
