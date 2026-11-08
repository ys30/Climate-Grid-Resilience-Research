# Paper C — July 2024 reciprocal bilateral EIA-930 reporting differences: temporal and source-partition audit

## Verified engineering and source lineage

- [Authenticated 41-pair, 6,888 pair-hour directed original EIA-930 audit, CI 42447683798](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447683798).
- [New six-pair temporal breakdown, five tests, manuscript figure and reporting-specific checks: SUCCESS, CI 42449384398](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42449384398).
- [Download reproducible PNG, PDF, six-pair summary, seven-day hourly source cohort, daily metrics, UTC-hour means, Jan–Jun/Jul–Dec source-partition table, and scope JSON (artifact 13604443280)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42449384398/artifacts/13604443280).

Comparison window: July 1–7, 2024 **UTC**. EIA original `INTERCHANGE` source end-hour timestamps converted to UTC start-hour. For every unordered BA pair, the descriptive reporting-identity residual is `R(t) = reported interchange A-to-B + reported interchange B-to-A`. It is computed only if both directional data values are present and finite. Hourly observations are not treated as independent random samples; sums, directional counts and diurnal profiles are descriptive, not inferential statistics.

The raw original source has 41 distinct pair groups across 6,888 pair-hour keys. To identify diagnostically useful structure without a sprawling graphic, this table uses six **preidentified high-deviation or negative-control pairs** and gates the identical original 168-hour calendar for every one. They have 7 UTC hours represented in the Jan–Jun source archive and 161 UTC hours from Jul–Dec; that partition is traceability metadata, not evidence that a systematic level shift occurred exactly at the archive boundary.

## CI-verified six-pair results

| BA pair | Positive residual hours (>1 MW) | Negative residual hours (<−1 MW) | Within ±1 MW | Signed week mismatch (MWh) | Sum absolute weekly mismatch (MWh) |
|---|---:|---:|---:|---:|---:|
| BPAT–GRID | 168 | 0 | 0 | **+129,398** | **129,398** |
| BPAT–SCL | 168 | 0 | 0 | **+90,046** | **90,046** |
| AZPS–CISO | 100 | 68 | 0 | **+31,004** | **49,080** |
| AZPS–SRP | 0 | 168 | 0 | **−37,195** | **37,195** |
| CISO–SRP | 22 | 104 | 42 | **−45,738** | **45,896** |
| BPAT–CISO | 0 | 0 | 168 | **0** | **0** |

All 168 hours for each of these six selected pairs have both numeric directions available. Direction counts use strict ±1 MW threshold, so plus/minus/within-tolerance counts sum to 168. The BPAT–CISO pair is a useful **source reporting negative-control**, entirely reciprocal, while multiple neighboring pairs are not. These results point to persistent signed pair-specific reporting asymmetry for BPAT–GRID, BPAT–SCL and AZPS–SRP, with **mixed directional reporting mismatch** for AZPS–CISO; they do not identify its operational or administrative mechanism.

### Separation from BA-wide accounting anomalies

- BPAT's own original reported **BA Total Interchange** agrees almost exactly with the sum of its reporting counterparties (4 MWh summed absolute difference over the seven-day cohort). Yet multiple individual reciprocal pair reports disagree; BPAT's earlier **−741,860 MWh** original BA generation−demand−interchange bookkeeping residual remains unexplained. Sum-of-own-reports and reciprocity across *two reporting entities* are different audit targets.
- CISO's original BA Total Interchange is missing for 144 hours; bilateral records exist but **shadow** accounting closes only 17/144 of those hours. Pairwise reciprocity does not restore missing original total interchange or validate grid deliverability.

### Figure design and caveat

The new reproducible two-panel supplemental figure (PDF/PNG) shows:
1. Absolute reported reciprocal mismatch accumulated over 168 complete paired hours by selected BA pair.
2. Daily sums of absolute mismatch for five interesting source pairs (the fully reciprocal BPAT–CISO negative-control is retained in the CSV and upper comparison panel).

All plotted differences are sums/curves of **reported data inconsistency**, not observed energy that was physically lost or underdelivered. In particular, never substitute any of these MWh values for a PyPSA link rating, station loss, grid blackout or measured expected unserved energy.

### Additional gates for a physically interpretable model

1. Check the original official EIA-930 directional reporting definition, specific pseudo-tie/dynamic-scheduling arrangements and source-version history for the highest-persistence asymmetries.
2. Reconcile full BA generation and area interchange with reporting entity boundaries, retaining original-versus-adjusted and absent values.
3. Locate defensible time-varying available generation and verified transfer limits from independent operational data before converting the climate stress screening model into a physical adequacy or resilience estimate.

**Scientific status:** This enhances independent source lineage, data-quality evaluation and transparent limitations. The study still cannot identify actual historical EENS, unserved load, or the true system reliability value of hypothetical storage.
