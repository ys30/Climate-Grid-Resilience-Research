"""Seven-day EIA-930 BA/fuel observation accounting against *modeled* output.

EIA-930 net-generation fuel categories and the generic gas/wind PyPSA
generators are not source-equivalent. Do not call any comparison an empirical
coverage fraction, generation calibration, actual shortage or firm capacity.
"""
import argparse
import csv
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pandas as pd
import numpy as np
from .eia930_fuel_decomposition import FMT,FUELS

BAS=("AZPS","BPAT","CISO","SRP")
MAPPING={"Natural Gas":"generic_thermal_proxy","Wind":"wind"}
SCENARIO="baseline"

def extract(source, start, hours=168):
    first=pd.Timestamp(start)
    if first.tzinfo is None or first.utcoffset()!=pd.Timedelta(0):
        raise ValueError("Explicit UTC start time required")
    if hours!=168:raise ValueError("Period contract requires 168h")
    expected=pd.date_range(first,periods=hours,freq="h")
    seen=set()
    rows=[]
    fuelcols={fuel:"Net Generation (MW) from "+fuel for fuel in FUELS}
    required={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"}|set(fuelcols.values())
    with Path(source).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing official EIA930 fuel/net generation columns")
        for raw in reader:
            ba=raw["Balancing Authority"].strip()
            if ba not in BAS:continue
            stamp=datetime.strptime(raw["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if stamp<first.to_pydatetime() or stamp>=first.to_pydatetime()+timedelta(hours=hours):continue
            key=(stamp,ba)
            if key in seen:raise ValueError("Duplicate EIA930 BA hour")
            seen.add(key)
            total=raw["Net Generation (MW)"].strip()
            if not total:raise ValueError("Missing official net generation")
            total=float(total)
            if not np.isfinite(total):raise ValueError("Nonfinite EIA930 net generation")
            for fuel,col in fuelcols.items():
                value=raw[col].strip()
                if value:
                    value=float(value)
                    if not np.isfinite(value):raise ValueError("Nonfinite reported fuel MW")
                    rows.append({"timestamp":stamp.isoformat(),"ba":ba,"fuel":fuel,
                                 "reported":True,"observed_mwh":value,"observed_net_generation_mwh":total})
                else:
                    rows.append({"timestamp":stamp.isoformat(),"ba":ba,"fuel":fuel,
                                 "reported":False,"observed_mwh":float("nan"),
                                 "observed_net_generation_mwh":total})
    if seen!={(t.to_pydatetime(),ba) for t in expected for ba in BAS}:
        raise ValueError(f"Incomplete official EIA930 BA-hour grid: {len(seen)}/672")
    obs=pd.DataFrame(rows)
    if len(obs)!=hours*len(BAS)*len(FUELS):
        raise ValueError("Incomplete fuel observation grid")
    summary=obs.groupby(["ba","fuel"],sort=True).agg(
        reported_hours=("reported","sum"),
        signed_observed_mwh_reported_hours_only=("observed_mwh","sum"),
        observed_negative_hours=("observed_mwh",lambda x:int((x<0).sum()))
    ).reset_index()
    summary["blank_hours"]=hours-summary.reported_hours
    summary.loc[summary.reported_hours.eq(0),"signed_observed_mwh_reported_hours_only"]=np.nan
    summary["observed_full_period_mwh"]=summary.signed_observed_mwh_reported_hours_only.where(
        summary.reported_hours.eq(hours))
    totals=obs.drop_duplicates(["timestamp","ba"])[["ba","observed_net_generation_mwh"]]
    net=totals.groupby("ba").observed_net_generation_mwh.sum().rename("official_ba_net_generation_mwh")
    summary=summary.merge(net,on="ba",validate="many_to_one")
    return summary


def model_comparison(observed, modeled,year,variant):
    needed={"timestamp","ba","scenario","technology","generation_mwh"}
    if not needed.issubset(modeled):
        raise ValueError("Missing modeled dispatch fields")
    a=modeled.loc[modeled.scenario.eq(SCENARIO)].copy()
    if len(a)!=168*len(BAS)*2 or set(a.ba)!=set(BAS) or set(a.technology)!=set(MAPPING.values()):
        raise ValueError("Modeled BA-hour generation must be complete")
    a["timestamp"]=pd.to_datetime(a.timestamp,utc=True,errors="raise")
    if a.duplicated(["timestamp","ba","technology"]).any() or a.timestamp.nunique()!=168:
        raise ValueError("Duplicate or incomplete model hour")
    a["generation_mwh"]=pd.to_numeric(a.generation_mwh,errors="raise")
    if not np.isfinite(a.generation_mwh).all() or a.generation_mwh.lt(-1e-4).any():
        raise ValueError("Invalid modeled generation")
    model=a.groupby(["ba","technology"]).generation_mwh.sum()
    out=observed.copy()
    out["model_technology_proxy"]=out.fuel.map(MAPPING)
    out["modeled_baseline_mwh"]=out.apply(
        lambda row:float(model.loc[(row.ba,row.model_technology_proxy)])
        if row.fuel in MAPPING else float("nan"),axis=1)
    out["period_year"]=year
    out["network_variant"]=variant
    out["observed_and_modeled_different_reporting_scope"]=True
    out["actual_generation_coverage_fraction_certified"]=False
    out["historical_eens_or_outages_identified"]=False
    return out


def main():
    p=argparse.ArgumentParser()
    for key in ("source","start","model","output","network-variant"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--year",type=int,required=True)
    args=p.parse_args()
    if args.year not in (2023,2024) or pd.Timestamp(args.start).year!=args.year:
        raise ValueError("Source-window annual year mismatch")
    result=model_comparison(
        extract(args.source,args.start),pd.read_csv(args.model),args.year,args.network_variant)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(out,index=False)
    audit={"year":args.year,"start_utc":args.start,"hours_per_ba":168,
           "fuel_category_ba_groups":len(result),"fully_observed_fuel_groups":
           int(result.reported_hours.eq(168).sum()),
           "partially_or_entirely_blank_fuel_groups":int(result.reported_hours.lt(168).sum()),
           "observed_fuel_columns_not_imputed":True,
           "net_generation_is_BA_reported_not_source_matched_generator_sum":True,
           "modeled_generic_thermal_proxy_not_same_as_observed_Natural_Gas":True,
           "model_dispatch_vs_actual_hourly_generator_identity_calibrated":False,
           "historical_energy_not_served_estimated":False}
    out.with_suffix(".manifest.json").write_text(json.dumps(audit,indent=2)+chr(10))
    print(json.dumps(audit,indent=2))
    print(result[result.fuel.isin(MAPPING)].to_string(index=False))


if __name__=="__main__":main()
