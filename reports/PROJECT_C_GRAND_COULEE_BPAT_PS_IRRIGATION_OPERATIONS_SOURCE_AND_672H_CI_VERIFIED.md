# Project C — Grand Coulee PS site-identity and competing irrigation service: a source-grounded 672h scenario stress test

**Status: Official physical-facility identity independently corroborated; hypothetical operational-access sensitivity solved and exact-replayed in CI. Not historical hydro dispatch calibration.**

## 1. Verified facility is a multipurpose water project, not generic battery storage

Original **EIA-860 2024** source [CI 42126016886](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42126016886) identified **Plant 6163 = Grand Coulee, BPAT**, with six operable pump-generator **PG7, PG8, PG9, PG10, PG11, PG12**, total positive PS generator nameplate **314 MW**. Individual source nameplates: **50 MW** for PG7/PG8; **53.5 MW** each for PG9–PG12. Original 2024 Energy Storage worksheet had **zero exact plant-generator key matches** for these six PS units; it did **not** independently establish plant-specific usable MWh, actual charge/discharge electrical MW, observed 2024 SOC, measured roundtrip efficiency or month-specific reservoir availability. EIA-860 PS prime-mover generation nameplate is not identical to verified pumping input MW.

The federal plant owner/operator, **U.S. Bureau of Reclamation (USBR)**, identifies these as six reversible pump generators at the **John W. Keys III Pump-Generating Plant** (alongside **six distinct dedicated irrigation pumps**), which lifts water from Roosevelt Lake via feeder canal to **Banks Lake** for irrigation and can reverse part of the pumping fleet for power production. Primary original official source pages:

- https://www.usbr.gov/projects/index.php?id=526 — Grand Coulee Powerplant: six pump-generators PG7–PG12, **irrigation operation** and power load-shifting; approximately 600 MW electrical consumption is stated for **all 12 pumps** as an operational plant-wide swing, **NOT a measured PS-only 314 MW pumping rating**.
- https://www.usbr.gov/pn/grandcoulee/cbp/johnkeys/index.html — John W. Keys III official site, six reversible units and irrigation of >670,000 acres.
- https://www.usbr.gov/projects/index.php?id=438 — Columbia Basin Project multipurpose irrigation, flood, fish and power context; 12 units, six dedicated pumps and six pump/generators; other competing water service obligations.
- https://www.usbr.gov/projects/index.php?id=228 — Banks Lake reservoir: **715,000 acre-ft active water storage**; this is **multiuse irrigation water storage, NOT PS-usable electrical MWh**. Converting this entire water volume to a battery-style reservoir MWh without head variation, water rights, day-specific levels and irrigation withdrawals is not source-verified.

[Official source and six-generator-key CI 42129966383](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42129966383) **SUCCESS**, [original-source and physical-operating-context artifact 13462129232](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42129966383/artifacts/13462129232). Its fail-closed gate confirms six specific original 2024 PS units and nameplates and explicitly records the unknown reservoir energy MWh, historical SOC and daily irrigation service.

## 2. Pre-defined hypothetical operating-access sensitivity

To test whether the previous PS benefit is conditional on *assumed unconstrained access* to the reversible units, the [actual 672-hour PyPSA sensitivity CI 42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635) (**SUCCESS**) reruns all 16 combinations: four **assumed** constant fractions (0%, 25%, 50%, 100%) of the official 314 MW nameplate allocated to power dispatch × four original baseline/heat-only/wind-only/heat+wind stress cases.

Each assumed PS availability fraction is applied **both to symmetric modeled charge/discharge MW and to a 4-hour assumed energy capacity** (duration fixed), with **80% assumed roundtrip efficiency**, **zero initial/terminal SOC**, hourly power and energy conservation, one 672-hour optimization, no weekly reservoir reset.

**CRITICAL:** none of 0/25/50/100% is measured 2024 Grand Coulee irrigation reserve, water duty, pump-use time fraction or operator-authorized generation rights. A constant model-access fraction is a synthetic *capacity withholding stress test*, **not** a physical reconstruction of irrigation scheduling or water allocation.

All other source inputs are identical: the source-verified corrected-hour EIA930 July 1–28 demand, ERA5 representative weather, **incomplete** 2024 EIA860 gas/wind proxy, four isolated BAs (AZPS, BPAT, CISO, SRP), original synthetic heat/wind stress rules and *fixed hypothetical conventional BPAT HY 2,000 MW/598,947.6 MWh budget*. These are not observed lost-load events.

