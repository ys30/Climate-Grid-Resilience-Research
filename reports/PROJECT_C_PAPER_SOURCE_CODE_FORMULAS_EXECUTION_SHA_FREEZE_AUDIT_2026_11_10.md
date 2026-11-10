# Paper C — Source code execution identities and reproducibility freeze audit (10 November 2026)

**Scope:** Verified source-code settings and immutable historical GitHub Actions execution identities, not a fully locked software/container or calibrated physical grid. This public report does not contain the unpublished manuscript.

## Exact code-level scenario implementation

The matched four-case [factorial_dispatch.py](../src/grid_resilience/factorial_dispatch.py) defines **(heat °C, fractional wind derating)** as baseline (0, 0), heat-only (+4, 0), wind-only (0, .30), compound (+4, .30).

For each BA and hour, demand is adjusted:
`D'_t = D_t {1 + 0.012 [max(T_t + ΔT - 30,0) - max(T_t-30,0)]}`,
where original EIA930 BA demand D is MW and point-proxy ERA5 T is °C. The coefficient is an assumption, **not a BA-specific estimated measured heat elasticity**. Wind proxy under scenario is `a'_t = a_t(1 - δ_w)`. The original-source [era5_proxy.py](../src/grid_resilience/era5_proxy.py) defines a synthetic 100m wind availability curve: clip[(v³−3³)/(12³−3³),0,1] for v<25m/s; 0 otherwise. This is not a calibrated turbine curve.

The modeled factorial term is I = U(compound) − U(heat only) − U(wind only) + U(baseline), where U is the optimized sum of fictitious high-penalty unserved generators; this is **not historical measured unserved load, real EENS/LOLE, nor a causal climate blackout estimate**.

In [four-week source admission](../src/grid_resilience/july2024_four_week_factorial_inputs.py), 2024 EIA930 end-of-hour timestamps are shifted to UTC **start hour**. The 2024 July 1–28 data include **672 UTC hourly keys × four BAs**. The 3 illustrative bidirectional edges are CISO–AZPS, AZPS–SRP, CISO–BPAT, with 10% of the **smaller endpoint's week-one peak demand** held fixed for all four weeks. The 4×168h optimizations are distinct; they are adjacent input windows, not independent weather extremes. Generator supply contains a 2024 EIA860 partial generic thermal/gas and wind proxy. Original PyPSA scenario solver calls `optimize(solver_name="highs")`.

The Grand Coulee experiment in [bpat_july2024_hy_ps_soc_pypsa.py](../src/grid_resilience/bpat_july2024_hy_ps_soc_pypsa.py) is a *different* 672h continuous, isolated-BA resource configuration: assumed 2,000MW/598,947.6MWh conventional HY, hypothetical Grand Coulee PS 0/25/50/100% of six-unit 314MW EIA860 generating nameplate; hypothetical 4h duration, 80% roundtrip, and 0 starting/terminal SOC. Whole-installation observed USACE pumping MWh is **not PG7–PG12 measured charging**. Do **not** pool its optimized shortages or factorial contrasts with the four-week no-HY formulation.

## Exact original-source run identities

| Component | Successful GitHub Actions run | Exact head commit SHA |
|---|---|---|
| Four-week 2024 PyPSA solve | [42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361) | `6831206284ffa86f176974972314038f49e7794f` |
| Crossyear source model | [42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209) | `35ba7bf2edb46659895a9ff9b9fb860215c4dd20` |
| Grand Coulee 16-case PS | [42130327635](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42130327635) | `aca4b93ecd69790708bafdcf5ef3a9c5c6ab0a9c` |
| Corrected four-week original figure | [42878609152](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42878609152) | `3c6fe6cee52d3f96e602325b4940e195ac26c4d0` |
| Crossyear original figure | [42441181359](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42441181359) | `9d0c51b9691a49c616932ad44bf903d854ff56ac` |
| Grand Coulee original figure | [42882357268](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42882357268) | `4b8928846aa2d00fd37c6671e4f6ec618f19d591` |
| EIA930 original fuel source audit | [42855419578](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42855419578) | `a4c0456c8d80135f38a296d7f30eaed208a1f9e3` |

## Reproducibility gates still NOT completed

- Python **3.11** is specified by the GitHub Actions setup; `pyproject.toml` requires `pypsa>=0.34`, `highspy>=1.7`, `numpy>=1.26`, `pandas>=2.0`, etc. These are **minimum constraints, NOT locked exact original package builds**. Archive `pip freeze` or UV/Conda lock plus original runner solver versions before claiming environment-bitwise reproduction.
- Code SHA is recorded but does not by itself save a complete source input file set. Archive source input SHA256, original EIA/ERA5/USACE source bytes, source scope and CI artifacts under permanent DOI-backed versioning.
- The original weather proxy is **one point per BA** and the original generation fleet and intertie ratings are structurally incomplete. Historical physical grid adequacy, actual EENS, true PS available MW/MWh and compound climate attributable blackouts are **not verified**.
- The manuscript v8 private citation-string check observes six author-year bibliography references and six distinct DOI strings. That is **not equivalent to a new complete publisher-by-publisher bibliography check**.

This report records exact, independently observed GitHub-run code SHAs for source/model and figure jobs and the actual scenario formulae. It should not be labeled an already fully frozen/pinned software environment.
