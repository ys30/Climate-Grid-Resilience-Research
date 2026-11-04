# July 2024 SRP EPA CAMD source observations aligned to ERA5: Part 75 clock convention

## Source interpretation and verifiable method

The U.S. EPA [Part 75 Emissions Monitoring Policy Manual](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P100WXUK.TXT) (Question 13.4) states that emissions hours are reported in **local standard time**, even when the civil clock uses daylight saving time. The [December 2024 ECMPS Emissions Reporting Instructions](https://ecmps.camdsupport.com/documents/ECMPS%20Emissions%20Reporting%20Instructions%202024%20Q4.pdf) define Hourly Operating Data `Date`, `Hour`, and `OperatingTime` as the fraction of the hour when fuel is burned. The archived Arizona EPA reported timestamps must therefore not be treated as UTC or daylight-shifted Mountain Time. The [U.S. Naval Observatory](https://aa.usno.navy.mil/faq/us_tzones) confirms Mountain **Standard** Time = UTC−07:00.

**For Plant 141, 55129 and 147 (Arizona), apply a constant +7 hour conversion to EPA clock timestamps, with no daylight saving adjustment.** Use the official original `Facility ID` and `Unit ID` source identifiers. EPA Unit IDs do not automatically match EIA-860 generator identities.

A complete EPA *July local standard* date/hour population extends from **2024-07-01 07:00 UTC through 2024-08-01 06:00 UTC**, inclusive (744 hourly labels). The source-backed ERA5 2024 **UTC July** weather file extends from **2024-07-01 00:00 UTC through 2024-07-31 23:00 UTC**. The exact intersection is **737 hourly timestamps** (July 1 07:00 through July 31 23:00 UTC). The seven excluded EPA local July 31 17:00–23:00 clock hours correspond to **August 1 00:00–06:00 UTC**, and require **real August ERA5** to fill. Repeating a July temperature or interpolating August is impermissible.

The reproducible [alignment script](../src/grid_resilience/srp_epa_era5_july_local_standard_alignment.py), [regression tests](../tests/test_srp_epa_era5_july_local_standard_alignment.py), and [independent official-source workflow](../.github/workflows/srp-2024-july-epa-era5-hourly-alignment.yml) enforce:
1. The original Zenodo-preserved EPA 2024 Arizona archive MD5 and complete unmodified existing EIA-860-linked July ERA5 source provenance.
2. Exact EPA 2024 local standard July 744-hour source calendar for each detected target EPA Unit ID, 0–23 hour validity, and no duplicate EPA unit-hour keys.
3. A 7-hour fixed local standard offset, never daylight saving shift, exact hourly site/UTC key joins, no ERA5 temperature fill on the seven August boundary hours.
4. Exactly 737 matched / 7 unmatched source hours per EPA unit as a calendar invariant, and separate source fields for `Operating Time`, `Gross Load (MW)` and `Heat Input`.
5. Explicit rejection of generator net MW, observed forced outage, generator temperature derating, lost power or EENS inference. A correlation between EPA source gross load and ERA5 ambient temperature is **not** a physical generator availability curve without a dispatch/commitment basis.

## CI-verified hourly alignment and preliminary descriptive experiment

**Confirmed, not merely expected:** [GitHub Actions run 41926491544](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41926491544) **SUCCESS**, accompanied by [Research Methods CI 41926491476](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41926491476) **SUCCESS**. Archived [artifact 13370145959](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41926491544/artifacts/13370145959) includes `epa_source_july_lstd_era5_utc_hourly.csv`, `epa_era5_july_hourly_alignment_summary.csv`, MD5 source provenance and the strict source-admission manifest.

The complete genuine EPA original Arizona 2024 source was re-downloaded, passed MD5, and cross-matched with the independently verified July 2024 ERA5 plant source. **All 10 EPA source Unit IDs each had 744 July LST hour records and 737 true July UTC ERA5 source-hour matches; 7 genuinely unobserved August UTC boundary hours remain unfilled.** This yields **7,370 matched EPA unit-hour observations** across three distinct plant sites (not 7,370 independent weather events). Every target unit passed unique hour and month validation.

| EPA Plant / Unit | July source calendar hours | July ERA5 matched UTC hours | Positive operating-time hours within matched source |
|---|---:|---:|---:|
| 141 / 1 | 744 | 737 | 329 |
| 141 / 2 | 744 | 737 | 330 |
| 141 / 3 | 744 | 737 | 383 |
| 141 / 7 | 744 | 737 | 111 |
| 141 / 8 | 744 | 737 | 99 |
| 55129 / DBG1 | 744 | 737 | 722 |
| 55129 / DBG2 | 744 | 737 | 730 |
| 55129 / DBG4 | 744 | 737 | 18 |
| 55129 / DBG5 | 744 | 737 | 19 |
| 147 / K-7 | 744 | 737 | 612 |

### Same-plant meteorological exposures — not replicated by number of EPA units

A separate [descriptive heat-bin CI 41927445294](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41927445294) **SUCCESS** with [Research Methods CI 41927445598](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41927445598) and [artifact 13369667121](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41927445294/artifacts/13369667121). At each site, count ERA5 temperature **once per unique UTC weather hour**, even though all colocated source EPA units use the same weather measurement.

| Plant | Below 35°C | 35°C–below 40°C | At least 40°C | Site-weather hours |
|---|---:|---:|---:|---:|
| 141 | 262 | 237 | **238** | **737** |
| 55129 | 312 | 239 | **186** | **737** |
| 147 | 279 | 225 | **233** | **737** |

The completed heat-bin artifact separately summarizes each EPA Unit's observed operating-hour fraction and gross load when an operating observation is present. As an illustration of the severe **dispatch/operation selection** issue, EPA Unit **141/1** has positive operating-time indicator in **47/262 = 17.9%** of source-hours below 35°C, versus **173/238 = 72.7%** of source-hours at least 40°C. This **does not establish that heat increases available power**, just as a negative gross-load association would **not** establish derating. Demand, dispatch, equipment, unit starts and site weather co-vary.

The 7 unmatched local-July hours per EPA unit correspond to actual **2024-08-01 00:00–06:00 UTC**, requiring independently measured August ERA5. The July-only weather file must not be extended by fill, interpolation, repeated readings or a false local/UTC timestamp alignment.

**Accepted:** documented local-standard timezone conversion; real byte-verified archive, exact plant-hour ERA5 alignment and three-plant weather deduplication; descriptive EPA source operating-hour/gross-load stratification. **Not accepted:** an EPA unit equals a specific EIA860 GT generator, EPA gross load equals EIA net MW, observed plant derating, dispatcher-held capacity, heat-induced forced outages, or EENS.

## Immediate next empirical gates

1. Obtain **2024-08-01 00:00–06:00 UTC** actual ERA5 source observations to complete a fully local-July-matched 744-hour panel with no imputation.
2. Establish site-specific monitored-unit/electrical-generator relationships via original ECMPS monitoring plans rather than static name similarities.
3. Develop control-rich within-unit source operation studies with demand and commitment context, multi-year validation and noncausal reporting until equipment availability/temperature output curves are independently calibrated.
