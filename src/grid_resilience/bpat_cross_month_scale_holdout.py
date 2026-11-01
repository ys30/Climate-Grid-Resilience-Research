"""Fit a one-parameter wind-proxy scale on February, evaluate untouched months.

This tests the *reported output ratio*, not physical weather generation potential.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

def data(path,month):
    x=pd.read_csv(path)
    needed={"timestamp","capacity_weighted_proxy_availability_pu","reported_ratio"}
    if not needed.issubset(x):raise ValueError("Missing wind proxy columns")
    x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="raise")
    if x.timestamp.duplicated().any() or x.empty or not x.timestamp.dt.strftime("%Y-%m").eq(month).all():
        raise ValueError("Duplicate or wrong-month observed hour")
    x=x.sort_values("timestamp")
    a=x.capacity_weighted_proxy_availability_pu.to_numpy(dtype=float)
    b=x.reported_ratio.to_numpy(dtype=float)
    if not np.isfinite(a).all() or not np.isfinite(b).all() or ((a<0)|(a>1)).any():
        raise ValueError("Invalid wind proxy observations")
    return a,np.clip(b,0,1),len(x)

def metrics(actual,pred):
    diff=pred-actual
    return {"mae_pu":float(np.mean(np.abs(diff))),"rmse_pu":float(np.sqrt(np.mean(diff**2))),
            "bias_pu":float(np.mean(diff))}

def evaluate(feb,march,july,out):
    x,y,n=data(feb,"2024-02")
    if n!=696:raise ValueError("Incomplete February training window")
    denom=float(x@x)
    if denom<=0:raise ValueError("No wind in training")
    scale=max(0.0,float((x@y)/denom))
    rows=[]
    for label,path in (("2024-02_train",feb),("2024-03_holdout",march),("2024-07_holdout",july)):
        xx,yy,hours=data(path,label[:7])
        if label.startswith("2024-03") and hours!=744:raise ValueError("Incomplete March")
        if label.startswith("2024-07") and hours<700:raise ValueError("Too few July observations")
        for method,pred in (("raw_proxy",xx),("feb_trained_scale",np.clip(xx*scale,0,1))):
            rows.append({"period":label,"method":method,"hours":hours,
                         "fitted_scale_from_feb":scale,**metrics(yy,pred)})
    result=pd.DataFrame(rows)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"bpat_feb_train_march_july_holdout.csv",index=False)
    report={"train_month":"2024-02","held_out_months":["2024-03","2024-07"],
            "february_fitted_scale":scale,"held_out_observations_used_in_fit":False,
            "historical_generation_calibrated":False,
            "warning":"One-parameter correction is a diagnostic of reported BA wind output, not independently verified weather-to-power physics or outage forecasts."}
    (out/"bpat_cross_month_holdout_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    for name in ("feb","march","july","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args();print(evaluate(a.feb,a.march,a.july,a.out).to_string(index=False))
if __name__=="__main__":main()
