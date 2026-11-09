# Paper C — July 2024 EIA-930 161-hour original modern fuel observation vectors

## Research finding and source scope

**Verified original-source CI:** [#42704596752 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42704596752). [Download original UTC hourly 644 BA-hour six-fuel cohort, BA summaries and original EIA source SHA256 (artifact 13712179032)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42704596752/artifacts/13712179032). The [code](../src/grid_resilience/paperc_2024_modern_161h_fuel_vector.py) passed five regression tests, explicitly rejects duplicate hours, missing/zero substitution, and non-source-identical modern partition.

**Window**: 2024 July 1 **07:00** UTC up to but excluding July 8 00:00 UTC (161 consecutive hours). The initial seven UTC hours were in original EIA-930 **2024 Jan–Jun** publication partition; the last 161 were in **2024 Jul–Dec**, with a different fuel taxonomy. **The two original reporting schemas have not been established to be equivalent.** This analysis deliberately uses only the latter 161-hour source-identical category definitions. It does not fill or recode the first seven hours.

Six **original EIA-930 reported fuel categories** are screened independently against raw BA net generation on identical UTC-hour/BA keys:
1. `Natural Gas`
2. `Coal`
3. `Nuclear`
4. `Wind without Integrated Battery Storage`
5. `Solar without Integrated Battery Storage`
6. `Hydropower Excluding Pumped Storage`

The source archive contains no independently source-certified per-generator dispatch, energy storage SOC, hourly available power or actual network intertie transfer rating. Six source-reporting labels are not a technology-complete physical BA fleet. The full EIA-930 reporting dataset has other categories, including petroleum, other and unknown fuel, and separate hybrid/battery categories with structural missingness. **Neither a six-category sum nor its difference from BA total is a certified estimate of omitted physical generation.**

## Main source-verified diagnostic

| BA | Original modern BA hours | Hours all six numeric | Original BA reported net generation (MWh) | Six selected original fuel columns, same available hours (MWh) | BA net minus six selected source reports (MWh) |
|---|---:|---:|---:|---:|---:|
| AZPS | 161 | **161** | **500,641** | **486,154** | **+14,487** |
| BPAT | 161 | **0** | **1,680,467** | **N/A** (original Coal blank in all 161 hours) | **N/A** |
| CISO | 161 | **161** | **4,447,446** | **4,473,383** | **−25,937** |
| SRP | 161 | **161** | **1,294,257** | **1,298,243** | **−3,986** |

The selected six original fuel-category values **exceed** the original BA net generation for both CISO and SRP over exactly matched 161-hour periods. Thus, a naive `BA net − six reported fuels` **does not even behave as a non-negative missing-generation budget**. The difference can reflect category definitions, reported fuels, balancing accounting or other original source reporting differences, but the original archive alone **does not identify a mechanism or certify its physical interpretation**. It is neither an EENS measurement, actual supply loss, transmission import energy nor proof of actual energy imbalance.

**Critical missingness:** BPAT original `Coal` field is nonnumeric for the entire modern 161-hour partition. Despite BPAT's original BA net generation being numeric throughout, **no six-component total is produced for BPAT**. Missing source cells must not be treated as zero-power generation. The CISO 2024 modern `Battery Storage` source field was also blank (documented by the prior [original taxonomy audit](PROJECT_C_EIA930_RENEWABLE_STORAGE_SOURCE_TAXONOMY_GAP_CI_VERIFIED.md)); the six-component sum here intentionally does not include it or infer its output from independent CAISO outlook values.

## Relation to four-BA physical calibration

[Verified four-BA historical PyPSA baseline admission audit](PROJECT_C_2024_FOUR_BA_HISTORICAL_BASELINE_ADMISSION_CI_VERIFIED.md) established complete BA hour keys and complete BA net-generation/demand fields, but rejected physical adequacy admission in all four BAs: AZPS/SRP report arithmetic closure yet lack fully calibrated plant availabilities and energy/transfer constraints; BPAT fails source arithmetic closure in all 168h; CISO has 144 missing original Total Interchange hours and 19 more nonclosing complete hours. This modern 161-hour disaggregation **does not repair any of those original physical or accounting gates**.

### Suggested supplementary manuscript statement

> In the July 2024 source-consistent 161-hour reporting partition, original EIA-930 six-fuel numerical vectors are complete for AZPS, CISO, and SRP, but not BPAT owing to blank coal fields. Their signed arithmetic differences from BA net generation are +14,487, −25,937, and −3,986 MWh, respectively. Negative values in CISO and SRP show that selected-category summation cannot be interpreted as missing physical supply. This source-based audit informs baseline reporting completeness but not a source-calibrated grid-adequacy or EENS estimate.

This is a **reporting provenance and data identifiability result**, not a demonstrated reliability consequence of extreme heat. Publication claims should avoid using these differences as modeled generation correction or inferred outage energy.

## Next credible step

- Audit the **full set** of original 2024 Jul–Dec fuel labels and their completeness by BA and UTC hour, including petroleum/other/unknown and solar/hybrid categories, before attributing signed differences to any missing source component. The source sum may still differ from BA net even with complete reporting and therefore must be accompanied by an explicit diagnostic rather than an inferred physical correction.
- Build source-consistent, **historically dated** actual plant availability and physical interchange capacities rather than equating 2025 preliminary generator nameplate or EIA-930 partner interchange with a technical rating.
- Only after confirmed generator inventory, hydro/storage energy/SOC budgets and intertie limits are available should a physical 168-hour historical PyPSA baseline be considered; no historical EENS is estimated by this work.
