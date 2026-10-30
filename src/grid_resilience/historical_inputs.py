"""Fail-closed preparation of observed hourly and verified capacity inputs for PyPSA.

This adapter does not fetch data or impute missing observations. Source CSVs must
be produced by audited upstream EIA/ERA5 pipelines.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def prepare(demand,weather,capacity,output,event_id):
    d=pd.read_csv(demand)
    w=pd.read_csv(weather)
    c=pd.read_csv(capacity)
    expected_d={"timestamp","ba","demand_mw"}
    expected_w={"timestamp","ba","temperature_c","wind_availability"}
    expected_c={"ba","gas_mw","wind_mw","source_year","capacity_source"}
    for name,df,cols in (("demand",d,expected_d),("weather",w,expected_w),("capacity",c,expected_c)):
        if not cols.issubset(df.columns):
            raise ValueError(f"{name} missing {sorted(cols-set(df.columns))}")
    if d.empty or w.empty or c.empty:raise ValueError("No empty source files accepted")
    for frame in (d,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.duplicated(["ba","timestamp"]).any():raise ValueError("Duplicate BA-hour rows")
    if c.ba.duplicated().any():raise ValueError("Duplicate capacity BA")
    bas=set(c.ba)
    if not bas or set(d.ba)!=bas or set(w.ba)!=bas:raise ValueError("BA sets do not agree")
    if c[["source_year","capacity_source"]].isna().any().any():raise ValueError("Missing capacity provenance")
    if c.capacity_source.astype(str).str.strip().eq("").any():raise ValueError("Empty capacity source")
    for frame,fields in ((d,["demand_mw"]),(w,["temperature_c","wind_availability"]),(c,["gas_mw","wind_mw"])):
        for field in fields:
            frame[field]=pd.to_numeric(frame[field],errors="raise")
            if frame[field].isna().any():raise ValueError(f"Missing {field}: no silent imputation")
    if (d.demand_mw<=0).any() or (c[["gas_mw","wind_mw"]]<0).any().any():
        raise ValueError("Demand must be positive and capacity nonnegative")
    if not w.wind_availability.between(0,1).all():raise ValueError("Wind values must be [0,1]")
    dates=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if len(dates)>1 and not (dates[1:]-dates[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Noncontiguous hourly event")
    pairs=pd.MultiIndex.from_product([dates,sorted(bas)],names=["timestamp","ba"])
    for frame in (d,w):
        if len(frame)!=len(pairs) or set(map(tuple,frame[["timestamp","ba"]].itertuples(index=False,name=None)))!=set(pairs):
            raise ValueError("Incomplete BA-hour observational coverage")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    for frame,name in ((d,"demand.csv"),(w,"weather.csv")):
        frame.sort_values(["timestamp","ba"]).to_csv(out/name,index=False)
    c.sort_values("ba").to_csv(out/"capacity.csv",index=False)
    manifest={"event_id":event_id,"first_hour_utc":dates[0].isoformat(),
              "last_hour_utc":dates[-1].isoformat(),"hours":len(dates),
              "bas":sorted(bas),"capacity_source_years":sorted(map(int,c.source_year.unique())),
              "capacity_source_labels":sorted(c.capacity_source.unique().tolist()),
              "claims":["Observed demand and weather are upstream-provided, not verified by this adapter.",
                        "Capacity classification must be separately audited against original EIA-860.",
                        "No flow or link rating has been inferred."]}
    (out/"input_provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for key in ("demand","weather","capacity","output","event-id"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(a.demand,a.weather,a.capacity,a.output,a.event_id),indent=2))
if __name__=="__main__":main()
