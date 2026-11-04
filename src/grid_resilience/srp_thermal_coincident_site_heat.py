"""Concurrent site-level ERA5 heat exposure by source-nameplate capacity.

Every site-hour is compared to a descriptive 2m-temperature threshold before
capacity weighting. Consecutive hours above a *capacity-share* threshold are
weather episodes, NOT electric capacity derating or power-system outages.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

TEMP_THRESHOLDS=(35.,40.)
SHARE_THRESHOLDS=(0.5,0.75)


def analyze(plant_hours,temperature_thresholds=TEMP_THRESHOLDS,
            share_thresholds=SHARE_THRESHOLDS):
    required={"timestamp_utc","technology","plant_id",
              "selected_nameplate_mw","temperature_2m_c"}
    if not required.issubset(plant_hours):
        raise ValueError("Missing site-level ERA5 fields")
    x=plant_hours.copy()
    x["plant_id"]=x.plant_id.astype("string").str.strip()
    x["technology"]=x.technology.astype("string").str.strip()
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    for field in ("selected_nameplate_mw","temperature_2m_c"):
        x[field]=pd.to_numeric(x[field],errors="coerce")
    if x.empty or x.plant_id.isna().any() or x.plant_id.eq("").any():
        raise ValueError("Empty source plant identities")
    if not set(x.technology.unique()).issubset({"gas","coal"}):
        raise ValueError("Unknown source technology")
    if not np.isfinite(x[["selected_nameplate_mw","temperature_2m_c"]].to_numpy(float)).all():
        raise ValueError("Invalid source numeric data")
    if (x.selected_nameplate_mw<=0).any() or not x.temperature_2m_c.between(-100,70).all():
        raise ValueError("Invalid source plant weather range")
    if x.duplicated(["timestamp_utc","technology","plant_id"]).any():
        raise ValueError("Duplicate site-hour")
    months={pd.Timestamp(t).strftime("%Y-%m") for t in x.timestamp_utc.dt.to_period("M")}
    if len(months)!=1:
        raise ValueError("Expected precisely one complete source month")
    ym=next(iter(months))
    expected=pd.date_range(ym+"-01",periods=pd.Period(ym).days_in_month*24,freq="h",tz="UTC")
    if ym not in ("2024-01","2024-07"):
        raise ValueError("Unexpected source-month scope")
    for (tech,plant),g in x.groupby(["technology","plant_id"]):
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Missing hours for site "+str(plant))
        if g.selected_nameplate_mw.nunique()!=1:
            raise ValueError("Changing site nameplate within month")
    cap=x.groupby(["technology","plant_id"],as_index=False).selected_nameplate_mw.first()
    hourly=[];episodes=[];summary=[]
    for tech,source in x.groupby("technology"):
        denominator=float(cap.loc[cap.technology.eq(tech),"selected_nameplate_mw"].sum())
        if denominator<=0:raise ValueError("Missing source capacity")
        for threshold in temperature_thresholds:
            if not np.isfinite(threshold):
                raise ValueError("Invalid source temperature threshold")
            exposed=source.assign(
                exposed_nameplate=source.selected_nameplate_mw*
                                   source.temperature_2m_c.ge(threshold).astype(float))
            agg=exposed.groupby("timestamp_utc",as_index=False).agg(
                exposed_nameplate_mw=("exposed_nameplate","sum"),
                exposed_site_count=("exposed_nameplate",lambda a:int((a>0).sum())))
            agg["source_nameplate_mw"]=denominator
            agg["exposed_capacity_share"]=agg.exposed_nameplate_mw/denominator
            if not agg.exposed_capacity_share.between(0,1).all():raise AssertionError("Impossible exposed fraction")
            agg["technology"]=tech
            agg["temperature_threshold_c"]=float(threshold)
            hourly.append(agg)
            for share in share_thresholds:
                if not (0<share<=1):raise ValueError("Invalid coincident-capacity fraction")
                hits=agg.exposed_capacity_share.to_numpy(float)>=share
                starts=np.flatnonzero(hits&~np.r_[False,hits[:-1]])
                ends=np.flatnonzero(hits&~np.r_[hits[1:],False])
                lengths=[]
                for begin,end in zip(starts,ends):
                    duration=int(end-begin+1)
                    lengths.append(duration)
                    episodes.append({
                        "technology":tech,"temperature_threshold_c":float(threshold),
                        "coincident_source_capacity_share_threshold":float(share),
                        "start_utc":agg.timestamp_utc.iloc[begin].isoformat(),
                        "end_utc_inclusive":agg.timestamp_utc.iloc[end].isoformat(),
                        "duration_hours":duration,
                        "maximum_exposed_source_capacity_share":float(
                            agg.exposed_capacity_share.iloc[begin:end+1].max())})
                summary.append({
                    "technology":tech,"temperature_threshold_c":float(threshold),
                    "coincident_source_capacity_share_threshold":float(share),
                    "hours":int(hits.sum()),"episode_count":len(lengths),
                    "longest_episode_hours":max(lengths,default=0),
                    "episodes_ge_6h":sum(a>=6 for a in lengths),
                    "episodes_ge_24h":sum(a>=24 for a in lengths),
                    "source_nameplate_mw":denominator,
                    "site_temperature_exposed_nameplate_mwh":float(agg.exposed_nameplate_mw.sum()),
                    "total_month_hours":len(agg)})
    h=pd.concat(hourly,ignore_index=True)
    e=pd.DataFrame(episodes,columns=["technology","temperature_threshold_c",
        "coincident_source_capacity_share_threshold","start_utc",
        "end_utc_inclusive","duration_hours","maximum_exposed_source_capacity_share"])
    s=pd.DataFrame(summary)
    ep=e.groupby(["technology","temperature_threshold_c",
                  "coincident_source_capacity_share_threshold"]).duration_hours.sum()
    for rec in s.itertuples(index=False):
        key=(rec.technology,rec.temperature_threshold_c,
             rec.coincident_source_capacity_share_threshold)
        if int(ep.get(key,0))!=rec.hours:
            raise AssertionError("Episode durations fail conservation")
        if rec.total_month_hours!=len(expected):
            raise AssertionError("Incomplete temperature hour summary")
    manifest={"source_month":ym,"hours_per_site":len(expected),
        "temperature_thresholds_c":list(temperature_thresholds),
        "coincident_capacity_share_thresholds":list(share_thresholds),
        "technology_source_nameplate_mw":{
            str(k):float(v) for k,v in cap.groupby("technology").selected_nameplate_mw.sum().items()},
        "exposure_is_nameplate_temperature_not_lost_capacity":True,
        "grid_cells_may_be_shared_between_sites":True,
        "generator_heat_derating_calibrated":False,
        "actual_outage_or_eens_inferred":False,
        "historical_reliability_calibrated":False}
    return h,e,s,manifest


def main():
    p=argparse.ArgumentParser()
    for arg in ("plant-hours","output"):p.add_argument("--"+arg,required=True)
    args=p.parse_args()
    h,e,s,m=analyze(pd.read_csv(args.plant_hours,dtype={"plant_id":"string"}))
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    h.to_csv(out/"site_coincident_heat_hourly.csv",index=False)
    e.to_csv(out/"site_coincident_heat_episodes.csv",index=False)
    s.to_csv(out/"site_coincident_heat_summary.csv",index=False)
    (out/"site_coincident_heat_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(s.to_string(index=False))

if __name__=="__main__":
    main()
