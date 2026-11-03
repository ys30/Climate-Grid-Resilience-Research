"""Source-preserving SRP monthly EIA-923 Page1 / EIA-930 fuel scope audit.

A monthly EIA-923 plant/fuel/prime-mover series is not an EIA-930 BA-hour
fuel series. Preserve blanks and original fuel codes; do not auto-allocate
EIA-923 fuels to EIA-930 reporting categories or interpret residual as error.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .eia930_fuel_decomposition import FUELS


def audit(page1, balance, *, ba="SRP", month="2024-01", expected_hours=None):
    p1_cols={"plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"}
    fields={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"}
    fuel_cols={"Net Generation (MW) from "+f for f in FUELS}
    if not p1_cols.issubset(page1.columns):
        raise ValueError("Missing EIA923 Page1 columns")
    if not fields.union(fuel_cols).issubset(balance.columns):
        raise ValueError("Missing EIA930 generation/fuel columns")
    start=pd.Timestamp(month+"-01",tz="UTC")
    end=start+pd.offsets.MonthBegin(1)
    hours=int((end-start).total_seconds()/3600)
    if expected_hours is not None:
        hours=int(expected_hours)
        if hours<1:raise ValueError("Invalid expected hours")
    a=page1.copy()
    a["reported_ba"]=a.reported_ba.astype("string").str.strip()
    a["period"]=a.period.astype("string").str.strip()
    a=a.loc[a.reported_ba.eq(ba)&a.period.eq(month)].copy()
    if a.empty:raise ValueError("Missing EIA923 BA month")
    a["net_generation_mwh"]=pd.to_numeric(a.net_generation_mwh,errors="coerce")
    if not np.isfinite(a.net_generation_mwh.to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite/missing EIA923 Page1 generation")
    if a[["reported_fuel","prime_mover"]].isna().any().any():
        raise ValueError("Missing EIA923 fuel or mover")
    b=balance.loc[balance["Balancing Authority"].astype("string").str.strip().eq(ba)].copy()
    b["_utc"]=pd.to_datetime(b["UTC Time at End of Hour"],utc=True,errors="raise")-pd.Timedelta(hours=1)
    b=b.loc[b._utc.ge(start)&b._utc.lt(end)].copy()
    if len(b)!=hours or b._utc.duplicated().any():
        raise ValueError("Incomplete or duplicate EIA930 BA UTC hours")
    if expected_hours is None:
        expected=pd.date_range(start,end,freq="h",inclusive="left")
        if not pd.DatetimeIndex(b._utc.sort_values()).equals(expected):
            raise ValueError("EIA930 BA UTC-hour coverage gap")
    b["Net Generation (MW)"]=pd.to_numeric(b["Net Generation (MW)"],errors="coerce")
    if not np.isfinite(b["Net Generation (MW)"].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite EIA930 total generation")
    rows=[]
    fuel_values=[]
    for fuel in FUELS:
        col="Net Generation (MW) from "+fuel
        raw=b[col].astype("string").str.strip()
        value=pd.to_numeric(raw.mask(raw.eq("")),errors="coerce")
        malformed=raw.notna() & raw.ne("") & value.isna()
        if malformed.any() or np.isinf(value.to_numpy(dtype=float)).any():
            raise ValueError("Invalid EIA930 fuel value: "+fuel)
        n=int(value.notna().sum())
        rows.append({"eia930_fuel":fuel,"reported_hours":n,
                     "blank_hours":hours-n,
                     "signed_reported_mwh":float(value.sum()) if n else None,
                     "monthly_sum_complete":n==hours})
        fuel_values.append(value)
    detail=pd.DataFrame(rows)
    p1=a.groupby(["prime_mover","reported_fuel"],dropna=False).agg(
        source_rows=("net_generation_mwh","size"),
        signed_page1_mwh=("net_generation_mwh","sum")
    ).reset_index()
    monthly_total=float(b["Net Generation (MW)"].sum())
    page1_total=float(a.net_generation_mwh.sum())
    all_hours_complete=bool(detail.monthly_sum_complete.all())
    complete_fuel_sum=float(detail.signed_reported_mwh.sum()) if all_hours_complete else None
    summary={"ba":ba,"period":month,"hours":hours,
             "eia930_total_reported_generation_mwh":monthly_total,
             "eia923_page1_reported_generation_mwh":page1_total,
             "page1_minus_eia930_source_scope_difference_mwh":page1_total-monthly_total,
             "eia930_all_fuels_hourly_complete":all_hours_complete,
             "eia930_complete_fuel_sum_mwh":complete_fuel_sum,
             "eia930_total_minus_complete_fuel_sum_mwh":(
                 monthly_total-complete_fuel_sum if all_hours_complete else None),
             "eia923_source_rows":int(len(a)),
             "eia923_prime_mover_fuel_groups":int(len(p1)),
             "category_crosswalk_certified":False,
             "physical_ba_boundary_reconciled":False,
             "historical_calibration_certified":False,
             "warning":"Do not add Page1 to Page4 or treat blank EIA930 fuel as zero. "
                       "Page1 fuel codes and BA-hour fuel groups are distinct reporting grains."}
    return detail,p1,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--page1",required=True)
    p.add_argument("--eia930",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--ba",default="SRP")
    p.add_argument("--month",default="2024-01")
    args=p.parse_args()
    a=pd.read_csv(args.page1,dtype={"plant_id":"string"},keep_default_na=False)
    b=pd.read_csv(args.eia930,low_memory=False)
    detail,p1,manifest=audit(a,b,ba=args.ba,month=args.month)
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    detail.to_csv(root/"eia930_monthly_fuel_reporting_coverage.csv",index=False)
    p1.to_csv(root/"eia923_page1_prime_mover_fuel_comparison.csv",index=False)
    (root/"eia923_eia930_fuel_scope_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
