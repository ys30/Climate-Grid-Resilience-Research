"""Audit observed BPAT wind output to flag unrealistic assumed full availability.

EIA-930 reported net generation and EIA-860 operable nameplate are not an
independently calibrated generation-availability relationship.
"""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pandas as pd
from .eia930_fuel_decomposition import FMT

def audit(balance,capacity,output):
    inventory=pd.read_csv(capacity)
    wind=inventory[(inventory.ba=="BPAT")&(inventory.technology=="wind")]
    if len(wind)!=1:raise ValueError("Missing unique BPAT wind group")
    cap=float(wind.iloc[0].nameplate_capacity_mw)
    if cap<=0:raise ValueError("Invalid BPAT wind nameplate")
    values=[];seen=set()
    with Path(balance).open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        col="Net Generation (MW) from Wind"
        if col not in (rd.fieldnames or []):raise ValueError("Missing official wind generation field")
        for row in rd:
            if row["Balancing Authority"].strip()!="BPAT":continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not datetime(2024,2,1,tzinfo=timezone.utc)<=t<datetime(2024,3,1,tzinfo=timezone.utc):continue
            if t in seen:raise ValueError("Duplicate BPAT hour")
            seen.add(t)
            v=row[col].strip()
            if not v:raise ValueError("Missing observed BPAT wind hour")
            value=float(v)
            if not -float("inf")<value<float("inf"):raise ValueError("Nonfinite wind")
            values.append({"timestamp":t.isoformat(),"reported_wind_mw":value,
                           "observed_generation_to_eia860_nameplate_ratio":value/cap})
    if len(values)!=696:raise ValueError(f"Only {len(values)} hours")
    df=pd.DataFrame(values);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"bpat_reported_wind_hourly.csv",index=False)
    res={"hours":len(df),"reported_eia930_wind_energy_mwh":float(df.reported_wind_mw.sum()),
        "reported_eia930_mean_wind_mw":float(df.reported_wind_mw.mean()),
        "reported_eia930_min_wind_mw":float(df.reported_wind_mw.min()),
        "eia860_2024_bpat_wind_nameplate_mw":cap,
        "reported_mean_to_nameplate_ratio":float(df.reported_wind_mw.mean()/cap),
        "reported_hours_below_half_nameplate":int((df.reported_wind_mw<0.5*cap).sum()),
        "net_generation_not_weather_potential":True,
        "wind_full_availability_baseline_empirically_supported":False,
        "historical_calibration_certified":False}
    (out/"bpat_wind_observation_manifest.json").write_text(json.dumps(res,indent=2)+"\n")
    return res
def main():
    p=argparse.ArgumentParser()
    for k in ("balance","capacity","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args();print(json.dumps(audit(a.balance,a.capacity,a.output),indent=2))
if __name__=="__main__":main()
