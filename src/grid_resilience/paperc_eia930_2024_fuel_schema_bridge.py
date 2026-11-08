"""Paper C boundary-aware original EIA-930 fuel provenance and model-scope audit.

Only raw BA net generation and natural-gas columns are stable enough to sum
through the 2024 half-year category revision. Wind is retained separately
for the legacy 7h and split modern 161h partitions; it is not silently
reclassified into an equivalent observed year-wide resource.
"""
import argparse
import csv
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
from .eia930_fuel_decomposition import FMT

BAS=("AZPS","BPAT","CISO","SRP")
NET="Net Generation (MW)"
GAS="Net Generation (MW) from Natural Gas"
WIND_OLD="Net Generation (MW) from Wind"
WIND_NEW="Net Generation (MW) from Wind without Integrated Battery Storage"
WIND_BATTERY="Net Generation (MW) from Wind with Integrated Battery Storage"


def read_half(path, start, end, partition, modern):
    rows={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        source=csv.DictReader(f)
        needed={"Balancing Authority","UTC Time at End of Hour",NET,GAS,
                WIND_NEW if modern else WIND_OLD}
        if modern:needed.add(WIND_BATTERY)
        if not needed.issubset(source.fieldnames or []):
            raise ValueError(f"Official fuel columns missing in {partition}: {sorted(needed-set(source.fieldnames or []))}")
        fuel_names=[name for name in source.fieldnames or []
                    if name.startswith("Net Generation (MW) from ")
                    and not name.endswith((" (Adjusted)"," (Imputed)"))]
        for r in source:
            ba=r["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(r["UTC Time at End of Hour"].strip(),FMT).replace(
                tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            key=(t,ba)
            if key in rows:raise ValueError("Duplicate BA-hour inside "+partition)
            def num(col,required=False):
                value=r[col].strip()
                if value=="":
                    if required:raise ValueError("Blank raw EIA930 net generation")
                    return None
                x=float(value)
                if not math.isfinite(x):raise ValueError("Nonfinite raw observed generation")
                return x
            rows[key]={"timestamp":t.isoformat(),"ba":ba,"partition":partition,
                       "net_mwh":num(NET,True),"gas_mwh":num(GAS),
                       "legacy_wind_mwh":num(WIND_OLD) if not modern else None,
                       "modern_wind_without_battery_mwh":num(WIND_NEW) if modern else None,
                       "modern_wind_with_battery_mwh":num(WIND_BATTERY) if modern else None}
    return rows,fuel_names


def audit_2024(jan_jun, jul_dec, start="2024-07-01T00:00:00Z"):
    first=pd.Timestamp(start)
    if first.tzinfo is None or first.utcoffset()!=pd.Timedelta(0) or first.year!=2024:
        raise ValueError("UTC July 2024 study window required")
    begin=first.to_pydatetime()
    end=begin+timedelta(hours=168)
    old,oldnames=read_half(jan_jun,begin,end,"2024_Jan_Jun",modern=False)
    new,newnames=read_half(jul_dec,begin,end,"2024_Jul_Dec",modern=True)
    overlaps=set(old).intersection(new)
    if overlaps:raise ValueError(f"Overlapping official BA-hour rows: {len(overlaps)}")
    both={**old,**new}
    expected={(begin+timedelta(hours=i),ba) for i in range(168) for ba in BAS}
    if set(both)!=expected:
        raise ValueError(f"Missing {len(expected-set(both))} or unexpected {len(set(both)-expected)} official BA-hour rows")
    detail=pd.DataFrame([both[key] for key in sorted(expected)])
    groups=[]
    for ba in BAS:
        x=detail.loc[detail.ba.eq(ba)]
        def safe_sum(field):
            vals=x[field].dropna()
            return float(vals.sum()) if len(vals)==168 else None
        nold=int(x.partition.eq("2024_Jan_Jun").sum())
        nnew=int(x.partition.eq("2024_Jul_Dec").sum())
        groups.append({"ba":ba,"source_year":2024,"hours":len(x),
                       "legacy_fuel_schema_hours":nold,"modern_fuel_schema_hours":nnew,
                       "raw_net_generation_mwh":safe_sum("net_mwh"),
                       "raw_natural_gas_mwh":safe_sum("gas_mwh"),
                       "legacy_unsplit_wind_mwh_reported_hours_only":
                           float(x.legacy_wind_mwh.sum()) if x.legacy_wind_mwh.count() else None,
                       "legacy_unsplit_wind_hours":int(x.legacy_wind_mwh.count()),
                       "modern_wind_without_battery_mwh_reported_hours_only":
                           float(x.modern_wind_without_battery_mwh.sum()) if x.modern_wind_without_battery_mwh.count() else None,
                       "modern_wind_without_battery_hours":int(x.modern_wind_without_battery_mwh.count()),
                       "modern_wind_with_battery_mwh_reported_hours_only":
                           float(x.modern_wind_with_battery_mwh.sum()) if x.modern_wind_with_battery_mwh.count() else None,
                       "modern_wind_with_battery_hours":int(x.modern_wind_with_battery_mwh.count()),
                       "cross_schema_wind_168h_comparable_certified":False,
                       "historical_model_calibration_certified":False})
    result=pd.DataFrame(groups)
    flags={"source_year":2024,"target_hours":672,
           "jan_jun_utc_hours":len(old),"jul_dec_utc_hours":len(new),
           "source_ba_hours_complete":len(both)==672,
           "all_net_generation_168h_complete":result.raw_net_generation_mwh.notna().all().item(),
           "all_natural_gas_168h_complete":result.raw_natural_gas_mwh.notna().all().item(),
           "old_fuel_columns":oldnames,"new_fuel_columns":newnames,
           "source_schema_changed":oldnames!=newnames,
           "old_wind_cannot_be_claimed_equivalent_to_modern_without_storage":True,
           "signed_net_gas_observation_not_firm_capacity":True,
           "model_generator_identity_reconciled":False,
           "historical_eens_identified":False}
    return detail,result,flags


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--jan-jun",required=True)
    p.add_argument("--jul-dec",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    detail,summary,flags=audit_2024(a.jan_jun,a.jul_dec)
    dest=Path(a.output);dest.mkdir(parents=True,exist_ok=True)
    detail.to_csv(dest/"2024_july_week1_raw_4ba_hourly_fuel_provenance.csv",index=False)
    summary.to_csv(dest/"2024_july_week1_4ba_raw_net_gas_and_unmatched_wind.csv",index=False)
    (dest/"2024_july_week1_schema_scope.json").write_text(json.dumps(flags,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps({k:v for k,v in flags.items() if not k.endswith("_columns")},indent=2))


if __name__=="__main__":
    main()
