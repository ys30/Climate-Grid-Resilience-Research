# SRP 2024-01: generator identity reconciliation and zero-output audit

**Source:** Archived successfully generated GitHub Actions [run 41542019155](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41542019155), artifact 13186838868. Files used: `ba_capacity_identity_review.csv`, `exact_generator_scope_rows.csv` and `exact_generator_scope_summary.csv`.

| Source-scoped quantity | Verified artifact value |
|---|---:|
| Generator identities matched across the review and Page4 source records | 40 |
| Screened generator identities | 37 |
| Excluded reviewed identities | 3 |
| Screened identities with January Page4 monthly net generation **equal to zero** | 3 |
| Excluded identities with January Page4 monthly net generation **equal to zero** | 3 |
| Screened identities with positive Page4 monthly net generation | 34 |
| Screened nameplate capacity | 7,453.1 MW |
| Excluded nameplate capacity | 390.4 MW |
| Screened Page4 source-reported monthly net generation | 2,160,272 MWh |
| Excluded Page4 source-reported monthly net generation | 0 MWh |

**Interpretation:** The 390.4 MW excluded capacity frontier represents a *hypothetical upper bound*, but the three excluded generators are all recorded as producing **0 MWh in this particular Page4 January subset**. This creates no historical evidence that they could have supplied the idealized +390.4 MW per hour scenario. Equally, a zero monthly observation does **not** establish lack of operability, forced outage, resource unavailability, or plant retirement. Some generators included in the inventory also report zero January output. This is a reconciliation of a partial source population, **not a census of all units physically serving the SRP balancing authority**.

A new module, `src/grid_resilience/srp_generator_monthly_identity_audit.py`, validates unique plant+generator identities, eligibility, complete joins, finite values and associated generation records. A new workflow gate runs it after the existing exact-generator audit, generating `outputs/srp_real_screen/srp_generator_monthly_identity_audit.json`. CI success of this new gate is not confirmed yet.

**No observed historical loss of load or fully calibrated BA adequacy result is claimed.**
