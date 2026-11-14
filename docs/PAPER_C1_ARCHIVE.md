# Paper C-1 — frozen research archive and access

**Paper:** *Modeled compound heat and low-wind stress depends on resource representation: a reserve-margin explanation for four western US balancing authorities*.

**Author:** Yu Song (sole author).

**Status:** E1–E3 computational analyses frozen; manuscript v13 under preparation for journal submission. The archive is **not** a claim that the manuscript has been published or accepted.

## Stable source

- Repository: https://github.com/ys30/Climate-Grid-Resilience-Research
- **Frozen C-1 source commit:** [6b549a6612f280646389f87bfc35453dd0e5d7dc](https://github.com/ys30/Climate-Grid-Resilience-Research/tree/6b549a6612f280646389f87bfc35453dd0e5d7dc)
- GitHub commit snapshot source ZIP: https://github.com/ys30/Climate-Grid-Resilience-Research/archive/6b549a6612f280646389f87bfc35453dd0e5d7dc.zip
- Pinned archival extraction workflow: [paperc-c1-source-archive-snapshot.yml](../.github/workflows/paperc-c1-source-archive-snapshot.yml).
- Zenodo dataset DOI: **pending** (do not cite a made-up DOI).
- Zenodo software DOI: **pending** (no GitHub Release published yet).

**Important:** This repository includes historical work outside Paper C-1. The fixed commit is a complete repository snapshot, not a minimal curated Paper C-1-only software distribution. C-2 climate attribution/prediction is separate; its later changes must not be retroactively included in the frozen C-1 reproducibility claim.

## Core evidence map

| Research component | Evidence |
|---|---|
| E1 source-scoped partial inventory and matching limits | [E1 audit report](../reports/PROJECT_C_E1_2024_EIA860_ANNUAL_VS_ORIGINAL_PARTIAL_PROXY_CI_VERIFIED.md) |
| E2 96-solve four-week capacity interaction experiment | [E2 report](../reports/PROJECT_C_E2_FOUR_WEEK_CAPACITY_INTERACTION_STABILITY_96_SOLVES_CI_VERIFIED.md) |
| E3 independent-year source-input and frozen resource comparison | [E3 report](../reports/PROJECT_C_E3_CROSSYEAR_FROZEN_RESOURCE_SHARED_2024_ANCHOR_FINAL_SOURCE_AUDIT.md) |
| Main four-factorial dispatch PyPSA implementation | [factorial_dispatch.py](../src/grid_resilience/factorial_dispatch.py) |
| EIA-923 generator-month extraction | [eia923_generator_extract.py](../src/grid_resilience/eia923_generator_extract.py) |
| EIA-860 / EIA-923 generator-keyed partial fleet matching | [eia860_partial_fleet_capacity.py](../src/grid_resilience/eia860_partial_fleet_capacity.py) |
| ERA5 weather proxy and hypothetical wind power curve | [era5_proxy.py](../src/grid_resilience/era5_proxy.py) |
| Grand Coulee hydro/pumped-storage separate 672h model | [bpat_july2024_hy_ps_soc_pypsa.py](../src/grid_resilience/bpat_july2024_hy_ps_soc_pypsa.py) |

## Scientific interpretation

C-1 quantifies **conditional model stress** under specified Heat × Wind scenarios, sensitivity to partial generator coverage, and illustrative connection/storage conditions. It does **not** estimate observed electricity outages, historical expected energy not supplied, actual Balancing Authority adequacy, or a calibrated future blackout forecast. Generic thermal and wind are explicitly represented in the original four-week factorial model. Hydro, solar, nuclear, and storage are not separately modeled there. The Grand Coulee 672h hydro/pumped-storage sensitivity is a separate hypothetical configuration.

## Long-term preservation and artifact retention

GitHub Actions execution artifacts and logs can expire; archived Git commit URLs and a formally published Zenodo record serve different purposes. For citations in a publication, use a **published Zenodo record with DOI** and pinned archive checksums once available, rather than linking only to expiring Actions artifacts. Original historical data from EIA and Open-Meteo/ERA5 may carry independent terms; the public curated deposit should not redistribute third-party raw hourly data without reviewing those terms. The private full-evidence backup, including original source inputs, is **not** intended for open Zenodo publication.

## Licensing and attribution

**No repository-wide software license has yet been granted.** The fact that this repository is publicly readable is not equivalent to MIT or other permission to redistribute and reuse. Copyright and reuse rights must be decided by the author. Original result tables/figures, project code, and third-party inputs may need different license scopes. A future `LICENSE_SCOPE.md` can document that decision; do not assume one license covers all archived contents.

## Suggested citation (until DOI publication)

Song, Y. (2026). *Modeled compound heat and low-wind stress depends on resource representation: a reserve-margin explanation for four western US balancing authorities* [research software and data, unpublished]. Source commit `6b549a6612f280646389f87bfc35453dd0e5d7dc`. https://github.com/ys30/Climate-Grid-Resilience-Research

Replace this provisional reference with the permanent dataset/software DOI citations after actual Zenodo publication.
