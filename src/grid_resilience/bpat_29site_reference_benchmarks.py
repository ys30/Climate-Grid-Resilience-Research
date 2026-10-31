"""Evaluate unfitted 29-site ERA5 proxy against transparent historical baselines.

Persistence uses previous observed generation and is NOT a fair operational
weather forecast comparison; it is only a scale/error sanity benchmark.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def score(reference,prediction):
    e=prediction-reference
    return {"n":int(len(e)),"mae_pu":float(np.mean(np.abs(e))),
            "rmse_pu":float(np.sqrt(np.mean(e**2))),
            "mean_bias_pu":float(np.mean(e)),
            "r2":float(1-np.sum(e**2)/np.sum((reference-reference.mean())**2))}

def evaluate(hourly,output):
    d=pd.read_csv(hourly)
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True)
    d=d.sort_values("timestamp")
    if len(d)!=696 or d.timestamp.duplicated().any():raise ValueError("Invalid February hourly grid")
    target=d.reported_ratio.clip(0,1).to_numpy(float)
    proxy=d.capacity_weighted_proxy_availability_pu.to_numpy(float)
    if not np.isfinite(target).all() or not np.isfinite(proxy).all():raise ValueError("Nonfinite input")
    results=[
      {"benchmark":"unfitted_era5_29_site_proxy",**score(target[24:],proxy[24:])},
      {"benchmark":"previous_hour_observed_persistence",**score(target[24:],target[23:-1])},
      {"benchmark":"previous_day_observed_persistence",**score(target[24:],target[:-24])}]
    path=Path(output);path.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(results).to_csv(path/"bpat_29site_reference_benchmark.csv",index=False)
    (path/"bpat_29site_reference_benchmark_manifest.json").write_text(json.dumps({
      "evaluation_hours":672,
      "target":"EIA-930 net wind output clipped to zero/nameplate",
      "proxy_training":"none; turbine power curve fixed before observing February output",
      "persistence_inputs":"prior EIA-930 observed wind generation",
      "fair_out_of_sample_weather_forecast_comparison":False,
      "independent_month_validation_completed":False,
      "caution":"Persistence references use the actual generation target history; comparison is diagnostic, not fair predictive skill certification."
    },indent=2)+"\n")
    return results
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(pd.DataFrame(evaluate(a.hourly,a.output)).to_csv(index=False))
if __name__=="__main__":main()
