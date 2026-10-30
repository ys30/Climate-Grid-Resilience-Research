"""Identify independent multi-BA heat, low-wind and compound-weather event windows.

These are configurable screening thresholds, not calibrated local extremes.
Wind availability is an assumed proxy unless separately validated.
"""
import argparse
from pathlib import Path
import pandas as pd

def identify(frame, heat_c=35.0, low_wind_cf=.20, min_bas=2,
             min_hours=6, separation_hours=24):
    required={"timestamp","ba","temperature_c","wind_availability"}
    if not required.issubset(frame):raise ValueError("Missing event weather fields")
    if frame.empty:raise ValueError("Empty weather series")
    if min_bas<1 or min_hours<1 or separation_hours<0:
        raise ValueError("Invalid event rules")
    f=frame.copy()
    f["timestamp"]=pd.to_datetime(f.timestamp,utc=True,errors="raise")
    if f.duplicated(["timestamp","ba"]).any():raise ValueError("Duplicate BA-hour")
    for name in ("temperature_c","wind_availability"):
        f[name]=pd.to_numeric(f[name],errors="raise")
        if f[name].isna().any():raise ValueError("Missing weather values")
    if not f.wind_availability.between(0,1).all():raise ValueError("Invalid availability")
    bas=sorted(f.ba.unique())
    if min_bas>len(bas):raise ValueError("min_bas exceeds available BAs")
    timestamps=pd.DatetimeIndex(sorted(f.timestamp.unique()))
    expected=pd.MultiIndex.from_product([timestamps,bas],names=["timestamp","ba"])
    actual=pd.MultiIndex.from_frame(f[["timestamp","ba"]])
    if len(f)!=len(expected) or set(actual)!=set(expected):
        raise ValueError("Incomplete BA-hour weather grid")
    if len(timestamps)>1 and not (timestamps[1:]-timestamps[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Nonconsecutive hourly weather input")
    f["heat"]=f.temperature_c.ge(heat_c)
    f["low_wind"]=f.wind_availability.le(low_wind_cf)
    f["compound"]=f.heat & f.low_wind
    hourly=f.groupby("timestamp")[["heat","low_wind","compound"]].sum().reindex(timestamps)
    rows=[]
    for label in ("heat","low_wind","compound"):
        active=hourly[label].ge(min_bas)
        starts=[]
        for t,is_active in active.items():
            if is_active:
                if not starts or (t-starts[-1][-1])>pd.Timedelta(hours=1):
                    starts.append([t])
                else:starts[-1].append(t)
        qualifying=[block for block in starts if len(block)>=min_hours]
        joined=[]
        for block in qualifying:
            if joined and (block[0]-joined[-1][-1])<=pd.Timedelta(hours=separation_hours+1):
                joined[-1].extend(block)
            else:joined.append(block[:])
        for i,block in enumerate(joined,1):
            # Active hours count excludes gaps introduced by the merge.
            rows.append({"event_id":f"{label}_{i:03d}","event_type":label,
                         "start_utc":block[0].isoformat(),
                         "end_utc_inclusive":block[-1].isoformat(),
                         "active_hours":len(block),"calendar_window_hours":int((block[-1]-block[0])/pd.Timedelta(hours=1))+1,
                         "threshold_min_bas":min_bas})
    return pd.DataFrame(rows,columns=["event_id","event_type","start_utc","end_utc_inclusive",
                                     "active_hours","calendar_window_hours","threshold_min_bas"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weather",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--heat-c",type=float,default=35)
    p.add_argument("--low-wind-cf",type=float,default=.2)
    p.add_argument("--min-bas",type=int,default=2)
    p.add_argument("--min-hours",type=int,default=6)
    p.add_argument("--separation-hours",type=int,default=24)
    a=p.parse_args()
    res=identify(pd.read_csv(a.weather),a.heat_c,a.low_wind_cf,a.min_bas,a.min_hours,a.separation_hours)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    res.to_csv(out,index=False)
    print(res.to_string(index=False))
if __name__=="__main__":main()
