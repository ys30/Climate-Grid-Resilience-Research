"""Select only complete BA-technology calendar years for diagnostic comparison.

Never interpret a complete time index as full generator fleet coverage.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def select(matrix_csv, output, year=2024):
    d=pd.read_csv(matrix_csv,dtype={"ba":str,"technology":str,"period":str})
    fields={"ba","technology","period","generation_mwh","record_present"}
    if d.empty or not fields.issubset(d): raise ValueError("Invalid coverage matrix")
    if d.duplicated(["ba","technology","period"]).any(): raise ValueError("Duplicate coverage keys")
    expected={f"{year}-{m:02d}" for m in range(1,13)}
    selected=[]
    rejected=[]
    for (ba,tech),part in d.groupby(["ba","technology"]):
        if set(part.period)==expected and part.record_present.astype(str).str.lower().eq("true").all() and part.generation_mwh.notna().all():
            selected.append(part)
        else:
            rejected.append({"ba":ba,"technology":tech,
                             "months_present":int(part.record_present.astype(str).str.lower().eq("true").sum())})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    if selected:
        pd.concat(selected)[["ba","technology","period","generation_mwh"]].sort_values(
            ["ba","technology","period"]).to_csv(out/"complete_year_candidate_diagnostics.csv",index=False)
    else:
        pd.DataFrame(columns=["ba","technology","period","generation_mwh"]).to_csv(
            out/"complete_year_candidate_diagnostics.csv",index=False)
    result={"year":year,"complete_groups":len(selected),"excluded_groups":rejected,
            "historical_calibration_certified":False,
            "warning":"Twelve observed months do not imply complete BA plant coverage or validation."}
    (out/"complete_year_gate_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--matrix",required=True);p.add_argument("--output",required=True)
    p.add_argument("--year",type=int,default=2024)
    a=p.parse_args()
    print(json.dumps(select(a.matrix,a.output,a.year),indent=2))
if __name__=="__main__":main()
