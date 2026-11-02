# EIA-860 / EIA-923 unmatched generator-month diagnostic (2024)

Source: actual `unmatched_generator_months.csv` from successful [EIA-860 workflow run 41341668303](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41341668303), artifact 13097269172, SHA-256 `65f6427c784b70082115337c41952c6b5f4c9d33921b6af2cf870debc2241638`.

## Observed unmatched identity groups

68 generator-month records reduce to **10 distinct plant + generator IDs**: BPAT: 12 rows, one generator; CISO: 56 rows, nine generators. No unmatched rows for AZPS or SRP in this Page-4 partial-source extraction.

| Reported BA | Plant ID | Generator ID | Unmatched months |
|---|---|---|---:|
| BPAT | 58109 | TG1 | 12 |
| CISO | 10446 | GEN1 | 11 |
| CISO | 10661 | GEN4 | 1 |
| CISO | 356 | 5 | 1 |
| CISO | 356 | 6 | 1 |
| CISO | 356 | 8 | 1 |
| CISO | 50632 | GEN1 | 12 |
| CISO | 50837 | GEN1 | 5 |
| CISO | 54626 | TG01 | 12 |
| CISO | 60100 | G-1 | 12 |

Counts come from the unmatched source CSV, not a reconstruction of the EIA dataset. These 10 generator keys represent unverified matching exceptions; monthly records must not be treated as 68 independent generators.

## Next diagnostic tests

Compare raw-string plant and generator identifiers against EIA-860 2024 operable and retired inventory, preserving leading zeros and punctuation. Determine whether unmatched IDs refer to excluded/non-operable vintage statuses, plant-name/ownership changes, generator renames, or source-extraction gaps. **Do not fuzzy-match IDs automatically**, or attribute a root cause without verified official source records.

The source inventory used by the current join is a selected operable EIA-860 inventory; absence there cannot by itself prove the generator never existed, nor that measured EIA-923 energy is zero. Keep original rows separately with `unmatched` status and source-year provenance.

This unmatched audit does not certify full-fleet coverage, plant-to-BA crosswalk, modeled-versus-observed monthly dispatch, or independent-year historical calibration.


## Same-plant inventory probe (2024 operable EIA-860)

Comparing all 10 unmatched keys against `eia860_2024_operable_generators.csv` in the **same artifact**: eight unmatched keys have no rows for their plant ID in this selected inventory. Two unmatched keys share a plant ID with a **different** generator:

| Unmatched EIA-923 key | Other generator in EIA-860 selected inventory | Decision |
|---|---|---|
| CISO plant 10661 / GEN4 | GEN5 | identity not confirmed; **do not auto-recode** |
| BPAT plant 58109 / TG1 | TG2 | identity not confirmed; **do not auto-recode** |

This does not prove either key changed names; other candidate generators are not justified matches. The other eight unmatched keys arise from seven distinct absent plant IDs (three separate generator keys at plant 356). This is a source-scope fact, not a root cause: status/vintage checks against full official EIA-860 are still required.


## Official EIA-860 full-status resolution (run 41395106441)

**Updated evidence:** [successful all-status workflow run 41395106441](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41395106441), code commit `f368e4708a7e358f9a0ab2f251caa9b93400ffda`, [artifact 13118652393](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41395106441/artifacts/13118652393). The workflow downloaded official 2024 EIA-860 and EIA-923 ZIPs, recomputed the unmatched set and checked each exact generator key against all recognized EIA-860 generator workbook sheets.

**7 of 10 distinct unmatched EIA-923 generator identities have exact matches in the official EIA-860 2024 `Retired and Canceled` worksheet with reported status `RE`:**

- BPAT `58109/TG1`
- CISO `10446/GEN1`, `10661/GEN4`, `50632/GEN1`, `50837/GEN1`, `54626/TG01`, `60100/G-1`

**3 remaining unmatched identities** are `CISO 356/5`, `CISO 356/6` and `CISO 356/8`. No corresponding plant was located in recognized 2024 EIA-860 generator workbook sheets. This is absence from the examined workbook, **not proof of retirement or zero generation**.

The previously observed `58109/TG2` and `10661/GEN5` are other same-plant operable generator IDs, *not* verified renames or replacements for TG1/GEN4. Seven matches on `RE` mean only that the official 2024 workbook carries those precise IDs in the `Retired and Canceled` sheet with that code; further study would be needed to reconcile EIA-923 reported energy with specific retirement dates and status definitions.

**Historical calibration certified: NO.** Full BA fleet completeness and withheld-year modeled-versus-observed generation validation remain pending.


## Historical identity evidence for plant 356 (2021 reference; not 2024 status)