## 3. Actual 672h PyPSA model results — from independent CI

**No-PS original source model baseline:** 1,508,297.366980 MWh of *modeled* four-BA shortage; **not historical EENS**.

| Assumed Grand Coulee PS allocation | Hypothetical symmetric PS charge/discharge MW | Assumed 4h usable energy MWh | 28-day four-BA baseline modeled shortage MWh | Modeled shortage reduction vs no PS MWh | Heat×wind modeled shortage second difference MWh |
|---|---:|---:|---:|---:|---:|
| 0% | 0 | 0 | **1,508,297.366980** | **0.000000** | **+53,241.973340** |
| 25% | 78.5 | 314 | **1,500,630.261214** | **7,667.105766** | **+53,236.024540** |
| 50% | 157 | 628 | **1,493,497.715304** | **14,799.651676** | **+53,579.909244** |
| 100% | 314 | 1,256 | **1,480,655.729555** | **27,641.637424** | **+55,385.708435** |

The **absolute size of the modeled PS effect decreases sharply when the assumed fraction of named PS capacity usable for grid dispatch declines**. The heat×wind interaction is *not necessarily monotone in the assumed PS operating fraction* (25% falls slightly below zero-PS interaction): resource-constrained nonlinear model responses can vary with what binds. This alone is not a validated effect of real irrigation management.

[Original solved 16-case/hourly SOC artifact 13462104608](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635/artifacts/13462104608).

**Independent exact-control reconciliation:** [GitHub CI 42130613044](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130613044) **SUCCESS**, [replay/interaction CSV and JSON artifact 13461909861](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130613044/artifacts/13461909861). The 0% PS model reproduces **all 64 BA×week×climate records of the earlier original HY-only 672h PyPSA experiment** with **0.000000 MWh maximum difference**. Independently, the 100% / 314 MW / assumed 4h / 80% scenario reproduces **all 64 corresponding original 314MW PS experiment records** with **0.000000 MWh maximum difference**. Total: **128/128 original model comparator rows exactly matched**. This verifies computations and original source boundaries—not historical PS operation.

## 4. New scientific interpretation for the private Paper C manuscript

**Positive contribution:** source-linked specific facility evidence shows why treating PS as a generic free-to-dispatch battery is an unsuitable representation of a multipurpose federal irrigation-hydropower project. Both the model shortage response and compound heat×wind interaction vary when a physically motivated but **unmeasured** operating-access parameter is changed. Hydro-electric power scheduling and non-power water obligations should enter explicitly into hypothesis design and uncertainty.

**Major restrictions (still unresolved):**
- The 2024 USBR/EIA860 source validates **generator identity and 314 MW generating nameplate**, but no hourly output availability, site-specific reversible electrical pumping limit, recoverable electrical reservoir MWh, energy roundtrip efficiency, initial/final water levels, reservoir operating rights, flow releases, canal constraints or irrigation withdrawals for July 2024.
- Actual Banks Lake 715,000 acre-ft water volume is **not** dispatchable electrical storage MWh and must not be added as a fixed SOC.
- The July observations cannot identify *what fraction* of the six reversible units was available for energy arbitrage; all availability fractions in the table remain arbitrary stress assumptions.
- Underlying generator roster remains partial and regional links isolated. Therefore a model-optimized shortage difference is **not observed grid outage avoidance, EENS, LOLE, actual heat derating or causal climate risk**.

**Next data gate before further physical model claims:** USBR Hydromet historical Banks Lake elevation/inflow/irrigation delivery by day and plant-level pump/generator daily operations, generator pump curves, head-dependent efficiencies and operational restrictions (including potential operating agreements). Where unavailable, explicitly bracket rather than invent flows, durations or monthly operating-state fractions. Require independent-year validation and complete BA resource/intertie modeling before calibrated adequacy conclusions.

**Code:** [Grand Coulee exact PS source concordance](../src/grid_resilience/bpat_grand_coulee_ps_usbr_concordance.py), [irrigation-access 672h PyPSA study](../src/grid_resilience/bpat_grand_coulee_ps_irrigation_access_sensitivity.py), [official generator CI](../.github/workflows/bpat-grand-coulee-usbr-ps-concordance.yml), [PyPSA study CI](../.github/workflows/bpat-grand-coulee-irrigation-ps-availability-pypsa.yml), [128-control independent replay CI](../.github/workflows/bpat-grand-coulee-irrigation-ps-access-reconciliation.yml).

**Historical grid reliability/hydro water physics validated: NO.**
