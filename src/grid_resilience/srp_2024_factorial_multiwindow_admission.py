"""Fail-closed independent-event coverage admission for existing 4-BA factorial.

Every balancing authority occupies a row at each hour: 672 BA-hour rows
represent *168 distinct hours*, not four independent 168h events. Inspect
actual source timestamps before authorizing any multiweek or multi-year claim.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS={"CISO","AZPS","BPAT","SRP"}


def source_audit(demand,weather,capacity):
    fields={"timestamp","ba"}
    for label,x in (("demand",demand),("weather",weather)):
        if not fields.issubset(x):
            raise ValueError(f"{label} missing source timestamps or BA")
    d=demand.copy();w=weather.copy()
    for frame in (d,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.duplicated(["timestamp","ba"]).any():
            raise ValueError("Duplicated BA hour")
    dates=pd.DatetimeIndex(sorted(d.timestamp.unique()))
    if len(dates)==0:
        raise ValueError("Empty observational source")
    if not dates.equals(pd.DatetimeIndex(sorted(w.timestamp.unique()))):
        raise ValueError("Demand/weather source time grids differ")
    if set(d.ba)!=BAS or set(w.ba)!=BAS or set(capacity.ba)!=BAS or capacity.ba.duplicated().any():
        raise ValueError("Unexpected four-BA roster")
    if len(d)!=len(dates)*4 or len(w)!=len(dates)*4:
        raise ValueError("Incomplete BA-hour source coverage")
    required=pd.MultiIndex.from_product([dates,sorted(BAS)],names=["timestamp","ba"])
    for frame in (d,w):
        actual=pd.MultiIndex.from_frame(frame[["timestamp","ba"]])
        if not actual.isin(required).all() or len(actual.unique())!=len(required):
            raise ValueError("Missing or unexpected BA-hour source")
    if len(dates)>1 and not (dates[1:]-dates[:-1]==pd.Timedelta(hours=1)).all():
        raise ValueError("Noncontiguous observed hourly interval")
    hours=len(dates)
    return {
        "source_distinct_utc_hours":hours,
        "source_four_ba_hourly_rows":len(d),
        "ba_count":4,
        "complete_disjoint_168h_windows_possible":hours//168,
        "additional_hours_excluded":hours%168,
        "four_week_replication_supported_by_this_source":hours>=672,
        "first_observed_hour_utc":dates[0].isoformat(),
        "last_observed_hour_utc":dates[-1].isoformat(),
        "source_ba_rows_not_independent_hours":True,
        "independent_calendar_years_verified":False,
        "fabricated_event_source_rows_allowed":False,
        "historical_reliability_calibration_completed":False
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("demand","weather","capacity","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    m=source_audit(pd.read_csv(a.demand),pd.read_csv(a.weather),
                   pd.read_csv(a.capacity))
    root=Path(a.output);root.mkdir(parents=True,exist_ok=True)
    (root/"factorial_multiwindow_source_admission.json").write_text(
        json.dumps(m,indent=2)+"\n")
    print(json.dumps(m,indent=2))
    if not m["four_week_replication_supported_by_this_source"]:
        print("NOT ADMITTED: independent four-week replication requires additional source-observed hours")


if __name__=="__main__":
    main()
