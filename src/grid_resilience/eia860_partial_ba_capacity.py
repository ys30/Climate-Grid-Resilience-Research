"""Conservative SRP capacity candidates from exact EIA-860/Page-4 identity joins.

BA assignments are inferred *only* from observed EIA-923 Page-4 reported BA,
not from the complete EIA-860 inventory. Therefore PARTIAL FLEET, not certified.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def build(eia860,page4,ba):
    ids=["plant_id","generator_id"]
    a,b=eia860.copy(),page4.copy()
    need_a=set(ids+["nameplate_capacity_mw","energy_source_1","energy_source_2","multiple_fuels"])
    need_b=set(ids+["reported_ba"])
    if not need_a.issubset(a.columns) or not need_b.issubset(b.columns):
        raise ValueError("Required provenance columns missing")
    for df in (a,b):
        for key in ids:
            df[key]=df[key].astype("string").str.strip()
            if df[key].isna().any() or df[key].eq("").any():raise ValueError("Null/blank generator key")
        df["plant_id"]=df.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
    if a.duplicated(ids).any():raise ValueError("EIA-860 generator IDs duplicate")
    assignments=b[ids+["reported_ba"]].drop_duplicates()
    conflict=assignments.groupby(ids).reported_ba.nunique()
    if (conflict>1).any():raise ValueError("Conflicting reported BA for generator")
    assignments=assignments[assignments.reported_ba.eq(ba)]
    joined=a.merge(assignments,on=ids,how="inner",validate="one_to_one")
    joined["nameplate_capacity_mw"]=pd.to_numeric(joined.nameplate_capacity_mw,errors="coerce")
    sec=joined.energy_source_2.fillna("").astype(str).str.strip().str.upper()
    mf=joined.multiple_fuels.fillna("").astype(str).str.strip().str.upper()
    fuel=joined.energy_source_1.fillna("").astype(str).str.strip().str.upper()
    eligible=(joined.nameplate_capacity_mw.gt(0)&joined.nameplate_capacity_mw.notna()&
              ~mf.isin(["Y","YES","1","TRUE"])&sec.isin(["","NA","NONE","."])&
              ~fuel.isin(["","NA","NONE","."]))
    joined["screening_candidate"]=eligible
    accepted=joined.loc[eligible].copy()
    if accepted.empty:raise ValueError("No eligible candidate capacities")
    capacities=accepted.groupby("energy_source_1",as_index=False).nameplate_capacity_mw.sum()
    capacities["ba"]=ba
    capacities=capacities.rename(columns={"energy_source_1":"technology","nameplate_capacity_mw":"capacity_mw"})
    capacities["marginal_cost"]=50.0 # explicit flat counterfactual cost, NOT EIA cost
    return capacities[["ba","technology","capacity_mw","marginal_cost"]],joined

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia860",required=True);p.add_argument("--page4",required=True)
    p.add_argument("--ba",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    capacities,ledger=build(pd.read_csv(a.eia860,dtype="string"),pd.read_csv(a.page4,dtype="string"),a.ba)
    o=Path(a.output);o.mkdir(parents=True,exist_ok=True)
    capacities.to_csv(o/"partial_ba_capacity_screen.csv",index=False)
    ledger.to_csv(o/"ba_capacity_identity_review.csv",index=False)
    (o/"capacity_screen_manifest.json").write_text(json.dumps({
        "ba":a.ba,"candidate_generator_ids":int(ledger.screening_candidate.sum()),
        "excluded_candidate_ids":int((~ledger.screening_candidate).sum()),
        "capacity_sum_mw":float(capacities.capacity_mw.sum()),
        "complete_ba_fleet":False,"historical_availability_certified":False,
        "capacity_basis":"2024 EIA-860 Operable nameplate joined only to generators in partial EIA-923 Page-4 BA extract",
        "assumptions":"All candidate capacity available every hour; equal invented 50 cost; no grid imports/exports, ramping, or storage dispatch."
    },indent=2)+"\n")
if __name__=="__main__":main()
