"""Combine verified EIA-923 Page 1 HY and PS plant-month observations.

Monthly net energy is observational evidence, NOT hourly power availability.
"""
import argparse, json
from pathlib import Path
import pandas as pd

BAS=("AZPS","BPAT","CISO","SRP")
MONTHS=tuple(f"2024-{i:02d}" for i in range(1,13))
REQUIRED={"plant_id","reported_ba","prime_mover","period","net_generation_mwh"}

def combine(hy_csv,ps_csv,output):
    parts=[]
    for path,tech,source in [(hy_csv,"HY","Page 1 Generation and Fuel Data"),
                             (ps_csv,"PS","Page 1 Energy Storage")]:
        df=pd.read_csv(path,dtype={"plant_id":str,"reported_ba":str,"prime_mover":str,"period":str},
                       keep_default_na=False)
        if not REQUIRED.issubset(df.columns):raise ValueError(f"Missing {tech} input fields")
        if not df.empty:
            if df[["plant_id","reported_ba","prime_mover","period"]].eq("").any().any():
                raise ValueError(f"Missing {tech} identifiers")
            if not df.prime_mover.eq(tech).all() or not df.reported_ba.isin(BAS).all() or not df.period.isin(MONTHS).all():
                raise ValueError(f"Unexpected {tech} BA/month/prime mover")
            if df.duplicated(["plant_id","reported_ba","prime_mover","period"]).any():
                raise ValueError(f"Duplicate {tech} plant-month")
            df["net_generation_mwh"]=pd.to_numeric(df.net_generation_mwh,errors="raise")
            if not df.net_generation_mwh.map(lambda v:-float("inf")<float(v)<float("inf")).all():
                raise ValueError(f"Invalid {tech} MWh")
        df["source_sheet"]=source
        parts.append(df)
    combined=pd.concat(parts,ignore_index=True)
    observed=combined.groupby(["reported_ba","prime_mover","period"],as_index=False).agg(
        net_generation_mwh=("net_generation_mwh","sum"),
        plant_month_rows=("plant_id","size"),
        negative_plant_month_rows=("net_generation_mwh",lambda s:int((s<0).sum())),
        zero_plant_month_rows=("net_generation_mwh",lambda s:int((s==0).sum())))
    full=pd.MultiIndex.from_product([BAS,("HY","PS"),MONTHS],
                                     names=["reported_ba","prime_mover","period"])
    result=observed.set_index(["reported_ba","prime_mover","period"]).reindex(full).reset_index()
    result["coverage_status"]=result.plant_month_rows.notna().map(
        {True:"observed_source_rows",False:"missing_source_rows"})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"eia923_hy_ps_ba_month_observed_2024.csv",index=False)
    report={"expected_ba_technology_month_slots":96,
            "observed_slots":int(result.plant_month_rows.notna().sum()),
            "missing_slots":int(result.plant_month_rows.isna().sum()),
            "hy_plant_month_records":len(parts[0]),"ps_plant_month_records":len(parts[1]),
            "by_technology":[{"prime_mover":t,"observed_ba_months":int(((result.prime_mover==t)&result.plant_month_rows.notna()).sum())}
                             for t in ("HY","PS")],
            "historical_calibration_certified":False,
            "note":"Two separately sourced, plant-level reported net MWh series. Missing BA-months are NOT zero; source coverage is not full-fleet verification or hourly availability."}
    (out/"eia923_hy_ps_ba_month_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hy",required=True);p.add_argument("--ps",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(combine(a.hy,a.ps,a.output),indent=2))
if __name__=="__main__":main()
