# SRP January 2024: verified EIA-923 Page 1 vs EIA-930 fuel reporting audit

**Provenance:** successful official EIA-923/EIA-930 [GitHub Actions run 41734281064](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41734281064), source commit `f046d518cd9faa3553e8b9c37cd6a301eb293d18`, [artifact 13276708566](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41734281064/artifacts/13276708566). Source ZIP checksums/URLs reside in `source_provenance.json` and `eia930_source_provenance.json`. Source-specific data `eia930_monthly_fuel_reporting_coverage.csv`, `eia923_page1_prime_mover_fuel_comparison.csv`, and `eia923_eia930_fuel_scope_manifest.json` were verified in the archived artifact. **These are different reporting grains; historical calibration is not certified.**

## EIA-930: 744 SRP UTC-hour records by published fuel heading

| EIA-930 fuel heading | Nonblank hours / 744 | Signed reported MWh |
|---|---:|---:|
| Coal | 744 | 536,833 |
| Natural Gas | 744 | 1,425,116 |
| Nuclear | 744 | 2,987,096 |
| Hydropower and Pumped Storage | 744 | 1,057 |
| Solar | 744 | 128,884 |
| Wind | 744 | 20,287 |
| Other Fuel Sources | 744 | -346 |
| All Petroleum Products | 0 | missing |
| Unknown Fuel Sources | 0 | missing |

The seven fully reported fuel headings add arithmetically to **5,098,927 MWh**, matching EIA-930's BA-level monthly generation total exactly. **This numeric zero residual does not mean blank oil/unknown categories equal zero, or that fuel reporting is complete.** The scope audit intentionally keeps the complete-fuel-sum/complete-fuel-residual fields **null** while any source category has missing hours.

## EIA-923 Page 1: reported BA, plant / fuel / prime mover monthly source rows

There are **61** reported January rows, across **14** original fuel/prime-mover combinations, totaling **5,306,052.001 MWh** of signed net generation. Important unmodified source aggregates include:

| EIA-923 Page 1 source records | Signed reported MWh |
|---|---:|
| ST / NUC | 2,987,772 |
| CA+CS+CT+GT / NG (and ST/NG = 0) | 1,902,868.304 |
| ST / SUB | 270,112.610 |
| PV / SUN | 141,235 |
| WT / WND | 9,957 |
| HY / WAT | 1,015 |
| PS / WAT | -132 |
| BA / MWH | -6,956 |
| GT+ST / DFO | 180.087 |

The underlying Page 1 categories are retained rather than automatically allocated to EIA-930 published fuel headings. The **2,987,772 MWh** nuclear figure includes three distinct ST/NUC source rows at one plant; they were preserved, not deduplicated.

## What the cross-source differences can and cannot establish

- **Total Page 1 minus EIA-930:** **+207,125.001 MWh**. This is a difference across non-identical BA and reporting boundaries, **not** a calibrated prediction residual, physical load loss, or dispatch imbalance.
- **Nuclear numeric comparison:** 2,987,772 Page 1 vs 2,987,096 EIA-930: **+676 MWh**, or about 0.023% of the EIA-930 reported nuclear value. The apparent close agreement does not independently establish identical plant membership or measurement conventions.
- **Natural gas numeric comparison:** Page 1 source codes grouped as NG total 1,902,868.304 vs EIA-930 Natural Gas 1,425,116: **+477,752.304 MWh**; this indicates major source-boundary/classification disagreement requiring a plant-to-BA crosswalk.
- **Coal numeric comparison:** Page 1 ST/SUB = 270,112.610 vs EIA-930 Coal = 536,833: **-266,720.390 MWh**; Page 1 SUB is not automatically a verified complete coal-to-EIA930 category correspondence.
- **Solar numeric comparison:** 141,235 Page 1 PV/SUN vs 128,884 EIA-930 Solar: **+12,351 MWh**; temporal and reporting scope differ.
- **Wind numeric comparison:** 9,957 Page 1 WT/WND vs 20,287 EIA-930 Wind: **-10,330 MWh**.
- **HY+PS numeric comparison:** 883 Page 1 signed HY/PS vs 1,057 EIA-930 combined hydro/pumped: **-174 MWh**. Negative pumping net generation must not be discarded.

These comparisons are descriptive source-coverage diagnostics, **not** validated like-for-like technology bias estimates. A zero difference in one grouping does not certify historical dispatch calibration.

## Research implications

1. Preserve EIA-930 fuel group missingness (oil and unknown entirely blank for this BA/month), even though the seven reported categories numerically sum to the BA total.
2. Investigate coal and natural gas first: large differences dominate the source-technology mismatch. Check original reporting BA attribution, plant jurisdiction/contractual generation, multi-fuel operation and Prime Mover rules.
3. Reconcile original EIA-923 Page 1 plant/fuel monthly rows to EIA-860 source plant/BA membership and EIA-930 hourly BA fuel aggregates with documented confidence; do not merge Page 1 and Page 4 MWh.
4. Only after this source and seasonality gate should the paper fit hourly technology availability, out-of-year validation, transfer limitations and matched climate-stress factorial dispatch.

**Observed outages inferred: NO. Historical calibration certified: NO.**
