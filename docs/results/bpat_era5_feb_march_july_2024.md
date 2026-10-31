# BPAT 29-site ERA5 wind proxy: three-season-point validation (2024)

**Verified source runs:** February [41227782144](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41227782144), March [41238968791](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41238968791), July [41246040163](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41246040163). These are model-to-observed-net-generation diagnostics, not operational forecast validation or historical blackout reconstruction.

| Month | Actual matched hours | Total calendar hours | Pearson r | Mean ERA5 proxy | Mean clipped observed | MAE (pp) | RMSE (pp) | Mean bias (pp) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-02 | 696 | 696 | 0.893405 | 13.897% | 19.170% | 7.483 | 10.965 | −5.273 |
| 2024-03 | 744 | 744 | 0.904463 | 11.102% | 19.332% | 8.648 | 12.527 | −8.230 |
| 2024-07 | **737** | 744 | 0.864359 | 12.933% | 22.501% | 10.249 | 13.328 | −9.568 |

## July missing-hour audit

The July EIA-930 observation parsing produces **737 matched hourly records (99.06% coverage)**. The 7 absent UTC timestamps are contiguous at the beginning of the requested month, **2024-07-01 00:00 through 06:00 UTC inclusive**. These values were **not interpolated or treated as zero**. July correlation and errors are restricted to the 737 matched hours. The contiguous boundary gap warrants an audit of EIA-930 six-month archive cutoffs and the UTC end-of-hour timestamp convention before claiming complete-month coverage.

## Conclusions and limits

The seasonal transfer preserves reasonably high wind timing correlation but exhibits a progressively larger negative amplitude bias in these three selected months. The 29 EIA-860 plant locations, nameplate weights, ERA5 wind-source/model, and idealized 3/12/25 m/s wind curve remain unchanged. The reported EIA-930 target is net generation with operating, dispatch and curtailment effects, **not raw meteorological generation potential**. These three months do not establish operational forecast skill, year-round generalization, or calibrated PyPSA adequacy.

Use **737**, never 744, as the July matched observation count. The 744-hour ERA5 weather grid is separate and complete.
