# SRP January 2024: official EIA-923 Page 1 / Page 4 plant-overlap audit

**Source and verification:** successful [official-source GitHub Actions run 41732671528](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41732671528), commit `f925760e6a3303e4ce519ef02c18d66a16a05681`. The run downloads the official 2024 EIA-923 ZIP, extracts January SRP Page 1 and Page 4, runs `eia923_page1_page4_scope_bridge`, and uploads the underlying CSVs and manifest. **Scope audit only: not historical grid reliability calibration.**

## Source records and coverage

| Item | 2024-01 SRP |
|---|---:|
| Page 1 extracted rows | 61 |
| Page 1 distinct plant IDs | 35 |
| Page 1 signed net generation | 5,306,052.001 MWh |
| Page 4 extracted generator-month rows | 40 |
| Page 4 distinct plant IDs | 11 |
| Page 4 signed net generation | 2,160,272 MWh |
| Plants present in both | 11 |
| Plants only in Page 1 | 24 |
| Plants only in Page 4 | 0 |
| Page 1 generation at plants also represented in Page 4 | 2,160,935.001 MWh |
| Page 1 generation at Page 1-only plants | 3,145,117 MWh |
| Page 4 generation at shared plants | 2,160,272 MWh |

Page 4 is a subset by **plant ID in this selected BA/month extract**. This does *not* establish that Page 4 and Page 1 are duplicate generation datasets at the generator level.

Page 1 includes three separate reported `ST/NUC` rows for plant 6008: 989,360; 998,663; and 999,749 MWh, totaling **2,987,772 MWh**. Their common plant/fuel/prime-mover/month key is not unique; these must remain three source observations. The bridge now reports coarse-key repetitions instead of discarding or rejecting legitimate rows.

## Shared-plant reconciliation details (Page 1 minus Page 4, MWh)

| Plant ID | Signed difference |
|---|---:|
| 141 | -45 |
| 147 | +204 |
| 55129 | +504 |
| 55306, 55455, 55481, 58557, 59338, 60768, 8068 | 0 each |
| 6177 | +0.001 |

The **net shared-plant difference** is **+663.001 MWh**; the **sum of absolute plant-level differences** is **753.001 MWh**. The nonzero discrepancies need per-plant fuel/prime-mover and source-footnote follow-up; no forced balancing adjustment is justified.

The Page 1 source-reported total is **207,125.001 MWh larger** than the previously extracted EIA-930 SRP January generation total of 5,098,927 MWh (approximately **4.06% relative to EIA-930**). Because the source definitions and BA reporting boundaries differ, this is a *scope reconciliation gap*, not a calibrated residual, dispatch error or unreported electricity outage. Page 1 + Page 4 must **not** be added: the shared plants are already represented in both.

## CI and scientific acceptance gate

- Official archive fetched and SHA-256 retained in the artifact provenance.
- Synthetic module and real-source execution pass at commit `f925760e`.
- Multiple Page 1 source rows per coarse key are preserved and counted, not collapsed.
- Raw signed negative generation and source-specific totals are preserved.
- Separate Page 1 and Page 4 summaries are exported; merging their MWh is prohibited by design.
- No inference is made about generator ownership, hourly availability, intertie deliverability or observed outages.
- **Historical calibration certified: false.**

**Next work:** reconcile shared-plant deviations, confirm Page 1 fuel/prime-mover reporting versus EIA-930 BA-time/fuel conventions, quantify signed source rows and omitted source populations, then construct a controlled technology-aware hourly model rather than replacing the partial fleet with all nameplate MW.
