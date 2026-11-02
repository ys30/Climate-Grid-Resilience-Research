# EIA-860 × EIA-923: verified 2024 generator identity matching gate

## Reproducible evidence

Actual artifact from successful [official EIA-860 workflow run 41341668303](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41341668303), source commit `7e9493ace5b41e256e73fd3d23c3d970362ee912`, artifact `13097269172`; ZIP SHA-256 `65f6427c784b70082115337c41952c6b5f4c9d33921b6af2cf870debc2241638`.

This report supersedes statements that generator-level EIA-860/923 matching has *not yet been performed*. It has been performed on the **partial EIA-923 Page-4 extraction**, but not certified as a complete BA fleet historical calibration.

## Observed identity-match outcome

| Item | Value |
|---|---:|
| EIA-923 generator-month records considered | 3,392 |
| Matched to EIA-860 generator identities | 3,324 |
| Unmatched generator-month records | 68 |
| Record-weighted match rate | 97.9953% |
| Matched records with multifuel flags | 651 |
| Matched records with secondary energy source | 651 |

These are **record-weighted**, not distinct generators or MW-weighted match fractions; 68 unmatched rows are not equivalent to 68 plants. The 651 multifuel cases cannot be assigned completely to a single fuel merely by prime mover.

## Observational source coverage versus full fleet

- Conservative single-fuel candidate inclusion: 2,419 generator-month records; 973 excluded; candidate net generation 113,835,979.61 MWh. **This is not complete BA electricity generation.**
- Candidate monthly completeness: 84 observed BA/technology/month cells of 96 expected for the selected scope. Seven of eight BA/technology groups have all 12 reporting months; one CISO coal group has no rows. **A complete sequence of 12 months is not full-fleet certification.**
- Full national EIA-860 operable generator inventory: 26,855 positive-nameplate generators and 1,324,741.4 MW across the **nation**, not the four BAs.
- EIA-923-linked partial nameplate capacity: 34,052.1 MW; it is a **subset** and cannot be used as the complete four-BA fleet.
- The workflow explicitly reports that **independent plant-to-BA crosswalk verification is incomplete**, despite source-reported BA attribution and partial candidate calculations.

## Methodological consequences

1. Maintain separate scopes: Page-4 generator-month observations, Page-1 HY/PS plant-month observations, EIA-860 operable generator inventory and source-reported BA fields; do not sum overlapping levels without reconciliation.
2. Investigate 68 unmatched generator-month rows by normalized plant/generator identifiers, source reporting year and status; report both row count and unique generator count.
3. Resolve 651 flagged multifuel observations or exclude them with transparent denominators. Do not infer hourly availability from monthly energy totals.
4. Audit BA fleet completeness against official plant-level year-vintage BA attribution and generator status dates; distinguish national inventory from BA fleet.
5. Historical calibration requires an actual **full-month modeled generation** series and a non-overlapping temporal holdout. The 2024-only source cannot create a 2019–2023 training series or valid multi-year held-out evaluation by itself.
6. Keep EIA-923 measured generation, EIA-930 observed BA flows/demand and modeled shortfall separate, and retain `historical_calibration_certified: false`.

## Research status

Generator **identity matching on partial Page-4 records: completed and artifact-verified**. Complete-fleet four-BA mapping: **not certified**. HY/PS full-fleet reconciliation: **not certified**. Observed-versus-modeled monthly calibration and independent-year predictive validation: **not performed**.
