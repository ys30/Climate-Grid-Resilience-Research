"""Conservative quality gate for partial-fleet factorial adequacy screening.

This is a *disclosure* gate, not physical calibration or a reliability standard.
It deliberately fails closed if the excluded-capacity inventory is unavailable.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

SCENARIOS = {"baseline", "heat_only", "wind_only", "heat_wind"}

def assess(dispatch_csv, capacity_csv, excluded_csv, output_json,
           max_baseline_fraction=0.01, max_excluded_fraction=0.05):
    for name, value in (("max_baseline_fraction", max_baseline_fraction),
                        ("max_excluded_fraction", max_excluded_fraction)):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must lie in [0, 1]")
    d = pd.read_csv(dispatch_csv)
    c = pd.read_csv(capacity_csv)
    e = pd.read_csv(excluded_csv)
    if not {"scenario", "ba", "unserved_energy_mwh"}.issubset(d):
        raise ValueError("Dispatch requires scenario, ba and unserved_energy_mwh")
    if not {"ba", "gas_mw", "wind_mw"}.issubset(c):
        raise ValueError("Capacity requires ba, gas_mw and wind_mw")
    if not {"ba", "technology", "capacity_mw"}.issubset(e):
        raise ValueError("Excluded inventory requires ba, technology and capacity_mw")
    if d.empty or c.empty or c.ba.duplicated().any() or d.duplicated(["scenario", "ba"]).any():
        raise ValueError("Missing or duplicate capacity/dispatch groups")
    bas = set(c.ba)
    if set(d.ba) != bas or set(d.scenario) != SCENARIOS:
        raise ValueError("Dispatch BA or scenario coverage mismatch")
    if len(d) != len(bas) * len(SCENARIOS) or not set(e.ba).issubset(bas):
        raise ValueError("Incomplete factorial matrix or unknown excluded BA")
    for frame, fields in ((d, ["unserved_energy_mwh"]),
                          (c, ["gas_mw", "wind_mw"]), (e, ["capacity_mw"])):
        for field in fields:
            frame[field] = pd.to_numeric(frame[field], errors="raise")
            if not frame[field].notna().all() or not (frame[field] >= 0).all():
                raise ValueError(f"Nonfinite/negative or missing {field}")
            if not pd.Series(frame[field]).map(lambda x: float(x) < float("inf")).all():
                raise ValueError(f"Nonfinite {field}")
    included = float(c[["gas_mw", "wind_mw"]].sum().sum())
    omitted = float(e.capacity_mw.sum())
    if included + omitted <= 0:
        raise ValueError("Total inventoried nameplate must be positive")
    excluded_fraction = omitted / (included + omitted)
    baseline_mwh = float(d.loc[d.scenario == "baseline", "unserved_energy_mwh"].sum())
    # Without hourly demand, a baseline-shortfall fraction cannot be calculated.
    # This gate therefore does NOT silently treat EENS / installed capacity as a ratio.
    report = {
        "classification": "partial_fleet_screening_not_calibrated",
        "bas": sorted(bas),
        "baseline_unserved_energy_mwh": baseline_mwh,
        "included_nameplate_mw": included,
        "excluded_nameplate_mw": omitted,
        "excluded_nameplate_fraction": excluded_fraction,
        "thresholds": {"max_excluded_fraction": max_excluded_fraction,
                       "max_baseline_fraction": max_baseline_fraction},
        "baseline_energy_fraction": None,
        "pass_for_historical_reliability_claims": False,
        "blocking_reasons": [
            "No independently benchmarked historical generation or observed intertie ratings",
            "No hourly load totals supplied: baseline unserved-energy fraction cannot be assessed"
        ],
    }
    if excluded_fraction > max_excluded_fraction:
        report["blocking_reasons"].append("Omitted nameplate exceeds screening tolerance")
    if baseline_mwh > 0:
        report["blocking_reasons"].append("Positive baseline modeled unserved energy")
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dispatch", required=True)
    p.add_argument("--capacity", required=True)
    p.add_argument("--excluded", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max-excluded-fraction", type=float, default=0.05)
    a = p.parse_args()
    print(json.dumps(assess(a.dispatch, a.capacity, a.excluded, a.output,
                            max_excluded_fraction=a.max_excluded_fraction), indent=2))

if __name__ == "__main__":
    main()
