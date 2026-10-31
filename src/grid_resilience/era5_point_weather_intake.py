"""Download four explicitly illustrative ERA5 point meteorological series.

These point samples do NOT represent balancing-authority-wide weather,
wind farm locations, production potential, or calibrated availability.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from .independent_weather_gate import validate

# Illustrative city-near point coordinates; not BA polygons or wind-farm sites.
SITES={
    "AZPS":{"name":"Tucson-area illustrative point","latitude":32.22,"longitude":-110.97},
    "BPAT":{"name":"Portland-area illustrative point","latitude":45.52,"longitude":-122.68},
    "CISO":{"name":"Sacramento-area illustrative point","latitude":38.58,"longitude":-121.49},
    "SRP":{"name":"Phoenix-area illustrative point","latitude":33.45,"longitude":-112.07},
}
BASE="https://archive-api.open-meteo.com/v1/archive"
def download(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows=[];meta=[]
    for ba,site in SITES.items():
        query={"latitude":site["latitude"],"longitude":site["longitude"],
               "start_date":"2024-02-01","end_date":"2024-02-29",
               "hourly":"wind_speed_10m,wind_speed_100m,temperature_2m",
               "models":"era5","wind_speed_unit":"ms","timezone":"GMT"}
        url=BASE+"?"+urlencode(query)
        with urlopen(Request(url,headers={"User-Agent":"GridResilienceResearch/1.0"}),timeout=120) as response:
            payload=response.read()
        data=json.loads(payload)
        hourly=data.get("hourly",{})
        times=hourly.get("time",[])
        speeds=hourly.get("wind_speed_10m",[])
        speeds100=hourly.get("wind_speed_100m",[])
        temperatures=hourly.get("temperature_2m",[])
        if any(len(v)!=696 for v in (times,speeds,speeds100,temperatures)):
            raise ValueError(f"Incomplete hourly ERA5 proxy for {ba}")
        units=data.get("hourly_units",{})
        if units.get("wind_speed_10m")!="m/s" or units.get("wind_speed_100m")!="m/s":
            raise ValueError(f"Unexpected ERA5 wind units for {ba}: {units}")
        if len(times)!=len(set(times)):raise ValueError("Duplicate weather timestamps")
        for t,w,w100,temp in zip(times,speeds,speeds100,temperatures):
            if any(v is None for v in (w,w100,temp)):raise ValueError("Null ERA5 measurement")
            rows.append({"timestamp":t+"Z","ba":ba,"wind_speed_ms":w,
                "wind_speed_100m_ms":w100,"temperature_2m_c":temp,
                "weather_source":"Open-Meteo ERA5 point reanalysis",
                "source_variable":"wind_speed_10m"})
        meta.append({"ba":ba,**site,"query_url":url,"response_sha256":hashlib.sha256(payload).hexdigest(),
                     "returned_latitude":data.get("latitude"),"returned_longitude":data.get("longitude"),
                     "elevation_m":data.get("elevation")})
    source=out/"era5_proxy_points_raw.csv"
    with source.open("w",newline="") as handle:
        wr=csv.DictWriter(handle,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    gate=validate(source,out/"validated")
    result={"period":"2024-02","dataset":"ERA5 via Open-Meteo Historical Weather API",
            "site_type":"illustrative city-near point proxies, not entire BA footprint",
            "points":meta,"hourly_rows":len(rows),"quality_gate":gate,
            "regional_weather_calibration_completed":False,
            "wind_turbine_capacity_factor_model_completed":False,
            "historical_reliability_calibrated":False}
    (out/"era5_proxy_point_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    r=download(args.output)
    print(json.dumps({"hourly_rows":r["hourly_rows"],"points":len(r["points"]),
                      "regional_weather_calibration_completed":False},indent=2))
if __name__=="__main__":main()
