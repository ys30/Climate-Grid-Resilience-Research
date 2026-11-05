"""Independent old-weather / canonical-demand first-week factorial replay.

Exactly the same model parameters, annual partial fleet and assumed links
from the source-certified 4-week output. Refuse any unequal weather or BA
start-hour demand before claiming exact-input parity. This does not validate
historical electricity shortages or real thermal availability.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from grid_resilience.research_run import run as run_factorial

BAS=("AZPS","BPAT","CISO","SRP")
CASES=("baseline","heat_only","wind_only","heat_wind")


def source_parity(original_weather,canonical_weather,canonical_demand):
    keys=["timestamp","ba"]
    records=[]
    for label,frame,fields in (("legacy_weather",original_weather,
          ["temperature_c","wind_availability"]),
          ("canonical_weather",canonical_weather,
          ["temperature_c","wind_availability"]),
          ("canonical_demand",canonical_demand,["demand_mw"])):
        if not set(keys+fields).issubset(frame):
            raise ValueError(f"Incomplete {label} source schema")
        x=frame.copy()
        x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="raise")
        if len(x)!=672 or x.duplicated(keys).any() or set(x.ba)!=set(BAS):
            raise ValueError(f"Invalid {label} 4-BA 168h source keys")
        for ba,g in x.groupby("ba"):
            expected=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
            if not pd.DatetimeIndex(g.timestamp.sort_values()).equals(expected):
                raise ValueError(f"Nonidentical {label} UTC hourly model calendar")
        records.append(x)
    old,w,d=records
    matched=old.merge(w,on=keys,validate="one_to_one",suffixes=("_legacy","_canonical"))
    for field in ("temperature_c","wind_availability"):
        if not np.array_equal(
            pd.to_numeric(matched[field+"_legacy"]).to_numpy(float),
            pd.to_numeric(matched[field+"_canonical"]).to_numpy(float)):
            raise ValueError(f"Original weather does not match canonical {field} source")
    if not np.isfinite(d.demand_mw.to_numpy(dtype=float)).all():
        raise ValueError("Missing source official demand")
    return {"weather_source_hour_exact_pairs":len(matched),
            "independent_four_ba_hour_observations":672,
            "canonical_demand_source_hour_pairs":len(d),
            "source_hour_clock":"2024 July 1–7 UTC model start-hour",
            "source_weather_exact_match":True,
            "missing_source_interpolation":False}


def replay(old_weather,new_weather,demand,capacity,links,benchmark,output):
    evidence=source_parity(old_weather,new_weather,demand)
    target=Path(output);target.mkdir(parents=True,exist_ok=True)
    w=target/"verified_legacy_weather.csv"
    d=target/"verified_canonical_demand.csv"
    old_weather.to_csv(w,index=False)
    demand.to_csv(d,index=False)
    outcomes=[]
    for variant,source in links.items():
        dest=target/variant
        report=run_factorial(d,w,capacity,source,dest,
            "JULY2024_WEEK_1",f"fourba_partial_fleet_{variant}","hypothetical")
        if report["input_validation"]["hours"]!=168:
            raise ValueError("Replay actual source event must be exactly 168 hours")
        result=pd.read_csv(dest/"solved/factorial_dispatch.csv")
        result["network_variant"]=variant
        outcomes.append(result)
    frame=pd.concat(outcomes,ignore_index=True)
    keys=["event_id","network_variant","scenario","ba"]
    expected=benchmark.loc[benchmark.event_id.eq("JULY2024_WEEK_1")].copy()
    if len(frame)!=32 or len(expected)!=32 or frame.duplicated(keys).any() or expected.duplicated(keys).any():
        raise ValueError("Original baseline and rerun matched PyPSA 4-case source records incomplete")
    compared=frame.merge(expected,on=keys,validate="one_to_one",suffixes=("_replayed","_canonical"))
    if len(compared)!=32:
        raise ValueError("Canonical first-week source scenario records not identical")
    for col in ("unserved_energy_mwh","shortage_hours","peak_shortfall_mw"):
        x=compared[col+"_replayed"].to_numpy(float)
        y=compared[col+"_canonical"].to_numpy(float)
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("Nonfinite scenario output")
        compared[col+"_absolute_discrepancy"]=np.abs(x-y)
    # Require tight tolerance for two equivalent deterministic solves.
    # Do not silently replace any existing evidence with new results.
    mismatch=compared.unserved_energy_mwh_absolute_discrepancy.gt(.01).any()
    evidence.update({
        "factorial_scenario_ba_results_compared":len(compared),
        "max_unserved_energy_absolute_replay_error_mwh":float(
            compared.unserved_energy_mwh_absolute_discrepancy.max()),
        "all_scenario_unserved_energy_replayed_within_0_01_mwh":bool(not mismatch),
        "result_is_physical_generator_calibration":False,
        "results_are_historical_observed_eens":False,
        "legacy_unshifted_eia_demand_used":False,
        "same_partial_fleet_and_hypothetical_links":True
    })
    compared.to_csv(target/"corrected_legacy_weather_vs_official_source_firstweek_replay.csv",index=False)
    (target/"canonical_firstweek_factorial_replay_manifest.json").write_text(
        json.dumps(evidence,indent=2)+"\n")
    print(json.dumps(evidence,indent=2))
    if mismatch:
        raise ValueError("Original weather plus canonical EIA demand did not reproduce known four-week first-week PyPSA model output")
    return compared,evidence


def main():
    p=argparse.ArgumentParser()
    for arg in ("legacy-weather","canonical-weather","canonical-demand",
                "capacity","isolated-links","linked-links","baseline","output"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    replay(pd.read_csv(a.legacy_weather),pd.read_csv(a.canonical_weather),
           pd.read_csv(a.canonical_demand),a.capacity,
           {"isolated":a.isolated_links,"links_10pct":a.linked_links},
           pd.read_csv(a.baseline),a.output)


if __name__=="__main__":
    main()
