# BPAT February-trained scale: independent March/July hourly holdout

**Verified CI:** [holdout run 41271568762](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41271568762), success; [research methods CI 41271568785](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41271568785), success.

The one-parameter nonnegative least-squares scale **1.041040379509748** was estimated **only from February 2024 (696 hours)** using the 29-site capacity-weighted ERA5 idealized wind-availability proxy and observed BPAT EIA-930 wind generation / nameplate ratio. March 2024 (744 hours) and July 2024 (737 matched hours) were never used to fit the coefficient.

| Month | Method | MAE (pu) | RMSE (pu) | Bias (pu) |
|---|---|---:|---:|---:|
| February training | Raw proxy | 0.074831281 | 0.109649680 | -0.052730049 |
| February training | February-trained scale | 0.073784526 | 0.109166327 | -0.047026638 |
| March held out | Raw proxy | 0.086476509 | 0.125273538 | -0.082298517 |
| March held out | February-trained scale | 0.082885149 | 0.120535125 | -0.077742134 |
| July held out | Raw proxy | 0.102491365 | 0.133282573 | -0.095684554 |
| July held out | February-trained scale | 0.098980858 | 0.129066179 | -0.090376947 |

Held-out relative MAE improvements are approximately **4.15%** (March) and **3.43%** (July). Held-out RMSE also improves in both tested months. The remaining biases are still substantial and systematically negative, particularly July.

**Interpretation and decision:** The transfer of a February-trained multiplicative correction across March/July provides preliminary out-of-sample diagnostic support for a small positive scale factor, **not calibrated weather-to-generation physics**. Treat the scale as a **candidate diagnostic only**. Do not substitute it for the hypothetical **30% wind-loss perturbation** in the July PyPSA four-scenario model, since they represent different quantities. A sensitivity-tested, physically supported weather-dependent plant generation formulation and broader independent months are required before promoting it to the main paper's power-system simulation.

**Known limitations:** EIA-930 reported net wind generation is not the same as unconstrained weather potential; generator roster/curtailment, BA mapping and plant status have uncertainty; February and both holdouts are from the same year and weather source; seven July observations missing; no observed power outages or validated intertie transfer ratings. **Historical generation calibrated: false.**
