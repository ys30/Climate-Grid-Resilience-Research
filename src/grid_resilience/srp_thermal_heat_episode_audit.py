"""Identify contiguous hourly ERA5 heat-exposure events, never generator outages.

Input: CI-validated matched January/July hourly weather aggregates.
Contiguous events are defined on the nameplate-weighted *fleet mean*
temperature threshold, not independent per-plant threshold counts.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

THRESHOLDS=(35.,40.)


def events(hourly,thresholds=THRESHOLDS):
    required={"month","technology","timestamp_utc","capacity_weighted_temperature_c"}
    if not required.issubset(hourly):
        raise ValueError("Missing validated source weather columns")
    x=hourly.copy()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    x["capacity_weighted_temperature_c"]=pd.to_numeric(
        x.capacity_weighted_temperature_c,errors="coerce")
    if not np.isfinite(x.capacity_weighted_temperature_c.to_numpy(float)).all():
        raise ValueError("Nonfinite weather exposure")
    if not set(x.month).issubset({"January","July"}) or not set(x.technology).issubset({"gas","coal"}):
        raise ValueError("Unknown source month or fuel class")
    if x.duplicated(["month","technology","timestamp_utc"]).any():
        raise ValueError("Duplicate technology-hour weather")
    for (month,tech),frame in x.groupby(["month","technology"]):
        expected=pd.date_range(
            f"2024-{'01' if month=='January' else '07'}-01",periods=744,
            freq="h",tz="UTC")
        if not pd.DatetimeIndex(frame.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Missing or misaligned UTC weather hours")
    episodes=[]
    summaries=[]
    for (month,tech),frame in x.groupby(["month","technology"]):
        s=frame.sort_values("timestamp_utc").reset_index(drop=True)
        temp=s.capacity_weighted_temperature_c.to_numpy(float)
        timestamps=s.timestamp_utc
        for threshold in thresholds:
            if not np.isfinite(threshold):raise ValueError("Bad temperature threshold")
            hits=temp>=threshold
            starts=np.flatnonzero(hits & ~np.r_[False,hits[:-1]])
            ends=np.flatnonzero(hits & ~np.r_[hits[1:],False])
            durations=[]
            for begin,end in zip(starts,ends):
                hours=int(end-begin+1)
                durations.append(hours)
                episodes.append({
                    "month":month,"technology":tech,"threshold_c":float(threshold),
                    "start_utc":timestamps.iloc[begin].isoformat(),
                    "end_utc_inclusive":timestamps.iloc[end].isoformat(),
                    "duration_hours":hours,
                    "max_fleet_weighted_temperature_c":float(temp[begin:end+1].max()),
                    "mean_fleet_weighted_temperature_c":float(temp[begin:end+1].mean())
                })
            summaries.append({
                "month":month,"technology":tech,"threshold_c":float(threshold),
                "hot_hours":int(hits.sum()),"episode_count":len(durations),
                "longest_episode_hours":max(durations,default=0),
                "episodes_at_least_6h":sum(d>=6 for d in durations),
                "episodes_at_least_24h":sum(d>=24 for d in durations),
                "coverage_hours":len(s)
            })
    e=pd.DataFrame(episodes,columns=[
        "month","technology","threshold_c","start_utc","end_utc_inclusive",
        "duration_hours","max_fleet_weighted_temperature_c",
        "mean_fleet_weighted_temperature_c"])
    m=pd.DataFrame(summaries)
    if not m.coverage_hours.eq(744).all():
        raise AssertionError("Incomplete matching source hours")
    check=e.groupby(["month","technology","threshold_c"]).duration_hours.sum()
    for r in m.itertuples(index=False):
        if int(check.get((r.month,r.technology,r.threshold_c),0))!=r.hot_hours:
            raise AssertionError("Episode-hour conservation failed")
    return e,m


def main():
    p=argparse.ArgumentParser()
    for key in ("hourly","output"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    e,m=events(pd.read_csv(a.hourly))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    e.to_csv(out/"heat_exposure_episodes.csv",index=False)
    m.to_csv(out/"heat_exposure_episode_summary.csv",index=False)
    (out/"heat_exposure_episode_manifest.json").write_text(json.dumps({
        "source":"Matched source ERA5 EIA860 plant-location weather",
        "event_basis":"capacity-weighted fleet mean temperature, not independent site conditions",
        "temperature_thresholds_c":list(THRESHOLDS),
        "minimum_event_length_h":1,
        "missing_hours_allowed":False,
        "generator_derating_or_outage_inferred":False,
        "climate_causality_estimated":False
    },indent=2)+"\n")
    print(m.to_string(index=False))


if __name__=="__main__":
    main()
