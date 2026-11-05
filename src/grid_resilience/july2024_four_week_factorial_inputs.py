"""Admit four source-observed July 2024 168h PyPSA comparison weeks.

Official EIA-930 BA hourly raw demand (end-hour to UTC start-hour) +
Open-Meteo ERA5 BA point-proxy hourly weather. EIA-860 capacity and all
hypothetical network parameters held fixed across weeks. Never invent a BA
polygon, verified intertie rating or physical thermal availability.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
EDGES=(("CISO","AZPS"),("AZPS","SRP"),("CISO","BPAT"))
START=pd.Timestamp("2024-07-01T00:00:00Z")
DAYS=28
HOURS=672


def admit_july(demand_source,weather,capacity,output):
    required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
    if not required.issubset(demand_source):
        raise ValueError("Official source schema missing")
    d=demand_source.loc[demand_source["Balancing Authority"].astype("string").str.strip().isin(BAS)].copy()
    d["timestamp"]=pd.to_datetime(d["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p",utc=True,errors="raise")-pd.Timedelta(hours=1)
    d["ba"]=d["Balancing Authority"].astype("string").str.strip()
    d["demand_mw"]=pd.to_numeric(d["Demand (MW)"],errors="coerce")
    original=pd.date_range(START,periods=744,freq="h")
    if len(d)!=744*4 or d.duplicated(["ba","timestamp"]).any():
        raise ValueError("Official full month SRP/BA source incomplete")
    for ba,g in d.groupby("ba"):
        if not pd.DatetimeIndex(g.timestamp.sort_values()).equals(original):
            raise ValueError(f"Missing official July BA hour for {ba}")
    if not np.isfinite(d.demand_mw.to_numpy(float)).all() or d.demand_mw.le(0).any():
        raise ValueError("Official EIA930 demand source has missing, invalid or nonpositive observations")
    d=d.loc[d.timestamp.lt(START+pd.Timedelta(hours=HOURS)),["timestamp","ba","demand_mw"]].copy()
    w=weather.copy()
    needed={"timestamp","ba","temperature_c","wind_availability"}
    if not needed.issubset(w):
        raise ValueError("ERA5 BA point-proxy source columns incomplete")
    w["timestamp"]=pd.to_datetime(w.timestamp,utc=True,errors="raise")
    if w.duplicated(["ba","timestamp"]).any() or set(w.ba)!=set(BAS):
        raise ValueError("Weather source BA identity/UTC hour duplicated")
    expected=pd.date_range(START,periods=HOURS,freq="h")
    for ba,g in w.groupby("ba"):
        if not pd.DatetimeIndex(g.timestamp.sort_values()).equals(expected):
            raise ValueError("Incomplete true 672 UTC-hour ERA5 weather source")
    for col in ("temperature_c","wind_availability"):
        w[col]=pd.to_numeric(w[col],errors="coerce")
    if not np.isfinite(w[["temperature_c","wind_availability"]].to_numpy(float)).all() or not w.wind_availability.between(0,1).all():
        raise ValueError("Invalid actual ERA5 point observations")
    c=capacity.copy()
    cap_required={"ba","gas_mw","wind_mw","source_year","capacity_source"}
    if not cap_required.issubset(c) or set(c.ba)!=set(BAS) or c.ba.duplicated().any():
        raise ValueError("Expected original explicit four-BA EIA860 partial fleet")
    if not c.capacity_source.astype(str).str.contains("GENERIC_THERMAL_PROXY").all():
        raise ValueError("Expected only original uncalibrated capacity proxy")
    for col in ("gas_mw","wind_mw"):
        c[col]=pd.to_numeric(c[col],errors="coerce")
    if not np.isfinite(c[["gas_mw","wind_mw"]].to_numpy(float)).all() or c[["gas_mw","wind_mw"]].lt(0).any().any():
        raise ValueError("Invalid frozen original capacity source")
    if d.shape[0] != 4*HOURS or w.shape[0] != 4*HOURS:
        raise ValueError("Source 4-BA hourly coverage incomplete")
    z=d.merge(w,on=["timestamp","ba"],how="inner",validate="one_to_one")
    if len(z)!=HOURS*4:
        raise ValueError("Actual weather and official BA demand hours do not align")
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    c.to_csv(root/"frozen_partial_eia860_capacity.csv",index=False)
    first=d.loc[d.timestamp.lt(START+pd.Timedelta(hours=168))]
    peak=first.groupby("ba").demand_mw.max()
    links=pd.DataFrame([
        {"from_ba":a,"to_ba":b,
         "capacity_mw":float(min(peak[a],peak[b])*.1),
         "rating_source":"HYPOTHETICAL_10PCT_FIRST_WEEK_SMALLER_BA_PEAK_NOT_PHYSICAL"}
        for a,b in EDGES])
    links.to_csv(root/"frozen_hypothetical_links.csv",index=False)
    isolated=pd.DataFrame(columns=["from_ba","to_ba","capacity_mw"])
    isolated.to_csv(root/"isolated_ba_links.csv",index=False)
    events=[]
    for index in range(4):
        start=START+pd.Timedelta(hours=168*index)
        end=start+pd.Timedelta(hours=168)
        selected=(z.timestamp>=start)&(z.timestamp<end)
        frame=z.loc[selected].sort_values(["timestamp","ba"])
        if len(frame)!=4*168 or frame.timestamp.nunique()!=168:
            raise ValueError("Incomplete independent window source")
        folder=root/f"week_{index+1}"
        folder.mkdir(parents=True,exist_ok=True)
        frame[["timestamp","ba","demand_mw"]].to_csv(folder/"demand.csv",index=False)
        frame[["timestamp","ba","temperature_c","wind_availability"]].to_csv(folder/"weather.csv",index=False)
        events.append({"week":index+1,"first_hour_utc":start.isoformat(),
                       "last_hour_utc":(end-pd.Timedelta(hours=1)).isoformat(),
                       "ba_hourly_rows":len(frame),"distinct_hours":168,
                       "mean_observed_site_temperature_c":float(frame.temperature_c.mean()),
                       "mean_observed_ba_demand_mw":float(frame.demand_mw.mean()),
                       "source_proxy_wind_availability_mean":float(frame.wind_availability.mean())})
    summary=pd.DataFrame(events)
    summary.to_csv(root/"four_distinct_july_weeks_source_coverage.csv",index=False)
    manifest={
        "source_utc_month":"2024-07","four_balancing_authorities":list(BAS),
        "source_distinct_hourly_timestamps":HOURS,
        "source_hour_rows":4*HOURS,"nonoverlapping_168h_windows":4,
        "frozen_capacity":"same EIA860 annual partial gas/wind proxy each week",
        "frozen_links":"10 pct of first-week smaller BA demand peak on three hypothetical edges",
        "link_ratings_physically_verified":False,
        "actual_era5_weather_proxy_is_ba_polygon_weather":False,
        "wind_power_curve_calibrated":False,
        "missing_demand_weather_hours_interpolated":False,
        "original_month_from_official_eia930":True,
        "heat_load_and_wind_shock_factors_are_hypothetical":True,
        "physical_eens_or_historical_outages_estimated":False,
        "independent_year_or_month_replication":False}
    (root/"four_week_source_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))
    return summary,manifest


def main():
    p=argparse.ArgumentParser()
    for x in ("eia930-july","era5-fourba-672","capacity","output"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    admit_july(
        pd.read_csv(a.eia930_july,dtype="string"),
        pd.read_csv(a.era5_fourba_672),
        pd.read_csv(a.capacity),
        a.output)


if __name__=="__main__":
    main()
