"""Uncalibrated wind power-curve sensitivity at SRP ERA5 wind-plant points.

Transforms individual plant-hour ERA5 100m winds BEFORE capacity-weighting.
No inference of observed generation, verified fleet capacity factor, or EENS.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .era5_point_wind_curve import power_curve

CURVES={
    "low_cut_in":(2.5,10.0,25.0),
    "reference":(3.0,12.0,25.0),
    "high_cut_in":(4.0,14.0,25.0),
}


def analyze(weather, *, curves=CURVES):
    required={"timestamp_utc","plant_id","wind_speed_100m_ms",
              "site_nameplate_mw","capacity_weight"}
    if not required.issubset(weather):
        raise ValueError("Missing ERA5 site weather fields")
    x=weather.copy()
    x["plant_id"]=x.plant_id.astype("string").str.strip()
    if x.plant_id.isna().any() or x.plant_id.eq("").any():
        raise ValueError("Missing wind plant identity")
    x["timestamp_utc"]=pd.to_datetime(x.timestamp_utc,utc=True,errors="raise")
    hours=pd.date_range("2024-01-01",periods=744,freq="h",tz="UTC")
    plant_ids=sorted(x.plant_id.unique().tolist())
    if not plant_ids or x.duplicated(["timestamp_utc","plant_id"]).any() or len(x)!=744*len(plant_ids):
        raise ValueError("Missing/duplicate full plant-hour grid")
    for plant,frame in x.groupby("plant_id"):
        if not pd.DatetimeIndex(frame.timestamp_utc.sort_values()).equals(hours):
            raise ValueError(f"Wrong 744h time coverage: {plant}")
    for key in ("wind_speed_100m_ms","site_nameplate_mw","capacity_weight"):
        x[key]=pd.to_numeric(x[key],errors="coerce")
    if not np.isfinite(x[["wind_speed_100m_ms","site_nameplate_mw","capacity_weight"]].to_numpy(float)).all():
        raise ValueError("Nonfinite source weather/plant weight")
    if (x.wind_speed_100m_ms<0).any() or (x.wind_speed_100m_ms>=100).any():
        raise ValueError("Invalid 100m wind speed")
    if (x.site_nameplate_mw<=0).any() or (x.capacity_weight<=0).any():
        raise ValueError("Nonpositive source nameplate or weight")
    by=x.groupby("plant_id").agg(
        unique_capacity=("site_nameplate_mw","nunique"),
        unique_weights=("capacity_weight","nunique"),
        capacity=("site_nameplate_mw","first"),
        weight=("capacity_weight","first"))
    if not by.unique_capacity.eq(1).all() or not by.unique_weights.eq(1).all():
        raise ValueError("Inconsistent plant-hour nameplate/weights")
    if abs(by.weight.sum()-1)>1e-6 or not np.allclose(
        by.weight.to_numpy(),by.capacity.to_numpy()/by.capacity.sum(),rtol=0,atol=1e-6):
        raise ValueError("Wind fleet capacity weights differ from source nameplates")
    if not curves:raise ValueError("No curve scenarios")
    records=[]
    for name,(cut_in,rated,cut_out) in curves.items():
        # Guard against invalid curves even if observations don't hit a threshold.
        if not (0<cut_in<rated<cut_out):
            raise ValueError("Invalid wind curve")
        y=x[["timestamp_utc","plant_id","capacity_weight","site_nameplate_mw"]].copy()
        y["curve_scenario"]=name
        y["uncalibrated_proxy_pu"]=x.wind_speed_100m_ms.map(
            lambda value:power_curve(value,cut_in,rated,cut_out))
        records.append(y)
    site=pd.concat(records,ignore_index=True)
    site["weighted_proxy"]=site.uncalibrated_proxy_pu*site.capacity_weight
    fleet=site.groupby(["curve_scenario","timestamp_utc"],as_index=False).agg(
        fleet_uncalibrated_proxy_pu=("weighted_proxy","sum"))
    fleet["fleet_proxy_power_mw"]=fleet.fleet_uncalibrated_proxy_pu*float(by.capacity.sum())
    fleet["timestamp_utc"]=fleet.timestamp_utc.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    summary=fleet.groupby("curve_scenario",as_index=False).agg(
        mean_uncalibrated_proxy_pu=("fleet_uncalibrated_proxy_pu","mean"),
        proxy_energy_mwh=("fleet_proxy_power_mw","sum"),
        hourly_min_proxy_pu=("fleet_uncalibrated_proxy_pu","min"),
        hourly_max_proxy_pu=("fleet_uncalibrated_proxy_pu","max"),
        zero_proxy_fleet_hours=("fleet_uncalibrated_proxy_pu",lambda s:int(s.eq(0).sum())))
    if fleet.groupby("curve_scenario").size().ne(744).any():
        raise AssertionError("Lost source hours")
    if not fleet.fleet_uncalibrated_proxy_pu.between(0,1).all():
        raise AssertionError("Proxy output outside [0,1]")
    if (summary.proxy_energy_mwh>float(by.capacity.sum())*744+1e-6).any():
        raise AssertionError("Energy above nameplate ceiling")
    manifest={
        "source_period":"2024-01","source_plant_count":len(plant_ids),
        "source_site_hours":len(x),
        "source_eligible_wind_nameplate_mw":float(by.capacity.sum()),
        "curve_cases":{k:{"cut_in_ms":v[0],"rated_ms":v[1],"cut_out_ms":v[2]}
                       for k,v in curves.items()},
        "spatial_operation":"transform each site-hour wind, then capacity-weight output",
        "all_744_utc_hours_per_curve_verified":True,
        "wind_100m_is_plant_point_era5_not_turbine_hub_measurement":True,
        "estimated_actual_wind_generation":False,
        "wind_fleet_production_calibrated":False,
        "historical_reliability_calibrated":False,
        "real_outage_or_eens_inferred":False,
    }
    return site,fleet,summary,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weather",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    site,fleet,summary,manifest=analyze(pd.read_csv(
        a.weather,dtype={"plant_id":"string"}))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    site.to_csv(out/"srp_era5_wind_curve_plant_hourly.csv",index=False)
    fleet.to_csv(out/"srp_era5_wind_curve_fleet_hourly.csv",index=False)
    summary.to_csv(out/"srp_era5_wind_curve_sensitivity_summary.csv",index=False)
    (out/"srp_era5_wind_curve_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
