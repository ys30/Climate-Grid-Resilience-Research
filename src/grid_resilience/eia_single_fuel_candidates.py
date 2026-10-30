"""Create conservative BA/technology/month observational diagnostic candidate totals.

Only single-fuel, non-storage, exact-ID-matched generators with compatible
prime mover and reviewed EIA-860 primary source codes are included. Exclusions
remain visible. This is NOT a full-fleet or historical calibration result.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .eia_classification_eligibility import audit as audit_eligibility
from .eia860_generator_join import FUEL_TO_TECH

def build(eia923, eia860, output):
    out=Path(output)
    audit_eligibility(eia923,eia860,out/"eligibility")
    keys=["plant_id","generator_id"]
    a=pd.read_csv(eia923,dtype={k:str for k in keys},keep_default_na=False)
    b=pd.read_csv(eia860,dtype={k:str for k in keys},keep_default_na=False)
    for frame in (a,b):
        for k in keys: frame[k]=frame[k].astype(str).str.strip()
    if a.duplicated(keys+["period"]).any() or b.duplicated(keys).any():
        raise ValueError("Duplicate generator join keys")
    j=a.merge(b,on=keys,how="left",validate="many_to_one",
              indicator=True,suffixes=("_923","_860"))
    def clean(c): return j[c].fillna("").astype(str).str.strip().str.upper()
    fuel=clean("energy_source_1")
    second=clean("energy_source_2")
    multi=clean("multiple_fuels").eq("Y") | second.ne("")
    technology=j.get("reported_technology",pd.Series("",index=j.index)).fillna("").astype(str)
    storage=technology.str.contains("Storage|Battery|Pumped",case=False,regex=True)
    pm_match=clean("prime_mover_923").eq(clean("prime_mover_860"))
    eligible=(j["_merge"].eq("both") & ~multi & ~storage & pm_match &
              fuel.isin(FUEL_TO_TECH))
    j["technology"]=fuel.map(FUEL_TO_TECH)
    j["generation_mwh"]=pd.to_numeric(j.generation_mwh,errors="raise")
    if not j.generation_mwh.map(lambda x:-float("inf")<float(x)<float("inf")).all():
        raise ValueError("Nonfinite generation")
    if not eligible.any():
        raise ValueError("No clean single-fuel candidate records")
    totals=(j.loc[eligible].groupby(["reported_ba","technology","period"],as_index=False)
            .generation_mwh.sum().rename(columns={"reported_ba":"ba"}))
    out.mkdir(parents=True,exist_ok=True)
    totals.to_csv(out/"observed_single_fuel_candidate_ba_technology_month.csv",index=False)
    manifest={"all_generator_month_records":len(j),
              "included_candidate_records":int(eligible.sum()),
              "excluded_records":int((~eligible).sum()),
              "included_net_mwh":float(j.loc[eligible,"generation_mwh"].sum()),
              "historical_calibration_certified":False,
              "warning":"Partial-fleet candidate totals omit unresolved/multifuel/storage and must never be used as complete BA output or adequacy calibration."}
    (out/"single_fuel_candidate_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923",required=True)
    p.add_argument("--eia860",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(build(a.eia923,a.eia860,a.output),indent=2))
if __name__=="__main__": main()
