"""Audit cross-month wind-proxy error without mislabeling shape as calibration."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(csv_path,output):
    x=pd.read_csv(csv_path)
    required={"month","hours","pearson_r","mae_pu","rmse_pu","mean_bias_pu","ci_run"}
    if not required.issubset(x) or set(x.month)!={"2024-02","2024-03","2024-07"} or len(x)!=3:
        raise ValueError("Expected February March July source-linked wind evidence")
    for field in ("hours","pearson_r","mae_pu","rmse_pu","mean_bias_pu"):
        x[field]=pd.to_numeric(x[field],errors="raise")
        if not x[field].map(lambda v:-float("inf")<float(v)<float("inf")).all():
            raise ValueError("Nonfinite cross-month evidence")
    if not x.pearson_r.between(-1,1).all() or (x.mae_pu<0).any() or (x.rmse_pu<0).any():
        raise ValueError("Invalid error statistics")
    x["abs_bias_percentage_points"]=100*x.mean_bias_pu.abs()
    x["shape_vs_amplitude_mismatch"]=x.pearson_r.gt(0.8)&x.abs_bias_percentage_points.gt(5)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    x.sort_values("month").to_csv(out/"bpat_cross_month_shape_amplitude_audit.csv",index=False)
    report={"months":sorted(x.month.tolist()),
            "all_months_high_shape_correlation":bool(x.pearson_r.gt(.8).all()),
            "months_with_gt_5pp_amplitude_bias":sorted(x.loc[x.abs_bias_percentage_points.gt(5),"month"].tolist()),
            "max_absolute_bias_percentage_points":float(x.abs_bias_percentage_points.max()),
            "calibration_certified":False,
            "warning":"Correlation and shape checks do not establish calibrated wind output or a defensible 30% weather derating."}
    (out/"bpat_cross_month_evidence_gate.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output),indent=2))
if __name__=="__main__":main()
