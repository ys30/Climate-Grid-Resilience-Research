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
