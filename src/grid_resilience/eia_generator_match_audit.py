"""Audit exact EIA-923 to EIA-860 generator matches without dropping unmatched rows."""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(eia923, eia860, output):
    keys=["plant_id","generator_id"]
    a=pd.read_csv(eia923,dtype={k:str for k in keys},keep_default_na=False)
    b=pd.read_csv(eia860,dtype={k:str for k in keys},keep_default_na=False)
    needed_a=set(keys+["reported_ba","period","generation_mwh"])
    needed_b=set(keys+["energy_source_1","energy_source_2","multiple_fuels","prime_mover"])
    if a.empty or b.empty or not needed_a.issubset(a) or not needed_b.issubset(b):
        raise ValueError("Empty or incomplete generator inventory")
    for frame in (a,b):
        for k in keys:
            frame[k]=frame[k].str.strip()
            if frame[k].eq("").any(): raise ValueError("Blank generator identity")
    if b.duplicated(keys).any(): raise ValueError("Ambiguous EIA-860 identifiers")
    if a.duplicated(keys+["period"]).any(): raise ValueError("Duplicate EIA-923 generator-month")
    joined=a.merge(b,on=keys,how="left",indicator=True,validate="many_to_one",suffixes=("_923","_860"))
    matched=joined["_merge"].eq("both")
    multi=joined["multiple_fuels"].fillna("").astype(str).str.strip().eq("Y")
    second=joined["energy_source_2"].fillna("").astype(str).str.strip().ne("")
    grouped=joined.groupby("reported_ba",dropna=False).agg(
        generator_month_records=("period","size"),
        unique_generators=("generator_id","nunique"),
        matched_generator_month_records=("_merge",lambda s:int(s.eq("both").sum())),
        unmatched_generator_month_records=("_merge",lambda s:int(s.ne("both").sum())),
    ).reset_index()
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    grouped.to_csv(output/"generator_join_coverage_by_ba.csv",index=False)
    joined.loc[~matched,keys+["reported_ba","period"]].to_csv(output/"unmatched_generator_months.csv",index=False)
    result={"generator_month_records":len(joined),
            "matched_generator_month_records":int(matched.sum()),
            "unmatched_generator_month_records":int((~matched).sum()),
            "match_rate_records":round(float(matched.mean()),6),
            "matched_multifuel_flag_records":int((matched & multi).sum()),
            "matched_secondary_energy_source_records":int((matched & second).sum()),
            "historical_calibration_certified":False,
            "warning":"Generator match rate does not establish fleet/BA coverage, fuel-specific dispatch, or historical calibration."}
    (output/"generator_join_coverage_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923",required=True);p.add_argument("--eia860",required=True)
    p.add_argument("--output",required=True)
    x=p.parse_args()
    print(json.dumps(audit(x.eia923,x.eia860,x.output),indent=2))
if __name__=="__main__":main()
