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
