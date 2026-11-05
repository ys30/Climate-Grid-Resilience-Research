# Independent 2024 January versus July observed EPA source-unit operating comparison — CI verified

**Observed source workflow:** [GitHub Actions 42072156313](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42072156313) **SUCCESS**, with source artifact [13437047622](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42072156313/artifacts/13437047622); source commit `44ee67134720cd5d4e85df59cec64803ad771a9b`.

## Independently recovered evidence

The CI independently **downloaded and MD5-verified the original 2024 Arizona EPA hourly archive** ([Zenodo record 15059567](https://zenodo.org/records/15059567), 183,084,007 source bytes, fixed MD5 `7123a5070f652890f46e819dcc890ec0`), extracted the **actual January** observations of the same **10 EPA source units in plants 141, 147, 55129**, and matched their EPA Part75 Arizona local standard time (UTC−07, no DST) to previously verified [January full 13-plant ERA5 archive run 41775332025](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41775332025). The July counterpanel uses the separately verified [EPA–ERA5 July full local-month run 41961038085](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41961038085).

The comparison **restricts each month to actual UTC source-month overlaps**: 737/744 valid local-month source-weather hours **per unit in each month**, with 7 hours crossing into the next UTC month. January's February-UTC weather boundary **was not fabricated**. July's full local-month weather exists but the last 7 UTC-August hours are excluded for symmetrical source-month comparison. There are **7,370 source unit-hours per month** and **20 per-unit/month summary records**; source identities are strictly identical. Each temperature site series is repeated across colocated units and is not an independent sample for each unit.

## Observed same-unit seasonal contrasts

| EPA source unit | Jan temp °C | Jul temp °C | Jan positive running hours /737 | Jul positive running hours /737 | Jan conditional source gross MW | Jul conditional source gross MW |
|---|---:|---:|---:|---:|---:|---:|
| 141 / 1 | 11.37 | 37.27 | **0** | **329** | **Not observed** | 62.41 |
| 141 / 2 | 11.37 | 37.27 | **0** | **330** | **Not observed** | 61.22 |
| 141 / 3 | 11.37 | 37.27 | **0** | **383** | **Not observed** | 93.06 |
| 141 / 7 | 11.37 | 37.27 | 6 | 111 | 41.83 | 32.30 |
| 141 / 8 | 11.37 | 37.27 | 6 | 99 | 35.50 | 33.75 |
| 147 / K-7 | 11.45 | 37.00 | **354** | **612** | 207.34 | 214.68 |
| 55129 / DBG1 | 11.25 | 36.22 | **599** | **722** | 259.12 | 254.75 |
| 55129 / DBG2 | 11.25 | 36.22 | **656** | **730** | 261.97 | 254.78 |
| 55129 / DBG4 | 11.25 | 36.22 | 11 | 18 | 29.91 | 37.50 |
| 55129 / DBG5 | 11.25 | 36.22 | 10 | 19 | 29.90 | 37.53 |

Conditional mean gross load is reported only on positive EPA Operating Time rows. For 141 / 1, 2, 3, **January has no eligible operating gross-load observations**, so a January gross-load average and winter–summer delta **must be missing**, not zero or a calculated temperature loss.

**Source-derived differences**: K-7's positive operating share increases by **35.01 percentage points** (354/737 → 612/737), with conditional EPA Gross Load rising by **7.35 MW**; DBG1 rises by **16.69 percentage points** in operating share while conditional gross load declines **4.36 MW**; DBG2 rises by **10.04 percentage points** while conditional gross load declines **7.19 MW**. The opposite directions make it inappropriate to translate seasonal gross-load differences into a single common heat coefficient.

## Scientific implications and exact acceptance

1. This is **a genuinely independent calendar season's source operating evidence**, not another July-only bootstrap resample. It verifies exposure and observed operating patterns across January and July with same 10 source IDs. It **does not yet externally validate the July per-unit regression slope**, which also controlled for SRP EIA-930 demand, MST time-of-day and MST date.
2. The marked increase in EPA positive operating indicators during hot-season source months is compatible with dispatch and demand selection; it **cannot be labeled heat improving physical generator availability**. A zero reported January operating indicator is **not a verified forced outage**.
3. The winter month contains no operating gross-load sample for three Plant 141 source units, creating an explicit **support and positivity limitation** for model transfer. Weather support differs by roughly 25°C at all three plants.
4. January and July seasonality, calendar effects, fuel, economics, meteorology, fuel-price or dispatch policies are not held fixed. No causal climate effects, measured load loss, true GT available net MW, EENS, LOLE or generator-specific forced outage coefficients have been inferred.
5. The historical EPA unit-to-EIA physical generator identity is still unresolved; the four units without static crosswalk links remain unmapped. Only strict source EPA unit IDs are paired across months.

**Next empirical step:** Add an independently source-admitted January EIA930 SRP demand series to permit **January-only demand/hour/day-controlled model fits** in units with enough reported operating data, and assess whether coefficients can be compared without extrapolating outside winter weather support. No direct winter slope fitting is possible for units with zero winter positive gross-load observations.

Code: [independent January source extractor and January/July comparison](../src/grid_resilience/srp_epa_2024_january_july_observed_seasonal.py), [source-clock and identity tests](../tests/test_srp_epa_2024_january_july_observed_seasonal.py).
