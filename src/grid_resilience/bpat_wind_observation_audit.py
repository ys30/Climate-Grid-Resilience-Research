"""Audit observed BPAT wind output to flag unrealistic assumed full availability.

EIA-930 reported net generation and EIA-860 operable nameplate are not an
independently calibrated generation-availability relationship.
"""
import argparse,csv,json,calendar
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pandas as pd
from .eia930_fuel_decomposition import FMT

def audit(balance,capacity,output,year=2024,month=2):
    if not 1<=month<=12 or not 2000<=year<=2100:raise ValueError('Invalid calendar month')
    from datetime import timezone as tz
    start=datetime(year,month,1,tzinfo=tz.utc)
    end=datetime(year+1,1,1,tzinfo=tz.utc) if month==12 else datetime(year,month+1,1,tzinfo=tz.utc)
    n_hours=24*calendar.monthrange(year,month)[1]
    inventory=pd.read_csv(capacity)
    wind=inventory[(inventory.ba=="BPAT")&(inventory.technology=="wind")]
    if len(wind)!=1:raise ValueError("Missing unique BPAT wind group")
    cap=float(wind.iloc[0].nameplate_capacity_mw)
    if cap<=0:raise ValueError("Invalid BPAT wind nameplate")
    values=[];seen=set()
    with Path(balance).open(newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        col="Net Generation (MW) from Wind"
        headers=[h.strip() for h in (rd.fieldnames or []) if h]
        if col in headers:
            groups=[[col]]
        else:
            base="Net Generation (MW) from Wind "
            categories=["without Integrated Battery Storage","with Integrated Battery Storage"]
            groups=[]
            for category in categories:
                names=[base+category+suffix for suffix in ("", " (Imputed)", " (Adjusted)")]
                present=[name for name in names if name in headers]
                if not present:raise ValueError(f"Missing EIA-930 wind category {category}")
                groups.append(present)
        source_cols=[group[0] for group in groups]
        used_columns={}
        print(f"EIA-930 wind category candidates: {groups}")
        for row in rd:
            if row["Balancing Authority"].strip()!="BPAT":continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            if t in seen:raise ValueError("Duplicate BPAT hour")
            seen.add(t)
            values_by_group=[]
            for candidates in groups:
                valid=[(name,row.get(name,"").strip()) for name in candidates if row.get(name,"") and row.get(name,"").strip()]
                if not valid:raise ValueError(f"Missing EIA-930 BPAT wind category at {t}")
                # Favor adjusted when supplied, else imputed, else original.
                name,raw=valid[-1]
                used_columns[name]=used_columns.get(name,0)+1
                values_by_group.append(float(raw))
            value=sum(values_by_group)
            if not -float("inf")<value<float("inf"):raise ValueError("Nonfinite wind")
            values.append({"timestamp":t.isoformat(),"reported_wind_mw":value,
                           "observed_generation_to_eia860_nameplate_ratio":value/cap})
    if len(values)!=n_hours:raise ValueError(f"Expected {n_hours} hours; found {len(values)}")
    df=pd.DataFrame(values);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"bpat_reported_wind_hourly.csv",index=False)
    res={"year":year,"month":month,"wind_generation_source_columns":source_cols,"actual_variant_column_hours":used_columns,"hours":len(df),"reported_eia930_wind_energy_mwh":float(df.reported_wind_mw.sum()),
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
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=2)
    a=p.parse_args();print(json.dumps(audit(a.balance,a.capacity,a.output,a.year,a.month),indent=2))
if __name__=="__main__":main()
