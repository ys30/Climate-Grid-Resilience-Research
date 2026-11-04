# SRP January 2024: 36-case gas × coal × nuclear × wind screening decomposition

**Verified:** [full official EIA/744h PyPSA workflow 41765278058](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41765278058) and [Research Methods CI 41765278116](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41765278116), both successful at source commit `3f43dabf5204aecfd574b4b16deb22608f924099`. [Evidence artifact 13293110396](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41765278058/artifacts/13293110396) contains **37 files**, including the 36-row `gas_coal_grid/gas_coal_nuclear_wind_grid.csv`, 12-row `conditional_gas_threshold_brackets.csv`, and model/source manifest.

## Model design, not observed outages

2024 January, 744 consecutive UTC hourly periods. EIA-930 hourly SRP demand and net interchange define the boundary. EIA-860 annual Plant BA operable generator list supplies nameplate (108 generators in the BA-plant roster, 97 classified, 11 excluded; classified total **15,576.5 MW**). Nuclear, gas, coal, hydro, wind, and solar are mutually exclusive primary-fuel/prime-mover categories. Battery and pumped-storage devices do not receive unconstrained supply. The BA's dispatch ownership, transmission capacity and every-hour plant operating state are **not independently certified**.

The optimization has six technology classes with base *assumed* availability: gas/coal .85, nuclear .90, hydro .50, wind .35, solar daylight-sine ×.80. This study does **not replay EIA-930 generation**, use ERA5 or claim meteorologically derived forced outage probabilities. Its four independently varied multipliers are:

- Gas {0.50, 0.625, 0.75}
- Coal {0.50, 0.75, 1.00}
- Nuclear {0.75, 1.00}
- Wind {0, 1.00}

All **36/36 optimization cases** completed and passed coverage, monotonicity, and workflow assertions. **13/36** have strictly positive *artificial model coverage gaps*. The largest is **136,752.327 MWh** at gas .50, coal .50, nuclear .75, wind 0. This is neither measured outage, EENS, nor historical adequacy verification.

## Revealing contrasts

Hold **gas .50 and nuclear .75**:

| Coal assumed multiplier | Wind 0: artificial gap MWh | Wind 1: artificial gap MWh |
|---:|---:|---:|
| .50 | 136,752.327 | 113,630.084 |
| .75 | 89,286.333 | 71,830.347 |
| 1.00 | 53,482.989 | 40,456.545 |

Thus raising coal from .50 to 1.00 cuts the model gap by **83,269.338 MWh** at zero wind, but does not eliminate it in this case. This is a *conditional assumed-resource sensitivity*, not observed coal derating evidence.

Hold **gas .50, nuclear 1.00, wind 1.00**: the artificial gap is **673.186 MWh** at coal .50 but **0 MWh** at coal .75 and 1.00. Under wind 0 and the same nuclear setting, gaps are **2,260.263**, **133.240**, and **0 MWh** at coal .50, .75 and 1.00 respectively.

Hold **coal .50, nuclear .75, wind 0**: the gap falls from **136,752.327 MWh** (gas .50) to **3,277.206 MWh** (gas .625), and **0** (gas .75). In this sampled range, gas has the larger marginal contribution to easing coverage constraints; do not infer this is a measured weather sensitivity.

## Identified conditional gas-factor brackets

The **lowest tested gas multiplier with zero artificial gap** and **highest tested gas multiplier still with positive gap** depend on coal/nuclear/wind:

- Coal .50, nuclear .75, either wind endpoint: tested transition between gas **.625 and .75**.
- Coal .75, nuclear .75, either wind endpoint: same bracket **.625–.75**.
- Coal 1.00, nuclear .75, either wind endpoint: bracket **.50–.625**.
- Coal .50, nuclear 1.00, either wind endpoint: bracket **.50–.625**.
- Coal .75, nuclear 1.00, wind 0: bracket **.50–.625**; wind 1: zero gap already at lowest tested gas .50.
- Coal 1.00, nuclear 1.00, both wind endpoints: zero gap already at lowest tested gas .50.

These are **sampled discrete brackets**, not continuous fitted thresholds or empirically measured probability bands. For combinations where gas .50 already yields zero gap, the lower transition is **not identified**, not zero by assumption.

## Implications

1. The original **joint thermal factor** pooled gas, coal and nuclear and obscured the contribution of each assumed resource group.
2. Decoupling gas/coal/nuclear reveals that nuclear availability, gas availability, coal availability and wind assumptions all affect the modeled gap in the near-critical parameter space.
3. The current evidence supports a reproducible *stress-screening methodology and assumption transparency*, not a finding about real thermal outages due to heat, 2024 reliability, or future climate risk.
4. Next analyze the remaining boundary uncertainty (annual nameplate versus BA controllability; excluded storage and fuels) and introduce independent temperature, wind-speed or irradiance inputs only where temporally and geographically verified. Separate actual heat response calibration from abstract scenario derating.

**History-calibrated reliability: NO. Observed outages or EENS: NO. Causal climate attribution: NO.**
