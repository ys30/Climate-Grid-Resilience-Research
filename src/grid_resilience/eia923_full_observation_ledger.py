"""Audit full extracted EIA-923 Page-4 ledger against EIA-860 operable keys.

A join to Operable is an identity-screen, not full BA-fleet or calibration certification.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def build(page4,operable):
    req={"plant_id","generator_id","reported_ba","period","generation_mwh"}
    if not req.issubset(page4): raise ValueError("Missing Page-4 columns")
    if not {"plant_id","generator_id"}.issubset(operable): raise ValueError("Missing EIA-860 IDs")
    a,b=page4.copy(),operable.copy()
    for d in (a,b):
        for k in ("plant_id","generator_id"):
            d[k]=d[k].astype("string").str.strip()
            if d[k].isna().any() or d[k].eq("").any(): raise ValueError("Invalid identity")
        d["plant_id"]=d.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if a.duplicated(["plant_id","generator_id","reported_ba","period"]).any():
        raise ValueError("Duplicate reported generator month")
    if b.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate operable key")
    a["generation_mwh"]=pd.to_numeric(a.generation_mwh,errors="raise")
    if not a.generation_mwh.map(lambda v:float("-inf")<float(v)<float("inf")).all():
        raise ValueError("Missing/nonfinite MWh")
    matched=a.merge(b[["plant_id","generator_id"]].assign(in_operable=True),
                   how="left",on=["plant_id","generator_id"],validate="many_to_one")
    matched["identity_status"]=matched.in_operable.fillna(False).map(
        {True:"in_2024_operable_identity_list",False:"outside_2024_operable_identity_list"})
    matched["historical_capacity_certified"]=False
    return matched.drop(columns=["in_operable"])

def main():
    p=argparse.ArgumentParser()
    for k in ("page4","operable","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    r=build(pd.read_csv(a.page4,dtype={"plant_id":"string","generator_id":"string"}),
            pd.read_csv(a.operable,dtype={"plant_id":"string","generator_id":"string"}))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    r.to_csv(out/"eia923_page4_full_observation_ledger.csv",index=False)
    summary=r.groupby(["reported_ba","identity_status"],dropna=False).agg(
        generator_month_rows=("generation_mwh","size"),
        net_generation_mwh=("generation_mwh","sum"),
        distinct_plant_ids=("plant_id","nunique")).reset_index()
    summary.to_csv(out/"eia923_page4_coverage_summary.csv",index=False)
    print(json.dumps({"total_generator_month_rows":len(r),
        "reported_total_mwh":float(r.generation_mwh.sum()),
        "identity_status_counts":r.identity_status.value_counts().to_dict(),
        "historical_calibration_certified":False},indent=2))
if __name__=="__main__": main()
