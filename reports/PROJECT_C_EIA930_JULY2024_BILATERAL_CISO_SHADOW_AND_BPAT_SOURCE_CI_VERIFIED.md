# Paper C — July 2024 original EIA-930 bilateral interchange source reconciliation and CISO shadow accounting

## CI-verified original-source lineage

- [Official Jan–Jun plus Jul–Dec BALANCE and INTERCHANGE source CI 42447109422](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447109422), passing five source-accounting tests, with [source SHA256 and 672-hour bilateral versus total interchange artifact 13604042646](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447109422/artifacts/13604042646).
- [Independent shadow-only missing-Total-Interchange arithmetic CI 42447308854](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447308854), passing five tests, with [hour-aligned original-source-preserving 672h shadow residual and BA summary artifact 13604485341](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447308854/artifacts/13604485341).
- Earlier [raw vs adjusted EIA-930 July 2024 BA accounting CI 42446170248](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42446170248) established that CISO missing 144 original BA total-interchange entries are **also missing in the adjusted version**. The independent [raw D−G−TI source accounting run 42446010127](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42446010127) independently recovers 168 BA-hours × 4.

All timestamp joins use **UTC start of hour** after subtracting one hour from official EIA-930 end-hour records. Calendar cohort: **July 1–7, 2024 inclusive**, four BAs, 168 hours per BA. Old/new half-year archives are separate and original source SHA256 values are preserved.

## Official reported bilateral totals versus BA reported total interchange

| BA | BA Total Interchange reported hours | Bilateral BA-hour records available | BA-hour direct comparisons | Sum of absolute direct bilateral minus total differences (MWh) | Total missing, bilateral source available |
|---|---:|---:|---:|---:|---:|
| AZPS | 168 | 168 | 168 | 0 | 0 |
| BPAT | 168 | 168 | 168 | **4** | 0 |
| CISO | **24** | 168 | **24** | **0** | **144** |
| SRP | 168 | 168 | 168 | 0 | 0 |

The bilateral source contains numerically present counterparty rows at all 168 hours for each BA. This **does not certify the complete universe of physical counterparties or independent line-flow meters**. The CISO 144 missing BA *Total Interchange* values must remain **null** in official original-balance data. The bilateral sum is a **candidate diagnostic only**, never a silently imputed replacement. BPAT direct hourly bilateral-versus-total differences total just **4 MWh absolute** (two hours exceed the strict ≤1 MW equality test); thus simple bilateral summation disagreement is far too small to explain its −741,860 MWh original BA generation−demand−interchange bookkeeping residual. This does not identify its real cause.

## Key negative result: CISO bilateral candidate does NOT restore 144h balance closure

For the **144 hours where CISO BA-reported raw Total Interchange is missing**, the source-preserving shadow calculation uses

`shadow_R = original Net Generation − original Demand − sum of original directed bilateral Interchange`.

The results, **not inserted into the raw BA source columns**, are:

| Candidate metric for only the 144 missing-original-total hours | Verified value |
|---|---:|
| Missing original Total Interchange hours with bilateral sum | **144** |
| Shadow arithmetic closing hours, threshold max(1 MW, 1% demand) | **17** |
| Shadow arithmetic nonclosing hours | **127** |
| Signed shadow residual across those missing-original-total hours | **−5,150 MWh** |
| Sum absolute shadow hourly residual across missing-original-total hours | **160,354 MWh** |

This is a substantive **negative calibration finding**: even though official bilateral reports supply diagnostic estimates for all 144 previously missing CISO BA-total hours and exactly match the BA total on the 24 hours where a total is reported, applying bilateral sums as a separate **shadow** does not make the missing hours' demand−generation−interchange identity close. The **signed residual conceals substantial hour-to-hour positive/negative cancellation**, hence the 160,354 MWh absolute mismatch. No physical losses, blackouts, unserved electricity, or statistically expected EENS should be inferred.

The 24 original CISO reported-total hours independently include **5 closing and 19 nonclosing hours**. Together with the 144 shadow candidate hours (17 closing, 127 nonclosing) there are at most **22/168 hours that close the chosen arithmetic screen under a combined *diagnostic* source scenario**. This is **not a source-complete original reported-total record** or historical adequacy validation.

## Publication-facing interpretation

The apparently large four-BA model energy deficit should **not** be given a historical-reliability interpretation. Current evidence identifies two distinct source issues:
1. **CISO:** original total interchange incomplete; official bilateral candidate observables available but most candidate residuals still fail closure.
2. **BPAT:** original total interchange complete, and bilateral sum nearly identical, yet BA demand/generation/total exchange nonclosure remains severe. Further review should focus on BA reporting boundaries, generation accounting and official vintage / adjusted reporting basis, **not** an invented link-capacity correction.

**Next scientific gate:** source-grounded EIA-930 accounting-definition review and counterparty pairwise reciprocity on the *same reporting direction and hour*, with careful treatment of asymmetric BA territories. Even reciprocal bilateral reporting does **not** constitute a transmission thermal limit or deliverable import capacity. Preserve both prior source hashes, January-versus-July revision histories and any reconciled provenance.

All files identify this as **reported-data bookkeeping and model-scope assessment**, not a historical blackout record, simulated dispatch calibration, generator available capacity or physical intertie rating.
