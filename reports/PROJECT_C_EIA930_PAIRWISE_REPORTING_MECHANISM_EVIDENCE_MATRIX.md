# Paper C — EIA-930 official reporting mechanisms versus observed July 2024 bilateral asymmetries

## Audit status and source basis

This is a **documentary mechanism-evidence gate**, not another model simulation. It joins the official EIA data-element definitions to previously CI-verified **original** bilateral reporting observations. No actual cause for a named BA pair is claimed without independent primary-source evidence.

- [EIA: About the EIA-930 data, including Data Relationships, Pseudo-ties and Dynamic Scheduling, Data Quality, and Interchange](https://www.eia.gov/electricity/930-content/about.html), accessed 2026-11-08.
- [Source-verified 41 BA-pair reciprocity: CI 42447683798](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447683798).
- [Source-verified hour-of-day and daily decomposition: CI 42449384398](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42449384398).
- [CISO shadow arithmetic and BPAT BA-wide accounting: CI 42447308854](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447308854).

## Verifiable reporting rules from EIA

1. **EIA interchange sign:** Positive interchange is net outflow from the reporting BA; negative is net inflow. Directly interconnected BA pairs should report approximately equal-magnitude and opposite-sign values. A non-zero `TI(A→B) + TI(B→A)` is a reporting discrepancy, **not a physical line loss**.
2. **Measurement and cadence:** Hourly BA data are reported as integrated one-hour averages with an *hour-ending* timestamp. EIA collects BA Total Interchange approximately a day after the operating period; bilateral partner interchange is obtained later to take advantage of an interchange check-out process. Earlier raw and later partner-report values can therefore have different revision and reconciliation status. This is a **possible general explanation**, not proven for any pair here.
3. **Physical boundary vs commercial scheduling:** EIA requests metered physical generation, tie-line interchange and physically bounded demand, excluding pseudo-ties and dynamic schedules where practical. EIA explicitly warns that some respondents cannot exclude those arrangements and that accounting for pseudo-tied/dynamically scheduled resources can cause reported differences.
4. **Data-quality scope:** Original individual-BA hourly data are published as reported; EIA applies some quality controls to aggregated products. Unmatched, absent or revised original BA values must not be filled as zero or silently replaced.
5. **Not a capacity definition:** Reported interchange (MW averaged over an hour) is an observed/scheduled accounting flow and is not a thermal transmission rating, available transfer capability, N-1 secure capacity or deliverable network maximum.

## Pair-specific observations and mechanism-admission status

All six selected pairs have 168/168 original *two-direction numerical* hours in July 1–7, 2024 UTC. Pairwise difference is the signed sum of the two BA-directed values; counts use ±1 MW tolerance.

| Pair | Signed 168h sum (MWh) | Positive / negative / near-zero hours | Confirmed in this project | Official mechanisms possibly relevant | Pair-specific mechanism verified? |
|---|---:|---|---|---|---|
| BPAT–GRID | +129,398 | 168 / 0 / 0 | Sustained positive reported mismatch | Checkout vintage, BA operational boundary, dynamic schedule/pseudo-tie, meter corrections | **No** |
| BPAT–SCL | +90,046 | 168 / 0 / 0 | Sustained positive reported mismatch | Same generic EIA-recognized mechanisms | **No** |
| AZPS–SRP | −37,195 | 0 / 168 / 0 | Sustained negative reported mismatch | Same generic EIA-recognized mechanisms | **No** |
| AZPS–CISO | +31,004 | 100 / 68 / 0 | Difference changes signed direction | Same mechanisms; no basis to attribute switching to a specific cause | **No** |
| CISO–SRP | −45,738 | 22 / 104 / 42 | Mostly negative or within tolerance | Same mechanisms | **No** |
| BPAT–CISO | 0 | 0 / 0 / 168 | Reciprocal reporting for all 168 hours | Source-reporting negative control | Not needed |

**Important:** A persistent one-sided pair discrepancy **does not identify which BA report is incorrect** or which accounting mechanism drives it. No physical cause or statistical event dependence can be inferred from the signs alone.

## Relationship to BA total imbalance

BPAT's own original hourly bilateral sums match its reported BA Total Interchange closely (4 MWh absolute over seven days), yet raw BA generation minus demand minus Total Interchange sums to −741,860 MWh. These audit identities ask different questions: bilateral aggregation, inter-BA report reciprocity and whole-BA accounting. One identity passing does not validate the others.

CISO has 144 missing original and adjusted BA Total Interchange hours. Individual directed counterparty reports exist but substituting their sum *only as a separately labeled shadow diagnostic* closes 17 of the 144 missing-total hours; 127 do not close. EIA's documented checkout cadence and boundary/accounting complications justify further investigation, but do not constitute proof of a cause or license to replace missing raw columns.

## Manuscript-ready interpretation

> The original EIA-930 directed interchange records exhibit spatially heterogeneous reporting reciprocity. Several pairs display persistent signed imbalances over a seven-day interval, whereas BPAT–CISO is reciprocal in all recorded hours. These are source-reporting discrepancies, not measured transmission losses. EIA identifies reporting checkout, dynamic scheduling and pseudo-tie accounting as known sources of such inconsistencies, but this analysis does not resolve a specific mechanism for any BA pair. Consequently, inferred physical link ratings and observed system inadequacy are not identifiable from the interchange records used here.

## Evidence required before specific causal attribution

1. Obtain an **official BA-specific reporting explanation**, vintage, correction log or documented interchange agreement for BPAT–GRID, BPAT–SCL, AZPS–SRP and AZPS–CISO.
2. Reconcile both directions using the *same hour-start convention and dated data vintage*. Identify any known pseudo-ties/dynamic schedules from source documents, not assumptions.
3. If independent source records cannot identify the mechanism, retain this as an **unresolved measurement/BA accounting uncertainty**.
4. For a physical grid-model claim, independently obtain generator and tie-line available MW, transmission topology/thermal limits, confirmed import/export deliverability and reliable adequacy outcomes. Do not use reported hourly MW or mismatch MWh directly as PyPSA line ratings.

This report supports **Supplementary Methods / source validation / limitations**. It must not be described as independent validation of historic climate-induced blackouts, EENS, or the true resilience value of hypothetical pumped storage.
