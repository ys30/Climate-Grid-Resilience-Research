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
           max_baseline_fraction=0.01, max_excluded_fraction=0.05, demand_csv=None):
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
    for name, frame in (("dispatch", d), ("capacity", c), ("excluded", e)):
        if frame.ba.isna().any() or frame.ba.astype(str).str.strip().eq("").any():
            raise ValueError(f"{name}: missing BA label")
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
    baseline_fraction = None
    if demand_csv is not None:
        demand = pd.read_csv(demand_csv)
        if not {"timestamp", "ba", "demand_mw"}.issubset(demand):
            raise ValueError("Demand requires timestamp, ba, demand_mw")
        if demand.empty or demand[["timestamp", "ba"]].isna().any().any() or demand.duplicated(["timestamp", "ba"]).any():
            raise ValueError("Missing or duplicate demand BA-hour rows")
        if set(demand.ba) != bas:
            raise ValueError("Demand BA coverage mismatch")
        demand["demand_mw"] = pd.to_numeric(demand.demand_mw, errors="raise")
        if not demand.demand_mw.map(lambda x: 0 < float(x) < float("inf")).all():
            raise ValueError("Demand must be positive and finite")
        hours = set(demand.timestamp)
        if any(set(group.timestamp) != hours for _, group in demand.groupby("ba")):
            raise ValueError("Incomplete hourly demand panel")
        times = pd.DatetimeIndex(sorted(pd.to_datetime(list(hours), utc=True, errors="raise")))
        if len(times) > 1 and not (times[1:] - times[:-1] == pd.Timedelta(hours=1)).all():
            raise ValueError("Demand timestamps must be contiguous hours")
        total_load_mwh = float(demand.demand_mw.sum())
        if baseline_mwh > total_load_mwh + 1e-6:
            raise ValueError("Baseline shortfall exceeds total demand energy")
        baseline_fraction = baseline_mwh / total_load_mwh
    # Missing denominator is unknown, never zero.
    report = {
        "classification": "partial_fleet_screening_not_calibrated",
        "bas": sorted(bas),
        "baseline_unserved_energy_mwh": baseline_mwh,
        "included_nameplate_mw": included,
        "excluded_nameplate_mw": omitted,
        "excluded_nameplate_fraction": excluded_fraction,
        "thresholds": {"max_excluded_fraction": max_excluded_fraction,
                       "max_baseline_fraction": max_baseline_fraction},
        "baseline_energy_fraction": baseline_fraction,
        "pass_for_historical_reliability_claims": False,
        "blocking_reasons": [
            "No independently benchmarked historical generation or observed intertie ratings",
        ],
    }
    if baseline_fraction is None:
        report["blocking_reasons"].append("No hourly load totals supplied: baseline unserved-energy fraction cannot be assessed")
    elif baseline_fraction > max_baseline_fraction:
        report["blocking_reasons"].append("Baseline shortage fraction exceeds screening tolerance")
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
    p.add_argument("--max-baseline-fraction", type=float, default=0.01)
    p.add_argument("--demand", default=None)
    a = p.parse_args()
    print(json.dumps(assess(a.dispatch, a.capacity, a.excluded, a.output,
                            max_excluded_fraction=a.max_excluded_fraction,
                            max_baseline_fraction=a.max_baseline_fraction,
                            demand_csv=a.demand), indent=2))

if __name__ == "__main__":
    main()
