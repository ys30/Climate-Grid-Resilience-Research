"""Reconcile Page 1 PS observations into BA-month coverage (not hourly calibration)."""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
PERIODS=tuple(f"2024-{m:02d}" for m in range(1,13))
REQUIRED={"plant_id","reported_ba","prime_mover","period","net_generation_mwh"}

def reconcile(input_csv, output):
    df=pd.read_csv(input_csv,dtype={"plant_id":str,"reported_ba":str,"prime_mover":str,"period":str},keep_default_na=False)
    if not REQUIRED.issubset(df.columns):raise ValueError("Missing PS source fields")
    if not df.empty:
        if df[list(REQUIRED)].isna().any().any() or df[list(REQUIRED-{"net_generation_mwh"})].eq("").any().any():
            raise ValueError("Null or blank PS source")
        if not df.reported_ba.isin(BAS).all() or not df.period.isin(PERIODS).all() or not df.prime_mover.eq("PS").all():
            raise ValueError("Unexpected BA, year, or non-PS record")
        if df.duplicated(["plant_id","reported_ba","prime_mover","period"]).any():
            raise ValueError("Duplicate plant-month PS observation")
        df["net_generation_mwh"]=pd.to_numeric(df.net_generation_mwh,errors="raise")
        if not df.net_generation_mwh.map(lambda x:-float("inf")<x<float("inf")).all():
            raise ValueError("Nonfinite PS energy")
    grouped=df.groupby(["reported_ba","period"],as_index=False).agg(
        net_generation_mwh=("net_generation_mwh","sum"),
        plant_rows=("plant_id","size"),
        zero_plant_rows=("net_generation_mwh",lambda s:int((s==0).sum())),
        negative_plant_rows=("net_generation_mwh",lambda s:int((s<0).sum())))
    index=pd.MultiIndex.from_product([BAS,PERIODS],names=["reported_ba","period"])
    result=grouped.set_index(["reported_ba","period"]).reindex(index).reset_index()
    result["coverage_status"]=result.plant_rows.notna().map({True:"observed_source_rows",False:"missing_source_rows"})
    result["net_generation_mwh"]=result.net_generation_mwh.astype("Float64")
    for c in ("plant_rows","zero_plant_rows","negative_plant_rows"):
        result[c]=result[c].astype("Int64")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"page1_ps_ba_month_2024.csv",index=False)
    manifest={
        "observed_ba_months":int(result.plant_rows.notna().sum()),
        "missing_ba_months":int(result.plant_rows.isna().sum()),
        "source_plant_month_rows":int(df.shape[0]),
        "by_ba":[{"ba":ba,"observed_months":int(((result.reported_ba==ba)&result.plant_rows.notna()).sum())} for ba in BAS],
        "historical_calibration_certified":False,
        "note":"Source row coverage is not independently verified fleet completeness; missing is not zero. Do not combine with Page 4 or equate net MWh to hourly availability."}
    (out/"page1_ps_ba_month_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(reconcile(a.input,a.output),indent=2))
if __name__=="__main__":main()
