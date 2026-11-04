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

## Status and acceptance gate

The controlled [GitHub Actions 41926491544](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41926491544) is the mandatory data-execution gate. A proven **737/744 calendar-hour intersection** is a methodological expectation; until an actual successful CI artifact is checked, it must **not** be described as empirically matched source rows.

Once successful, the artifact will contain `epa_source_july_lstd_era5_utc_hourly.csv` with strictly aligned original July EPA unit-hour observations and site ERA5 weather, `epa_era5_july_hourly_alignment_summary.csv` and `epa_era5_july_alignment_manifest.json`. These are source-level descriptive exposure join data and do not establish calibrated thermal derating.

**Next:** extend weather extraction through 2024-08-01 06:00 UTC for a full local July 744/744 match; inspect source hour/temperature and observed operating-time subsets, checking independent-unit weather-grid dependence and dispatch selection. No automatic hourly EIA electrical-generator allocation.
