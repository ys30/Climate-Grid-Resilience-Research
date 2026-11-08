"""Paper C raw EIA-930 seven-day four-BA balance and eligibility audit.

Read both official 2024 semiannual CSV partitions. BA-hour source coverage,
raw D/NG/TI field presence, and closure are three separate gates. Neither
exact arithmetic closure nor an adjusted balance proves physical adequacy.
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
FIELDS={"demand_mw":"Demand (MW)","net_generation_mw":"Net Generation (MW)",
        "net_interchange_mw":"Total Interchange (MW)"}


def source_half(path, start, stop, label):
    result={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        source=csv.DictReader(f)
        required={"Balancing Authority","UTC Time at End of Hour",*FIELDS.values()}
        if not required.issubset(source.fieldnames or []):
            raise ValueError("Missing raw EIA930 balance fields in "+label)
        for raw in source:
            ba=raw["Balancing Authority"].strip()
            if ba not in BAS:continue
            at=datetime.strptime(raw["UTC Time at End of Hour"].strip(),FMT).replace(
                tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=at<stop:continue
            key=(at,ba)
            if key in result:raise ValueError("Duplicate BA-hour in "+label)
            values={}
            for out,col in FIELDS.items():
                source_value=raw[col].strip()
                if source_value:
                    value=float(source_value)
                    if not math.isfinite(value):raise ValueError("Nonfinite source field")
                    values[out]=value
                else:
                    values[out]=None
            result[key]={"ba":ba,"utc_hour_start":at.isoformat(),"source_partition":label,**values}
    return result


def audit(first_half,second_half,start="2024-07-01T00:00:00Z"):
    first=pd.Timestamp(start)
    if first.year!=2024 or first.tzinfo is None or first.utcoffset()!=pd.Timedelta(0):
        raise ValueError("2024 explicit UTC window required")
    start_dt=first.to_pydatetime()
    stop=start_dt+timedelta(hours=168)
    old=source_half(first_half,start_dt,stop,"2024_Jan_Jun")
    new=source_half(second_half,start_dt,stop,"2024_Jul_Dec")
    if set(old)&set(new):raise ValueError("Overlapping official BA-hours")
    joined={**old,**new}
    expected={(start_dt+timedelta(hours=i),ba) for i in range(168) for ba in BAS}
    if set(joined)!=expected:
        raise ValueError(f"Official source BA-hour grid incomplete: {len(joined)}/672")
    data=pd.DataFrame(joined[k] for k in sorted(expected))
    present=data[list(FIELDS)].notna().all(axis=1)
    data["raw_triplet_present"]=present
    data["raw_generation_minus_demand_minus_interchange_mw"]=(
        data.net_generation_mw-data.demand_mw-data.net_interchange_mw)
    data.loc[~present,"raw_generation_minus_demand_minus_interchange_mw"]=float("nan")
    data["closure_tolerance_mw"]=data.demand_mw.abs().mul(.01).clip(lower=1.0)
    data["raw_arithmetic_closes"]=(
        present &
        data.raw_generation_minus_demand_minus_interchange_mw.abs().le(data.closure_tolerance_mw))
    result=[]
    for ba,part in data.groupby("ba",sort=True):
        valid=part.loc[part.raw_triplet_present]
        residual=valid.raw_generation_minus_demand_minus_interchange_mw
        original_counts=part.source_partition.value_counts()
        result.append({"ba":ba,"source_hours":len(part),
            "jan_jun_hours":int(original_counts.get("2024_Jan_Jun",0)),
            "jul_dec_hours":int(original_counts.get("2024_Jul_Dec",0)),
            "triplet_complete_hours":len(valid),
            "missing_raw_demand_hours":int(part.demand_mw.isna().sum()),
            "missing_raw_net_generation_hours":int(part.net_generation_mw.isna().sum()),
            "missing_raw_total_interchange_hours":int(part.net_interchange_mw.isna().sum()),
            "hourly_arithmetic_closing_hours":int(part.raw_arithmetic_closes.sum()),
            "hourly_arithmetic_nonclosing_hours":int(len(valid)-part.raw_arithmetic_closes.sum()),
            "signed_raw_residual_valid_hours_mwh":float(residual.sum()),
            "absolute_raw_residual_valid_hours_mwh":float(residual.abs().sum()),
            "maximum_absolute_raw_residual_mw":float(residual.abs().max()) if len(valid) else None,
            "all_raw_triplets_complete":len(valid)==168,
            "all_raw_hours_close":len(valid)==168 and bool(part.raw_arithmetic_closes.all()),
            "historical_supply_adequacy_calibrated":False})
    out=pd.DataFrame(result)
    manifest={"source_period":"2024-07-01 to 2024-07-08 UTC exclusive",
        "raw_sources":"official EIA930 2024 Jan-Jun and Jul-Dec original",
        "total_source_ba_hours":len(data),"source_ba_hours_complete":len(data)==672,
        "identity":"raw net generation minus raw demand minus raw total interchange",
        "closure_tolerance":"max(1MW, 1% of absolute reported raw hourly demand)",
        "raw_reported_values_never_imputed":True,
        "cross_ba_interchange_flows_or_generator_identity_reconciled":False,
        "raw_arithmetic_eligibility_is_not_physical_calibration":True,
        "historical_energy_not_served_estimated":False}
    return data,out,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--jan-jun",required=True)
    p.add_argument("--jul-dec",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    hourly,summary,meta=audit(a.jan_jun,a.jul_dec)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    hourly.to_csv(out/"paper_c_july2024_168h_raw_ba_balance_hourly.csv",index=False)
    summary.to_csv(out/"paper_c_july2024_168h_raw_ba_balance_by_ba.csv",index=False)
    (out/"paper_c_july2024_raw_ba_balance_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
