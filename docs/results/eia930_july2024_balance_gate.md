# July 2024 EIA-930 observed generation / demand / interchange balance gate

Source: four-BA observed EIA-930 NG, D, TI for 168 UTC hours, and simulated storage charging. CI verified: [run 41287330742](../../actions/runs/41287330742).

## Two alternative sign interpretations

Hourly bookkeeping diagnostic: R_minus = NG − D − TI; R_plus = NG − D + TI. A nonclosing hour has absolute residual greater than max(1 MW, 1% of demand). This is **not** a proof that the reported series have an identical balancing boundary.

| BA | R_minus nonclosing hours | R_plus nonclosing hours | R_minus signed weekly residual MWh | R_minus sum of absolute hourly residuals MWh |
|---|---:|---:|---:|---:|
| AZPS | 0 / 168 | 168 / 168 | 0 | 0 |
| BPAT | 168 / 168 | 168 / 168 | −742,788 | 742,788 |
| CISO | 146 / 168 | 164 / 168 | −3,354 | 187,050 |
| SRP | 0 / 168 | 168 / 168 | −2 | 2 |

**Interpretation:** R_minus is numerically more consistent for AZPS/SRP and has the smaller absolute residual for all four BAs. It is not reasonable to switch TI signs per BA merely to minimize residuals. The larger BPAT mismatch cannot be remedied by either global sign convention; CISO's modest *signed* weekly residual hides substantial positive/negative hourly disagreement.

## Data and claims gate

- AZPS, SRP: this narrow hourly accounting diagnostic closes to within the specified threshold, **not** a comprehensive historical generation or storage calibration.
- BPAT: **NOT PASSED** hourly accounting gate; 168/168 hours nonclosing. Do not describe its simulated storage relief as historically validated.
- CISO: **NOT PASSED** hourly accounting gate; 146/168 hours nonclosing. Do not treat its very large simulated storage relief as historically demonstrated.
- Under compound heat+wind the model charged CISO storage approximately 191,986 MWh; 49 simulated charging hours overlapped historical R_minus nonclosure. Such overlaps flag a representativeness concern but do not measure true battery charge availability.
- Investigate adjusted-vs-raw demand, BA boundaries, net generation reporting and interchange revisions before calibration. Reconcile the underlying hourly series, with documented provenance and no silent imputation.

No observed outage or battery charging benefit is established by this screening model.

## Residual structure: fixed offset versus hourly variation

[Verified EIA-930 residual decomposition CI](../../actions/runs/41288200906), 168 observed hours. No offset is applied to source or optimization data.

| BA | Median residual MW | Standard deviation MW | Range MW | Sum absolute raw residual MWh | Sum absolute residual after *diagnostic* median subtraction MWh | Still nonclosing hours after subtraction |
|---|---:|---:|---|---:|---:|---:|
| AZPS | 0 | 0 | 0 to 0 | 0 | 0 | 0 / 168 |
| BPAT | −4,311.5 | 742.4 | −6,122 to −3,187 | 742,788 | 103,116 | 156 / 168 |
| CISO | −1.5 | 1,301.8 | −2,766 to +2,756 | 187,050 | 187,050 | 146 / 168 |
| SRP | 0 | 0.11 | −1 to 0 | 2 | 2 | 0 / 168 |

**BPAT:** the mismatch has a large persistent negative component, but median subtraction still leaves extensive hourly nonclosure. Its source requires BA boundary, reporting scope, adjustments and generation/interchange accounting review; do not treat the apparent offset as an independently verified correction.

**CISO:** the weekly signed residual nearly cancels, while the large hourly positive/negative changes remain. A fixed offset does not explain this behavior. Review time-specific adjusted vs raw observations and balancing adjustments rather than simply rescaling generation or demand.

**Fail-closed interpretation:** Neither BPAT nor CISO passes the hourly historical balance gate. Modelled battery benefit remains a screening counterfactual, not actual avoided unserved load.

## Official July 2024 full-month H1/H2 CSV reconciliation

[Verified CI run 41321070691](../../actions/runs/41321070691) assembled 744 unique UTC hourly source rows per BA from official H1/H2 CSVs without imputing values. The first seven July UTC hours were in the H1 CSV.

| BA | Source rows | Valid raw D/NG/TI hours | Missing TI hours | Absolute residual MWh (valid hours only) |
|---|---:|---:|---:|---:|
| AZPS | 744 | 744 | 0 | 0 |
| BPAT | 744 | 744 | 0 | 3,470,215 |
| CISO | 744 | 233 | 511 | 236,522 |
| SRP | 744 | 744 | 0 | 10 |

Raw and adjusted totals were identical in this audit. Source-row coverage is **not** field completeness. CISO has 511 empty interchange observations; its 236,522 MWh absolute residual only covers 233 evaluable hours, not the entire month. BPAT still has severe nonclosure with all 744 hours present. These are arithmetic diagnostics, not historical calibration.

**Gate:** Calendar rows complete for all four BAs. Full D/NG/TI field coverage for AZPS, BPAT, SRP only. Balance closure near reporting precision for AZPS/SRP only. BPAT does not close; CISO cannot be certified for the whole month, and the partial month is materially nonclosing. Historical calibration is **not certified** for any BA. Investigate CISO reporting gaps and BPAT BA accounting scope before making historical reliability claims.
