# Paper C — EIA-930 July 2024 full original 16-fuel reporting coverage (161-hour modern schema)

## Original source and CI

[CI #42716078830 — SUCCESS](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42716078830), four source-scope regression tests plus the real archived EIA-930 source-panel join. [Download original 16-category × four-BA completeness, 644 BA-hour records, four-BA summary and manifest (artifact 13718545889)](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42716078830/artifacts/13718545889). [Code](../src/grid_resilience/paperc_2024_full_fuel_schema_audit.py).

The source window is strictly 2024 July 1 07:00 UTC to July 8 00:00 UTC (161 BA-hours), all from **EIA-930 2024 Jul–Dec**. The original first seven UTC hours fall in the Jan–Jun archive and differ in taxonomy, so they are not interpolated or patched. The code joins the independently CI-verified [original six-fuel BA-hour comparison](PROJECT_C_2024_161H_ORIGINAL_SIX_FUEL_ACCOUNTING_SCOPE_CI_VERIFIED.md) on identical BA and UTC-hour keys.

### All 16 original source categories — completeness

Each BA has 161 × 16 = **2,576** original category cells:

| BA | Numeric fuel-category cells | Blank original category cells | BA hours with all 16 labels numeric | Complete six-label hours |
|---|---:|---:|---:|---:|
| AZPS | 1,288 | 1,288 | **0 / 161** | 161 |
| BPAT | 1,127 | 1,449 | **0 / 161** | 0 |
| CISO | 1,288 | 1,288 | **0 / 161** | 161 |
| SRP | 1,127 | 1,449 | **0 / 161** | 161 |

**Every BA has source fuel-category blanks in every one of the 161 hours**. Consequently a full source-categorized net-generation total cannot be admitted at any hour without making an unsupported blank=zero assumption. This is a *reporting-completeness and source schema finding*, not proof of actual fuel production being absent or surplus.

### Additional original-category arithmetic clues (not established physical causes)

The prior original six-category results showed BA-net minus selected six fuel reports of **+14,487 MWh (AZPS)**, **−25,937 MWh (CISO)**, and **−3,986 MWh (SRP)**, on the identical 161-hour partition. The 16-label audit adds the following independently source-numeric 161-hour totals:

| BA | Original `Other Fuel Sources` (MWh) | `All Petroleum Products` (MWh) | Comparison with six-component difference |
|---|---:|---:|---|
| AZPS | **+14,487** | **0** | Other Fuel Sources equals the six-component residual numerically |
| BPAT | **+23,835** | **blank all 161h** | Six-component comparison inadmissible because Coal blank |
| CISO | **−36,109** | **+10,183** | These sum to −25,926 MWh; the six-component residual is −25,937 MWh, a difference of **−11 MWh** |
| SRP | **−3,986** | **blank all 161h** | Other Fuel Sources equals the six-component residual numerically |

These are *exact signed reported category totals*, not inferred fuel quantities. For AZPS and SRP, the numerical equality is consistent with a straightforward arithmetic reconciliation of the **selected source components** once `Other Fuel Sources` is included. For CISO, the original source's signed reported Other Fuel + Petroleum values leave an **11 MWh** difference from the selected-six residual; absent evidence, this cannot be attributed to any specific mechanism, rounding convention, source revision or physical delivery.

**Do not conclude full fuel accounting closes in any BA.** Other labels (Battery Storage, Pumped Storage, etc.) are blank throughout; their absent reported values do not equal physical zero. The presence of signed negative `Other Fuel Sources` totals shows source reports need not represent a simple nonnegative gross generation partition. Different EIA definitions, adjustments, storage and accounting rules can matter, but a BA-specific cause has not been established from this audit.

### Implications for historical PyPSA baseline

This result improves the empirical diagnosis of six-category versus BA-net arithmetic, but **does not admit** historical CISO/SRP/AZPS/BPAT generation technology completeness, technical resource availability, storage SOC/MWh, hydro reservoir constraints, physical intertie ratings, real-world shortages or EENS. The [four BA historical source admission](PROJECT_C_2024_FOUR_BA_HISTORICAL_BASELINE_ADMISSION_CI_VERIFIED.md) remains closed.

Recommended manuscript placement: **Supplementary data source accounting and modern taxonomy completeness**. The valid main-text takeaway is that apparently simple source-generation residuals can be explained in part, or even exactly matched numerically, by the original source's signed reporting categories, but full original-source accounting remains non-identifiable because entire categories lack reported values.

Next research gate: produce a **source-constrained, hour-by-hour seven-/eight-category arithmetic reconciliation** with strict no-imputation flags (including CISO petroleum where numeric) and report the remaining signed arithmetic difference explicitly as a reporting diagnostic rather than inferred missing power. Compare any attempted source reconciliation against official EIA-930 category definitions before making a physical attribution.
