"""Time-block validation of the BPAT 29-site ERA5 proxy against EIA-930.

Diagnostic correlations by week and first/second half; not out-of-sample
model validation, since the physical power curve was fixed a priori.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def report(hourly_csv,output):
    x=pd.read_csv(hourly_csv)
    needed={"timestamp","capacity_weighted_proxy_availability_pu","observed_nonnegative_ratio"}
    if not needed.issubset(x):
        if "reported_ratio" in x:
            x["observed_nonnegative_ratio"]=x.reported_ratio.clip(0,1)
        else:raise ValueError("Missing observed ratio")
    x["timestamp"]=pd.to_datetime(x.timestamp,utc=True)
    x=x.sort_values("timestamp")
    if len(x)!=696 or x.timestamp.duplicated().any():raise ValueError("Expected 696 unique hourly records")
    groups=[("days_01_07",x.iloc[:168]),("days_08_14",x.iloc[168:336]),
            ("days_15_21",x.iloc[336:504]),("days_22_29",x.iloc[504:]),
            ("first_half",x.iloc[:348]),("second_half",x.iloc[348:])]
    rows=[]
    for name,frame in groups:
        r=float(frame.capacity_weighted_proxy_availability_pu.corr(frame.observed_nonnegative_ratio))
        rows.append({"period":name,"hours":len(frame),"pearson_r":r,
                     "mean_proxy":float(frame.capacity_weighted_proxy_availability_pu.mean()),
                     "mean_observed":float(frame.observed_nonnegative_ratio.mean())})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/"bpat_29site_time_block_correlation.csv",index=False)
    metadata={"blocks":len(rows),"all_hours":696,"independent_test_set":False,
              "scope":"within-month diagnostic stability only",
              "wind_fleet_generation_calibrated":False}
    (out/"bpat_29site_time_block_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return rows
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(pd.DataFrame(report(a.hourly,a.output)).to_csv(index=False))
if __name__=="__main__":main()
