"""Audit EIA-923 generator-month net generation by reported BA/prime mover.

Prime mover is NOT a fuel technology: preserve the raw code and refuse any
implicit gas/coal/nuclear/solar mapping. Negative net MWh are retained.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

KEYS=["plant_id","generator_id","prime_mover","reported_ba","period"]
COLS=KEYS+["generation_mwh"]

def audit(input_csv, output):
    df=pd.read_csv(input_csv,dtype={k:str for k in KEYS},keep_default_na=False)
    if df.empty or not set(COLS).issubset(df):
        raise ValueError("Empty or missing generator-month fields")
    for col in KEYS:
        df[col]=df[col].str.strip()
        if df[col].eq("").any():
            raise ValueError(f"Missing {col}; do not infer missing BA or generator IDs")
    if not df.period.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Period must be YYYY-MM")
    if df.duplicated(KEYS).any():
        raise ValueError("Duplicate generator-month key: avoid double counting")
    df["generation_mwh"]=pd.to_numeric(df.generation_mwh,errors="raise")
    if not df.generation_mwh.map(lambda v:-float("inf")<float(v)<float("inf")).all():
        raise ValueError("Nonfinite or missing net generation")
    df["negative_net_mwh"]=df.generation_mwh.where(df.generation_mwh<0,0)
    df["positive_net_mwh"]=df.generation_mwh.where(df.generation_mwh>0,0)
    grouped=df.groupby(["reported_ba","prime_mover","period"],as_index=False).agg(
        net_generation_mwh=("generation_mwh","sum"),
        positive_net_mwh=("positive_net_mwh","sum"),
        negative_net_mwh=("negative_net_mwh","sum"),
        generator_month_records=("generation_mwh","size"),
        zero_records=("generation_mwh",lambda x:int((x==0).sum())),
        negative_records=("generation_mwh",lambda x:int((x<0).sum())),
        distinct_plants=("plant_id","nunique"))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    grouped.sort_values(["reported_ba","prime_mover","period"]).to_csv(out/"ba_prime_mover_month_audit.csv",index=False)
    manifest={"total_records":len(df),"negative_records":int((df.generation_mwh<0).sum()),
              "zero_records":int((df.generation_mwh==0).sum()),
              "reported_bas":sorted(df.reported_ba.unique().tolist()),
              "prime_mover_codes":sorted(df.prime_mover.unique().tolist()),
              "technology_mapping_certified":False,
              "historical_calibration_certified":False,
              "warning":"Prime mover is not a unique fuel classifier. Missing cells omitted upstream must be reconciled with source inventory; no missing-to-zero imputation."}
    (out/"prime_mover_audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.input,a.output),indent=2))
if __name__=="__main__":
    main()
