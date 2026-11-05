"""Four nonoverlapping July 2024 windows for matched PyPSA factorial replication.

Source: archived 672 hourly observations across CISO, AZPS, BPAT, SRP.
Do not relabel weeks within July as independent seasons or years.
Hold capacity, link topology/ratings, heat/wind responses and cost fixed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS={"CISO","AZPS","BPAT","SRP"}
EDGES=(("CISO","AZPS"),("AZPS","SRP"),("CISO","BPAT"))
SCENARIOS={"baseline","heat_only","wind_only","heat_wind"}


def prepare_windows(demand,weather,capacity,output):
    for name,frame,fields in [
        ("demand",demand,{"timestamp","ba","demand_mw"}),
        ("weather",weather,{"timestamp","ba","temperature_c","wind_availability"}),
        ("capacity",capacity,{"ba","gas_mw","wind_mw","source_year","capacity_source"})]:
        if not fields.issubset(frame):
            raise ValueError(f"Missing {name} fields: {fields-set(frame.columns)}")
    d,w,c=demand.copy(),weather.copy(),capacity.copy()
    if set(d.ba)!=BAS or set(w.ba)!=BAS or set(c.ba)!=BAS or c.ba.duplicated().any():
        raise ValueError("Four-BA source cohort failed")
    for frame in (d,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.duplicated(["ba","timestamp"]).any():
            raise ValueError("Duplicate source BA hour")
        if frame.isna().any().any():
            raise ValueError("Missing observed source data")
    expected=pd.date_range("2024-07-01T00:00:00Z",periods=168,freq="h")
    # Original observed source window is 2024-07-01 00:00 to Jul-07 23:00
    # unless source pins show a different start; require 672 distinct shared hours
    timestamps=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    weather_times=pd.DatetimeIndex(sorted(w.timestamp.unique()))
    if len(timestamps)!=168 or not timestamps.equals(weather_times):
        raise ValueError("Archived observed dataset contains ONE 168h event, not 672h")
    if not (timestamps[1:]-timestamps[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Source event hourly discontinuity")
    if len(d)!=672 or len(w)!=672:
        raise ValueError("Expected 168 hourly events at four BA, not four weeks")
    # The 672 rows are BA-hour records, NOT 672 distinct hours or 4 events.
    raise ValueError("Only one observed 168-hour event in pinned source archive; need four separate 168h windows")


def source_audit(demand,weather,capacity):
    """Admit exact source evidence and state what can and cannot be replicated."""
    fields={"timestamp","ba"}
    if not fields.issubset(demand) or not fields.issubset(weather):
        raise ValueError("Missing source timestamps or balancing authorities")
    d=demand.copy();w=weather.copy()
    for frame in (d,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.duplicated(["timestamp","ba"]).any():
            raise ValueError("Duplicated source BA hour")
    dates=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if not dates.equals(pd.DatetimeIndex(sorted(w.timestamp.unique()))):
        raise ValueError("Demand/weather time grids do not match")
    if set(d.ba)!=BAS or set(w.ba)!=BAS or set(capacity.ba)!=BAS:
        raise ValueError("Unexpected BA cohort")
    if len(d)!=len(w)!=len(dates)*4:
        raise ValueError("Incomplete observed BA-hour coverage")
    if not (dates[1:]-dates[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Non-contiguous hourly observed event")
    hours=len(dates)
    return {
        "source_distinct_hourly_timestamps":hours,
        "source_ba_hourly_records":len(d),
        "source_ba_count":4,
        "distinct_168h_nonoverlap_windows":hours//168,
        "unallocated_source_hours":hours%168,
        "multiwindow_4x168_replication_admitted":hours>=672,
        "observed_event_first_utc":dates[0].isoformat(),
        "observed_event_last_utc":dates[-1].isoformat(),
        "ba_hour_records_are_not_distinct_time_hours":True,
        "independent_years_available":False,
        "synthetic_window_fabrication_allowed":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",required=True)
    p.add_argument("--weather",required=True)
    p.add_argument("--capacity",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    d=pd.read_csv(args.demand);w=pd.read_csv(args.weather);c=pd.read_csv(args.capacity)
    m=source_audit(d,w,c)
    path=Path(args.output);path.mkdir(parents=True,exist_ok=True)
    (path/"2024_july_observed_four_ba_multiweek_admission.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print(json.dumps(m,indent=2))
    if not m["multiwindow_4x168_replication_admitted"]:
        print("GATE: multiweek original-source replication blocked; cannot count BA rows as distinct hourly windows.")
        return

if __name__=="__main__":
    main()
