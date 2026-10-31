# BPAT ERA5 wind proxy: February 2024 blocked temporal holdout

Verified [GitHub Actions run 41238077955](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41238077955) (Success). This is an independent **within-month held-out-hours** diagnostic, not an independently sampled season or a prospective weather forecast.

| Split | Test hours | Input | Fitted scale | Test MAE (percentage points) | Test RMSE (percentage points) | Mean bias (percentage points) |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Train February 1–14, test February 15–29 | 360 | ERA5 29-site proxy (no adjustment) | 1.000 | 7.206 | 11.086 | −3.008 |
| Train February 1–14, test February 15–29 | 360 | Train-only nonnegative least-squares scale, clipped to [0,1] | 1.788 | 12.190 | 19.636 | +9.201 |
| Train February 15–29, test February 1–14 | 336 | ERA5 29-site proxy (no adjustment) | 1.000 | 7.781 | 10.834 | −7.700 |
| Train February 15–29, test February 1–14 | 336 | Train-only nonnegative least-squares scale, clipped to [0,1] | 0.970 | 7.975 | 11.087 | −7.904 |

**Finding.** The one-parameter calibration **worsens** held-out MAE and RMSE in both chronological directions. Scale estimates 1.788 and 0.970 differ substantially. In-sample hourly correlation (r ≈ 0.893) is insufficient to claim stable out-of-sample generation amplitude calibration.

**Important limitations.** EIA-930 BPAT reported wind is net generation, not unconstrained wind power potential. EIA-860 2024 nameplate attribution and idealized 3/12/25 m/s power curve are approximations, with no turbine-specific hub heights, outages, curtailment, aggregation, or time-varying fleet calibration. The two temporal blocks share the same month and weather regime. No independent-month or operational forecast skill claim follows.

**Decision.** Preserve the original ERA5 uncalibrated baseline in PyPSA studies and do **not** apply the fitted scale to March or make a calibrated historical shortfall claim. Next priority: independent-month verification using unchanged 29 plant locations, unchanged ERA5 model, unchanged idealized power curve, separately extracted EIA-930 month.
