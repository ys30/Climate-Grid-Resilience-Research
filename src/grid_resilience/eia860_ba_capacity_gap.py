"""Flag the BA attribution gap before using the complete EIA-860 fleet.

The generator workbook does not contain an independently verified BA mapping.
An EIA-923 matched subset is NOT the complete BA capacity inventory.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def assess(inventory_csv,partial_capacity_csv,key_audit_csv,output):
    inv=pd.read_csv(inventory_csv,dtype={"plant_id":str,"generator_id":str},keep_default_na=False)
    partial=pd.read_csv(partial_capacity_csv)
    keys=pd.read_csv(key_audit_csv)
    for c in ("plant_id","generator_id","nameplate_capacity_mw"):
        if c not in inv:raise ValueError("Missing full inventory field "+c)
    if inv.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate full inventory ID")
    full=pd.to_numeric(inv.nameplate_capacity_mw,errors="coerce")
    known=full.notna() & (full>0)
    if known.sum()==0:raise ValueError("No positive capacity in official fleet")
    if "nameplate_capacity_mw" not in partial or "key_status" not in keys:raise ValueError("Missing earlier audits")
    m={"full_operable_inventory_generators":len(inv),
       "full_operable_generators_with_positive_nameplate":int(known.sum()),
       "national_full_inventory_positive_nameplate_mw":float(full[known].sum()),
       "partial_eia923_linked_capacity_mw":float(pd.to_numeric(partial.nameplate_capacity_mw).sum()),
       "observed_only_ba_technology_groups":int(keys.key_status.eq("observed_only").sum()),
       "national_capacity_is_not_four_ba_capacity":True,
       "verified_full_plant_to_ba_crosswalk":False,
       "historical_calibration_certified":False,
       "next_requirement":"Obtain independent plant-level EIA-860 BA attribution and generator status dates before building complete BA capacities."}
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"eia860_ba_capacity_gap_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    return m
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inventory",required=True);p.add_argument("--partial",required=True)
    p.add_argument("--keys",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(assess(a.inventory,a.partial,a.keys,a.output),indent=2))
if __name__=="__main__":main()