A public 2021 EIA-860 Schedule 6A boiler/generator association table submitted as a regulatory document identifies **plant code 356** as **AES Redondo Beach LLC** (utility ID 22484) and lists generator IDs **5, 6, 7, 8**, including exactly the three 2024 EIA-923 unmatched keys 5/6/8. Source: [EPA regulatory attachment, 2021 EIA-860 Schedule 6A](https://downloads.regulations.gov/EPA-R06-OAR-2025-0197-0061/attachment_16.pdf).

This resolves a historical *plant and generator identification lead*, but **does not resolve 2024 operating/retirement status**, why the three identifiers are absent from the examined 2024 EIA-860 generator workbook, or 2024 EIA-923 reporting interpretation. Do not relabel them as 2024 operable or as zero generation. Investigate the official 2021–2023 EIA-860 status snapshots and 2024 EIA-923 reporting months before excluding or aliasing any measurements.

**Status accounting:** 7 exact keys found in the 2024 Retired and Canceled worksheet; 3 remaining keys have a historical 2021 official-form identification lead, with 2024 classification unresolved. Full BA historical calibration remains **NOT CERTIFIED**.


## Historical retirement evidence for AES Redondo Beach (plant 356)

**Source confirmation beyond the 2024 EIA-860 workbook:** The [AES 2023 Form 10-K](https://www.sec.gov/Archives/edgar/data/874761/000087476124000011/aes-20231231.htm) states that remaining AES Redondo Beach once-through-cooling generating units were permanently retired effective **January 1, 2024**. The [CAISO 2023–2024 transmission-plan appendix](https://www.caiso.com/documents/appendix-a-board-approved-2023-2024-transmission-plan.pdf) separately identifies Redondo Beach units **5, 6 and 8** with end-2023 retirement/compliance timing. This supports a retired-by-2024 explanation of all three unmatched EIA-923 source identifiers, without inventing a generator alias.

**Crucial limitation:** The [EIA-860 annual data documentation](https://www.eia.gov/electricity/data/eia860/) warns that the Retired and Canceled tab is not a comprehensive historical-retirement register. These statements explain why absence from the 2024 annual workbook is compatible with retirement, **but do not independently establish how reported EIA-923 2024 monthly entries for the same IDs should be interpreted**. Before model-observation reconciliation, inspect the three 2024 EIA-923 month-level rows, signed MWh, any reporting adjustments, and 2023 final or EIA-860M status records. Do not auto-convert a missing identity into zero observed energy.

**Assessment:** Generator identity is historically corroborated and a contemporaneous corporate retirement effective date is supported; the remaining issue is reconciling 2024 EIA-923 reporting with retirement and documenting the chosen treatment. Historical grid-model calibration is still **not certified**.


## 2024 EIA-923 month-level reconciliation for plant 356 (artifact-verified)

Inspected the actual `eia923_generator_month_net_mwh.csv` from [official EIA-923 workflow run 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401), artifact `13065659112`. There are precisely **three** 2024 Page-4 extracted records at plant ID 356:

| Plant ID | Generator ID | Prime mover | Reported BA | Reporting month | Net generation (MWh) |
|---|---|---|---|---|---:|
| 356 | 5 | ST | CISO | 2024-01 | 0.0 |
| 356 | 6 | ST | CISO | 2024-01 | 0.0 |
| 356 | 8 | ST | CISO | 2024-01 | 0.0 |

No February–December rows for these generators occur **in the extracted Page-4 source**. Absence in an extracted source must not be translated into 11 months of observed zero generation. This narrow observation is consistent with the AES 2024-01-01 retirement statement and CAISO unit list. It does not imply all 2024 2024 plant output is independently certified, nor resolve full-BA source coverage.

**Revised status:** The three 2024 unmatched identities now have a coherent historical retirement explanation *and* a checked January 2024 zero-generation source entry. Retain the measured January zero rows with a retired-source flag, and exclude these retired IDs from 2024 operable nameplate supply; do not silently discard or auto-impute missing later-month records. The 7 earlier RE rows may carry different month/energy behavior and still require separate reconciliation.


## 2024 EIA-923 observed generation among seven RE-sheet generator identities

**Source:** actual `eia923_generator_month_net_mwh.csv` from successful [EIA-923 intake run 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401), artifact `13065659112`. The seven IDs were confirmed in the 2024 EIA-860 Retired and Canceled sheet by [run 41395106441](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41395106441). Source CSV was filtered by **exact plant ID and generator ID**, retaining original period and signed MWh.

| Reported BA | Plant / generator | 2024 reported months | Nonzero months | Reported 2024 net MWh |
|---|---|---:|---:|---:|
| BPAT | 58109 / TG1 | 12 | 0 | 0 |
| CISO | 10446 / GEN1 | 11 (Jan–Nov) | 0 | 0 |
| CISO | 10661 / GEN4 | 1 (Dec) | 1 | 10,252 |
| CISO | 50632 / GEN1 | 12 | 12 | 61,886 |
| CISO | 50837 / GEN1 | 5 (Jan–May) | 3 | 10,476 |
| CISO | 54626 / TG01 | 12 | 9 | 179,693 |
| CISO | 60100 / G-1 | 12 | 0 | 0 |
| **Total** | **7 exact IDs** | **65 reported month rows** | **25 nonzero month rows** | **262,307** |

Together with plant 356 units 5/6/8, the unmatched Page-4 set comprises 68 generator-month observations; the plant-356 entries each appear once in January at observed 0 MWh. The sum of unmatched 2024 EIA-923 generation remains **262,307 MWh**, originating from four RE-sheet generator IDs. This energy is measured under the source reporting conventions, but the precise retirement dates and whether retroactive adjustments contributed to individual entries have **not** been independently reviewed.

**Modeling gate:** Preserve all measured generation values in an *observational reconciliation ledger*, with RE-sheet identity and source vintage flags. Do **not** add these generators into 2024 operable nameplate availability merely because reported generation is nonzero; equally, do **not** remove their measured MWh from an observed-energy reconciliation silently. Resolve retirement-effective dates, operation windows and EIA revision semantics before declaring a final 2024 active fleet and BA completeness.

**Historical calibration certified: NO.** This audit does not imply that a full-month or held-out-year PyPSA dispatch comparison has been completed.
