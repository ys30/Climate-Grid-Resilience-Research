"""Match observed EIA-930 load to observed ERA5 point weather without imputation."""
import argparse
import json
from pathlib import Path
import pandas as pd

def match(demand,weather,output):
    d=pd.read_csv(demand);w=pd.read_csv(weather)
    required_d={"timestamp","ba","demand_mw"}
    required_w={"timestamp","ba","temperature_c","wind_availability"}
    if not required_d.issubset(d) or not required_w.issubset(w):raise ValueError("Missing observed columns")
    if d.empty or w.empty:raise ValueError("Empty source")
    for frame in (d,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.duplicated(["timestamp","ba"]).any():raise ValueError("Duplicate BA-hour")
    if set(map(tuple,d[["timestamp","ba"]].itertuples(index=False,name=None)))!=set(map(tuple,w[["timestamp","ba"]].itertuples(index=False,name=None))):
        raise ValueError("EIA-930/ERA5 BA-hour keys differ")
    if len(d)!=len(w):raise ValueError("EIA-930/ERA5 row counts differ")
    if set(d.ba)!={"CISO","AZPS","BPAT","SRP"}:raise ValueError("Incorrect BA set")
    if d.groupby("ba").size().ne(168).any():raise ValueError("Incomplete event week")
    for frame,columns in ((d,["demand_mw"]),(w,["temperature_c","wind_availability"])):
        for c in columns:
            frame[c]=pd.to_numeric(frame[c],errors="raise")
            if frame[c].isna().any():raise ValueError("Missing observed values")
    if d.demand_mw.le(0).any() or not w.wind_availability.between(0,1).all():raise ValueError("Out-of-range inputs")
    timestamps=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if not (timestamps[1:]-timestamps[:-1]==pd.Timedelta(hours=1)).all():raise ValueError("Non-consecutive UTC hours")
    joined=d.merge(w,on=["timestamp","ba"],validate="one_to_one",how="inner").sort_values(["timestamp","ba"])
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    joined.to_csv(out/"matched_hourly.csv",index=False)
    d.sort_values(["timestamp","ba"]).to_csv(out/"demand.csv",index=False)
    w.sort_values(["timestamp","ba"]).to_csv(out/"weather.csv",index=False)
    meta={"rows":len(joined),"bas":sorted(d.ba.unique()),"hours_per_ba":168,
          "period_start_utc":timestamps[0].isoformat(),"period_end_inclusive_utc":timestamps[-1].isoformat(),
          "sources":["EIA-930 BA reported demand","ERA5 historical meteorology at representative BA point coordinates"],
          "wind_availability":"hypothetical conversion from ERA5 wind speed, NOT observed wind generation",
          "calibration_status":"not performed","generator_fleet_status":"not joined"}
    (out/"match_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",required=True);p.add_argument("--weather",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(match(a.demand,a.weather,a.output),indent=2))
if __name__=="__main__":main()
