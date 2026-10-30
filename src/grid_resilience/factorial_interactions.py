"""Factorial climate-interaction analysis; never infer interactions from only 3 scenarios.

Inputs are matched PyPSA per-event/BA results, not raw historical reliability observations.
"""
import argparse
from pathlib import Path
import pandas as pd

SCENARIOS={"baseline","heat_only","wind_only","heat_wind"}
KEYS=["event_id","ba","network_variant"]
METRICS=["unserved_energy_mwh","shortage_hours","peak_shortfall_mw"]

def decompose(frame):
    missing=set(KEYS+["scenario"]+METRICS)-set(frame.columns)
    if missing:raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame[KEYS+["scenario"]].isna().any().any():raise ValueError("Missing identifiers")
    if frame.duplicated(KEYS+["scenario"]).any():raise ValueError("Duplicate matched scenario")
    for metric in METRICS:
        frame[metric]=pd.to_numeric(frame[metric],errors="raise")
        if frame[metric].isna().any() or (frame[metric]<0).any():
            raise ValueError(f"Invalid {metric}")
    groups=frame.groupby(KEYS,dropna=False)
    rows=[]
    for key,group in groups:
        actual=set(group.scenario)
        if actual!=SCENARIOS or len(group)!=4:
            raise ValueError(f"{key}: complete factorial required, got {sorted(actual)}")
        d=group.set_index("scenario")
        row=dict(zip(KEYS,key))
        for metric in METRICS:
            b,h,w,c=(float(d.loc[s,metric]) for s in ("baseline","heat_only","wind_only","heat_wind"))
            row[metric+"_baseline"]=b
            row[metric+"_heat_effect"]=h-b
            row[metric+"_wind_effect"]=w-b
            row[metric+"_compound_effect"]=c-b
            row[metric+"_nonadditive_interaction"]=c-h-w+b
        rows.append(row)
    if not rows:raise ValueError("No events")
    return pd.DataFrame(rows).sort_values(KEYS).reset_index(drop=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=decompose(pd.read_csv(a.input))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(out,index=False)
    print(result.to_string(index=False))

if __name__=="__main__":main()
