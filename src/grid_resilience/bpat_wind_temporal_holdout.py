"""Blocked February holdout of a ONE-PARAMETER wind-proxy scale calibration.

Training and testing are chronologically disjoint; this is within-month
validation, not independent cross-month or operational forecast validation.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def score(y,p):
    e=p-y
    return {"mae_pu":float(np.mean(abs(e))),"rmse_pu":float(np.sqrt(np.mean(e*e))),
            "mean_bias_pu":float(np.mean(e))}

def evaluate(source,out):
    d=pd.read_csv(source)
    required={"timestamp","reported_ratio","capacity_weighted_proxy_availability_pu"}
    if not required.issubset(d):raise ValueError("Missing expected hourly data")
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True)
    d=d.sort_values("timestamp")
    if len(d)!=696 or d.timestamp.duplicated().any():raise ValueError("Expected February's 696 unique hours")
    if not (d.timestamp.diff().dropna()==pd.Timedelta(hours=1)).all():raise ValueError("Time discontinuity")
    x=d.capacity_weighted_proxy_availability_pu.to_numpy(dtype=float)
    y=d.reported_ratio.clip(0,1).to_numpy(dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all() or not ((x>=0)&(x<=1)).all():
        raise ValueError("Invalid proxy/observations")
    # 14 full training days followed by 15 held-out days, and the reverse.
    blocks=[("first14_to_last15",np.arange(0,336),np.arange(336,696)),
            ("last15_to_first14",np.arange(336,696),np.arange(0,336))]
    rows=[]
    for name,tr,te in blocks:
        denom=float(x[tr]@x[tr])
        if denom<=0:raise ValueError("Cannot fit wind scale with zero training wind")
        scale=max(0.0,float((x[tr]@y[tr])/denom))
        uncal=x[te]
        calibrated=np.clip(scale*x[te],0,1)
        for mode,p in [("uncalibrated",uncal),("train_only_scale_clipped",calibrated)]:
            rows.append({"split":name,"method":mode,"train_hours":len(tr),"test_hours":len(te),
                         "fitted_scale":scale if mode!="uncalibrated" else 1.0,
                         **score(y[te],p)})
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/"bpat_wind_temporal_holdout.csv",index=False)
    manifest={"split_policy":"two disjoint chronological February 2024 blocks",
              "training_uses_held_out_hours":False,
              "calibration":"nonnegative one-parameter OLS on training hours; clipped to [0,1] in test",
              "independent_month_out_of_sample_validation":False,
              "causal_climate_hazard_assessment":False,
              "warning":"Temporal holdout evaluates amplitude stability within a single month; EIA-930 reported wind is a net-generation ratio, not physical potential."}
    (out/"bpat_wind_temporal_holdout_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return pd.DataFrame(rows)
def main():
    a=argparse.ArgumentParser();a.add_argument("--input",required=True);a.add_argument("--output",required=True)
    args=a.parse_args();print(evaluate(args.input,args.output).to_csv(index=False))
if __name__=="__main__":main()
