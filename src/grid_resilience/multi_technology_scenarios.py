"""Matched climate perturbations for the isolated multi-technology model.

Produces scenario-specific input CSVs without modifying the historic solver.
Temperature and wind response functions are explicit assumptions, not
empirically fitted impacts. All four runs use identical BA/hour inventories.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

SCENARIOS = {
    "baseline": (0., 0.),
    "heat_only": (4., 0.),
    "wind_only": (0., .30),
    "heat_wind": (4., .30),
}

def prepare_scenarios(demand_csv, weather_csv, availability_csv, output_dir,
                      heat_coefficient=.012, threshold_c=30.):
    if not 0 <= heat_coefficient <= 1:
        raise ValueError("Heat coefficient must be in [0,1]")
    demand = pd.read_csv(demand_csv)
    weather = pd.read_csv(weather_csv)
    avail = pd.read_csv(availability_csv)
    schemas = (
        (demand, {"timestamp","ba","demand_mw"}),
        (weather, {"timestamp","ba","temperature_c"}),
        (avail, {"timestamp","ba","technology","availability_pu"}),
    )
    for frame, schema in schemas:
        if frame.empty or not schema.issubset(frame) or frame[list(schema)].isna().any().any():
            raise ValueError("Missing or invalid climate input schema")
    for frame, keys in ((demand,["timestamp","ba"]),
                        (weather,["timestamp","ba"]),
                        (avail,["timestamp","ba","technology"])):
        if frame.duplicated(keys).any():
            raise ValueError("Duplicate BA-hour or technology-hour")
        frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True, errors="raise")
    if set(map(tuple,demand[["timestamp","ba"]].itertuples(index=False,name=None))) != set(
            map(tuple,weather[["timestamp","ba"]].itertuples(index=False,name=None))):
        raise ValueError("Weather and demand BA-hour coverage mismatch")
    demand["demand_mw"] = pd.to_numeric(demand.demand_mw, errors="raise")
    weather["temperature_c"] = pd.to_numeric(weather.temperature_c, errors="raise")
    avail["availability_pu"] = pd.to_numeric(avail.availability_pu, errors="raise")
    for series, label in ((demand.demand_mw,"demand"),
                          (weather.temperature_c,"temperature"),
                          (avail.availability_pu,"availability")):
        if not series.map(lambda x: -float("inf") < float(x) < float("inf")).all():
            raise ValueError(f"Nonfinite {label}")
    if (demand.demand_mw < 0).any() or not avail.availability_pu.between(0,1).all():
        raise ValueError("Invalid demand or availability bounds")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    merged = demand.merge(weather, on=["timestamp","ba"], validate="one_to_one")
    result = {}
    for scenario,(heat,wind_loss) in SCENARIOS.items():
        d = merged[["timestamp","ba","demand_mw"]].copy()
        excess_old = (merged.temperature_c - threshold_c).clip(lower=0)
        excess_new = (merged.temperature_c + heat - threshold_c).clip(lower=0)
        d["demand_mw"] *= 1 + heat_coefficient * (excess_new-excess_old)
        a = avail.copy()
        a.loc[a.technology.eq("wind"),"availability_pu"] *= 1-wind_loss
        folder = out / scenario
        folder.mkdir(exist_ok=True)
        d.to_csv(folder/"demand.csv",index=False)
        a.to_csv(folder/"availability.csv",index=False)
        result[scenario] = {"heat_increment_c":heat, "wind_availability_loss":wind_loss}
    manifest = {"classification":"assumed_matched_scenario_inputs_not_calibrated",
                "scenarios":result,"heat_coefficient":heat_coefficient,
                "threshold_c":threshold_c,
                "warning":"No empirically calibrated demand response or technology outage forcing."}
    (out/"scenario_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for name in ("demand","weather","availability","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(prepare_scenarios(a.demand,a.weather,a.availability,a.output),indent=2))

if __name__=="__main__":
    main()
