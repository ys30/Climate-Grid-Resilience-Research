"""Describe exact BA/hour interchange reporting mismatches without inventing thermal limits."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(hourly,output):
    d=pd.read_csv(hourly)
    required={"ba","timestamp","difference_mw","balance_interchange_mw","sum_bilateral_interchange_mw"}
    if not required.issubset(d.columns):raise ValueError("Missing exchange reconciliation columns")
    if d.duplicated(["ba","timestamp"]).any():raise ValueError("Duplicate BA-hour")
    if set(d.ba)!={"AZPS","BPAT","CISO","SRP"}:raise ValueError("Unexpected BA scope")
    if len(d)!=2784 or not (d.groupby("ba").size()==696).all():raise ValueError("Incomplete February BA-hour coverage")
    d["abs_difference_mw"]=d.difference_mw.abs()
    g=d.groupby("ba",sort=True).agg(hours=("difference_mw","size"),nonzero_hours=("abs_difference_mw",lambda s:int((s>0.001).sum())),absolute_difference_mwh=("abs_difference_mw","sum"),peak_hourly_difference_mw=("abs_difference_mw","max")).reset_index()
    if abs(g.absolute_difference_mwh.sum()-331)>0.001:raise ValueError("Official interchange baseline changed; investigate")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    g.to_csv(out/"interchange_outlier_summary.csv",index=False)
    d.loc[d.abs_difference_mw>0.001].sort_values("abs_difference_mw",ascending=False).to_csv(out/"interchange_outlier_hours.csv",index=False)
    manifest={"matched_ba_hours":len(d),"absolute_difference_mwh":float(g.absolute_difference_mwh.sum()),"thermal_capacity_inferred":False}
    (out/"interchange_outlier_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.hourly,a.output),indent=2))
if __name__=="__main__":main()
