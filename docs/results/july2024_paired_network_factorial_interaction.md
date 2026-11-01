# July 2024: network-dependent compound-weather interaction

**Verified:** [paired four-scenario GitHub Actions run 41270337858](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41270337858), success; [research methods CI 41270337863](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41270337863), success.

Two *matched* 168-hour July 2024 four-scenario PyPSA simulations use EIA-930 historical load, ERA5 observed weather inputs and an EIA-860 **partial-fleet thermal/wind proxy**. The sole design contrast is **isolated BA buses** versus **illustrative/hypothetical BA links**. Both use uncalibrated heat demand and wind derating response coefficients. Neither represents observed outages.

Interaction is a modeled second difference, in MWh:
`I = U(heat+wind) - U(heat-only) - U(wind-only) + U(baseline)`.

| BA | Isolated interaction (MWh) | Hypothetical links interaction (MWh) | Linked minus isolated (MWh) |
|---|---:|---:|---:|
| AZPS | 1,174.974837 | 7,013.481419 | +5,838.506583 |
| BPAT | 223.721600 | 15,487.959480 | +15,264.237880 |
| CISO | 14,038.101876 | 805.495769 | −13,232.606107 |
| SRP | 0.000000 | 0.000000 | 0.000000 |
| **SYSTEM** | **15,436.798313** | **23,306.936668** | **+7,870.138355** |

**Interpretation:** BPAT's interaction decreases by approximately **98.56%** when the assumed links are removed. This is evidence of **model-network sensitivity**, NOT evidence for physical BPAT cross-border transfer mechanisms. CISO shows the reverse pattern. The system-wide nonadditivity is also network-sensitive, rising approximately 51.0% relative to isolated.

**Reliability limitations:** illustrative link endpoints and ratings have not been compared to real electric transmission topology or capacity; the supply fleet excludes technology and plant classes; generator weather response and thermal dispatch proxy are not calibrated; no observed outages are available for this contrast. The contrast must not be described as measured grid reliability or proof of a weather×intertie causal effect.

**Next decisive checks:** (1) multiple hypothetical topology/capacity configurations; (2) independently observed wind, heat and generator output response; (3) independent event holdouts; (4) audited generator-to-BA inventory, dispatch and transfer constraints. Report negative and zero contrasts as carefully as positive ones.

**Empirical calibration certified: false. Physical transfer ratings certified: false.**
