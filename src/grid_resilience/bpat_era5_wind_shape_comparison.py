"""Compare BPAT ERA5 city-point wind proxy with EIA-930 observed fleet output.

Correlation and mean differences are diagnostic only: one city point is
not a wind-farm-weighted regional weather signal, and net generation is
not independently estimated meteorological availability.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def compare(proxy_csv,wind_csv,capacity_csv,output):
    p=pd.read_csv(proxy_csv); w=pd.read_csv(wind_csv);caps=pd.read_csv(capacity_csv)
    p=p[p.ba=="BPAT"].copy()
    c=caps[(caps.ba=="BPAT")&(caps.technology=="wind")]
    if len(c)!=1:raise ValueError("Expected unique BPAT capacity")
    mw=float(c.iloc[0].nameplate_capacity_mw)
    if not 0<mw<float("inf"):raise ValueError("Invalid installed capacity")
    for frame in (p,w):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.timestamp.duplicated().any():raise ValueError("Duplicate UTC hour")
    both=p.merge(w[["timestamp","reported_wind_mw"]],on="timestamp",how="outer",indicator=True,validate="one_to_one")
    if len(both)!=696 or not both._merge.eq("both").all():
        raise ValueError("Missing or unmatched BPAT hourly data")
    both["timestamp"]=both["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    both["observed_generation_to_nameplate"]=both.reported_wind_mw/mw
    both["observed_nonnegative_proxy"]=both.observed_generation_to_nameplate.clip(lower=0,upper=1)
    correlation=float(both.proxy_availability_pu.corr(both.observed_nonnegative_proxy))
    if not -1<=correlation<=1:raise ValueError("Invalid or undefined correlation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    both.drop(columns="_merge").to_csv(out/"bpat_era5_point_vs_reported_wind_hourly.csv",index=False)
    summary={"hours":len(both),"pearson_hourly_correlation":correlation,
       "era5_city_point_mean_idealized_wind_proxy":float(both.proxy_availability_pu.mean()),
       "eia930_reported_wind_mean_to_eia860_nameplate":float(both.observed_generation_to_nameplate.mean()),
       "negative_reported_wind_hours":int((both.reported_wind_mw<0).sum()),
       "proxy_is_ba_representative":False,"observed_generation_is_weather_availability":False,
       "independent_historical_generation_prediction_validated":False,
       "warning":"This checks hourly shape only; reported wind output contains dispatch and curtailment, and ERA5 is sampled at a city point."}
    (out/"bpat_era5_point_wind_comparison_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary
def main():
    p=argparse.ArgumentParser()
    for x in ("proxy","wind","capacity","output"):p.add_argument("--"+x,required=True)
    a=p.parse_args();print(json.dumps(compare(a.proxy,a.wind,a.capacity,a.output),indent=2))
if __name__=="__main__":main()
