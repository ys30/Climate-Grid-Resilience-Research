"""Join observed EIA-930 category candidates to partial EIA-860 capacity.

This is a key-coverage audit, not a physical fleet mapping or calibration.
"""
import argparse,json
from pathlib import Path
import pandas as pd
KEYS=["ba","technology"]
def audit(capacity_csv,candidates_csv,output):
    cap=pd.read_csv(capacity_csv,dtype={"ba":str,"technology":str})
    cand=pd.read_csv(candidates_csv,dtype={"ba":str,"pypsa_technology":str})
    required_cap=set(KEYS+["nameplate_capacity_mw"])
    required_cand={"ba","pypsa_technology","mapping_status"}
    if not required_cap.issubset(cap) or not required_cand.issubset(cand):
        raise ValueError("Missing candidate/capacity schema")
    cand=cand.rename(columns={"pypsa_technology":"technology"})
    if cap.duplicated(KEYS).any() or cand.duplicated(KEYS).any():
        raise ValueError("Duplicate BA technology capacity or observation keys")
    if not cand.mapping_status.eq("direct_category_candidate").all():
        raise ValueError("Non-direct EIA-930 observation candidate")
    cap["nameplate_capacity_mw"]=pd.to_numeric(cap.nameplate_capacity_mw,errors="raise")
    if not cap.nameplate_capacity_mw.map(lambda v:0<float(v)<float("inf")).all():
        raise ValueError("Invalid capacity")
    merged=cand.merge(cap,on=KEYS,how="outer",indicator=True,validate="one_to_one")
    merged["key_status"]=merged["_merge"].map({"both":"key_matched","left_only":"observed_only","right_only":"capacity_only"}).astype(str)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    merged.drop(columns="_merge").sort_values(KEYS).to_csv(out/"eia930_eia860_capacity_key_audit.csv",index=False)
    counts={status:int((merged.key_status==status).sum()) for status in ("key_matched","observed_only","capacity_only")}
    result={"counts":counts,"capacity_subset_only":True,"source_fleet_equivalence_certified":False,
            "hourly_available_capacity_certified":False,"historical_calibration_certified":False,
            "warning":"Matching BA and technology labels does NOT validate the same plant fleet, generator net output basis, or hourly availability."}
    (out/"eia930_eia860_capacity_key_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capacity",required=True);p.add_argument("--candidates",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.capacity,a.candidates,a.output),indent=2))
if __name__=="__main__":main()
