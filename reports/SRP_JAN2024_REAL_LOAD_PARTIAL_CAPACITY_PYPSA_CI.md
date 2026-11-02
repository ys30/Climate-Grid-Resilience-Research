# First actual-load / partial-capacity January 2024 SRP PyPSA screen

**CI verified:** [run 41407513836](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407513836), source commit `1ed3c89f8f211c27db81ebd7324e6593c0c30abb`, [artifact 13123873738](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41407513836/artifacts/13123873738).

A complete 744-hour SRP January 2024 UTC load profile was reassembled from official EIA-930 2023H2 and 2024H1 Balance CSV sources (7 plus 737 hours, no interpolation). The supply side was limited to 2024 EIA-860 Operable generator nameplate entries exactly matched to generator IDs for which the *partial* EIA-923 Page-4 source reported BA SRP. Explicit exclusion removed missing/ambiguous primary fuel or multifuel flags. **This identity-linked sample is not a complete SRP fleet.**

| Quantity | CI output |
|---|---:|
| Actual observed SRP January demand integrated from hourly EIA-930 | 2,455,626 MWh |
| EIA-860 nameplate capacity in eligible, source-linked subset | 7,453.1 MW |
| Modeled January generation | 2,455,626 MWh |
| Modeled unserved energy | 0 MWh |

The modeled generation matching total demand follows power balance in the model, not empirical goodness of fit with EIA-923 observed dispatch. The 0 MWh shortage holds *only under this artificial assumption set*: all candidate generators available at nameplate every hour; homogeneous invented marginal cost of 50; no interchanges, transmission losses, dispatch ramping, energy limits, maintenance, storage or import representation. This is an **integration and feasibility screen**, not a calibrated historical capacity adequacy finding.

CI artifact includes `input_provenance.json` with original download SHA256, `observed_hourly_demand.csv`, `partial_ba_capacity_screen.csv`, `ba_capacity_identity_review.csv`, `capacity_screen_manifest.json`, `modeled_monthly_generation.csv`, and `screening_manifest.json`.

## Next research tasks

1. Reconcile generator BA membership beyond EIA-923 Page-4 sample; screen exact EIA-860 plant identifiers and geographic coverage, retirement-effective dates and non-thermal technologies.
2. Use a documented sensitivity range for generator availability, realistic marginal cost ordering and fuel restrictions, and monthly hydro/PS treatment from Page-1, without pretending these assumptions are empirical calibration.
3. Compare modeled BA/technology net generation with EIA-923 observed monthly generation after aligning technology labels, source scope and missingness.
4. Extend into multiple months and truly withheld years, with robustness tests.

**Historical calibration certified: NO. Independent holdout validation completed: NO.**
