"""Inject independent 29-plant ERA5 wind ceiling into PyPSA BA availability.

The wind field is a *potential proxy*, not calibrated generation. All other
BA/technology cells are kept unchanged. UTC hour coverage is strict.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def inject(availability_csv,weather_csv,output):
    base=pd.read_csv(availability_csv)
    weather=pd.read_csv(weather_csv)
    needed={"timestamp","ba","technology","availability_pu"}
    if not needed.issubset(base):raise ValueError("Missing PyPSA availability columns")
    if not {"timestamp","capacity_weighted_proxy_availability_pu"}.issubset(weather):
        raise ValueError("Missing 29-plant wind weather")
    if base.duplicated(["timestamp","ba","technology"]).any() or weather.timestamp.duplicated().any():
        raise ValueError("Duplicate model or weather hours")
    base["time_utc"]=pd.to_datetime(base.timestamp,utc=True,errors="raise")
    weather["time_utc"]=pd.to_datetime(weather.timestamp,utc=True,errors="raise")
    mask=base.ba.eq("BPAT")&base.technology.eq("wind")
    if mask.sum()!=696 or len(weather)!=696:raise ValueError("Expected 696 BPAT wind hours")
    if not set(base.loc[mask,"time_utc"])==set(weather.time_utc):
        raise ValueError("ERA5 and dispatch time coverage differ")
    values=pd.to_numeric(weather.capacity_weighted_proxy_availability_pu,errors="raise")
    if values.isna().any() or not values.between(0,1).all():
        raise ValueError("Invalid wind capacity-factor proxy")
    original=base.loc[~mask,["timestamp","ba","technology","availability_pu"]].copy()
    lookup=pd.Series(values.to_numpy(),index=weather.time_utc)
    base.loc[mask,"availability_pu"]=base.loc[mask,"time_utc"].map(lookup).to_numpy()
    assert original.reset_index(drop=True).equals(base.loc[~mask,["timestamp","ba","technology","availability_pu"]].reset_index(drop=True))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    base.drop(columns="time_utc").to_csv(out/"era5_29site_wind_availability.csv",index=False)
    info={"replaced_bpat_wind_hours":int(mask.sum()),
      "mean_era5_29site_wind_proxy":float(values.mean()),
      "non_wind_inputs_unchanged":True,
      "weather_to_generation_calibrated":False,
      "ba_wide_weather_validated":False,
      "historical_reliability_calibrated":False,
      "note":"Only a conditional PyPSA input substitution; an independent adequacy claim requires hydro, transfers, and thermal availability."}
    (out/"era5_29site_wind_availability_manifest.json").write_text(json.dumps(info,indent=2)+"\n")
    return info
def main():
    p=argparse.ArgumentParser()
    for name in ("availability","weather","output"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(inject(a.availability,a.weather,a.output),indent=2))
if __name__=="__main__":main()
