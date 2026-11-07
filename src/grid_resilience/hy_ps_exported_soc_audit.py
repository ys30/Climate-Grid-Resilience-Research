"""Independent post-solver audit of exported 672h HY/PS screening trajectories.

Does not use PyPSA variables or turn synthetic PS parameters into historical
unit observations. All time steps are one hour and all energy units MWh.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = {"resource_scenario", "scenario", "timestamp",
            "hydro_optimized_mw", "ps_charge_mw",
            "ps_discharge_delivered_mw", "ps_soc_mwh"}
SCENARIOS = {"baseline", "heat_only", "wind_only", "heat_wind"}


def audit_exported_hourly(frame, specs, hydro_budget_mwh=598947.6, hydro_power_mw=2000.0):
    """Validate a 672-hour scenario-by-scenario exported result dataset.

    specs is a dict: scenario label -> (assumed PS MW, assumed MWh, roundtrip).
    """
    if not REQUIRED.issubset(frame.columns):
        raise ValueError("Missing exported HY/PS fields")
    if not specs or not np.isfinite([hydro_budget_mwh, hydro_power_mw]).all():
        raise ValueError("Missing audit assumptions")
    if hydro_budget_mwh < 0 or hydro_power_mw < 0:
        raise ValueError("Negative HY assumptions")
    expected_hours = pd.date_range("2024-07-01T00:00:00Z", periods=672, freq="h")
    if set(frame.resource_scenario) != set(specs) or set(frame.scenario) != SCENARIOS:
        raise ValueError("Incomplete scenario grid")
    if len(frame) != len(specs) * 4 * 672:
        raise ValueError("Incomplete hourly record count")
    reports = []
    for (label, scenario), block in frame.groupby(["resource_scenario", "scenario"]):
        if len(block) != 672:
            raise ValueError("Incomplete 672h group")
        g = block.copy()
        g["timestamp"] = pd.to_datetime(g["timestamp"], utc=True, errors="raise")
        if g.timestamp.duplicated().any():
            raise ValueError("Duplicated scenario hour")
        g = g.sort_values("timestamp")
        if not pd.DatetimeIndex(g.timestamp).equals(expected_hours):
            raise ValueError("Incorrect 672h UTC calendar")
        numeric = ["hydro_optimized_mw", "ps_charge_mw",
                   "ps_discharge_delivered_mw", "ps_soc_mwh"]
        x = {k: pd.to_numeric(g[k], errors="coerce").to_numpy(float) for k in numeric}
        if any(not np.isfinite(arr).all() for arr in x.values()):
            raise ValueError("Missing or nonfinite optimized hourly values")
        hydro, charge, discharge, soc = (x[k] for k in numeric)
        power, energy, roundtrip = map(float, specs[label])
        if not np.isfinite([power, energy, roundtrip]).all() or power < 0 or energy < 0 or not (0 < roundtrip <= 1):
            raise ValueError("Invalid counterfactual PS configuration")
        if (power == 0) != (energy == 0):
            raise ValueError("PS zero-power and zero-energy must agree")
        tol = 0.11
        if hydro.min() < -tol or hydro.max() > hydro_power_mw+tol or hydro.sum() > hydro_budget_mwh+tol:
            raise ValueError("HY power or single-horizon budget violation")
        if min(charge.min(), discharge.min(), soc.min()) < -tol:
            raise ValueError("Negative PS operation or SOC")
        if charge.max() > power+tol or discharge.max() > power+tol or soc.max() > energy+tol:
            raise ValueError("PS power or capacity violation")
        if abs(soc[-1]) > tol:
            raise ValueError("Nonzero terminal SOC")
        if power == 0:
            if max(abs(charge).max(), abs(discharge).max(), abs(soc).max()) > tol:
                raise ValueError("Zero-PS configuration contains operation")
        else:
            eta = np.sqrt(roundtrip)
            residual = np.diff(np.r_[0.0, soc]) - (eta*charge - discharge/eta)
            if np.max(np.abs(residual)) > tol:
                raise ValueError("PS hourly energy conservation violation")
            if abs(discharge.sum() - roundtrip*charge.sum()) > tol:
                raise ValueError("Closed-cycle electrical energy mismatch")
        reports.append({
            "resource_scenario": label, "scenario": scenario,
            "hours": 672, "hydro_total_mwh": float(hydro.sum()),
            "assumed_ps_charge_power_mw": power,
            "assumed_ps_usable_energy_mwh": energy,
            "assumed_ps_roundtrip_efficiency": roundtrip,
            "ps_total_charge_mwh": float(charge.sum()),
            "ps_total_discharge_mwh": float(discharge.sum()),
            "ps_final_soc_mwh": float(soc[-1]),
            "energy_balance_audited": True,
            "historically_calibrated": False
        })
    return {"groups_checked": len(reports), "hours_per_group": 672,
            "model_source_scope": "four-BA isolated incomplete-fleet screening",
            "measured_ps_equipment_operation": False,
            "historical_eens_identified": False, "groups": reports}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hourly", required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    scope = json.loads(Path(args.scope).read_text())
    specs = {}
    for row in scope["ps_sensitivity_configurations"]:
        power, energy, eta = map(float, row)
        label = f"PS_{int(power)}MW_{int(energy)}MWh_eta{int(eta*100)}"
        specs[label] = (power, energy, eta)
    out = audit_exported_hourly(pd.read_csv(args.hourly), specs)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, indent=2)+chr(10))
    print("INDEPENDENT EXPORTED HY/PS SOC CONSERVATION AUDIT:", out["groups_checked"], "groups")


if __name__ == "__main__":
    main()
