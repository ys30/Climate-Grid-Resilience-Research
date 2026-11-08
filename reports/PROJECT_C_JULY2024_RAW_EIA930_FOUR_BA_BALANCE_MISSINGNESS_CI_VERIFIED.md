# Paper C — July 2024 four-BA original EIA-930 raw hourly electricity accounting: reproducible source-partition gate

## Run, raw inputs and denominator provenance

**Successfully re-executed** [CI run 42446010127](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42446010127), including five source-contract regression tests and [hourly CSV, four-BA summary, manifest and raw source SHA256 artifact 13603567519](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42446010127/artifacts/13603567519). Source: official original `EIA930_BALANCE_2024_Jan_Jun.csv` and `EIA930_BALANCE_2024_Jul_Dec.csv`, retrieved independently, with 7 plus 161 **UTC hour-start** records per BA for July 1–7. Demand, net generation and total interchange are the **raw**, not adjusted/imputed, fields.

For each independently source-present hour with all three raw fields present, define a bookkeeping diagnostic:
```
R = raw net generation - raw demand - raw total interchange
arithmetic closure = abs(R) <= max(1 MW, 0.01 * abs(raw demand))
```
The sign convention and reporting boundaries **are not proof of transmission physics**, historical adequacy or a calibrated power-system model. Missing interchange is **never** interpreted as zero. Net imports or exports under EIA reporting conventions should not be reinterpreted as a shortfall.

## Original-source-confirmed weekly results

| BA | BA source rows | Full raw D/NG/TI triplets | Triplet hours passing arithmetic closure | Triplet hours failing | Raw TI field missing | Signed residual, evaluated triplets (MWh) | Sum absolute residual, evaluated triplets (MWh) |
|---|---:|---:|---:|---:|---:|---:|---:|
| AZPS | 168 | 168 | 168 | 0 | 0 | 0 | 0 |
| BPAT | 168 | 168 | 0 | 168 | 0 | **−741,860** | **741,860** |
| CISO | 168 | **24** | **5** | **19** | **144** | **+773** | **25,673** |
| SRP | 168 | 168 | 168 | 0 | 0 | −2 | 2 |

**The closure denominator is the number of complete raw D/NG/TI triplets, not necessarily the number of source BA-hour rows.** For CISO, raw interchange is missing on 144/168 hours: treating them as 144 non-closing arithmetic observations would be incorrect. BPAT has no raw field missingness but substantial nonclosure (maximum absolute hourly residual 6,122 MW). AZPS/SRP close to reporting precision on every hour, but this is a narrow source-accounting check, **not** physical reliability calibration.

### Revision/version consistency concern with archived earlier claims

The older [July model-context balance report](../docs/results/eia930_july2024_balance_gate.md) gives 168-hour closure counts for CISO and a somewhat different BPAT weekly residual from an earlier analysis/run. The **new two-half original file audit** explicitly checks all 672 official BA-hour rows and separately counts raw TI blanks. It finds only **24 complete CISO raw triplets and 19 failures among them**, and BPAT signed −741,860 MWh versus previously reported −742,788 MWh. These differences must remain visible. Potential causes include original-data revision, raw/adjusted source basis, input snapshot or time filtering. **None of these explanations is currently demonstrated**. The source SHA256 manifest permits further evidence-based reconciliation. Do not silently overwrite historical output or claim that the exact discrepancy mechanism has been resolved.

## Use in the manuscript

This result belongs in **Source and Data Quality**, **Supply–Demand Accounting**, and **Limitations**, not the Results as observed unserved load.

- **Source-admitted for arithmetic inspection:** AZPS and SRP, with reported 168/168 triplets and closure under a stated screening tolerance, but *not* power-system calibration.
- **Source-reported and nonclosing:** BPAT, 168/168 complete triplets with large residual; investigate BA boundaries, interchange reporting and generation data vintage.
- **Source-incomplete:** CISO, missing 144 raw interchange hours and nonclosing on 19 of 24 evaluable hours; require versioned/raw/adjusted interchange and reporting-entity reconciliation before any physical balance narrative.
- **Model remains conditional:** Four-BA PyPSA partial-fleet shortage under hypothetical hazards and links is **not** actual historical EENS, blackouts, observed climate impact, or verified storage benefit.

## Next verification gate

1. Compare **original source hash/date/version and hour-level raw-versus-adjusted TI** for CISO and BPAT with earlier archived balance diagnostics, without filling nulls.
2. Match BA demand/NG/TI to official bilateral interchange records where EIA-930 reporting permits, and check sign conventions and interchange completeness.
3. Keep raw electric-accounting missingness separate from generation technology omissions, capacity/dispatch reconciliation, and true adequacy validation.
