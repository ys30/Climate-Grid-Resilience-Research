"""Audit a 168-hour EIA930 window spanning a local-date six-month CSV boundary.

The EIA six-month downloads may partition rows by BA-local calendar date
rather than the requested UTC period. Never fill absent values or combine
non-equivalent old/new fuel categories across schema revisions.
"""
import argparse
import csv
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path

import pandas as pd

from .eia930_fuel_decomposition import FMT
BAS=("AZPS","BPAT","CISO","SRP")


def _read_period(path, start, finish, label):
    raw={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames or []
        required={"Balancing Authority","UTC Time at End of Hour",
                  "Net Generation (MW)","Net Generation (MW) from Natural Gas"}
        if not required.issubset(headers):
            raise ValueError("Official BA/time/net/gas columns unavailable in "+label)
        names=sorted(x.removeprefix("Net Generation (MW) from ") for x in headers
                     if x.startswith("Net Generation (MW) from ")
                     and not x.endswith((" (Imputed)"," (Adjusted)")))
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            at=datetime.strptime(row["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=at<finish:continue
            key=(at,ba)
            if key in raw:raise ValueError("Duplicate BA-hour within "+label)
            total=row["Net Generation (MW)"].strip()
            gas=row["Net Generation (MW) from Natural Gas"].strip()
            if not total:raise ValueError("Missing official BA net generation: "+label)
            raw[key]={"source_partition":label,"official_ba_net_generation_mwh":float(total),
                      "official_gas_generation_mwh":float(gas) if gas else None}
    return raw,names


def audit(previous, current, start="2024-07-01T00:00:00Z"):
    first=pd.Timestamp(start)
    if first.tzinfo is None or first.utcoffset()!=pd.Timedelta(0):
        raise ValueError("Explicit UTC start is required")
    if first.year!=2024:raise ValueError("Source check is for 2024 annual boundary")
    begin=first.to_pydatetime()
    end=begin+timedelta(hours=168)
    earlier,early_names=_read_period(previous,begin,end,"2024_Jan_Jun")
    later,later_names=_read_period(current,begin,end,"2024_Jul_Dec")
    overlap=set(earlier)&set(later)
    if overlap:raise ValueError(f"Duplicate BA-hours across half-year files: {len(overlap)}")
    merged={**earlier,**later}
    expected={(begin+timedelta(hours=h),ba) for h in range(168) for ba in BAS}
    extras=set(merged)-expected
    if extras:raise ValueError("Unexpected official BA-hour records")
    rows=[]
    for at,ba in sorted(expected):
        item=merged.get((at,ba))
        rows.append({"timestamp_utc_start":at.isoformat(),"ba":ba,
                     "source_partition":item["source_partition"] if item else "MISSING",
                     "official_ba_net_generation_mwh":item["official_ba_net_generation_mwh"] if item else None,
                     "official_gas_generation_mwh":item["official_gas_generation_mwh"] if item else None})
    data=pd.DataFrame(rows)
    by_ba=[]
    for ba in BAS:
        d=data.loc[data.ba.eq(ba)]
        counts=d.source_partition.value_counts().to_dict()
        net=d.official_ba_net_generation_mwh
        gas=d.official_gas_generation_mwh
        by_ba.append({"ba":ba,"original_jan_jun_hours":int(counts.get("2024_Jan_Jun",0)),
                      "original_jul_dec_hours":int(counts.get("2024_Jul_Dec",0)),
                      "still_missing_hours":int(counts.get("MISSING",0)),
                      "complete_observed_net_168h_mwh":float(net.sum()) if net.notna().all() else None,
                      "complete_observed_natural_gas_168h_mwh":float(gas.sum()) if gas.notna().all() else None})
    missing=int(data.source_partition.eq("MISSING").sum())
    result={"source_year":2024,"start_utc":start,"end_utc_exclusive":end.isoformat(),
            "target_four_ba_hours":672,"source_jan_jun_hours":len(earlier),
            "source_jul_dec_hours":len(later),"overlapping_ba_hours":0,
            "unrecovered_missing_ba_hours":missing,
            "all_utc_ba_hours_source_recovered":missing==0,
            "jan_jun_official_fuel_categories":early_names,
            "jul_dec_official_fuel_categories":later_names,
            "cross_partitions_fuel_schema_identical":early_names==later_names,
            "old_wind_solar_hydro_not_silently_split_or_reallocated":True,
            "cross_schema_sevenday_full_fuel_mix_calibrated":False,
            "full_fleet_or_historical_eens_calibrated":False,
            "by_ba":by_ba}
    return data,result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--previous",required=True)
    p.add_argument("--current",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    data,manifest=audit(args.previous,args.current)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    data.to_csv(out/"july2024_merged_source_partition_observation_168h.csv",index=False)
    (out/"july2024_merged_source_partition_manifest.json").write_text(
        json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":main()
