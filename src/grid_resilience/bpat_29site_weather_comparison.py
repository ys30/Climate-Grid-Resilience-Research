"""Diagnostic compare 29-site ERA5 proxy with BPAT reported net wind generation."""
import argparse,json,calendar
from pathlib import Path
import pandas as pd

def compare(weighted_csv,observed_csv,capacity_mw,output):
    weather=pd.read_csv(weighted_csv);obs=pd.read_csv(observed_csv)
    for frame in (weather,obs):
        frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
        if frame.timestamp.duplicated().any():raise ValueError("Duplicate UTC hour")
    aligned=weather.merge(obs[["timestamp","reported_wind_mw"]],on="timestamp",how="outer",indicator=True,validate="one_to_one")
    month=weather.timestamp.dt.month.unique()
    years=weather.timestamp.dt.year.unique()
    if len(month)!=1 or len(years)!=1:raise ValueError("Weather records must span exactly one calendar month")
    expected=24*calendar.monthrange(int(years[0]),int(month[0]))[1]
    if len(aligned)!=expected or not aligned._merge.eq("both").all():raise ValueError("Missing matching month hours")
    aligned["reported_ratio"]=aligned.reported_wind_mw/float(capacity_mw)
    aligned["observed_nonnegative_ratio"]=aligned.reported_ratio.clip(lower=0,upper=1)
    r=float(aligned.capacity_weighted_proxy_availability_pu.corr(aligned.observed_nonnegative_ratio))
    if not -1<=r<=1:raise ValueError("Invalid correlation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    aligned.drop(columns="_merge").to_csv(out/"bpat_29site_proxy_vs_reported.csv",index=False)
    manifest={"year":int(years[0]),"month":int(month[0]),"hours":len(aligned),
      "pearson_r_29_site_capacity_weighted":r,
      "mean_29site_idealized_proxy":float(aligned.capacity_weighted_proxy_availability_pu.mean()),
      "mean_reported_generation_to_nameplate":float(aligned.reported_ratio.mean()),
      "wind_fleet_actual_generation_independently_predicted":False,
      "regional_weather_model_calibrated":False,
      "note":"EIA-930 observed net wind generation differs from weather potential; correlation only diagnostic."}
    if int(years[0])==2024 and int(month[0])==2:
        manifest["pearson_r_prior_city_single_point"]=0.22479308594940883
        manifest["delta_pearson_r_vs_single_point"]=r-0.22479308594940883
    (out/"bpat_29site_comparison_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def main():
    p=argparse.ArgumentParser()
    for key in ("weighted","observed","output"):p.add_argument("--"+key,required=True)
    p.add_argument("--capacity-mw",type=float,required=True)
    a=p.parse_args()
    print(json.dumps(compare(a.weighted,a.observed,a.capacity_mw,a.output),indent=2))
if __name__=="__main__":main()
