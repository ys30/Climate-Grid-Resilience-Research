# Paper C — EIA-930 July 2024 directed bilateral reciprocity audit (CI verified)

**Successful run:** [GitHub Actions 42447683798](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447683798). Five tests passed. [Download 6,888 pair-hour rows, 41-pair source audit, archive SHA256 and scope artifact 13604900043](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42447683798/artifacts/13604900043). [Code](../src/grid_resilience/paperc_eia930_2024_reciprocity.py).

## Definition and source limitations

The [official EIA-930 methodology](https://www.eia.gov/electricity/930-content/about.html) states that positive interchange means net outflow, negative means inflow, and adjacent BA reports should be opposites. It also notes reciprocal inconsistency caused by reporting revisions, dynamic scheduling, pseudo-ties, and differing system definitions. We therefore check the sum of both directional values for each BA pair and hour, **only when both values are reported**. Absolute sums are an exchange-reporting consistency measure, **not physical energy losses, line thermal ratings, outages or EENS**.

The original 2024 Jan–Jun and Jul–Dec EIA-930 INTERCHANGE source files were retrieved independently and timestamped to the beginning of UTC hours for July 1–7, 2024. We inspected all named source counterparties of AZPS, BPAT, CISO and SRP, including partners outside the four study BAs. The source contains **13,440 directed rows** in the target date window, corresponding to **6,888 unique unordered pair-hour keys across 41 unordered BA pairs**. Some pair-hour records lack the reverse-direction source or a numeric reverse-direction value. These are missing, never assigned zero.

## CI-confirmed pairwise results

| Directed reporting pair | Both numeric directions (hours) | Opposite within 1 MW (hours) | Sum of absolute signed-pair discrepancies, MWh | Maximum difference, MW |
|---|---:|---:|---:|---:|
| BPAT / CISO | 168 | 168 | 0 | 0 |
| AZPS / CISO | 168 | 0 | 49,080 | 726 |
| AZPS / SRP | 168 | 0 | 37,195 | 337 |
| CISO / SRP | 168 | 42 | 45,896 | 669 |
| BPAT / GRID | 168 | 0 | 129,398 | 1,199 |
| BPAT / SCL | 168 | 0 | 90,046 | 877 |
| CISO / TIDC | 168 | 1 | 61,382 | 805 |
| AZPS / PACE | 168 | 168 | 0 | 0 |
| BPAT / BANC | 168 | 168 | 0 | 0 |

At AZPS / LDWP, BPAT / BCHA, BPAT / LDWP and CISO / CEN the sample contains 168 pair-hour keys but **zero complete reciprocal numeric pairs**. This reflects absent counterpart reporting in this source view and is **not** proof of zero flows.

Source causes for individual pair discrepancies have **not** been identified; possibilities named in EIA methodological guidance should not be asserted as established explanations for any particular pair.

## Why this matters for BPAT and CISO

The earlier [bilateral-versus-BA-total audit](PROJECT_C_EIA930_JULY2024_BILATERAL_CISO_SHADOW_AND_BPAT_SOURCE_CI_VERIFIED.md) showed BPAT's own bilateral sources aggregate to its BA total interchange to within **4 MWh sum absolute discrepancy** over 168 hours. This **does not** imply neighboring BAs report exact reverse flows: BPAT / GRID and BPAT / SCL alone show substantial pairwise disagreements. The BPAT BA accounting identity remains nonclosing and its **−741,860 MWh weekly signed residual has not been explained**.

CISO has 144 missing BA Total Interchange hours, yet bilateral counterpart records for those hours; the separately labeled shadow accounting closed **only 17/144**. The reciprocal **BPAT / CISO** pair is consistent in all hours, whereas **AZPS / CISO** and **CISO / SRP** are not. No original total-interchange null is filled.

## Further scientific gates

1. Quantify pairwise disagreement in hourly time plots and separate its sign/size by the source archive partition; no causal mechanisms without corroborating reporting agreements.
2. Review the EIA-930 reporting boundary, pseudo-tie and dynamically scheduled generation guidance for the specific counterparties. The official data explicitly may not form a complete physical snapshot.
3. Compare the source-provenance annual vintage and counterparty roster, and preserve raw-versus-adjusted-versus-imputed distinctions.
4. Obtain independently verified transmission limits and generator operating state before interpreting the PyPSA model as physical adequacy. Directional reported tie-line interchange is **not** a certified available transfer limit.

This report supports Paper C's source-quality and uncertainty sections, not observed outage or calibrated EENS claims.
