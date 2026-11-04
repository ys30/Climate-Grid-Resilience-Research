# SRP 2024-01: EIA-860 Plant BA versus EIA-923 Page 4 generator reporting coverage

## Verified source run

Initial official EIA audit [41766082852](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41766082852) completed successfully on code commit `6b12d7d9703f4c06ddff6dd3470ff0fdaec52ac7`; [artifact 13292493031](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41766082852/artifacts/13292493031) includes the exact source-audit rows and manifest. Research Methods CI on that commit [41766082831](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41766082831) passed. Follow-up code `08129141ac6ea1d4ea10435ca9a41d781ad93d78` explicitly preserves missing monthly technology MWh as missing instead of a numerical zero; regression test `811645c72580a65e76b4f346ac948607190c580d` checks this fail-closed behavior.

## Matched population: reporting scope, NOT power-system capacity certification

The official EIA-860 2024 *Plant*-reported BA census has **108** operable generator records with **16,863.6 MW** annual nameplate. Single-primary-fuel and compatible prime-mover classification includes **97 generator records** with **15,576.5 MW**. Eleven records / 1,287.1 MW are deliberately excluded from unconstrained conventional supply, including pumped storage and battery classifications.

The official EIA-923 **Page 4, reported BA=SRP, January 2024** contains **40** generator-month records with **2,160,272 MWh signed net generation**. Each of these 40 generator keys exists within the EIA-860 Plant BA SRP census. This is *identity overlap*, not validation that all SRP physically controllable generation belongs to this population. **68** annual Plant BA generators have **no matching Page 4 SRP January record**.

| Primary-source / mover technology | Annual EIA-860 plant-BA generator records | January EIA-923 Page4 matches | EIA-860 annual nameplate (MW) | Matched Page4 reported net (MWh) |
|---|---:|---:|---:|---:|
| Gas | 64 | 38 | 8,550.1 | 1,889,999 |
| Coal | 2 | 2 | 821.8 | 270,273 |
| Nuclear | 3 | 0 | 4,209.6 | **not reported in this Page4 scope** |
| Solar | 18 | 0 | 1,674.9 | **not reported in this Page4 scope** |
| Wind | 2 | 0 | 226.0 | **not reported in this Page4 scope** |
| Conventional hydro | 8 | 0 | 94.1 | **not reported in this Page4 scope** |
| Excluded/unmodeled | 11 | 0 | 1,287.1 | **not reported in this Page4 scope** |

Reported Page4 source values are signed, and conservation holds: **1,889,999 + 270,273 = 2,160,272 MWh**, with **zero** Page4 identities outside the annual SRP Plant BA roster in this filtered source comparison. This Page4 sum and the separate EIA-923 Page1 BA/fuel source sum are *different source reporting scopes*, so nonidentity does not establish measurement error.

**Critical missingness warning:** Page4 noncoverage is not observed zero generation, an outage, or evidence of lack of physical BA deliverability. The corrected technology summary uses a missing value for technology classes without any matching monthly Page4 net generation.

## Implication for PyPSA

- The synthetic multi-technology sensitivity model may use clearly labeled **annual EIA-860 nameplate-based scenario resources** but it cannot cite the 40 Page4 reported generator records as validation of all 97 modeled generators' January output.
- Do not impute the nuclear, solar, wind, or hydro Page4 blanks to zero or classify these resources as January outages.
- An EIA-930 **BA-wide** hourly generation-by-fuel series is neither a direct plant-by-plant generator allocation nor a substitute for ownership, availability, weather sensitivity, or plant dispatch entitlement.
- Separate EIA-860 Plant BA association, EIA-923 Page4 reported-BA coverage, EIA-923 Page1 fuel observations, and EIA-930 BA operational generation in both code manifests and manuscript text.

## Recommended next scientific gate

Before adding climate-linked thermal or renewable availability: use source-independent, geolocated plant/fleet meteorology with verified UTC hours and explicit source provenance; maintain separate *assumed baseline* versus *weather-derived* scenario descriptions. For historical generation validation, acquire genuinely comparable generator/unit or plant dispatch and operating-BA rights rather than extrapolating Page4 BA/month coverage.

**BA dispatch-right certification: NO. Generator-level January completeness: NO. Historical reliability calibration: NO. Climate-driven outage attribution: NO.**
