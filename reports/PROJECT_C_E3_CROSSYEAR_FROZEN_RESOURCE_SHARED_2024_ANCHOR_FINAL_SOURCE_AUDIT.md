# Paper C E3 — Distinct-year frozen-resource conditional-model validation (scope CLOSED, 2026-11-10)

## Verifiable original archived evidence

**No new PyPSA solves:** this final E3 audit re-examines source files and the four climate-scenario BA solver records in the already-successful, immutable original [2023–2024 crossyear PyPSA CI 42419234209](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42419234209), original [2024 four-week source CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361), and the [completed E2 four-week capacity matrix CI 42923134596](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42923134596). All three original ZIP archives were retrieved and independently read.

- 2023 real-source input: **July 10–16, 2023**, 168 contiguous UTC start-hours × four BAs (AZPS, BPAT, CISO, SRP), EIA-930 demand and ERA5 *point-proxy* weather. The code-level assumed heat-load response was active in **509/672 BA-hours**.
- 2024 original input: **July 1–7, 2024**, also 168 contiguous UTC start-hours × four BAs. It is the **same Week 1 anchor reused in the four-week E2 series**, and **must not** be counted as an additional independent validation window.
- The 2023 run intentionally uses the **frozen original 2024 EIA860 partial generic-thermal plus wind proxy** capacity for all four BAs; the two source-archive input capacity files are exactly equal when normalized by BA key (their raw CSV row orders differ). 2023 is **not** modeled with its historical fleet.
- Both years use the same model factorial assumptions: +4°C with a 30°C threshold and a 0.012/°C load coefficient; a 30% synthetic wind proxy reduction; isolated BA or the same 2024 Week-1-derived illustrative links (no verified transmission ratings).
- The original 2023 run manifests' SHA256 **exactly match source archive raw demand, ERA5 weather and the 2024 original frozen-capacity file**. The manifest hashes correspond to **input files before preparation**, so a prepared CSV, which is re-sorted and/or rewritten, need not have identical bytes even if its table values are the same.
- The original 2023 solver's 16 BA/scenario outputs per network reconstruct both reported 2023 system second differences and baseline modeled gaps to within **1e-6 MWh**. The independently archived 2024 Week 1 system outcome exactly matches the crossyear report and the +0% E2 first-week result to within **1e-6 MWh**.

## Audited cross-year result, identical resource convention (modeled MWh)

| Network assumption | 2023 July 10–16: Heat×Wind second difference | 2024 July 1–7: Heat×Wind second difference | 2023 baseline model gap | 2024 baseline model gap |
|---|---:|---:|---:|---:|
| Isolated BAs | **+12,968.975027** | **+14,630.333329** | 417,730.627847 | 440,029.150992 |
| Fixed illustrative interties | **+12,886.902774** | **+22,515.997901** | 238,300.278102 | 292,031.962482 |

This is **cross-calendar-year *input* sign persistence for one fixed 2024 partial proxy**, not calibrated reliability or climate causality. The linked-model magnitudes differ considerably; 2023/2024 source windows are not matched for observed weather severity, generator availability or network status. Two weeks, though in different years, are not a statistical ensemble of independently classified compound extremes.

### Contrasting E3 and E2: deliberately different inferential axes

- **E3** varies observed calendar-year source weather/demand while holding the frozen incomplete resource and illustrative links constant. It supports sign persistence under *that controlled model convention only*.
- **E2** held each of four July 2024 week-specific observed inputs fixed while varying synthetic 0/25/50% BA-peak perfectly firm thermal capacity. E2 found major magnitudes and local sign changes, including a **nonmonotone** Week 2 linked-system second difference, **+16,204.695 → +18,602.415 → 0 MWh**. Hence the two-window E3 sign persistence does **not** overturn E2's finding that model interaction results are structurally capacity-sensitive.
- **E1** verified annual EIA860 3,268 generator IDs and conservative technology screening, but did **not** establish hourly physical availability, storage SOC, or actual BA transfer limits.

## Frozen E1–E3 program decision

**E1 source generator-identity inventory: CLOSED. E2 four-week assumption-robustness screening: CLOSED. E3 two-year source-input frozen-resource crosscheck: CLOSED.** The paper should now be revised once to make **capacity/fleet representation dependence** its primary scientific finding, with the crossyear result explicitly a *limited conditional check*, not extra climate-risk evidence. No arbitrary capacity grids, no further period searches, and no PS/network calibration experiments are added under this frozen screening-paper scope.

The manuscript, modeled shortages and model-based energy interactions must not claim actual EENS, LOLE, historical outages, physically verified line ratings, historical fleet-wide reliability, or climate-attributable capacity requirements. Source redistribution rights and exact third-party solver environment lock remain outstanding reproducibility/public-release tasks, not authorizations for further experimental expansion.
