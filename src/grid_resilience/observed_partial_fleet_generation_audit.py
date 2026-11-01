"""Compare July 2024 modeled *partial-fleet* BA generation to reported EIA-930 NG.

This is a descriptive mismatch diagnostic, NOT a calibration of total BA fleet.
"""
import argparse
import json
import os
from pathlib import Path
import pandas as pd
from .eia930_hourly import fetch

BAS=("AZPS","SRP")
SCENARIOS=("baseline","heat_wind")

def run(artifact, output, api_key):
    root=Path(artifact)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(root/"demand.csv")
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True)
    times=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if len(times)!=168 or not (times[1:]-times[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Expected exactly 168 consecutive matched observed demand hours")
    if not set(BAS).issubset(set(d.ba)):
        raise ValueError("Missing eligible BA")
    ng,meta=fetch(BAS,times[0].isoformat(),(times[-1]+pd.Timedelta(hours=1)).isoformat(),api_key,data_type="NG")
    ng=ng.rename(columns={"demand_mw":"observed_eia930_ng_mw"})
    rows=[]
    technology_rows=[]
    for scenario in SCENARIOS:
        path=root/"no_storage"/"solved"/scenario/"generation_hourly.csv"
        mod=pd.read_csv(path)
        mod["timestamp"]=pd.to_datetime(mod.timestamp,utc=True)
        if mod.duplicated(["timestamp","ba","technology"]).any():
            raise ValueError("Duplicate modeled generation")
        if not {"gas","wind"}.issubset(set(mod.technology)):
            raise ValueError("Missing partial fleet technology")
        mod=mod[mod.ba.isin(BAS)].copy()
        bytech=mod.groupby(["ba","technology"],as_index=False).generation_mwh.sum()
        bytech["scenario"]=scenario
        technology_rows.append(bytech)
        mod=mod.groupby(["timestamp","ba"],as_index=False).generation_mwh.sum()
        matched=ng.merge(mod,on=["timestamp","ba"],how="outer",validate="one_to_one",indicator=True)
        if len(matched)!=336 or not matched._merge.eq("both").all():
            raise ValueError("Incomplete modeled-vs-observed BA hour match")
        matched=matched.drop(columns="_merge")
        matched["scenario"]=scenario
        matched["partial_fleet_minus_observed_ng_mw"]=matched.generation_mwh-matched.observed_eia930_ng_mw
        matched["absolute_difference_mw"]=matched.partial_fleet_minus_observed_ng_mw.abs()
        rows.append(matched)
    by_technology=pd.concat(technology_rows,ignore_index=True)
    by_technology.to_csv(out/"partial_fleet_generation_by_technology.csv",index=False)
    hourly=pd.concat(rows,ignore_index=True).sort_values(["scenario","ba","timestamp"])
    hourly.to_csv(out/"partial_fleet_vs_observed_ng_hourly.csv",index=False)
    stats=[]
    for (scenario,ba),frame in hourly.groupby(["scenario","ba"]):
        denominator=frame.observed_eia930_ng_mw.abs().sum()
        stats.append({"scenario":scenario,"ba":ba,"matched_hours":len(frame),
                      "reported_ng_mwh":float(frame.observed_eia930_ng_mw.sum()),
                      "modeled_partial_fleet_mwh":float(frame.generation_mwh.sum()),
                      "difference_mwh":float(frame.partial_fleet_minus_observed_ng_mw.sum()),
                      "mae_mw":float(frame.absolute_difference_mw.mean()),
                      "wape_descriptive":float(frame.absolute_difference_mw.sum()/denominator) if denominator>0 else None,
                      "historical_calibration_certified":False})
    summary=pd.DataFrame(stats)
    assert len(summary)==4 and summary.matched_hours.eq(168).all()
    summary.to_csv(out/"partial_fleet_vs_observed_ng_summary.csv",index=False)
    (out/"manifest.json").write_text(json.dumps({
        "status":"diagnostic_only","eligible_arithmetic_gate_bas":["AZPS","SRP"],
        "scope":"isolated BA, generic-thermal-proxy-labeled-gas plus wind generation, no storage",
        "gas_label_is_verified_fuel":False,
        "thermal_capacity_source":"GENERIC_THERMAL_PROXY from upstream observed-storage workflow",
        "thermal_availability_assumption":"100 percent hourly availability",
        "reported_generation_is_entire_BA_not_same_fleet":True,
        "weather_scenarios_are_counterfactual":True,
        "not_a_full_fleet_error_metric":True,
        "historical_calibration_certified":False,"api_metadata":meta},indent=2)+"\\n")
    print("CAUTION: gas label is a generic thermal proxy, NOT verified BA gas generation")
    print("PARTIAL FLEET MODELLED TECHNOLOGY MIX (not whole-BA composition):")
    print(by_technology.to_string(index=False))
    print(summary.to_string(index=False))
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    run(a.artifact,a.output,os.getenv("EIA_API_KEY"))

if __name__=="__main__":main()
