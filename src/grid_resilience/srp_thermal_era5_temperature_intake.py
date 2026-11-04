"""Fetch source-provenanced ERA5 2m temperatures at selected SRP thermal plants.

Plant coordinates and site selection come from EIA860. These are point
reanalysis exposures, NOT temperature-to-derating coefficients.
"""
import argparse
import calendar
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
import numpy as np
import pandas as pd

BASE="https://archive-api.open-meteo.com/v1/archive"


def validate_response(payload,*,year=2024,month=1):
    obj=json.loads(payload)
    if obj.get("error") or obj.get("utc_offset_seconds")!=0:
        raise ValueError("ERA5 response error or non-UTC offset")
    if obj.get("hourly_units",{}).get("temperature_2m") not in ("°C","C"):
        raise ValueError("Wrong ERA5 temperature units")
    hourly=obj.get("hourly",{})
    n=calendar.monthrange(year,month)[1]*24
    timestamps=pd.to_datetime(pd.Series(hourly.get("time",[])),utc=True,errors="raise")
    expected=pd.date_range(f"{year}-{month:02d}-01",periods=n,freq="h",tz="UTC")
    if not pd.DatetimeIndex(timestamps).equals(expected):
        raise ValueError("ERA5 744h UTC time mismatch")
    t=np.asarray(hourly.get("temperature_2m",[]),dtype=float)
    if len(t)!=n or not np.isfinite(t).all() or (t<-100).any() or (t>70).any():
        raise ValueError("ERA5 missing/unphysical temperature")
    return expected,t,obj


def sample(sites,output,*,year=2024,month=1,fetch=None):
    needed={"technology","plant_id","latitude","longitude","nameplate_mw"}
    if not needed.issubset(sites):raise ValueError("Missing selected site columns")
    s=sites.copy()
    s["plant_id"]=s.plant_id.astype("string").str.strip()
    if s.empty or s.duplicated(["technology","plant_id"]).any():
        raise ValueError("Empty or duplicate selected thermal sites")
    if not set(s.technology).issubset({"gas","coal"}):
        raise ValueError("Unsupported thermal category")
    for col in ("latitude","longitude","nameplate_mw"):
        s[col]=pd.to_numeric(s[col],errors="coerce")
    if not np.isfinite(s[["latitude","longitude","nameplate_mw"]].to_numpy(float)).all():
        raise ValueError("Missing site coordinates/nameplate")
    if not s.latitude.between(20,55).all() or not s.longitude.between(-130,-95).all():
        raise ValueError("Invalid plant coordinate")
    if (s.nameplate_mw<=0).any():raise ValueError("Nonpositive site capacity")
    if not (2000<=year<=2100 and 1<=month<=12):
        raise ValueError("Invalid ERA5 requested month")
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    records=[];provenance=[]
    for site in s.sort_values(["technology","plant_id"]).itertuples(index=False):
        query=urlencode({"latitude":float(site.latitude),"longitude":float(site.longitude),
                         "start_date":date(year,month,1).isoformat(),
                         "end_date":date(year,month,calendar.monthrange(year,month)[1]).isoformat(),
                         "hourly":"temperature_2m","models":"era5","timezone":"GMT"})
        url=BASE+"?"+query
        if fetch is None:
            with urlopen(Request(url,headers={"User-Agent":"GridResilienceResearch/1.0"}),timeout=120) as h:
                payload=h.read(10_000_001)
        else:payload=fetch(url)
        if not isinstance(payload,bytes) or not payload or len(payload)>10_000_000:
            raise ValueError("ERA5 response bytes invalid")
        hours,t,obj=validate_response(payload,year=year,month=month)
        records.extend({"timestamp_utc":hour.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "technology":site.technology,"plant_id":str(site.plant_id),
                        "temperature_2m_c":float(temp),
                        "selected_nameplate_mw":float(site.nameplate_mw)}
                       for hour,temp in zip(hours,t))
        provenance.append({"technology":site.technology,"plant_id":str(site.plant_id),
                           "url":url,"sha256":hashlib.sha256(payload).hexdigest(),
                           "requested_latitude":float(site.latitude),
                           "requested_longitude":float(site.longitude),
                           "returned_latitude":obj.get("latitude"),
                           "returned_longitude":obj.get("longitude")})
    raw=pd.DataFrame(records)
    n=24*calendar.monthrange(year,month)[1]
    if len(raw)!=n*len(s) or raw.duplicated(
        ["timestamp_utc","technology","plant_id"]).any():
        raise ValueError("Incomplete site-hour evidence")
    raw.to_csv(root/"srp_thermal_era5_plant_hourly.csv",index=False)
    raw["weighted"]=raw.temperature_2m_c*raw.selected_nameplate_mw
    aggregate=raw.groupby(["timestamp_utc","technology"],as_index=False).agg(
        weighted_celsius=("weighted","sum"),nameplate_mw=("selected_nameplate_mw","sum"))
    aggregate["capacity_weighted_temperature_c"]=aggregate.weighted_celsius/aggregate.nameplate_mw
    aggregate=aggregate.drop(columns="weighted_celsius")
    aggregate.to_csv(root/"srp_thermal_era5_technology_hourly.csv",index=False)
    metadata={"period":f"{year}-{month:02d}","hours_per_plant":n,
              "selected_site_count":len(s),"selected_site_hours":len(raw),
              "source":"ERA5 reanalysis via Open-Meteo Historical Weather API",
              "plant_provenance":provenance,
              "eia860_plant_ba_not_dispatch_right":True,
              "subset_point_coverage_not_entire_ba":True,
              "weather_to_generator_derating_calibrated":False,
              "historical_outage_or_eens_estimated":False}
    (root/"srp_thermal_era5_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return metadata


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sites",required=True);p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=1)
    args=p.parse_args()
    print(json.dumps(sample(pd.read_csv(args.sites,dtype={"plant_id":"string"}),
                            args.output,year=args.year,month=args.month),indent=2))


if __name__=="__main__":
    main()
