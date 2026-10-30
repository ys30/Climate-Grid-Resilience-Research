"""Summarize conservative EIA-923/EIA-860 matched record eligibility.

Keep unresolved, multifuel, and missing-source records outside clean
single-fuel diagnostics; do not silently assign them to model technology.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(eia923, eia860, output):
    keys=["plant_id","generator_id"]
    a=pd.read_csv(eia923,dtype={k:str for k in keys},keep_default_na=False)
    b=pd.read_csv(eia860,dtype={k:str for k in keys},keep_default_na=False)
    required={"energy_source_1","energy_source_2","multiple_fuels","prime_mover"}
    if not set(keys+["reported_ba","period","generation_mwh"]).issubset(a) or not required.issubset(b):
        raise ValueError("Input schema mismatch")
    for f in (a,b):
        for k in keys: f[k]=f[k].astype(str).str.strip()
    if a.duplicated(keys+["period"]).any() or b.duplicated(keys).any():
        raise ValueError("Ambiguous generator keys")
    joined=a.merge(b,on=keys,how="left",validate="many_to_one",indicator=True,suffixes=("_923","_860"))
    def tidy(s): return s.fillna("").astype(str).str.strip().str.upper()
    matched=joined["_merge"].eq("both")
    fuel=tidy(joined.energy_source_1)
    fuel2=tidy(joined.energy_source_2)
    multifuel=tidy(joined.multiple_fuels).eq("Y") | fuel2.ne("")
    storage=joined.get("reported_technology",pd.Series("",index=joined.index)).fillna("").astype(str).str.contains("Storage|Battery|Pumped",case=False,regex=True)
    missing=fuel.eq("") | fuel.eq("NAN")
    supported={"NG","BIT","SUB","LIG","RC","NUC","WAT","SUN","WND","GEO","DFO","RFO","JF"}
    unsupported=~fuel.isin(supported)
    conflict=tidy(joined.prime_mover_923).ne(tidy(joined.prime_mover_860))
    joined["eligibility"]="clean_single_fuel_candidate"
    joined.loc[~matched,"eligibility"]="unmatched"
    joined.loc[matched & missing,"eligibility"]="missing_fuel"
    joined.loc[matched & unsupported & ~missing,"eligibility"]="unsupported_fuel_requires_review"
    joined.loc[matched & multifuel,"eligibility"]="multifuel_requires_review"
    joined.loc[matched & storage,"eligibility"]="storage_separate_accounting"
    joined.loc[matched & conflict,"eligibility"]="prime_mover_conflict"
    grouped=joined.groupby(["reported_ba","eligibility"],as_index=False).size().rename(columns={"size":"generator_month_records"})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    grouped.to_csv(out/"classification_eligibility_by_ba.csv",index=False)
    manifest={"generator_month_records":len(joined),
              "eligibility_counts":{str(k):int(v) for k,v in joined.eligibility.value_counts().items()},
              "single_fuel_candidate_is_calibrated":False,
              "warning":"Candidate status is not independently validated technology, BA or capacity mapping. Multi-fuel and storage require separate treatment."}
    (out/"classification_eligibility_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923",required=True);p.add_argument("--eia860",required=True)
    p.add_argument("--output",required=True);x=p.parse_args()
    print(json.dumps(audit(x.eia923,x.eia860,x.output),indent=2))
if __name__=="__main__": main()
