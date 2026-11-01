"""Compare source-audited monthly hydro observations with explicitly supplied model MWh.

This diagnostic refuses incomplete or mismatched model coverage. Passing these
checks does not certify historical calibration of the electric grid.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEYS=["reported_ba","prime_mover","period"]
BAS={"AZPS","BPAT","CISO","SRP"}
TECH={"HY","PS"}

def compare(observed_csv, modeled_csv, output):
    obs=pd.read_csv(observed_csv,keep_default_na=False)
    model=pd.read_csv(modeled_csv,keep_default_na=False)
    required_ob=set(KEYS+["net_generation_mwh","coverage_status"])
    required_model=set(KEYS+["modeled_net_generation_mwh"])
    if not required_ob.issubset(obs.columns):raise ValueError("Observed source columns missing")
    if not required_model.issubset(model.columns):raise ValueError("Model monthly columns missing")
    for df,label in ((obs,"observed"),(model,"modeled")):
        if df.duplicated(KEYS).any():raise ValueError(f"Duplicate {label} BA/technology/month key")
        if df[KEYS].isna().any().any() or df[KEYS].eq("").any().any():
            raise ValueError(f"Missing {label} key")
        if not df.reported_ba.isin(BAS).all() or not df.prime_mover.isin(TECH).all() or not df.period.str.fullmatch(r"2024-(0[1-9]|1[0-2])").all():
            raise ValueError(f"Invalid {label} BA/technology/month")
    if not obs.coverage_status.isin(["observed_source_rows","missing_source_rows"]).all():
        raise ValueError("Unknown observation coverage status")
    measured=obs.loc[obs.coverage_status=="observed_source_rows"].copy()
    if measured.empty:raise ValueError("No observed source rows for comparison")
    measured["net_generation_mwh"]=pd.to_numeric(measured.net_generation_mwh,errors="raise")
    if not np.isfinite(measured.net_generation_mwh).all():raise ValueError("Nonfinite observed MWh")
    model["modeled_net_generation_mwh"]=pd.to_numeric(model.modeled_net_generation_mwh,errors="raise")
    if not np.isfinite(model.modeled_net_generation_mwh).all():raise ValueError("Nonfinite modeled MWh")
    missing_model=measured[KEYS].merge(model[KEYS],on=KEYS,how="left",indicator=True)
    if (missing_model._merge=="left_only").any():
        raise ValueError("Modeled input does not cover all observed source BA/technology/month cells")
    # Model rows with no observed data remain unmatched; they never enter error metrics.
    joined=measured.merge(model,on=KEYS,how="inner",validate="one_to_one",suffixes=("_observed","_model"))
    joined["signed_error_mwh"]=joined.modeled_net_generation_mwh-joined.net_generation_mwh
    joined["absolute_error_mwh"]=joined.signed_error_mwh.abs()
    joined["squared_error_mwh2"]=joined.signed_error_mwh**2
    groups=[]
    for (ba,tech),g in joined.groupby(["reported_ba","prime_mover"],sort=True):
        groups.append({"reported_ba":ba,"prime_mover":tech,"matched_months":len(g),
                       "bias_mwh":float(g.signed_error_mwh.mean()),
                       "mae_mwh":float(g.absolute_error_mwh.mean()),
                       "rmse_mwh":float(np.sqrt(g.squared_error_mwh2.mean()))})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    joined.sort_values(KEYS).to_csv(out/"monthly_hydro_model_vs_observed.csv",index=False)
    pd.DataFrame(groups).to_csv(out/"monthly_hydro_model_error_metrics.csv",index=False)
    report={"matched_observed_cells":len(joined),
            "unobserved_source_cells_excluded":int((obs.coverage_status=="missing_source_rows").sum()),
            "groups":len(groups),"historical_calibration_certified":False,
            "caution":"Signed monthly net generation is not hourly hydro availability; these diagnostics do not validate system reliability or outage claims."}
    (out/"monthly_hydro_comparison_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observed",required=True)
    p.add_argument("--modeled",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(compare(a.observed,a.modeled,a.output),indent=2))

if __name__=="__main__":main()
