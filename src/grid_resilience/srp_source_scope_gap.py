"""Quantify exact source-scope mismatch between Page-4 observations and screened model fleet.

No zeros inferred for missing resources. Only generator identities appearing in
the EIA-923 Page-4 source are eligible for identity matching.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(page4, inventory, screen, ba="SRP", month="2024-01"):
    keys=["plant_id","generator_id"]
    p=page4.copy();e=inventory.copy();s=screen.copy()
    for d in (p,e,s):
        for k in keys:
            if k in d:
                d[k]=d[k].astype("string").str.strip()
                if k=="plant_id":d[k]=d[k].str.replace(r"^0+(?=[0-9])","",regex=True)
    required={"reported_ba","period","generation_mwh",*keys}
    if not required.issubset(p.columns):raise ValueError("Missing Page4 columns")
    if not {*keys,"energy_source_1"}.issubset(e.columns):raise ValueError("Missing inventory columns")
    if not {"ba","technology","capacity_mw"}.issubset(s.columns):raise ValueError("Missing screen columns")
    if e.duplicated(keys).any():raise ValueError("Duplicate inventory keys")
    p=p[p.reported_ba.eq(ba)&p.period.eq(month)].copy()
    if p.empty:raise ValueError("No source observations")
    if p.duplicated(keys).any():raise ValueError("Duplicate monthly generator observations")
    p["generation_mwh"]=pd.to_numeric(p.generation_mwh,errors="raise")
    j=p.merge(e[keys+["energy_source_1"]],on=keys,how="left",validate="one_to_one",indicator=True)
    selected=set(s[s.ba.eq(ba)].technology.astype(str))
    j["source_scope_status"]="matched_inventory_excluded_from_model"
    j.loc[j["_merge"].ne("both"),"source_scope_status"]="outside_operable_inventory"
    j.loc[j["_merge"].eq("both")&j.energy_source_1.astype(str).isin(selected),"source_scope_status"]="fuel_present_in_model"
    # 'fuel_present' means only technology overlap; generator-level completeness is not certified
    stats=j.groupby("source_scope_status",dropna=False).agg(
        source_generator_rows=("generator_id","size"),observed_net_mwh=("generation_mwh","sum")).reset_index()
    known=set(j.energy_source_1.dropna().astype(str))
    missing_fuels=sorted(known-selected)
    manifest={"ba":ba,"month":month,"source_page4_rows":len(j),
        "page4_total_observed_mwh":float(j.generation_mwh.sum()),
        "modeled_fuel_codes":sorted(selected),"observed_fuel_codes_not_modeled":missing_fuels,
        "page1_hydro_pumped_storage_included":False,
        "model_and_observed_reporting_grain_reconciled":False,
        "calibration_certified":False,
        "critical_note":"Fuel-code overlap is NOT proof of complete matching generator inventory; missing source values not zero."}
    return j.drop(columns=["_merge"]),stats,manifest

def main():
    a=argparse.ArgumentParser()
    for key in ("page4","inventory","screen","output"):a.add_argument("--"+key,required=True)
    a.add_argument("--ba",default="SRP");a.add_argument("--month",default="2024-01")
    t=a.parse_args()
    j,s,m=audit(pd.read_csv(t.page4,dtype={"plant_id":"string","generator_id":"string"}),
                pd.read_csv(t.inventory,dtype={"plant_id":"string","generator_id":"string"}),
                pd.read_csv(t.screen),t.ba,t.month)
    o=Path(t.output);o.mkdir(parents=True,exist_ok=True)
    j.to_csv(o/"page4_month_scope_rows.csv",index=False)
    s.to_csv(o/"page4_month_scope_summary.csv",index=False)
    (o/"page4_month_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print(json.dumps({"summary":s.to_dict(orient="records"),"manifest":m},indent=2))
if __name__=="__main__":main()
