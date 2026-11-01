"""Explain scenario shortfalls against audited, nameplate-based BA margins.

Diagnostic only: capacity assumptions exclude storage, imports and generator
hourly constraints. Margin is not an operational reserve-margin estimate.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(demand_csv,capacity_csv,shortfall_csv,output):
    d=pd.read_csv(demand_csv)
    c=pd.read_csv(capacity_csv)
    s=pd.read_csv(shortfall_csv)
    for frame,fields in ((d,{"ba","demand_mw"}),(c,{"ba","capacity_mw"}),(s,{"ba","scenario","availability_fraction_assumed","unserved_energy_mwh"})):
        if not fields.issubset(frame):raise ValueError("Missing margin audit columns")
    if d.empty or c.empty or s.empty:raise ValueError("Empty input")
    for frame,field in ((d,"demand_mw"),(c,"capacity_mw"),(s,"availability_fraction_assumed"),(s,"unserved_energy_mwh")):
        frame[field]=pd.to_numeric(frame[field],errors="raise")
        if not frame[field].map(lambda x:float("-inf")<float(x)<float("inf")).all():raise ValueError("Nonfinite audit input")
    peak=d.groupby("ba").demand_mw.max().rename("peak_reported_demand_mw")
    installed=c.groupby("ba").capacity_mw.sum().rename("included_nameplate_mw")
    if set(peak.index)!=set(installed.index) or set(s.ba)!=set(peak.index):
        raise ValueError("BA sets mismatch")
    if s.duplicated(["ba","scenario"]).any():raise ValueError("Duplicate scenario BA")
    if (s.availability_fraction_assumed<=0).any() or (s.availability_fraction_assumed>1).any():
        raise ValueError("Invalid assumed availability")
    rows=s.join(peak,on="ba").join(installed,on="ba")
    rows["assumed_available_mw"]=rows.included_nameplate_mw*rows.availability_fraction_assumed
    rows["peak_capacity_margin_mw"]=rows.assumed_available_mw-rows.peak_reported_demand_mw
    rows["capacity_to_peak_demand_ratio"]=rows.included_nameplate_mw/rows.peak_reported_demand_mw
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows.sort_values(["ba","availability_fraction_assumed"],ascending=[True,False]).to_csv(out/"screening_ba_capacity_margin.csv",index=False)
    manifest={"ba_count":len(peak),"case_rows":len(rows),
              "historical_calibration_certified":False,
              "warning":"Scenario-wide capacity/peak arithmetic assumes uniform availability; excludes imports, storage and intra-month variation. Neither verified reserve margins nor weather-related outages."}
    (out/"screening_ba_capacity_margin_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for key in ("demand","capacity","shortfall","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    print(json.dumps(audit(a.demand,a.capacity,a.shortfall,a.output),indent=2))
if __name__=="__main__":main()
