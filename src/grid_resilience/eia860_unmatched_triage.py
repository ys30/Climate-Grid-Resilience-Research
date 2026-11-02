"""Triage 2024 EIA-923 unmatched generator IDs against 2024 EIA-860 Operable only.

A missing operable key cannot establish retirement, renaming, or data error.
No fuzzy matching or automatic ID substitution is performed.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def normalize_id(values):
    return values.astype("string").str.strip().str.replace(r"^0+(?=[0-9])", "", regex=True)

def triage(unmatched, operable):
    required_u={"plant_id","generator_id","reported_ba","period"}
    required_o={"plant_id","generator_id"}
    for label,df,needed in (("unmatched",unmatched,required_u),("operable",operable,required_o)):
        if not needed.issubset(df.columns):
            raise ValueError(f"{label} missing {sorted(needed-set(df.columns))}")
        if df.empty or df[list(needed)].isna().any().any():
            raise ValueError(f"{label} empty or missing identifiers")
    u=unmatched.copy()
    o=operable.copy()
    for df in (u,o):
        df["plant_id"]=normalize_id(df.plant_id)
        df["generator_id"]=df.generator_id.astype("string").str.strip()
        if df[["plant_id","generator_id"]].eq("").any().any():
            raise ValueError("blank plant or generator ID")
    if o.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("duplicate operable inventory ID")
    grouped=(u.groupby(["reported_ba","plant_id","generator_id"],dropna=False)
               .agg(unmatched_month_rows=("period","size"),
                    distinct_months=("period","nunique")).reset_index())
    operable_keys=set(map(tuple,o[["plant_id","generator_id"]].itertuples(index=False,name=None)))
    by_plant=o.groupby("plant_id").generator_id.apply(lambda v: sorted(set(v.astype(str)))).to_dict()
    grouped["exact_key_in_operable"]=grouped.apply(lambda row:(row.plant_id,row.generator_id) in operable_keys,axis=1)
    grouped["other_2024_operable_ids_same_plant"]=grouped.plant_id.map(lambda plant:";".join(by_plant.get(plant,[])))
    grouped["review_status"]=grouped.apply(
        lambda row:"unexpected_exact_operable_key" if row.exact_key_in_operable
        else ("other_generator_at_same_plant" if row.other_2024_operable_ids_same_plant
              else "plant_absent_from_selected_operable_inventory"),axis=1)
    grouped["identity_crosswalk_certified"]=False
    return grouped.sort_values(["reported_ba","plant_id","generator_id"]).reset_index(drop=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--unmatched",required=True)
    p.add_argument("--operable",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=triage(pd.read_csv(args.unmatched,dtype="string"),
                  pd.read_csv(args.operable,dtype="string"))
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(out,index=False)
    print(json.dumps({"distinct_unmatched_keys":len(result),
       "generator_month_rows":int(result.unmatched_month_rows.sum()),
       "reason_counts":result.review_status.value_counts().to_dict(),
       "historical_crosswalk_certified":False},indent=2))

if __name__=="__main__":
    main()
