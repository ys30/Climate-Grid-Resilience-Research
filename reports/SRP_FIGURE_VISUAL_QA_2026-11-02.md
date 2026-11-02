# SRP figure visual and numeric QA — 2026-11-02

## Verified source

GitHub Actions run [41386883075](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41386883075), commit `568f52f`, artifact `13115548069` (SHA-256 `784e93871ded9cd109e428c5bae05c3041c8200dd3c490b5394bb4a4fe10746a`). Examined the extracted `srp_hourly_figure_data.csv`, `srp_diurnal_figure_data.csv`, `fine_gas_hourly_vulnerability_summary.csv` and rendered hourly / diurnal PNGs for the most severe C100/N100/G30 heat-wind case.

**Scope:** this is a QA of modeled scenarios, not historical observed outages, calibration, or independent validation.

## Numeric audit

- 16 scenario cases × 168 hours = **2,688 hourly rows**.
- 16 × 24 UTC clock-hour groups = **384 diurnal rows**.
- 32 PNGs, two per scenario, each previously checked to be nonempty by CI.
- 4 scenarios have positive modeled shortage: baseline C100/N100/G30 (4 shortage hours; 450.880 MWh), heat_wind C100/N100/G30 (15 hours; 4,342.666 MWh), heat_wind C100/N100/G35 (5 hours; 635.731 MWh), heat_wind C50/N75/G55 (3 hours; 352.485 MWh).
- In the four cases with shortages, positive shortage occurs only at **01, 02, or 03 UTC**; case-level distribution is respectively `{02:4}`, `{01:4, 02:6, 03:5}`, `{02:5}`, and `{02:3}`.
- All source figures are based on a July 2024 168-hour modeled window and assumed generation availability. UTC 01–03 corresponds to **18:00–20:00 Arizona MST on the prior calendar date**.

## Visual QA observations

1. **Hourly overlay (inspected):** readable overall and shortage spikes visibly align with high demand, but uses *two y-axes* (demand MW and shortage MW). The right-side magnitude scale can mislead comparison; manuscript version should use vertically aligned panels with a shared time axis.
2. **Diurnal bar chart (inspected):** clearly shows concentrations at UTC 01–03. It currently displays 24 UTC groups, while readers studying Arizona summer peaks may better understand an additional local-MST axis or an explicitly labeled local-time version. Do not apply daylight saving time to Arizona here.
3. **Figure selection:** 12 of the 16 cases have no material shortage, so 24 of the 32 PNGs convey mainly zero bars / empty shortage overlays. Retain them in the reproducibility artifact but **do not include all 32 in the manuscript**. Prefer a curated comparison figure covering the four positive cases and a compact 16-row summary table.
4. **Claims:** do not read an exact critical availability threshold from the 5%-step grid. Do not infer solar causality from the assumed solar shape.

## Recommended manuscript figures

- **Main Figure A:** 168-hour SRP demand and modeled shortfall for heat_wind C100/N100/G30, as stacked panels, UTC axis clearly annotated with local MST interpretation.
- **Main Figure B:** four-case positive-shortfall comparison: 168-hour shortage MWh and count of shortage hours.
- **Supplementary Figure S:** complete gas availability grid with explicit zero-shortage cases and coal/nuclear derating strata.
- Archive all 32 original PNGs and the full CSVs unchanged for reproducibility.

## Remaining acceptance gates

- Review all plotted panels for readability and compare every figure's underlying numbers with original CSVs.
- Generate manuscript-ready selected plots with legible labels and zero / nonzero distinction.
- Cross-check EIA-923 and EIA-930 historical dispatch/input measurements and confirm independent-year performance before external-validity or historical reliability claims.
