# Paper C — CAISO 2023/2024 July historical battery-market source admission and interval completeness

## Purpose and highest-level research finding

This phase materially improves the historical storage-data evidence for **CISO only** without pretending that raw CAISO market results are actual metered charging/discharging, physical SOC or a physically validated grid adequacy baseline.

The prior [original EIA-930 2024 schema audit](PROJECT_C_EIA930_RENEWABLE_STORAGE_SOURCE_TAXONOMY_GAP_CI_VERIFIED.md) showed that Battery Storage, Pumped Storage and Wind with Integrated Battery Storage reported **0/161 original numeric cells** over the modern 2024 July cohort, despite EIA-930 having an associated source column. The [official EIA-930 methodology](https://www.eia.gov/electricity/930-content/about.html) specifies that **Battery Storage was added as an energy source beginning January 1, 2025**. Thus 2024's 161 blank cells **must not be treated as negative evidence of operational batteries**. There is a separate independently documented CAISO market dataset covering the exact study dates.

## Independently verified CAISO sources

CAISO published historical [Daily Energy Storage Report](https://www.caiso.com/library/daily-energy-storage-reports) original quarterly market data back through 2023, [explicitly announced in October 2024](https://www.caiso.com/notices/daily-energy-storage-report-for-1-1-23-9-30-24-data-posted), including preliminary system-level energy-market output and state-of-charge categories. The exact files are:

- [2023Q3 original CAISO spreadsheet](https://www.caiso.com/documents/storage-report-2023q3.xlsx); SHA256 `cbf978a1a244cdc7b513a6a827dac500b0cae72a449612ef68e4295e3e811634`
- [2024Q2 original CAISO spreadsheet](https://www.caiso.com/documents/storage-report-2024q2.xlsx); SHA256 `67c05c30bda9ec020dbe476f050436cbebb500b1a9119eec08f0275f3201926`
- [2024Q3 original CAISO spreadsheet](https://www.caiso.com/documents/storage-report-2024q3.xlsx); SHA256 `b8e58169f50e7a796fc29b7207ac591dbe16d7703ed9c5019a6c2bf6234dd725`
- [Official CAISO data dictionary / preliminary-data caveat](https://www.caiso.com/documents/data-release-and-definitions.pdf), specifying `TRADE_DATE`, `HOUR`, `INTERVAL`, `MARKET`, `RES_TYPE`, `TYPE`, `VALUE`. `LESR` includes batteries, stand-alone or co-located; `HYBD` designates hybrid resources; `SOC` denotes state-of-charge market output; RTD interval indices range 1–12. Data are preliminary market results, **not settlement quality**.

### Crucial source-format and time-boundary repairs

The official 13–15 MB XLSX quarter files have **defective worksheet dimension metadata indicating `A1`**, so standard read-only worksheet readers reported a single worksheet cell even though source ZIP XML contains >200,000 genuine `market_output` rows in each quarter. We audited ZIP-internal worksheet XML and recovered every physical row **without trusting the declared worksheet dimension**.

Source `TRADE_DATE` is the CAISO *local trade date*, not the EIA-930 UTC timestamp. July 2024 UTC begins **June 30, 2024 at 17:00 PDT**; hence a correct July 1–7 UTC cohort requires **2024Q2 for its first seven UTC hours**, then 2024Q3. For July 10–16, 2023 UTC, 2023Q3 includes all required CAISO local trade dates. This local/UTC bridge is explicit and regression tested, not guessed by comparing nominal dates.

## Source-CI audit results

1. [Quarterly original workbook and SHA256 validity #42510990132](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42510990132): SUCCESS.
2. [Raw XLSX ZIP internal data-structure investigation #42511058869](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511058869): SUCCESS.
3. [Original source XML header recovery #42511120602](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511120602): SUCCESS.
4. [Exact 2023/24 target UTC market-output extraction #42511395768](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511395768): SUCCESS with four regression tests. [Download complete market-output source records and SHA256 evidence (artifact 13629038073)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511395768/artifacts/13629038073).
5. [Market EN/SOC interval-specific reporting audit and supplemental figure #42511649380](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511649380): SUCCESS with four tests and real-source 2023/24 interval assertions. [Download PDF/PNG, 672 hourly type records, explicit missing-interval keys and source-scope manifest (artifact 13629463146)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511649380/artifacts/13629463146).

### Exact market-type and interval coverage

| Source market / resource / type | 2023 Jul 10–16 UTC | 2024 Jul 1–7 UTC |
|---|---:|---:|
| IFM / LESR / EN | 168 of 168 hourly records | 168 / 168 |
| IFM / LESR / SOC | 168 / 168 | 168 / 168 |
| RTD / LESR / EN | 2,004 of 2,016 expected five-minute interval records | 2,016 / 2,016 |
| RTD / LESR / SOC | 2,004 / 2,016 | 2,016 / 2,016 |
| RTD / LESR / EN hourly blocks with all 12 intervals | 166 / 168 | 168 / 168 |
| RTD / LESR / SOC hourly blocks with all 12 intervals | 166 / 168 | 168 / 168 |

**Original 2023 missing intervals for each of EN and SOC:**
- 2023-07-13 04:00–04:59 UTC: RTD interval indices **7–12** missing.
- 2023-07-13 05:00–05:59 UTC: RTD interval indices **1–6** missing.

All remaining 2023 RTD hours have a full 12-interval set. The incomplete hours remain **null for plot-level hourly mean**, not zero or interpolated, including the SOC market-type series. The [new paper supplementary figure](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42511649380/artifacts/13629463146) has four panels for the two distinct July study windows × EN and SOC preliminary market output, preserving those gaps.

## What can and cannot be inferred

**Supported:** CAISO-reported 2023/24 contemporaneous storage-market participation; sign and relative-hour patterns in reported `EN`, and variation in reported `SOC` category values; hourly source completeness; initial 2024-07-01 seven-hour UTC data from the *previous* calendar quarter. The data dictionary notes preliminary and non-settlement-quality values.

**Not supported:** That `EN` reflects actual, settlement-corrected metered MWh delivered to the grid, that `SOC` is a validated physical unit-level real-time energy state, or that a time average of market values equals generator actual dispatch. Raw `VALUE` units and physical interpretation cannot be strengthened beyond the official dictionary without corroboration. **Different markets (IFM, RTPD, RTD and RUC) must not be summed or averaged together as if independent physical output.** Market storage availability and performance of individual plants are not recovered from system-level aggregated rows. The CAISO source concerns **CISO only**, not AZPS, BPAT or SRP.

This remains a useful external source supporting realistic *candidate* storage-operating envelopes for later source-constrained PyPSA scenarios, but does not independently identify actual available battery MW, MWh energy state, outages, intertie capacity, generator fuel dispatch, or EENS. A reliable physical historical baseline requires additional metered operating data and an auditable physical BA boundary.

## Methodological next steps

1. Compare independently **CAISO public 5-minute supply/batteries historical chart files** to the market source's RTD/IFM system output on the same local and UTC time keys. Do not equate preliminary market awards to measured actual production before verifying measurement meaning.
2. Keep hydropower generation separate from battery `SOC`; obtain public reservoir/storage and actual hydro operations data for BPAT before modeling hydro energy constraints.
3. Derive representative 2023/24 **technology-specific dispatch *scenarios*** from verified historical source measurements only where matched; always label modeled batteries and hydro dynamics as calibrated only where physical data permit.
4. Cross-validate any future technology-complete PyPSA baseline against EIA-930's previously documented CISO raw Total Interchange missingness (144h) and BPAT nonclosure (all 168h). **No model output in this report is an observed historical outage or EENS.**
