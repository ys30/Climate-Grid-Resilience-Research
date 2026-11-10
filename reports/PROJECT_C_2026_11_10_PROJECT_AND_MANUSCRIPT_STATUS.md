# Paper C — Project and manuscript evidence status (10 November 2026)

## Executive decision

**Research and code have progressed considerably, but Paper C does not yet support a historically calibrated Western-US electricity-reliability inference.** Preserve the existing versioned portfolio V1 and the independently developed Research V2 as separate outputs. The core publishable approach is to separate (i) observed climate/exchange/storage and source-data limitations from (ii) explicitly assumption-conditioned PyPSA factorial response, and not label deterministic incomplete-fleet modeled deficits as actual outages, physical capacity shortfalls, or EENS.

### Status table

| Workstream | Completed and archived evidence | Blocker for physical reliability inference |
|---|---|---|
| 4-BA 2024 July 1–28 historical demand/ERA5 | Four 168h disjoint weeks; matched four-scenario PyPSA hypothetical-link solves; model nonadditivity | Four adjacent weeks are not independent events and generator/network are not calibrated |
| Independent-year/season response | Feb 2024 negative-control; July 2023 and 2024 heat-active comparisons; year-specific partial fleet sensitivities | No historical available-capacity and physical-transfer validation |
| BPAT hydro / Grand Coulee PS | 314 MW roster generating nameplate, 16 × 672h assumption-based PyPSA cases; independent SOC audits; 31-day real USACE whole-site pump MWh, reservoir elevation sources | Whole-site pump energy is not PG7–PG12 charge energy, usable MWh/SOC/efficiency unresolved |
| CAISO storage | Original observed 5min battery output and source-bounded *hypothetical* StorageUnit experiments | Battery power is not a verified historical storage-energy state |
| EIA930 BA balance / bilateral | Original 2024 168h four-BA source join; CISO 144 blank total-interchange hours, BPAT nonclosure, reciprocal auditing | Reporting boundary and accounting do not identify electrical line limits |
| Original source fuel categories | 161h modern 16-fuel null-safe audit CI #42716078830; source arithmetic clues | All four BAs have blank categories in every hour; physical generator availability unverified |
| New 7/8-category per-hour source reconciliation | Code, tests, GitHub Actions and README committed; additional nonzero-hour/maximum-absolute residual diagnostics | **CI conclusion and original source outputs not yet verified** |

## Supported numerical statements for manuscript drafts (strictly scoped)

1. Under frozen, *hypothetical* link capacities in **four consecutive July 2024 weeks**, modeled heat × wind second differences are **+22,516, +16,205, +25,211, +15,177 MWh**. These are screening-model responses; within-July weeks are not independent climate replications.
2. The Feb 2024 simulated interaction is zero because the scenario's assumed 30°C temperature-response threshold was not activated; **this is a model negative control**, not observed absence of winter grid risk.
3. Historical real 2024 Grand Coulee **whole Banks Lake pump installation** used **175,641 MWh** over July 1–31, **169,160 MWh** for July 1–28; six source-identified reversible PS generators have **314 MW generating nameplate**. This does not identify their individual electricity charge, usable hydro energy, or physical SOC.
4. Original 2024 Jul–Dec EIA930 161h source reporting has blanks in all 644 BA-hour original full-category vectors. Previous selected-six BA-net signed discrepancies were **AZPS +14,487**, **CISO −25,937**, **SRP −3,986 MWh**, and BPAT had blank Coal. Other Fuel numerically matches AZPS and SRP selected-six weekly discrepancies; CISO Other plus Petroleum leaves **−11 MWh signed aggregate**. The new hour-level workflow must verify whether any offsetting hourly differences remain.

## Paper outline (draft structure, not manuscript completion claim)

- **Introduction:** Compound climate exposure and adequacy sensitivity; avoid claiming historical blackout attribution.
- **Data:** EIA860/EIA923/EIA930, ERA5, CAISO storage and Grand Coulee operational sources, with explicit reporting vintage/time-zone and missingness rules.
- **Methods:** Four-scenario matched factorial contrast `U_HW - U_H - U_W + U_0`, capacity/transfer sensitivity, duration/energy constraints, data-admission gates, and model-vs-observation distinction.
- **Results 1:** Observed climate exposure and source completeness/technology representation (data-driven).
- **Results 2:** Paired conditional heat × wind model interactions, BA-specific signs, cross-week and cross-year stability.
- **Results 3:** Hydro/PS operating constraints under *assumed* 314MW access and realistic water-duty **observational context**; do not treat observed whole-site pumping as the model's PS charging.
- **Discussion:** Interpretation limited to modeled nonadditivity conditioned on an incomplete fleet and assumed links; effect of source gaps; transferability and physical validation needs.
- **Conclusions:** Reproducible conditional screening framework and empirical source-readiness limitations; no historical EENS claims.

## Proposed figure hierarchy

| ID | Main or supplement | Evidence and readiness |
|---|---|---|
| Fig 1 | Main | Source-data and scenario design schematic; source/map boundaries must be accurate |
| Fig 2 | Main | Four-week July 2024 matched factorial interaction, with separate BA and transfer conditions; already CI-verified data, re-validate final figure source |
| Fig 3 | Main | 2023/2024 summer and Feb 2024 negative-control model contrasts; model scope and thresholds on figure |
| Fig 4 | Main | Grand Coulee PS 16-case 672h response and conservation; explicitly hypothetical access |
| Fig 5 | Main | Observed USACE pumping and measured reservoir level context (separate axes, never inferred electric SOC) |
| Fig S1 | Supplement | EIA930 original 16-category availability and seven-/eight-category signed vs absolute hourly residual diagnostics; **new plots not yet run/validated** |
| Fig S2 | Supplement | CISO/BPAT raw accounting and reciprocal bilateral reporting limitation |

## Next decision gates (ordered)

**G1 — Source arithmetic:** Validate the new real-data 7/8 workflow, review uploaded hourly CSV, summarize signed vs absolute discrepancy and original-null coverage. Do not make claims from an unverified workflow configuration.

**G2 — Publishable conditional model:** Freeze a single reproducible cross-window dataset/config/commit; ensure every figure uses the same year, event UTC labels, fleet variant, heat/wind assumptions, link version and shortfall definitions. Do not pool incompatible proxy-fleet contrasts.

**G3 — Physical attribution:** Obtain full historically eligible generator availability, hydro/PS energy budgets and physically sourced transfer ratings or keep the article framed as *assumption-conditioned scenario screening*. Observed historical EENS is not inferred.

**G4 — Manuscript:** Draft complete Results and Discussion with an evidence registry linking each numerical statement to source, commit, exact CI run and artifact. Manuscript content remains private; the public repository holds code, method and source-gated portfolio evidence only.

## Verification and privacy

The code and docs in Research V2 are public; this status report contains **no private manuscript text**. Last inspected default branch commit on the status-check date was `409556ba` before the subsequent new diagnostic commits. GitHub workflow live conclusion was unavailable to the checker and must not be asserted as successful. All prior labeled successful CIs are referenced in the existing README and reports; their evidence scope is unchanged.
