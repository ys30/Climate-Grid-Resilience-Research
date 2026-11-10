"""Paper C Grand Coulee: separate hypothetical 672h PS model from observed pump use.

Distinct labeled axes, original CI-backed data, and fail-closed source scopes.
Neither the plotted model nor the USACE whole-project pump energy establishes
PG7-PG12 historical pumping or grid adequacy/EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

FRACTIONS = (0.0, 0.25, 0.5, 1.0)
CASES = ("baseline", "heat_only", "wind_only", "heat_wind")


def verify(model, assumptions, observed):
    req = {"resource_scenario", *CASES, "compound_interaction_mwh"}
    if not req.issubset(model) or len(model) != 4:
        raise ValueError("Missing four model access-fraction scenarios")
    if assumptions.get("hypothetical_available_PS_fraction_of_nameplate") != list(FRACTIONS):
        raise ValueError("Hypothetical access fractions mismatch")
    if (abs(float(assumptions.get("original_eia860_six_ps_2024_nameplate_mw", -1)) - 314) > 1e-5
            or assumptions.get("water_allocation_fraction_observed") is not False
            or assumptions.get("source_energy_capacity_MWh_observed") is not False
            or assumptions.get("historical_real_blackouts_or_avoided_EENS") is not False
            or assumptions.get("counterfactual_model_is_four_isolated_BA_incomplete_fleet") is not True):
        raise ValueError("Historical PS model source/scope not admitted")
    if len(model.resource_scenario.unique()) != 4:
        raise ValueError("Model scenario keys not unique")
    # The 78.5 MW fraction is rounded to PS_78MW in archived scenario names.\n    # The scenario is named by assumed PS MW; permit documented suffixes,
    # but require an unambiguous 0 / 78.5 / 157 / 314 MW mapping.
    expected_mw = (0, 78, 157, 314)
    keys = model.resource_scenario.astype(str).tolist()
    matches = []
    import re
    for k in keys:
        # Parse only the MW part; the MWh field must not masquerade as a second MW setting.
        match = re.fullmatch(r"PS_(\\d+)MW_\\d+MWh_eta\\d+", k)
        if match is None:
            raise ValueError(f"Malformed original PS scenario identifier: {k}")
        value_mw = float(match.group(1))
        candidates = [i for i, mw in enumerate(expected_mw) if abs(value_mw - mw) < 0.001]
        if len(candidates) != 1:
            raise ValueError(f"Ambiguous PS scenario naming: {k}")
        matches.append(candidates[0])
    if len(set(matches)) != 4:
        raise ValueError("Duplicate/missing assumed PS power settings")
    ordered = model.assign(fraction_index=matches).sort_values("fraction_index").reset_index(drop=True)
    for _, row in ordered.iterrows():
        values = np.array([float(row[c]) for c in CASES], dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError("Nonfinite or negative modeled supply gap")
        interaction = values[3] - values[1] - values[2] + values[0]
        if abs(interaction - float(row.compound_interaction_mwh)) > 0.001:
            raise ValueError("Source factorial arithmetic mismatch")
    if abs(float(ordered.iloc[0].baseline) - 1508297.366980) > 0.05:
        raise ValueError("Source scenario model baseline anchor unexpectedly changed")
    if abs(float(ordered.iloc[-1].baseline) - 1480655.729555) > 0.05:
        raise ValueError("Source 314MW model baseline anchor unexpectedly changed")
    x = observed.copy()
    required = {"date", "usace_banks_lake_pumping_electricity_mwh"}
    if not required.issubset(x):
        raise ValueError("Original USACE pumping columns absent")
    x["date"] = pd.to_datetime(x.date)
    x = x.sort_values("date")
    expected = pd.date_range("2024-07-01", periods=31, freq="D")
    if not x.date.reset_index(drop=True).equals(pd.Series(expected, name="date")):
        raise ValueError("Source USACE July daily cohort incomplete")
    v = pd.to_numeric(x.usace_banks_lake_pumping_electricity_mwh, errors="coerce")
    if not np.isfinite(v).all() or (v < 0).any():
        raise ValueError("USACE pumping observations missing/invalid")
    if abs(v.sum() - 175641) > 0.001 or abs(v.iloc[:28].sum() - 169160) > 0.001:
        raise ValueError("USACE independently audited project-wide source totals changed")
    return ordered, x


def render(model, observed, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(10.2, 8.6))
    ax1 = fig.add_axes([0.12, 0.62, 0.82, 0.31])
    ax2 = fig.add_axes([0.12, 0.24, 0.82, 0.27])
    fractions = [0, 25, 50, 100]
    reduced = (model.iloc[0].baseline - model.baseline.to_numpy(float)) / 1000
    ax1.plot(fractions, reduced, "o-", color="#527f9a", lw=2.0, markersize=6)
    for xp, yp in zip(fractions, reduced):
        ax1.annotate(f"{yp:.1f}", (xp, yp), xytext=(0, 6),
                     textcoords="offset points", ha="center", fontsize=9)
    ax1.set_xticks(fractions, ["0%", "25%", "50%", "100%"])
    ax1.set_ylabel("Reduction in modeled baseline gap\nrelative to no-PS case (10³ MWh)")
    ax1.set_title("A | Model: assumed access to 314 MW reversible-generator nameplate", loc="left")
    ax1.set_ylim(bottom=-2)
    ax1.grid(alpha=0.2)
    ax1.set_axisbelow(True)

    days = np.arange(1, 32)
    pump = observed.usace_banks_lake_pumping_electricity_mwh.to_numpy(float)
    ax2.bar(days[:28], pump[:28], color="#6e8d81", width=0.85, label="Within 672h model calendar")
    ax2.bar(days[28:], pump[28:], color="#b8b7ad", width=0.85, label="July 29–31, outside model calendar")
    ax2.axvline(28.5, color="#575757", linestyle="--", lw=1)
    ax2.set_xticks([1, 5, 10, 15, 20, 25, 28, 31])
    ax2.set_xlim(0, 32)
    ax2.set_xlabel("July 2024 calendar day")
    ax2.set_ylabel("Observed whole-project pumping (MWh/day)")
    ax2.set_title("B | Observation: USACE Banks Lake installation-wide pump electricity", loc="left")
    ax2.legend(frameon=False, fontsize=8, ncol=2)
    ax2.grid(axis="y", alpha=0.2)
    ax2.set_axisbelow(True)

    fig.text(0.12, 0.12,
             "Different evidence scopes: Model A assumes 4h storage, 80% roundtrip efficiency, symmetric PS power, "
             "partial fleet and isolated BAs.\n"
             "Observation B includes dedicated irrigation pumps and reversible equipment; it cannot identify "
             "PG7–PG12 charging, PS SOC or irrigation access.\n"
             "No physical electricity adequacy, observed outages, avoided EENS or calibrated reservoir-energy inference.",
             fontsize=8, va="top")
    fig.savefig(out / "paper_c_grand_coulee_model_vs_observed_context.png", dpi=250)
    fig.savefig(out / "paper_c_grand_coulee_model_vs_observed_context.pdf")
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    for name in ("model", "assumptions", "observed", "output"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    model, observed = verify(pd.read_csv(a.model),
                             json.loads(Path(a.assumptions).read_text()),
                             pd.read_csv(a.observed))
    render(model, observed, a.output)
    result = {
        "source_verified_2024_original_generator_nameplate_mw": 314,
        "model_ps_fraction_assumptions": list(FRACTIONS),
        "model_baseline_reductions_mwh": [
            round(float(model.iloc[0].baseline - val), 6) for val in model.baseline
        ],
        "observed_project_pumping_july_1_28_mwh": 169160,
        "observed_project_pumping_july_1_31_mwh": 175641,
        "model_access_fraction_is_observed": False,
        "observed_project_pumping_is_pg7_pg12_only": False,
        "historical_eens_calibrated": False,
    }
    (Path(a.output) / "paper_c_grand_coulee_model_observation_scope.json").write_text(
        json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
