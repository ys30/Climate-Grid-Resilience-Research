# Actual June–July 2024 joint-support EPA–ERA5–EIA930 exploratory source associations — CI verified

**Real observed-source model run:** [42093112865](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42093112865) **SUCCESS**, [result artifact 13444759823](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42093112865/artifacts/13444759823). Verified compact joined source-hour panels from [run 42092282072](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092282072), [artifact 13445258883](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092282072/artifacts/13445258883), each with original 2024 EPA Arizona MD5 and official EIA930 source SHA256 evidence. The later independently checked archived-panel workflow [42092315252](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092315252) also **SUCCESS** ([artifact 13446995330](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42092315252/artifacts/13446995330)). The EPA full source is not committed; only directly observed matched relevant source-hour excerpts and their public provenance are retained.

## Study design and source admission

This is the first real-source **common-cell observational slope sensitivity experiment** beyond January–July, whose actual temperature intervals had zero overlap. It uses the exact EPA source cohort of **10 units across three locations**, real source June 2024 ERA5/EIA930 hours (713 EPA MST-to-UTC calendar-matched hours/unit) and real July sources (737/unit), not interpolating June–July UTC boundary hours.

The prespecified same-site set of jointly occupied **2°C ERA5 site temperature × 500-MW observed SRP BA demand × 4-hour local clock** bins defines the permissible comparison sample. Both months must have ≥80 joint source hours spanning ≥10 dates for a descriptive covariate screen; the **conditional positive-operating Gross Load** model additionally requires ≥80 observed source gross records in each month in shared bins. All 10/10 source units pass the covariate screen, and **6/10 pass conditional gross support**. Same ERA5 plant and SRP BA demand time series may be repeated across colocated unit IDs and are not statistically independent.

Each month and EPA source separately fits **exploratory OLS** for positive EPA reported Operating Time (linear probability) and **source Gross Load MW conditional on positive Operating Time**, controlling for **SRP-wide BA observed EIA930 demand GW, MST local hour fixed effects, and local date fixed effects** within the restricted occupied-bin sample. A constant operating outcome is explicitly rejected as not identifying a nontrivial slope. There are **no valid inferential p-values, autocorrelation-adjusted SE, cross-unit pooled standard errors or physical generator derating outcomes**.

## Source-confirmed conditional Gross Load temperature coefficients

These units have sufficient observed gross source rows in **both** periods; the coefficients are MW per °C, *not* available net generator MW or measured heat losses.

| EPA unit | June matched joint-source hours | July matched joint-source hours | June reported gross rows while running | July reported gross rows while running | June coefficient MW/°C | July coefficient MW/°C |
|---|---:|---:|---:|---:|---:|---:|
| 141 / 1 | 451 | 685 | 110 | 309 | **−7.84** | **−1.55** |
| 141 / 2 | 451 | 685 | 120 | 310 | **−17.23** | **−3.26** |
| 141 / 3 | 451 | 685 | 98 | 352 | **−19.04** | **−7.15** |
| 147 / K-7 | 412 | 676 | 354 | 560 | **−3.17** | **+6.66** |
| 55129 / DBG1 | 415 | 702 | 376 | 687 | **−1.09** | **−0.10** |
| 55129 / DBG2 | 415 | 702 | 391 | 696 | **−0.83** | **+0.21** |

Unmapped or low-run 141/7 (7 June joint gross records), 141/8 (7), 55129/DBG4 (0) and DBG5 (0) are **explicitly withheld for both periods**, even if their July period alone has some reported gross records. None receives a valid conditional gross temperature slope.

## Running indicator temperature coefficients

All shown values are **linear probability changes in percentage points per °C** within source-specific and month-specific common-cell samples, not forecasted dispatch probabilities.

| EPA source | June running LPM coefficient (pp/°C) | July running LPM coefficient (pp/°C) |
|---|---:|---:|
| 141/1 | −5.20 | −3.12 |
| 141/2 | −0.18 | −1.74 |
| 141/3 | −3.86 | −0.87 |
| 141/7 | +0.44 | −0.29 |
| 141/8 | +0.60 | +1.35 |
| 147/K-7 | **+2.76** | **+2.07** |
| 55129/DBG1 | −1.05 | −0.03 |
| 55129/DBG2 | −0.24 | −0.24 |
| 55129/DBG4 | **Not estimable (constant zero June outcome)** | −0.81 |
| 55129/DBG5 | **Not estimable (constant zero June outcome)** | −0.47 |

## Scientific interpretation and limitations

**Positive common support eliminates the previous categorical source-temperature nonoverlap limitation, but does not identify a physical temperature response or a seasonal *change* in such a response.** In particular K-7's running coefficient is positive in both periods while its conditional gross coefficient changes sign (−3.17 → +6.66 MW/°C). That difference persists in the *defined shared bins* and signals important model/dispatch/operation-season dependence; there is **no uncertainty estimate for the difference**, so it is **not** evidence of a statistically significant shift. Other units demonstrate varied negative coefficients with sometimes large magnitude despite sparse source gross support—consistent with dispatch-selected outcomes and potential collinearity, not a validated physical heat-derating rate.

June/July overlap bins are a **descriptive common-cell screening rule**; they do not equate the joint distributions nor prove equal technology condition, dispatch state or positivity of every further unobserved determinant. June and July outcomes still exhibit different day composition, loading regime, engine operation and possible grid dispatch constraints. The model is **in-sample and observational in both months**: no actual held-out predictions, time-block uncertainty, generator available net MW, confirmed EIA physical generator identity, forced-outage labels, measured EENS/LOLE or physical PyPSA capacity calibration were produced.

## Future high-value steps

1. Estimate the **uncertainty/stability of within-common-support month coefficients** using date-block or multi-day-block methods, while respecting repeated site weather and month-specific operating selection. Report sparse/unidentified estimates without imputation.
2. Measure **out-of-month predictive transfer** using held-out observed source-hours and appropriately defined outcomes only after a trustworthy design, and distinguish descriptive month-specific coefficients from forecasting skill.
3. Acquire source ECMPS monitoring plans and original equipment-level net capacity/dispatch/availability data before claiming actual thermal performance, and retain existing PyPSA studies as **screening / scenario analysis** rather than empirically calibrated historical resilience.

Code: [common-cell unit model](../src/grid_resilience/srp_epa_june_july_overlap_models.py), [regression guards](../tests/test_srp_epa_june_july_overlap_models.py), [model workflow](../.github/workflows/srp-epa-june-july-joint-cell-models.yml).
