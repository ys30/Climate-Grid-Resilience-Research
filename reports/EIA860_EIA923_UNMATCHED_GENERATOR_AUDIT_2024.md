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
