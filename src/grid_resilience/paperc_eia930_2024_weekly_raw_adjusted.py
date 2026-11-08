"""Compare original EIA930 raw vs adjusted balances in July's two source partitions.

Adjusted values are separate reported data, never retroactive raw measurements
or certified physical interchange. Preserve missingness and exact BA-hour keys.
"""
import argparse
import csv
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import pandas as pd
from .eia930_fuel_decomposition import FMT

BAS=("AZPS","BPAT","CISO","SRP")
BASE=("Demand (MW)","Net Generation (MW)","Total Interchange (MW)")
MODES={"raw":BASE,"adjusted":tuple(c+" (Adjusted)" for c in BASE)}


def read(path,label,start,end):
    out={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        source=csv.DictReader(f)
        headers=set(source.fieldnames or [])
        needed={"Balancing Authority","UTC Time at End of Hour"}|set(BASE)|set(MODES["adjusted"])
        if not needed.issubset(headers):
            raise ValueError(f"Missing original/adjusted fields in {label}: {sorted(needed-headers)}")
        for row in source:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            timestamp=datetime.strptime(row["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=timestamp<end:continue
            key=(timestamp,ba)
            if key in out:raise ValueError("Duplicate BA-hour in "+label)
            item={"ba":ba,"timestamp":timestamp.isoformat(),"source_partition":label}
            for mode,columns in MODES.items():
                for k,col in zip(("demand","generation","interchange"),columns):
                    value=row[col].strip()
                    x=float(value) if value else np.nan
                    if value and not np.isfinite(x):raise ValueError("Nonfinite original source")
                    item[f"{mode}_{k}_mw"]=x
            out[key]=item
    return out


def compare(jan_jun,jul_dec,start="2024-07-01T00:00:00Z"):
    first=pd.Timestamp(start)
    if first.year!=2024 or first.tzinfo is None or first.utcoffset()!=pd.Timedelta(0):
        raise ValueError("Explicit UTC 2024 period required")
    begin=first.to_pydatetime()
    end=begin+timedelta(hours=168)
    old=read(jan_jun,"2024_Jan_Jun",begin,end)
    new=read(jul_dec,"2024_Jul_Dec",begin,end)
    if set(old)&set(new):raise ValueError("Overlapping original source partitions")
    both={**old,**new}
    expected={(begin+timedelta(hours=i),ba) for i in range(168) for ba in BAS}
    if set(both)!=expected:raise ValueError("Missing official BA-hour evidence")
    x=pd.DataFrame(both[k] for k in sorted(expected))
    for mode in MODES:
        cols=[f"{mode}_{s}_mw" for s in ("demand","generation","interchange")]
        present=x[cols].notna().all(axis=1)
        x[f"{mode}_triplet_present"]=present
        x[f"{mode}_residual_mw"]=x[cols[1]]-x[cols[0]]-x[cols[2]]
        x.loc[~present,f"{mode}_residual_mw"]=np.nan
        threshold=x[cols[0]].abs().mul(.01).clip(lower=1)
        x[f"{mode}_closes"]=present & x[f"{mode}_residual_mw"].abs().le(threshold)
    result=[]
    for ba,g in x.groupby("ba",sort=True):
        a={"ba":ba,"source_hours":len(g),"jan_jun_hours":int(g.source_partition.eq("2024_Jan_Jun").sum()),
           "jul_dec_hours":int(g.source_partition.eq("2024_Jul_Dec").sum()),
           "raw_interchange_missing_hours":int(g.raw_interchange_mw.isna().sum()),
           "adjusted_interchange_missing_hours":int(g.adjusted_interchange_mw.isna().sum()),
           "raw_TI_missing_but_adjusted_present_hours":
               int((g.raw_interchange_mw.isna()&g.adjusted_interchange_mw.notna()).sum()),
           "original_generator_population_calibrated":False}
        for mode in MODES:
            v=g.loc[g[f"{mode}_triplet_present"],f"{mode}_residual_mw"]
            a[f"{mode}_complete_triplet_hours"]=len(v)
            a[f"{mode}_closing_hours"]=int(g[f"{mode}_closes"].sum())
            a[f"{mode}_nonclosing_evaluable_hours"]=len(v)-a[f"{mode}_closing_hours"]
            a[f"{mode}_signed_residual_valid_hours_mwh"]=float(v.sum())
            a[f"{mode}_absolute_residual_valid_hours_mwh"]=float(v.abs().sum())
        result.append(a)
    summary=pd.DataFrame(result)
    manifest={"2024_original_utc_window":"2024-07-01T00:00:00Z to 2024-07-08T00:00:00Z exclusive",
              "raw_and_adjusted_are_distinct_source_fields":True,
              "never_substitute_adjusted_for_missing_raw":True,
              "source_ba_hours":len(x),"missing_source_ba_hours":672-len(x),
              "adjusted_interchange_not_verified_physical_transfer":True,
              "historical_model_adequacy_calibrated":False}
    return x,summary,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--jan-jun",required=True)
    p.add_argument("--jul-dec",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    detail,summary,meta=compare(a.jan_jun,a.jul_dec)
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    detail.to_csv(dest/"paper_c_eia930_raw_vs_adjusted_2024_week1_hourly.csv",index=False)
    summary.to_csv(dest/"paper_c_eia930_raw_vs_adjusted_2024_week1_by_ba.csv",index=False)
    (dest/"paper_c_raw_vs_adjusted_scope.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
