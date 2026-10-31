"""ERA5 independent point-weather sampler at EIA-860 BPAT wind plants."""
import argparse,json,time,calendar
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen,Request
import pandas as pd
from .era5_point_wind_curve import power_curve

def sample(plants,output,year=2024,month=2):
    if not 1<=month<=12 or not 2000<=year<=2100:raise ValueError('Invalid ERA5 year/month')
    start=date(year,month,1).isoformat()
    end=date(year,month,calendar.monthrange(year,month)[1]).isoformat()
    expected_hours=24*calendar.monthrange(year,month)[1]
    sites=pd.read_csv(plants,dtype={"plant_id":str})
    if not {"plant_id","latitude","longitude","nameplate_mw","capacity_weight_within_sample"}.issubset(sites):raise ValueError("Missing site metadata")
    if sites.empty or sites.plant_id.duplicated().any():raise ValueError("Invalid site IDs")
    if abs(sites.capacity_weight_within_sample.sum()-1)>1e-5:raise ValueError("Invalid weights")
    records=[]
    for site in sites.itertuples(index=False):
        q=urlencode({"latitude":site.latitude,"longitude":site.longitude,
           "start_date":start,"end_date":end,"hourly":"wind_speed_100m",
           "models":"era5","wind_speed_unit":"ms","timezone":"GMT"})
        url="https://archive-api.open-meteo.com/v1/archive?"+q
        for attempt in range(4):
            try:
                with urlopen(Request(url,headers={"User-Agent":"GridResilienceResearch/1.0"}),timeout=120) as response:
                    data=json.load(response)
                break
            except Exception:
                if attempt==3:raise
                time.sleep(3*(attempt+1))
        hourly=data["hourly"]
        if data["hourly_units"]["wind_speed_100m"]!="m/s" or len(hourly["time"])!=expected_hours:raise ValueError("Unexpected ERA5 data")
        for stamp,speed in zip(hourly["time"],hourly["wind_speed_100m"]):
            if speed is None:raise ValueError("Null wind sample")
            records.append({"timestamp":stamp+"Z","plant_id":site.plant_id,
                "capacity_weight":site.capacity_weight_within_sample,
                "wind_speed_100m_ms":speed,"idealized_availability":power_curve(speed)})
    samples=pd.DataFrame(records)
    if len(samples)!=expected_hours*len(sites) or samples.duplicated(["timestamp","plant_id"]).any():raise ValueError("Missing site hours")
    aggregate=samples.assign(weighted=samples.capacity_weight*samples.idealized_availability).groupby("timestamp",as_index=False).weighted.sum()
    aggregate=aggregate.rename(columns={"weighted":"capacity_weighted_proxy_availability_pu"})
    if len(aggregate)!=expected_hours or not aggregate.capacity_weighted_proxy_availability_pu.between(0,1).all():
        raise ValueError("Invalid fleet proxy")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    samples.to_csv(out/"bpat_era5_plant_hourly.csv",index=False)
    aggregate.to_csv(out/"bpat_era5_capacity_weighted_hourly.csv",index=False)
    result={"year":year,"month":month,"sites":len(sites),"site_hours":len(samples),"hours":len(aggregate),
      "mean_capacity_weighted_idealized_proxy":float(aggregate.capacity_weighted_proxy_availability_pu.mean()),
      "weather_source":"ERA5 via Open-Meteo, EIA-860 2024 Plant point locations",
      "wind_power_curve":"uncalibrated 3/12/25 m/s cut-in/rated/cut-out",
      "wind_farm_location_is_plant_proxy":True,"historical_wind_generation_validated":False,
      "regional_reliability_calibrated":False}
    (out/"bpat_era5_plant_weighted_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plants",required=True);p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--month",type=int,default=2)
    a=p.parse_args();print(json.dumps(sample(a.plants,a.output,a.year,a.month),indent=2))
if __name__=="__main__":main()
