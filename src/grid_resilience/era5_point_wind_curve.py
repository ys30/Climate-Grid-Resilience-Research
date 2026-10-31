"""Illustrative wind turbine power-curve transform of ERA5 100 m point winds.

NOT calibrated to operating wind farms, hub height, wake losses or plant fleet.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def power_curve(v,cut_in=3.0,rated=12.0,cut_out=25.0):
    if not 0<cut_in<rated<cut_out:raise ValueError("Invalid turbine thresholds")
    if pd.isna(v) or not 0<=float(v)<100:raise ValueError("Invalid wind speed")
    v=float(v)
    if v<cut_in or v>=cut_out:return 0.0
    if v>=rated:return 1.0
    return (v**3-cut_in**3)/(rated**3-cut_in**3)

def transform(weather,output):
    df=pd.read_csv(weather)
    required={"timestamp","ba","wind_speed_100m_ms","weather_source"}
    if not required.issubset(df):raise ValueError("Missing ERA5 wind inputs")
    if df.duplicated(["timestamp","ba"]).any() or len(df)!=2784:raise ValueError("Incomplete point-hour grid")
    df["proxy_availability_pu"]=df.wind_speed_100m_ms.apply(power_curve)
    if not df.proxy_availability_pu.between(0,1).all():raise AssertionError("Capacity factor out of bounds")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    df[["timestamp","ba","wind_speed_100m_ms","proxy_availability_pu"]].to_csv(out/"era5_point_wind_curve_proxy.csv",index=False)
    stats=df.groupby("ba",as_index=False).agg(mean_point_wind_ms=("wind_speed_100m_ms","mean"),
        mean_proxy_availability=("proxy_availability_pu","mean"),zero_proxy_hours=("proxy_availability_pu",lambda x:int((x==0).sum())))
    stats.to_csv(out/"era5_point_wind_curve_summary.csv",index=False)
    (out/"era5_point_wind_curve_manifest.json").write_text(json.dumps({
        "curve":"idealized cubic between 3 and 12 m/s, rated 12–25 m/s, shutoff at 25 m/s",
        "source":"ERA5 100m wind at four illustrative city-adjacent points",
        "is_operational_wind_fleet_availability":False,
        "is_calibrated_to_eia930_generation":False,
        "represents_full_balancing_authority":False,
        "technology_wake_curtailment_orographic_modeling":False,
        "historical_reliability_calibrated":False},indent=2)+"\n")
    return stats
def main():
    p=argparse.ArgumentParser();p.add_argument("--weather",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(transform(a.weather,a.output).to_string(index=False))
if __name__=="__main__":main()
