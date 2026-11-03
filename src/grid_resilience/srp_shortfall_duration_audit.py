"""Summarize temporal concentration of *modeled* SRP adequacy-screen gaps.

Input must be an already-validated hourly baseline. This is not a measure
of historical outage duration or realized load shedding.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def summarize(hourly, *, year=2024, month=1):
    needed={"timestamp_utc","modeled_unserved_mw","bus_balance_residual_mw"}
    if not needed.issubset(hourly.columns):
        raise ValueError("Missing source columns: "+str(sorted(needed-set(hourly.columns))))
    a=hourly.copy()
    a["timestamp_utc"]=pd.to_datetime(a.timestamp_utc,utc=True,errors="raise")
    start=pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")
    end=start+pd.offsets.MonthBegin(1)
    expected=pd.date_range(start,end,freq="h",inclusive="left")
    if len(a)!=len(expected) or a.timestamp_utc.duplicated().any() or not pd.DatetimeIndex(a.timestamp_utc).equals(expected):
        raise ValueError("Incomplete, duplicate or unordered UTC hours")
    for col in ("modeled_unserved_mw","bus_balance_residual_mw"):
        a[col]=pd.to_numeric(a[col],errors="raise")
    if not np.isfinite(a[["modeled_unserved_mw","bus_balance_residual_mw"]].to_numpy()).all():
        raise ValueError("Nonfinite screen diagnostics")
    if a.modeled_unserved_mw.min() < -1e-6:
        raise ValueError("Negative modeled unserved MW")
    if a.bus_balance_residual_mw.abs().max() > 1e-4:
        raise ValueError("Hourly bus balance not verified")
    u=a.modeled_unserved_mw.clip(lower=0)
    a["utc_date"]=a.timestamp_utc.dt.strftime("%Y-%m-%d")
    d=a.assign(positive_unserved_mw=u).groupby("utc_date").positive_unserved_mw.sum()
    total=float(u.sum())
    top_hours=int(np.ceil(len(u)*0.1))
    r={"period":f"{year}-{month:02d}","hours":len(u),
       "modeled_unserved_mwh":total,
       "hours_with_modeled_unserved":int((u>1e-6).sum()),
       "hours_above_1000_mw":int((u>1000).sum()),
       "peak_hourly_unserved_mw":float(u.max()),
       "p95_hourly_unserved_mw":float(u.quantile(0.95)),
       "p99_hourly_unserved_mw":float(u.quantile(0.99)),
       "top_decile_hours_share_of_unserved_energy":float(u.nlargest(top_hours).sum()/total) if total>0 else None,
       "days_with_modeled_unserved":int((d>1e-6).sum()),
       "maximum_utc_day":str(d.idxmax()) if total>0 else None,
       "maximum_daily_modeled_unserved_mwh":float(d.max()),
       "max_hourly_balance_residual_mw":float(a.bus_balance_residual_mw.abs().max()),
       "historical_outages_observed":False,
       "historical_calibration_certified":False,
       "definition":"Counterfactual partial-fleet screened unmet supply requirement; not recorded loss of load"}
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    args=p.parse_args()
    result=summarize(pd.read_csv(args.hourly),year=args.year,month=args.month)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
