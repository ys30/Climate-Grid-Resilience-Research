"""Audit hourly wind proxy amplitude error, without fitting to observed output."""
import argparse,json,calendar
from pathlib import Path
import numpy as np
import pandas as pd

def evaluate(hourly,output):
    x=pd.read_csv(hourly)
    a=x["capacity_weighted_proxy_availability_pu"].to_numpy(float)
    b=x["reported_ratio"].clip(0,1).to_numpy(float)
    times=pd.to_datetime(x["timestamp"],utc=True,errors="raise")
    year=times.dt.year.unique();month=times.dt.month.unique()
    if len(year)!=1 or len(month)!=1:raise ValueError("Exactly one calendar month required")
    expected=calendar.monthrange(int(year[0]),int(month[0]))[1]*24
    if not (int(expected*0.95)<=len(a)<=expected) or times.duplicated().any() or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError(f"Expected {expected} unique finite hourly observations")
    delta=a-b
    labels=pd.to_datetime(x["timestamp"],utc=True).dt.day
    result=[]
    for label,mask in [("month",np.ones(len(x),dtype=bool)),
                       ("days_01_07",(labels<=7).to_numpy()),
                       ("days_08_14",((labels>=8)&(labels<=14)).to_numpy()),
                       ("days_15_21",((labels>=15)&(labels<=21)).to_numpy()),
                       ("days_22_end",(labels>=22).to_numpy())]:
        v=delta[mask]
        result.append({"period":label,"hours":int(mask.sum()),
                       "mean_bias_pu":float(v.mean()),
                       "mae_pu":float(np.abs(v).mean()),
                       "rmse_pu":float(np.sqrt(np.mean(v*v))),
                       "mean_proxy_pu":float(a[mask].mean()),
                       "mean_observed_clipped_pu":float(b[mask].mean())})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(result).to_csv(out/"bpat_29site_proxy_error_diagnostics.csv",index=False)
    (out/"bpat_29site_proxy_error_manifest.json").write_text(json.dumps({
        "units":"fractions of EIA-860 nameplate, not MW",
        "model":"unfitted 29-plant capacity-weighted idealized power curve",
        "observed_target":"EIA-930 net wind generation clipped to [0,1] of nameplate",
        "same_month_only":True,"independent_forecast_skill_established":False,
        "note":"These are diagnostic errors between weather potential proxy and net generation, not operational forecast accuracy."
    },indent=2)+"\n")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--hourly",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    print(pd.DataFrame(evaluate(args.hourly,args.output)).to_csv(index=False))
if __name__=="__main__":main()
