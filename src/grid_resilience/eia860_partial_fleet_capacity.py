"""Estimate a strictly partial-fleet EIA-860 nameplate capacity inventory.

Selection uses exact generator IDs observed in EIA-923. This is an inventory
diagnostic, NOT complete installed BA capacity, a time-specific capacity
snapshot, or certified availability.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia860_generator_join import FUEL_TO_TECH

def build(eia923,eia860,output):
    keys=["plant_id","generator_id"]
    a=pd.read_csv(eia923,dtype={k:str for k in keys},keep_default_na=False)
    b=pd.read_csv(eia860,dtype={k:str for k in keys},keep_default_na=False)
    needed_a=set(keys+["reported_ba","prime_mover"])
    needed_b=set(keys+["nameplate_capacity_mw","energy_source_1","energy_source_2",
                       "multiple_fuels","reported_technology","prime_mover"])
    if not needed_a.issubset(a) or not needed_b.issubset(b):
        raise ValueError("Missing observed generator IDs or 2024 EIA-860 nameplate inventory")
    for frame in (a,b):
        for key in keys:frame[key]=frame[key].str.strip()
    if b.duplicated(keys).any():raise ValueError("Duplicate EIA-860 generator keys")
    # One EIA-923 generator can occur in all 12 months. Do not sum capacity 12x.
    ba_by_id=a[keys+["reported_ba","prime_mover"]].drop_duplicates()
    if ba_by_id.duplicated(keys).any():
        raise ValueError("Inconsistent BA or prime mover across 2024 monthly records")
    j=ba_by_id.merge(b,on=keys,how="left",validate="one_to_one",indicator=True,suffixes=("_923","_860"))
    def clean(col):return j[col].fillna("").astype(str).str.strip().str.upper()
    primary=clean("energy_source_1")
    second=clean("energy_source_2")
    multi=clean("multiple_fuels").eq("Y")|second.ne("")
    storage=clean("reported_technology").str.contains("STORAGE|BATTERY|PUMPED",regex=True)
    pm=clean("prime_mover_923").eq(clean("prime_mover_860"))
    capacity=pd.to_numeric(j["nameplate_capacity_mw"],errors="coerce")
    eligible=j["_merge"].eq("both")&~multi&~storage&pm&primary.isin(FUEL_TO_TECH)&capacity.notna()&(capacity>0)
    j["technology"]=primary.map(FUEL_TO_TECH)
    selected=j.loc[eligible].copy()
    selected["nameplate_capacity_mw"]=capacity.loc[eligible]
    grouped=(selected.groupby(["reported_ba","technology"],as_index=False)
             .agg(nameplate_capacity_mw=("nameplate_capacity_mw","sum"),
                  matched_generators=("generator_id","size"))
             .rename(columns={"reported_ba":"ba"}))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    grouped.to_csv(out/"partial_fleet_eia860_nameplate_capacity.csv",index=False)
    result={"observed_generator_ids":len(j),"eligible_generator_ids":int(eligible.sum()),
            "excluded_generator_ids":int((~eligible).sum()),
            "partial_fleet_capacity_mw":float(grouped.nameplate_capacity_mw.sum()),
            "historical_calibration_certified":False,
            "full_ba_capacity_certified":False,
            "limitations":"EIA-923-listed generators only; EIA-860 2024 Operable inventory; monthly operational status, full BA fleet, deratings and net/gross conversions not certified."}
    (out/"partial_fleet_eia860_capacity_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923",required=True);p.add_argument("--eia860",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(build(a.eia923,a.eia860,a.output),indent=2))
if __name__=="__main__":main()
