"""Cross-check observed monthly technology coverage against requested model keys.

An absent observed group is NEVER silently assigned zero; a missing model
technology is also treated as a comparison gap, not an implicit zero.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit(observed_csv, modeled_csv, output):
    keys=["ba","technology","period"]
    a=pd.read_csv(observed_csv,dtype={k:str for k in keys})
    b=pd.read_csv(modeled_csv,dtype={k:str for k in keys})
    if a.empty or b.empty or not set(keys+["generation_mwh"]).issubset(a) or not set(keys+["generation_mwh"]).issubset(b):
        raise ValueError("Missing comparison inputs or columns")
    if a.duplicated(keys).any() or b.duplicated(keys).any():
        raise ValueError("Duplicate BA/technology/month comparison keys")
    for df in (a,b):
        if df[keys].isna().any().any():
            raise ValueError("Null comparison key")
        df["generation_mwh"]=pd.to_numeric(df.generation_mwh,errors="raise")
        if not df.generation_mwh.map(lambda v:-float("inf")<float(v)<float("inf")).all():
            raise ValueError("Missing/nonfinite generation")
    merged=b.merge(a,on=keys,how="outer",indicator=True,validate="one_to_one",
                   suffixes=("_modeled","_observed"))
    labels={"both":"matched","left_only":"modeled_only","right_only":"observed_only"}
    merged["comparison_status"]=merged["_merge"].astype(str).map(labels)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    merged.drop(columns=["_merge"]).sort_values(keys).to_csv(out/"comparison_key_coverage.csv",index=False)
    counts={k:int((merged.comparison_status==k).sum()) for k in labels.values()}
    manifest={"status_counts":counts,"comparison_complete":counts["modeled_only"]==0 and counts["observed_only"]==0,
              "historical_calibration_certified":False,
              "warning":"Matched keys do not establish full-fleet comparability. Missing EIA coal is not zero generation."}
    (out/"comparison_key_coverage_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--observed",required=True);p.add_argument("--modeled",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.observed,a.modeled,a.output),indent=2))
if __name__=="__main__":main()
