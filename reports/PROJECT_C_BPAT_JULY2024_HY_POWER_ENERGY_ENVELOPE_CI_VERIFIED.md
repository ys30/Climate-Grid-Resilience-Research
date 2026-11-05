# Project C — BPAT July 2024 hydro power–energy optimistic envelope (real-source anchored; not a dispatch solution)

**Real-source computation:** [GitHub Actions 42119602112](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42119602112) **SUCCESS**, [16-row exploratory scenario result CSV and strict scope JSON, artifact 13456759171](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42119602112/artifacts/13456759171). Method: [source code](../src/grid_resilience/bpat_july2024_hydro_power_energy_envelope.py), [six tests](../tests/test_bpat_july2024_hydro_power_energy_envelope.py), [CI workflow](../.github/workflows/bpat-july2024-hydro-power-energy-envelope.yml).

## Original-source inputs

- The official **2024 July BPAT EIA-923 Page 1 conventional HY net generation** is **5,989,476 MWh** from 55 reporting plant-month rows ([official original source CI 41263007401](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41263007401) and [BPAT July reporting-scope CI 42117378382](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42117378382)).
- Original four-BA July PyPSA 2024 **four source-observed disjoint 168-hour weeks** were previously solved under explicit **partial gas/wind fleet** assumptions and corrected official EIA930 start-hour demand ([CI 42104106361](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42104106361)). The original **BPAT isolated BA baseline modeled shortage** in July 1–28 is **795,413.711741 MWh**, across 672 model hours. **No historical observed outages or measured EENS**.
- HY monthly reported energy spans **July 1–31 (744 hours)**, whereas the modeled weeks span **July 1–28 (672 hours)**. Consequently EIA923 July HY production **must not be silently allocated uniformly** to the 28-day study. The observed monthly HY MWh is used solely as an **explicit hypothetical energy-budget scaling reference**; it is not reservoir water availability, generator energy budget, hourly firm production, or transferable energy.
- EIA923 pumped storage PS signed net monthly energy is a separate category and is **excluded from this non-storage HY reference**. Pumped storage roundtrip efficiency, initial/final SOC, hours and charging power are **not represented**.

## Necessary-condition accounting, not a feasible hydro dispatch run

For the unchanged original partial PyPSA shortage \(S_0\), choose **a hypothetical incremental non-storage HY power limit \(P\) MW** and an **assumed 28-day energy-budget ceiling** \(E=f\times5{,}989{,}476\) MWh, with \(f\) one of 0.10, 0.25, 0.50 or 1.00. For 672 modeled hours, the *maximum conceivable total mitigation of baseline shortage* cannot exceed

\[
  \Delta U_{\max} \le \min\{S_0, 672P, E\}.
\]

A corresponding optimistic floor on **remaining original-model shortage** is

\[
  U_{\mathrm{floor}} = \max\{0,S_0-\min(S_0,672P,E)\}.
\]

This bound assumes in the most favorable case that energy can be shifted into precisely the shortage hours, without hydro reservoir constraints, ramping, location mismatch, competing exports or transmission deliverability. Such an ideal allocation need not be realizable. In particular, a bound of **0 on residual shortage does NOT predict or demonstrate zero modeled shortage after adding HY**. It only says *these very loose necessary-condition bounds no longer rule it out*. Conversely, a positive floor rules out an assumed HY-only mitigation of the full original partial-model shortage even under unrealistically perfect temporal allocation.

**Neither these exploratory P values nor budget fractions are physical BPAT HY capacity or measured water availability.** All of the power values **500, 2,000, 5,000, 10,000 MW** are clearly stated scenario assumptions pending independent EIA860 2024 BPAT nonstorage HY nameplate and plant/BA identity admission. They must not be conflated with EIA860 record data.

## Source-verified scenario accounting

| Assumed HY P (MW) | Assumed energy budget fraction | Assumed energy cap (MWh) | Optimistic mitigation ceiling (MWh) | Remaining modeled shortage floor (MWh) | Most restrictive of the three simple bounds |
|---|---:|---:|---:|---:|---|
| 500 | 0.10 | 598,947.6 | **336,000** | **459,413.712** | Power |
| 500 | 1.00 | 5,989,476 | **336,000** | **459,413.712** | Power |
| 2,000 | 0.10 | 598,947.6 | **598,947.6** | **196,466.112** | Energy |
| 2,000 | 0.25 | 1,497,369 | **795,413.712** | **0** (trivial optimistic bound only) | Original shortage |

The [complete CI artifact](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/42119602112/artifacts/13456759171) records all **4×4 = 16** assumed combinations, their bound classifications and explicit scope gates. This is an **analytical power/energy envelope using real measured source scales**, not 16 PyPSA optimizations, not generated hourly water discharge profiles and not observational validation.

## Paper C implications and next executable physical model

This study reinforces that **energy volume alone cannot determine climate/grid adequacy without temporal power limits**. It also demonstrates why the original July four-week large baseline model shortage is primarily a **structurally incomplete source-supply screening artifact** rather than a validated historic outage. The official reported HY monthly energy is substantial, but cannot be mechanically inserted into partial-fleet 168-hour windows as reliable dispatch.

The next physically more meaningful workflow must:
1. Reopen original **EIA860 2024 generator OP roster**, year-scoped Plant BA map, eligible **conventional HY and PS inventory separately**, record exact nameplate and plant/BA concordance; audit pumped, storage and multifuel exclusions.
2. Establish the monthly hydro energy budget **as an explicit assumption**, not from observed HY net MWh directly. For 28 days, use a controlled assumed budget grid and optionally examine a dimensionless EIA923 net-generation ratio only as observational context.
3. Run actual 672-hour PyPSA with **hourly HY link power limits + non-cyclic reservoir energy Store**, and independent PS charge/discharge links and SOC/efficiency bounds (existing project code provides components). Validate all intertemporal balances and full scenario feasibility; omit PS from a HY-only study until its independent power and energy assumptions are documented.
4. Compare the same four-week baseline and exact same hydro assumptions under heat-only/wind-only/compound and isolated/hypothetical links; verify that added technologies do not silently change cohort, weather or source hour constraints.
5. Preserve the distinction between **hypothetical intervention**, **modeled dispatch** and **observed historical operation**. No historical EENS/LOLE, physical temperature derating, actual firm hydro capacity or true BA intertie deliverability is estimated here.

**Status: monthly HY evidence validated; mathematical source-anchored envelope computed; EIA860 BPAT HY fleet revalidation and actual July intertemporal PyPSA HY/PS optimization still pending.**
