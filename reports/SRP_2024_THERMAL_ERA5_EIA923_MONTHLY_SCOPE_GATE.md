# SRP 2024 thermal ERA5 exposure versus EIA-923 Page 4 reporting: calibration admissibility audit

**Verified official EIA-923 2024 source plus immutable EIA-860/ERA5 source data:** [GitHub Actions run 41780946677](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41780946677) **SUCCESS** on commit `0847a00422263642f3bd404c553ebc8f68695db3`. [Artifact 13298498542](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41780946677/artifacts/13298498542) includes official Page4 archive checksum, generator source extraction manifest, all 26 source-plant-month slots, reporting coverage table, and noncalibration caution flags.

## Method

Join the 2024 EIA-860 *annual Plant BA=SRP* gas/coal plant-cohort and 2024-07 ERA5 site temperature observations to independent 2024 EIA-923 Page4 *reported BA=SRP* **generator-month signed net generation**, aggregated by reporting plant. Page4 has distinct reporting grain and BA attribution from Plant BA. Keep every eligible plant for each month (January and July), even when Page4 does not provide a matching month record. **Do not impute missing Page4 generation as zero or infer an unavailable generator from non-reporting**.

Only July site-temperature exposure is joined as a *site characteristic* to January and July source-month rows. It is NOT a paired January source-temperature covariate and not a valid month-level temperature-to-generation regression.

## Actual source matching

| Period | Eligible annual gas sites | Page4 reported gas sites | Unmatched gas sites | Eligible gas nameplate MW | Matched gas nameplate MW | Matched gas nameplate share | Signed Page4 gas net MWh |
|---|---:|---:|---:|---:|---:|---:|---:|
| January 2024 | **12** | **10** | **2** | **8,550.1** | **7,724.3** | **90.3416%** | **1,889,999** |
| July 2024 | **12** | **10** | **2** | **8,550.1** | **7,724.3** | **90.3416%** | **3,588,016** |

The single eligible annual source coal plant (821.8 MW) is reported in Page4 for both months (100% of this *coal cohort*), with **270,273 MWh** in January and **321,634 MWh** in July.

The two eligible gas plants not matching the filtered Page4 source are **Plant 56948 (726.0 MW)** and **Plant 58413 (99.8 MW)**, totaling **825.8 MW** of source annual nameplate. Their Page4 generator-month data are **unreported in this source view**, not observed zero generation, plant shutdown, or evidence of no dispatch rights.

An example of why source signed values must be preserved: Plant 141 has **0 MWh** reported in January, a real zero *reported at the Page4 source grain*, while Plant 56948 has **no matching Page4 record** for January; they are not analytically interchangeable.

## What these observations can — and cannot — identify

- The annual EIA-860 nameplate and observed Page4 monthly signed net MWh define a descriptive `signed_month_net_mwh / (annual_nameplate_MW × 744 h)` *reporting utilization ratio* for matched plant/month records. **It is not a measured availability factor**, capacity loss, forced outage rate, or turbine ambient-temperature performance curve.
- The **July ERA5 gas source plant exposures** and **January/July Page4 monthly net output** have neither the temporal resolution nor the controlled operational covariates needed to identify hot-hour thermal derating. Month-to-month signed output changes must not be called a causal heat effect, since dispatch, scheduled maintenance, demand, fuel, starts and stops, or market conditions can vary.
- EIA-923 Page4 generator-month, EIA-923 Page1 fuel/prime-mover, EIA-930 BA-hour generation, and EIA-860 annual Plant BA are **not automatically exchangeable populations**. BA reporting affiliation is not verified physical dispatch entitlement.
- Explicit outstanding prerequisites for calibration: comparable **unit-level actual hourly or subhourly net power output**, unit/equipment type and ambient performance specification, fuel availability and dispatch/commitment context, cooling/plant heat restrictions, forced outage or derating records, and independently verified ERA5/station/site intake conditions. Where only monthly observations exist, use separate descriptive reporting analysis, not a claimed hourly regression.

## Decision and next research direction

**Data admission gate:** official monthly evidence is valid for a plant reporting **coverage and source-identity audit**; it is **not sufficient for estimating temperature-to-MW derating functions**. Next perform an independent operating-data availability assessment (EIA-860 generator equipment metadata, EIA-923 Page1/4 source consistency, plant-owner public reporting, ISO unit dispatch datasets where accessible) and, separately, expand geolocated ERA5 hot-season events across independent years.

**Confirmed:** source Page4 monthly reporting overlap (10 of 12 gas plants, 1 of 1 coal; 90.34% of eligible gas nameplate). **Not confirmed:** physical heat-driven generation derating, actual reliability/EENS, climate-change causality.
