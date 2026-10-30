"""Open-Meteo ERA5 point-proxy weather ingestion for selected balancing authorities.

The point locations are representative proxies, NOT BA polygons or plant-level
meteorology. Wind availability is a *hypothetical* cubic-power-curve proxy,
not a calibrated wind generation capacity factor.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
import pandas as pd

POINTS={"CISO":(36.17,-119.75),"AZPS":(33.45,-112.07),
        "BPAT":(45.52,-122.68),"SRP":(33.42,-111.83)}
ENDPOINT="https://archive-api.open-meteo.com/v1/archive"

def convert(hourly,ba,start,end):
    need={"time","temperature_2m","wind_speed_100m"}
    if not need.issubset(hourly):raise ValueError(f"{ba}: missing ERA5 fields")
    frame=pd.DataFrame({key:hourly[key] for key in need})
    frame["timestamp"]=pd.to_datetime(frame.pop("time"),utc=True,errors="raise")
    frame["ba"]=ba
    frame["temperature_c"]=pd.to_numeric(frame.pop("temperature_2m"),errors="coerce")
    speed=pd.to_numeric(frame.pop("wind_speed_100m"),errors="coerce")
    if frame.timestamp.duplicated().any():raise ValueError(f"{ba}: repeated timestamps")
    if speed.isna().any() or (speed<0).any() or frame.temperature_c.isna().any():
        raise ValueError(f"{ba}: invalid ERA5 hourly values")
    # Wind: 3 m/s cut-in, 12 m/s rated, 25 m/s cut-out. Simplified model input only.
    availability=((speed**3-3**3)/(12**3-3**3)).clip(0,1)
    availability=availability.where(speed<25,0)
    frame["wind_availability"]=availability
    expected=pd.date_range(start,end,freq="h",inclusive="left",tz="UTC")
    frame=frame.loc[(frame.timestamp>=expected[0])&(frame.timestamp< pd.Timestamp(end))]
    if len(frame)!=len(expected) or set(frame.timestamp)!=set(expected):
        raise ValueError(f"{ba}: incomplete ERA5 hourly coverage")
    return frame[["timestamp","ba","temperature_c","wind_availability"]].sort_values("timestamp")

def fetch(bas,start,end):
    if not bas or len(set(bas))!=len(bas) or set(bas)-set(POINTS):
        raise ValueError("Unsupported/duplicated BA")
    st=pd.Timestamp(start);en=pd.Timestamp(end)
    if st.tzinfo is None or en.tzinfo is None:raise ValueError("UTC timestamps required")
    st=st.tz_convert("UTC");en=en.tz_convert("UTC")
    if en<=st or st.hour!=0 or en.hour!=0 or st.minute or en.minute:
        raise ValueError("Whole-day UTC boundaries required")
    if (en-st).days>31:raise ValueError("Use bounded <=31-day event windows")
    result=[]
    for ba in bas:
        lat,lon=POINTS[ba]
        params={"latitude":lat,"longitude":lon,
                "start_date":st.date().isoformat(),
                "end_date":(en-pd.Timedelta(days=1)).date().isoformat(),
                "hourly":"temperature_2m,wind_speed_100m",
                "models":"era5","timezone":"GMT"}
        with urlopen(ENDPOINT+"?"+urlencode(params),timeout=120) as response:
            obj=json.load(response)
        if "hourly" not in obj:raise ValueError(f"{ba}: invalid ERA5 response")
        result.append(convert(obj["hourly"],ba,st,en))
    return pd.concat(result,ignore_index=True).sort_values(["timestamp","ba"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bas",nargs="+",required=True)
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    frame=fetch(a.bas,a.start,a.end)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out,index=False)
    metadata={"source":"Open-Meteo ERA5 archive","model":"era5",
              "geography":"representative point proxies; NOT BA polygons",
              "ba_coordinates":{ba:POINTS[ba] for ba in a.bas},
              "wind_availability":"hypothetical 3/12/25 m/s power curve, not calibrated",
              "bas":a.bas,"hours_per_ba":len(frame)//len(a.bas),
              "start":a.start,"end_exclusive":a.end}
    out.with_suffix(".manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))
if __name__=="__main__":main()
