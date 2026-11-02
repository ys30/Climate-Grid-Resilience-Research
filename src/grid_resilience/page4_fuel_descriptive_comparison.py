"""Descriptive Page4 versus scenario fuel table; NEVER historical calibration."""
import argparse,json
from pathlib import Path
import pandas as pd

def compare(page4, review, model, ba="SRP", month="2024-01"):
    keys=["plant_id","generator_id"]
    a=page4.copy();r=review.copy();m=model.copy()
    for d in (a,r):
        for k in keys:
            d[k]=d[k].astype("string").str.strip()
            if d[k].isna().any() or d[k].eq("").any():raise ValueError("Invalid generator key")
        d["plant_id"]=d.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if r.duplicated(keys).any():raise ValueError("Duplicate review ID")
    a=a[a.reported_ba.eq(ba)&a.period.eq(month)].copy()
    if a.empty or a.duplicated(keys).any():raise ValueError("Bad Page4 monthly records")
    a["generation_mwh"]=pd.to_numeric(a.generation_mwh,errors="raise")
    if a.generation_mwh.isna().any():raise ValueError("Missing Page4 MWh")
    r["screening_candidate"]=r.screening_candidate.astype(str).str.lower().map({"true":True,"false":False})
    if r.screening_candidate.isna().any():raise ValueError("Invalid eligibility flag")
    j=a.merge(r[keys+["screening_candidate","energy_source_1"]],on=keys,how="left",validate="one_to_one",suffixes=("","_inventory"))
    j["source_status"]="excluded_or_unmatched"
    j.loc[j.screening_candidate.eq(True),"source_status"]="exact_candidate"
    fuel="energy_source_1_inventory" if "energy_source_1_inventory" in j else "energy_source_1"
    if fuel not in j:raise ValueError("Missing source fuel")
    j["fuel"]=j[fuel].astype("string").str.strip().str.upper()
    selected=j.source_status.eq("exact_candidate")
    if j.loc[selected,"fuel"].isna().any() or j.loc[selected,"fuel"].eq("").any():
        raise ValueError("Missing fuel for selected exact generator")
    observed=j[j.source_status.eq("exact_candidate")].groupby("fuel",as_index=False).agg(page4_matched_net_mwh=("generation_mwh","sum"),matched_rows=("generator_id","size"))
    m=m[m.ba.eq(ba)].copy()
    if m.empty or m.duplicated(["ba","technology"]).any():raise ValueError("Bad model fuel summary")
    m["modeled_generation_mwh"]=pd.to_numeric(m.modeled_generation_mwh,errors="raise")
    result=m.merge(observed,left_on="technology",right_on="fuel",how="outer",validate="one_to_one")
    result["calibration_comparable"]=False
    meta={"ba":ba,"month":month,"page4_observed_total_mwh":float(a.generation_mwh.sum()),
        "matched_page4_net_mwh":float(j.loc[j.source_status.eq("exact_candidate"),"generation_mwh"].sum()),
        "model_partial_fleet_total_mwh":float(m.modeled_generation_mwh.sum()),
        "calibration_certified":False,
        "reason":"Source selected Page4 generator net MWh is not EIA930 BA generation and screening scenario uses hypothetical availability/costs and exogenous export."}
    return result,meta

def main():
    p=argparse.ArgumentParser()
    for k in ("page4","review","model","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    table,meta=compare(pd.read_csv(a.page4,dtype={"plant_id":"string","generator_id":"string"}),
                       pd.read_csv(a.review,dtype={"plant_id":"string","generator_id":"string"}),
                       pd.read_csv(a.model))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"fuel_descriptive_noncali_comparison.csv",index=False)
    (out/"fuel_descriptive_noncali_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(table.to_string(index=False));print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
