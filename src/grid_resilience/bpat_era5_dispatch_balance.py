"""Audit hourly BPAT wind-to-shortfall changes under matched assumptions.

Only valid for the isolated BA scenario without storage/transfers; replacement
generation and curtailment mean wind energy delta need not equal shortage delta.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def run(root,output):
    root=Path(root);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    frames={}
    for case,sub in [("era5","era5_wind_dispatch"),("replay","observed_wind_dispatch")]:
        gen=pd.read_csv(root/sub/"generation_hourly.csv")
        gen=gen[gen.ba.eq("BPAT")].copy()
        gen.timestamp=pd.to_datetime(gen.timestamp,utc=True)
        if gen.duplicated(["timestamp","technology"]).any():raise ValueError("Duplicated generation")
        pivot=gen.pivot(index="timestamp",columns="technology",values="generation_mwh")
        if len(pivot)!=696 or pivot.isna().any().any():raise ValueError("Incomplete generation")
        frames[case]=pivot
    if not frames["era5"].columns.equals(frames["replay"].columns):
        raise ValueError("Different modeled BPAT technologies")
    diff=frames["era5"].subtract(frames["replay"])
    long=diff.stack().rename("era5_minus_replay_generation_mwh").reset_index()
    long.to_csv(out/"bpat_era5_minus_replay_generation_by_hour_technology.csv",index=False)
    totals=long.groupby("technology",as_index=False).era5_minus_replay_generation_mwh.sum()
    totals.to_csv(out/"bpat_era5_minus_replay_technology_totals.csv",index=False)
    short=pd.read_csv(root/"bpat_era5_pypsa_conditional_shortfall.csv")
    observed=float(short.loc[short.ba.eq("BPAT"),"era5_minus_observed_replay_shortfall_mwh"].iloc[0])
    gen_total=float(totals.era5_minus_replay_generation_mwh.sum())
    # Isolated BA dispatch with no storage and no interties; both scenarios meet
    # identical demand using generation and a penalty shortfall generator.
    if abs(gen_total+observed)>1.0:
        raise AssertionError(f"BPAT monthly power balance mismatch: {gen_total}+{observed}")
    summary={"hours":696,"era5_minus_replay_generation_total_mwh":gen_total,
             "era5_minus_replay_shortfall_mwh":observed,
             "absolute_balance_residual_mwh":abs(gen_total+observed),
             "storage_or_interties_included":False,"historical_adequacy_calibrated":False}
    (out/"bpat_era5_replay_generation_balance_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(run(a.root,a.output),indent=2))
if __name__=="__main__":main()
