"""Publish reproducible winter/spring/summer diagnostics after July CI.

February and March reference values are pinned to successful GitHub Actions
runs; July is read from the new execution, never filled with assumptions.
"""
import argparse,json
from pathlib import Path
import pandas as pd

BASELINES=[
 {"month":"2024-02","hours":696,"pearson_r":0.8934045249494896,"mae_pu":0.07483128114981306,"rmse_pu":0.10964967988052599,"mean_bias_pu":-0.05273004872215832,"ci_run":41227782144},
 {"month":"2024-03","hours":744,"pearson_r":0.904462969000032,"mae_pu":0.08647650949085936,"rmse_pu":0.12527353791826085,"mean_bias_pu":-0.0822985168338617,"ci_run":41238968791}]

def build(comparison,error,output):
    manifest=json.loads(Path(comparison).read_text())
    e=pd.read_csv(error)
    monthly=e[e.period.eq("month")]
    if len(monthly)!=1 or manifest.get("year")!=2024 or manifest.get("month")!=7 or manifest.get("hours")!=744:
        raise ValueError("July output missing or misdated")
    m=monthly.iloc[0]
    rows=BASELINES+[{"month":"2024-07","hours":744,
        "pearson_r":float(manifest["pearson_r_29_site_capacity_weighted"]),
        "mae_pu":float(m.mae_pu),"rmse_pu":float(m.rmse_pu),
        "mean_bias_pu":float(m.mean_bias_pu),"ci_run":None}]
    d=pd.DataFrame(rows)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"bpat_era5_three_month_validation.csv",index=False)
    summary={"reference_runs":[41227782144,41238968791],
      "july_pearson_r":float(d.iloc[-1].pearson_r),
      "july_minus_feb_pearson_r":float(d.iloc[-1].pearson_r-d.iloc[0].pearson_r),
      "july_minus_march_pearson_r":float(d.iloc[-1].pearson_r-d.iloc[1].pearson_r),
      "july_mae_pu":float(d.iloc[-1].mae_pu),
      "july_bias_pu":float(d.iloc[-1].mean_bias_pu),
      "calibration_claim":False,"same_frozen_wind_curve":True,
      "caution":"July wind reported net generation is not weather potential; no PyPSA historical outage validation."}
    (out/"bpat_era5_three_month_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary
def main():
    p=argparse.ArgumentParser()
    for field in ("comparison","error","output"):p.add_argument("--"+field,required=True)
    a=p.parse_args();print(json.dumps(build(a.comparison,a.error,a.output),indent=2))
if __name__=="__main__":main()
