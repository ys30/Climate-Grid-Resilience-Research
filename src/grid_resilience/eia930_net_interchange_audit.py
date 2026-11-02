"""Audit EIA-930's own hourly generation/interchange/demand balance, no EIA-923 mixing."""
import argparse,json
from pathlib import Path
import pandas as pd

FIELDS={"demand":"Demand (MW)","generation":"Net Generation (MW)","interchange":"Total Interchange (MW)"}

def audit(csv,ba,year,month):
    d=pd.read_csv(csv,low_memory=False)
    needed={"Balancing Authority","UTC Time at End of Hour",*FIELDS.values()}
    if not needed.issubset(d.columns):
        raise ValueError(f"Missing expected EIA-930 fields: {sorted(needed-set(d.columns))}; available: {list(d.columns)}")
    d=d.loc[d["Balancing Authority"].astype(str).str.strip().eq(ba)].copy()
    d["timestamp"]=pd.to_datetime(d["UTC Time at End of Hour"],utc=True,errors="raise")-pd.Timedelta(hours=1)
    start=pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")
    end=start+pd.offsets.MonthBegin(1)
    d=d.loc[d.timestamp.ge(start)&d.timestamp.lt(end)].copy()
    expected=pd.date_range(start,end,freq="h",inclusive="left")
    if len(d)!=len(expected) or d.timestamp.duplicated().any() or not pd.DatetimeIndex(d.timestamp.sort_values()).equals(expected):
        raise ValueError("Incomplete/duplicated official UTC hour coverage")
    for key,col in FIELDS.items():
        d[key+"_mw"]=pd.to_numeric(d[col],errors="coerce")
    if d[[k+"_mw" for k in FIELDS]].isna().any().any():raise ValueError("Missing generation/demand/interchange")
    d["balance_residual_mw"]=d.generation_mw-d.interchange_mw-d.demand_mw
    totals={key+"_mwh":float(d[key+"_mw"].sum()) for key in FIELDS}
    totals.update({"balance_residual_sum_mwh":float(d.balance_residual_mw.sum()),
                  "max_absolute_hourly_residual_mw":float(d.balance_residual_mw.abs().max()),
                  "nonzero_residual_hours":int(d.balance_residual_mw.abs().gt(1e-8).sum()),
                  "expected_hours":len(expected),
                  "identity_definition":"generation minus net interchange minus demand",
                  "historical_pypsa_calibration_certified":False})
    return d[["timestamp"]+[key+"_mw" for key in FIELDS]+["balance_residual_mw"]],totals

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--csv",required=True);a.add_argument("--ba",default="SRP")
    a.add_argument("--year",type=int,default=2024);a.add_argument("--month",type=int,default=1)
    a.add_argument("--output",required=True)
    x=a.parse_args();rows,metrics=audit(x.csv,x.ba,x.year,x.month)
    p=Path(x.output);p.mkdir(parents=True,exist_ok=True)
    rows.to_csv(p/"eia930_hourly_balance_audit.csv",index=False)
    (p/"eia930_balance_metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps(metrics,indent=2))
if __name__=="__main__":main()
