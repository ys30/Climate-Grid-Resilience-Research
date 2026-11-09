# Paper C — Independent CAISO 5-minute batteries telemetry versus RTD LESR market EN (2023/2024 source-reconciled)

## Main result

**Original-source independent comparison now CI verified:** [GitHub Actions run #42672045610 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42672045610). This is the first Paper C analysis aligning independently archived CAISO 5-minute batteries *Today's Outlook* summaries and previously audited CAISO storage market `RTD / LESR / EN` to **exact UTC five-minute keys** over the two historical seven-day cohorts.

The two original data products are *not interchangeable*: Today's Outlook **Total batteries** includes some hybrid battery-related resource components, and is a five-minute informational operations summary, while `RTD / LESR / EN` is a **preliminary 5-minute wholesale market outcome** for a different resource/reporting population. The high correlations below are descriptive, not market-clearing accuracy, individual-meter forecast skill, settlement validation, or actual physical battery SOC.

| Independent-source statistic | 2023-07-10 to 2023-07-16 UTC | 2024-07-01 to 2024-07-07 UTC |
|---|---:|---:|
| Original Today's Outlook battery 5-min telemetry observations | 2,016 / 2,016 | 2,016 / 2,016 |
| Exact UTC intervals with reported original RTD LESR EN | 2,004 / 2,016 | 2,016 / 2,016 |
| Missing original market RTD LESR EN intervals | 12 | 0 |
| Pairwise same-key Pearson correlation | **0.981133** | **0.992392** |
| Mean of (Total batteries 5-min MW − RTD LESR EN original VALUE) | **−11.73** | **−96.72** |
| Mean absolute same-key numeric difference | **227.94** | **304.73** |

**Do not label the final two columns an operational error, discrepancy in measured generation, actual spilled energy or lost supply:** resource populations and definitions differ. Specifically do not integrate `RTD/LESR/EN` into physical MWh delivered without determining market quantity and energy attribution conventions.

## Official data and independent source checks

- [CAISO Today's Outlook Supply and Batteries methodology](https://www.caiso.com/todays-outlook/supply): the Batteries trend contains **five-minute average power in MW**; negative battery values indicate charging direction and positive denote discharging. Some hybrid resources are included. The site explicitly says its charts are informational and *not for official billing or operational planning*.
- Original historical daily CAISO `storage.csv` feeds: `https://www.caiso.com/outlook/history/YYYYMMDD/storage.csv`. Source columns `Time`, `Total batteries`, `Stand-alone batteries`, `Hybrid batteries`.
- An independent per-day CAISO `fuelsource.csv` feed: `https://www.caiso.com/outlook/history/YYYYMMDD/fuelsource.csv`. This contains `Time` and `Batteries` among other fuel types. The audit retains both source columns and their exact-per-timestamp comparison, without assuming they reflect different underlying meters.
- [Source URL format and live 2023/24 history endpoints tested in CI #42671372854](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42671372854), with original URL, HTTP response, source schema and SHA256 for sample local days.
- The old `/outlook/SP/History/` historical path returns 404 for the tested dates; the verified current `/outlook/history/YYYYMMDD/` returns actual 5-minute CSV.

The 2023 EIA-930 study window begins **2023-07-10 00:00 UTC = 2023-07-09 17:00 PDT**, and the 2024 window begins **2024-07-01 00:00 UTC = 2024-06-30 17:00 PDT**. The source ingestion explicitly fetches **eight local-date CSVs per year**, including the previous day and final partial day, for a total of **32 official daily original CSVs**: battery/storage plus independent fuel-source snapshots. Each source-local day has 288 five-minute rows, and after the two PDT/UTC boundary crops each cohort has exactly **2,016 contiguous UTC points**. Source file SHA256/size/URL metadata, no-imputation rules and full matched time keys are archived in the CI output.

### Exact original source evidence delivered

[Download 2023/2024 original-source 5-minute battery data, RTD UTC matched records, cohort-level comparisons and 32 SHA256 source records — artifact 13697919745](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42672045610/artifacts/13697919745).

This joins the previously CI-verified [CAISO historic market RTD extraction #42511395768](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511395768), [original RTD EN/SOC missing-interval gate #42511649380](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511649380). The **12 missing 2023 five-minute RTD EN observations** are precisely the original July 13 UTC hour-04 intervals 7–12 and hour-05 intervals 1–6. The new Today's Outlook battery telemetry has numeric source observations at those times, but these **must not replace the missing RTD market results**. All comparisons use only the 2,004 or 2,016 truly paired intervals.

### Interpretation for the PyPSA C resource baseline

This is a substantial improvement over relying on the missing **2024 EIA-930 Battery Storage** fuel-category columns. The original EIA-930 documentation establishes that battery storage was added to its energy-source categories only in 2025, so the 2024 original category blanks are **not evidence of absent physical storage**.

The CAISO five-minute informational storage operations series provides an independently time-indexed, contemporary signed battery charging/discharging **pattern**, with cross-source alignment and sign interpretation. It is **not by itself** a full system or plant-level telemetry archive; it includes some hybrids, is informational, and cannot be directly assigned to EIA-930A generator IDs or July 2024 physical resource availability. The RTD market record provides an additional *contemporaneous market-operating signal*, not a separate physical energy measurement or a substitute for metered SOC.

Source limitations for Paper C remain:

1. These figures describe **CAISO/CISO only**, not AZPS, BPAT or SRP. BPAT hydro and the other two BA storage states still require separate historical sources.
2. The previous [EIA-930 2024 reporting and BA reconciliation](PROJECT_C_EIA930_RENEWABLE_STORAGE_SOURCE_TAXONOMY_GAP_CI_VERIFIED.md) documents CISO 144/168 missing Total Interchange hours and substantial bilateral reporting discrepancies. This new CAISO data **cannot repair those original EIA-930 fields**.
3. A physically consistent PyPSA storage representation requires verified power ratings, installed energy MWh, SOC bounds, initial SOC, round-trip efficiency, availability and the relevant transmission interchange deliverability. Daily five-minute observed-direction summaries alone do not establish those parameters.
4. The two 2023/2024 cohorts are **different calendar weeks**, so neither their pointwise comparison nor correlation differences constitutes a climate-treatment effect.

**Paper classification:** Strong, independently audited supplementary original-source data crosscheck and battery reporting-source completeness result. It is not historical outage detection, physical EENS calibration or proof of transfer-limit adequacy.

## Reproducible code

- [Primary historical `storage.csv` + `fuelsource.csv` and RTD/LESR/EN exact-five-minute UTC join](../src/grid_resilience/paperc_caiso_telemetry_vs_rtd.py).
- [Source-only original battery versus RTD profile and predeclared ±5/±10 minute lag sensitivity code](../src/grid_resilience/paperc_caiso_telemetry_rtd_figure.py). The plot CI is separately tracked; do not treat it as verified until it successfully runs and archives its PDF/PNG and numeric lag table.
- [Source-cohort and missingness regression checks](../tests/test_paperc_caiso_telemetry_vs_rtd.py) and [figure/lag regression checks](../tests/test_paperc_caiso_telemetry_rtd_figure.py).
