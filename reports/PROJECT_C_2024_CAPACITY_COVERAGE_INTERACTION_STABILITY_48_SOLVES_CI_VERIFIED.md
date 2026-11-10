# Paper C — Missing partial-fleet capacity stress: July 2024 weeks 1 and 3 (CI VERIFIED)

## Reproducibility

**Successfully executed 48 new PyPSA optimizations** in [GitHub Actions run #42918422115](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42918422115); the workflow passed six regression tests, restored the **original and immutable** 2024 four-week EIA930/ERA5/EIA860 proxy model archive from [run #42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361), and proved the zero-addition arms reproduce its published baseline shortage and factorial interaction within 0.001 MWh. Actual **maximum difference was 5.82 × 10⁻¹¹ MWh**. [Original 60-row BA+SYSTEM sensitivity and input capacity/scopes artifact #13809139743](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42918422115/artifacts/13809139743).

Code: [implementation](../src/grid_resilience/paperc_2024_capacity_coverage_sensitivity.py), [regression tests](../tests/test_paperc_2024_capacity_coverage_sensitivity.py), [48-solve Actions workflow](../.github/workflows/paperc-july2024-capacity-coverage-sensitivity.yml).

## Precise counterfactual experiment

The prior incomplete 2024 generic thermal/wind proxy roster is kept unchanged except for **additional hypothetical perfectly firm generation MW in each BA**, fixed at **0%, 25% or 50% of that BA's *observed 2024 July Week 1 hourly peak demand***. The extra MW is implemented as an incremental constant-MW **generic thermal proxy**, not generator units identified in EIA860 or demonstrated real thermal capacity. All matched scenarios share the same additive capacity; the weather changes are unchanged (+4°C thresholded heat demand, 30% proxy wind availability haircut). The original July Week 1 and Week 3 168-hour demand/weather are source-observed; the BAs remain AZPS/BPAT/CISO/SRP; links remain either zero or the same **hypothetical** 10%-of-smaller-endpoint week-one peak ratings. Original optimization horizons remain **168h** each: week 1 and 3 deliberately sampled for their previously negative BA-local contrasts. This is a **selected two-week model stress test**, not representative weather-event sampling or physical capacity expansion recommendation.

Three capacity settings × two weeks × two network variants × four climate scenarios = **48 separate optimal PyPSA solves**, with **192 BA-scenario solver output records** aggregated into **60 BA+SYSTEM comparison records**.

## New source-computed system results (MWh modeled factorial second difference)

| Week | Network | +0% BA peak | +25% BA peak | +50% BA peak |
|---|---|---:|---:|---:|
| July 1–7 | Isolated BAs | +14,630.333 | +5,203.678 | +1,205.834 |
| July 1–7 | Frozen illustrative links | +22,515.998 | +1,473.656 | **+45.245** |
| July 15–21 | Isolated BAs | +14,697.753 | +10,575.038 | +1,879.051 |
| July 15–21 | Frozen illustrative links | +25,211.030 | +3,291.243 | **+589.438** |

Key modeled behavior: with +50% BA-peak perfectly firm capacity, the linked Week 1 model factorial second difference declines by **99.80%**, and linked Week 3 by **97.66%**. The deficit-generating system is very different under the assumed additional capacity; this is a demonstration of **structural non-robustness of the original interaction magnitude**, not an estimate of an actual capacity addition's effectiveness in the Western grid.

## Original linked-model negative BA interactions do not survive hypothetical 25% capacity

| Week | BA | Original +0% links | Hypothetical +25% links | Hypothetical +50% links |
|---|---|---:|---:|---:|
| July 1–7 | CISO | **−5,763.712 MWh** | +136.199 MWh | 0.000 MWh |
| July 15–21 | BPAT | **−5,918.429 MWh** | +2,936.943 MWh | +589.438 MWh |

All four modeled **SYSTEM** interactions remain positive in the explored incremental capacity grid. That does not establish robustness to all plausible completed capacity rosters, nor is the change a real-weather causal treatment effect. The BA-local negative sign and system interaction magnitude are **not invariant** to hypothetical omitted-fleet representation.

## Source model shortage scale — why the sensitivity matters

Week 1 *linked* baseline model gaps fall from **292,031.962** to **13,682.571** and **0.000 MWh** as additions increase from 0 to +25% and +50%; Week 3 linked baseline gaps fall from **317,924.499** to **43,711.132** and **379.396 MWh**. These are diagnostic optimized screening shortfalls under a partial fleet. Their rapid collapse makes it especially inappropriate to interpret previous unserved energy or its second difference as physically calibrated missing supply, historical blackouts, or EENS.

## Scientific interpretation and manuscript implication

This new experiment is **not minor robustness support for the original quantitative interaction**: it identifies a **major model sensitivity that should be elevated in Results and Discussion**, with the original 4-week effects explicitly qualified as partial-fleet configuration dependent. A paper that foregrounds source provenance, structural sensitivity and bounds of inference is defensible; a paper claiming measured Western-U.S. compound weather reliability impacts is not.

**Remaining essential gates:** independently source complete BA-relevant thermal/wind/hydro/storage capacity and actual dispatch, credible vintage-based availability, verified physical exchange limits, BA/plant-specific weather, multiple matched events and source-entitled hydropower operation. Additional perfectly firm synthetic MW cannot substitute for these source constraints. No actual outage/EENS or adequate real-world capacity expansion size has been inferred.
