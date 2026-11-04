"""SRP wind-plant point ERA5 January 2024 intake, with strict source provenance.

EIA860 plant coordinates are not turbine coordinates. ERA5 reanalysis wind at
a grid cell is not observed wind production or validated availability.
"""
import argparse
import calendar
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request

import numpy as np
import pandas as pd

API="https://archive-api.open-meteo.com/v1/archive"


def validate_sites(sites):
    needed={"ba","plant_id","latitude","longitude","nameplate_mw"}
    if not needed.issubset(sites):raise ValueError("Missing site location fields")
    s=sites.loc[sites.ba.astype("string").str.strip().eq("SRP")].copy()
    if s.empty:raise ValueError("No SRP wind plants with coordinates")
    s["plant_id"]=s.plant_id.astype("string").str.strip()
    if s.plant_id.isna().any() or s.plant_id.eq("").any() or s.plant_id.duplicated().any():
        raise ValueError("Missing or duplicate plant identity")
    for k in ("latitude","longitude","nameplate_mw"):
        s[k]=pd.to_numeric(s[k],errors="coerce")
    if not np.isfinite(s[["latitude","longitude","nameplate_mw"]].to_numpy(float)).all():
        raise ValueError("Nonfinite site coordinates/capacity")
    if not s.latitude.between(20,55).all() or not s.longitude.between(-130,-95).all():
        raise ValueError("Plant coordinate outside western USA bounds")
    if (s.nameplate_mw<=0).any():raise ValueError("Nonpositive site nameplate")
    s=s.sort_values("plant_id").reset_index(drop=True)
    s["capacity_weight"]=s.nameplate_mw/s.nameplate_mw.sum()
    return s


def parse_response(raw,site,*,year=2024,month=1):
    obj=json.loads(raw)
    if obj.get("error"):raise ValueError("ERA5 API returned error")
    if int(obj.get("utc_offset_seconds",-100000))!=0:
        raise ValueError("ERA5 response not GMT/UTC")
    units=obj.get("hourly_units",{})
    if units.get("wind_speed_100m")!="m/s" or units.get("temperature_2m") not in ("°C","C"):
        raise ValueError("Unexpected ERA5 wind or temperature units")
    h=obj.get("hourly",{})
    n=24*calendar.monthrange(year,month)[1]
    times=h.get("time",[])
    wind=h.get("wind_speed_100m",[])
    temp=h.get("temperature_2m",[])
    if any(len(a)!=n for a in (times,wind,temp)):
        raise ValueError("Missing ERA5 hourly weather variables")
    expected=pd.date_range(f"{year}-{month:02d}-01",periods=n,freq="h",tz="UTC")
    actual=pd.to_datetime(pd.Series(times),utc=True,errors="raise")
    if not pd.DatetimeIndex(actual).equals(expected):
        raise ValueError("ERA5 UTC hour mismatch or duplicate")
    w=np.asarray(wind,dtype=float)
    t=np.asarray(temp,dtype=float)
    if not np.isfinite(w).all() or (w<0).any() or (w>100).any():
        raise ValueError("Invalid ERA5 wind speed")
    if not np.isfinite(t).all() or (t<-100).any() or (t>70).any():
        raise ValueError("Invalid ERA5 temperature")
    return pd.DataFrame({
        "timestamp_utc":expected.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ba":"SRP","plant_id":str(site["plant_id"]),
        "wind_speed_100m_ms":w,
        "temperature_2m_c":t,
        "site_nameplate_mw":float(site["nameplate_mw"]),
        "capacity_weight":float(site["capacity_weight"]),
        "weather_source":"ERA5 via Open-Meteo Historical Weather API",
    })


def run(sites,output,*,year=2024,month=1,fetch=None):
    if not (2000<=year<=2100 and 1<=month<=12):
        raise ValueError("Invalid source period")
    sites=validate_sites(sites)
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    first=date(year,month,1).isoformat()
    last=date(year,month,calendar.monthrange(year,month)[1]).isoformat()
    frames=[];provenance=[]
    for _,site in sites.iterrows():
        q=urlencode({
            "latitude":float(site.latitude),"longitude":float(site.longitude),
            "start_date":first,"end_date":last,
            "hourly":"wind_speed_100m,temperature_2m",
            "models":"era5","wind_speed_unit":"ms","timezone":"GMT",
        })
        url=API+"?"+q
        if fetch is None:
            with urlopen(Request(url,headers={"User-Agent":"GridResilienceResearch/1.0"}),
                         timeout=120) as response:
                data=response.read(10_000_001)
        else:
            data=fetch(url)
        if not isinstance(data,bytes) or not data or len(data)>10_000_000:
            raise ValueError("Unexpected source response bytes")
        frame=parse_response(data,site,year=year,month=month)
        frames.append(frame)
        raw=json.loads(data)
        provenance.append({
            "plant_id":str(site.plant_id),
            "eia860_plant_latitude":float(site.latitude),
            "eia860_plant_longitude":float(site.longitude),
            "site_nameplate_mw":float(site.nameplate_mw),
            "query_url":url,
            "source_response_sha256":hashlib.sha256(data).hexdigest(),
            "returned_latitude":raw.get("latitude"),
            "returned_longitude":raw.get("longitude"),
            "returned_elevation_m":raw.get("elevation"),
            "model_requested":"era5",
            "source_month":f"{year}-{month:02d}",
        })
    all_weather=pd.concat(frames,ignore_index=True)
    hours=24*calendar.monthrange(year,month)[1]
    if len(all_weather)!=hours*len(sites) or all_weather.duplicated(
            ["timestamp_utc","plant_id"]).any():
        raise ValueError("Incomplete independent wind plant-hour coverage")
    all_weather.to_csv(root/"srp_era5_wind_plant_hourly.csv",index=False)
    sites.to_csv(root/"srp_era5_wind_selected_plants.csv",index=False)
    summary=all_weather.assign(
        weighted_speed=all_weather.wind_speed_100m_ms*all_weather.capacity_weight,
        weighted_temperature=all_weather.temperature_2m_c*all_weather.capacity_weight
    ).groupby("timestamp_utc",as_index=False).agg(
        fleet_capacity_weighted_wind_speed_100m_ms=("weighted_speed","sum"),
        fleet_capacity_weighted_temperature_2m_c=("weighted_temperature","sum"))
    if len(summary)!=hours:raise AssertionError("ERA5 summary hours missing")
    summary.to_csv(root/"srp_era5_wind_fleet_hourly_exposure.csv",index=False)
    manifest={
        "source":"ERA5 reanalysis via Open-Meteo Historical Weather API",
        "ba":"SRP","year":year,"month":month,
        "plant_count":len(sites),"hours":hours,
        "site_hours":len(all_weather),
        "eligible_wind_nameplate_mw":float(sites.nameplate_mw.sum()),
        "plant_provenance":provenance,
        "plant_lat_lon_are_eia860_proxies_not_turbine_coordinates":True,
        "reanalysis_weather_not_direct_station_observation":True,
        "wind_fleet_exposure_not_generation_or_availability":True,
        "temperature_proxy_not_thermal_plant_heat_exposure":True,
        "wind_capacity_factor_calibrated":False,
        "hourly_generator_dispatch_certified":False,
        "historical_reliability_calibrated":False,
    }
    (root/"srp_era5_wind_source_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sites",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    args=p.parse_args()
    result=run(pd.read_csv(args.sites,dtype={"plant_id":"string"}),
               args.output,year=args.year,month=args.month)
    print(json.dumps({k:v for k,v in result.items() if k!="plant_provenance"},indent=2))


if __name__=="__main__":
    main()
