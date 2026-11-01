"""Interpret EIA-930 reported net interchange, with accounting discrepancy flags.

Reported BA net interchange is historical energy flow, NOT physical intertie
capacity or dispatchable import availability.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(interchange_csv,demand_csv,output,abs_tolerance_mwh=1):
    i=pd.read_csv(interchange_csv)
    d=pd.read_csv(demand_csv)
    expected_i={"ba","period","reported_interchange_mwh","generation_minus_demand_mwh","discrepancy_mwh"}
    if not expected_i.issubset(i) or not {"ba","timestamp","demand_mw"}.issubset(d):
        raise ValueError("Missing interchange audit fields")
    if i.empty or d.empty or i.ba.duplicated().any() or d.duplicated(["ba","timestamp"]).any():
        raise ValueError("Empty or duplicate BA data")
    if set(i.ba)!=set(d.ba):raise ValueError("BA coverage differs")
    for field in ("reported_interchange_mwh","generation_minus_demand_mwh","discrepancy_mwh"):
        i[field]=pd.to_numeric(i[field],errors="raise")
    d["demand_mw"]=pd.to_numeric(d.demand_mw,errors="raise")
    if not i[list(expected_i-{"ba","period"})].map(lambda v:-float("inf")<float(v)<float("inf")).all().all():
        raise ValueError("Nonfinite interchange")
    if not d.demand_mw.map(lambda v:0<=float(v)<float("inf")).all():raise ValueError("Invalid demand")
    sums=d.groupby("ba").demand_mw.sum().rename("reported_demand_mwh")
    out=i.join(sums,on="ba",validate="one_to_one")
    if out.reported_demand_mwh.isna().any() or (out.reported_demand_mwh<=0).any():
        raise ValueError("Missing demand energy")
    out["reported_net_import_mwh"]=-out.reported_interchange_mwh
    out["net_import_share_of_demand"]=out.reported_net_import_mwh/out.reported_demand_mwh
    out["absolute_accounting_discrepancy_mwh"]=out.discrepancy_mwh.abs()
    out["accounting_consistent_at_tolerance"]=out.absolute_accounting_discrepancy_mwh<=abs_tolerance_mwh
    out["net_import_direction"]=out.reported_net_import_mwh.map(
        lambda v:"net_import" if v>0 else ("net_export" if v<0 else "zero_net"))
    result=Path(output);result.mkdir(parents=True,exist_ok=True)
    out.sort_values("ba").to_csv(result/"reported_interchange_dependence_2024_02.csv",index=False)
    report={"bas":len(out),"accounting_consistent_bas":int(out.accounting_consistent_at_tolerance.sum()),
            "accounting_flagged_bas":sorted(out.loc[~out.accounting_consistent_at_tolerance,"ba"].tolist()),
            "net_imported_bas":sorted(out.loc[out.reported_net_import_mwh>0,"ba"].tolist()),
            "physical_transfer_capacity_inferred":False,"historical_calibration_certified":False,
            "warning":"EIA-930 reported net exchange and source accounting are NOT verified import capability, bilateral network topology or actual line ratings."}
    (result/"reported_interchange_dependence_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interchange",required=True);p.add_argument("--demand",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.interchange,a.demand,a.output),indent=2))
if __name__=="__main__":main()
