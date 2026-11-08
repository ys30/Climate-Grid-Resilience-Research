"""Source-native two-cohort EIA-930 hourly fuel reporting panel for Paper C.

2023 study: 2023-07-10..17 UTC exclusive, original 2023 Jul-Dec file.
2024 study: 2024-07-01..08 UTC exclusive, two official 2024 halves:
            7h Jan-Jun + 161h Jul-Dec for each BA.
Original fuel column labels and missingness are never conflated across
the mid-2024 fuel taxonomy change. MWh is hourly mean MW integrated 1 h,
not generator-level dispatch, firm MW, reliable transfer or EENS.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime,timedelta,timezone
from pathlib import Path

import pandas as pd

from .eia930_fuel_decomposition import FMT

BAS=("AZPS","BPAT","CISO","SRP")
PREFIX="Net Generation (MW) from "
FIELDS={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"}
YEARS={2023:"2023-07-10T00:00:00Z",2024:"2024-07-01T00:00:00Z"}


def parse_partition(path,year,part,start,stop):
    rows={}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        cols=reader.fieldnames or []
        if not FIELDS.issubset(cols):raise ValueError("Missing EIA930 source BA, UTC or Net Generation")
        fuels=[col for col in cols if col.startswith(PREFIX)
               and not col.endswith((" (Adjusted)"," (Imputed)"))]
        if len(fuels)<9 or len(fuels)!=len(set(fuels)):
            raise ValueError("Missing or duplicate EIA930 original fuel columns")
        if PREFIX+"Natural Gas" not in fuels:raise ValueError("Natural Gas original source column missing")
        if not any("Wind" in fuel for fuel in fuels):
            raise ValueError("Wind original source schema unrecognized")
        for r in reader:
            ba=r["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(r["UTC Time at End of Hour"].strip(),FMT).replace(
                tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<stop:continue
            key=(t,ba)
            if key in rows:raise ValueError("Duplicate official BA hour within original half-year")
            raw_net=r["Net Generation (MW)"].strip()
            net=float(raw_net) if raw_net else None
            if net is not None and not math.isfinite(net):raise ValueError("Nonfinite BA net MW")
            values={}
            for fuel in fuels:
                raw=r[fuel].strip()
                val=float(raw) if raw else None
                if val is not None and not math.isfinite(val):
                    raise ValueError("Nonfinite original reported fuel MW")
                values[fuel[len(PREFIX):]]=val
            rows[key]={"utc_hour_start":t.isoformat(),"year":year,"ba":ba,
                       "original_partition":part,"raw_ba_net_mwh":net,
                       "fuels":values}
    return rows,tuple(col[len(PREFIX):] for col in fuels)


def audit(paths):
    panels=[]
    categories=[]
    audit=[]
    for year in (2023,2024):
        first=pd.Timestamp(YEARS[year]).to_pydatetime()
        stop=first+timedelta(hours=168)
        chosen=("Jul_Dec",) if year==2023 else ("Jan_Jun","Jul_Dec")
        records={}
        for part in chosen:
            source=paths.get((year,part))
            if not source:raise ValueError("Missing original source partition")
            r,names=parse_partition(source,year,part,first,stop)
            if set(records)&set(r):raise ValueError("Overlapping original EIA930 BA hours")
            records.update(r)
            categories.append({"year":year,"partition":part,"original_fuel_fields":list(names),
                               "source_ba_hours":len(r),"schema_label_count":len(names)})
        expected={(first+timedelta(hours=h),ba) for h in range(168) for ba in BAS}
        if set(records)!=expected:
            raise ValueError(f"{year} BA-hour evidence incomplete: {len(records)}/672")
        if year==2024:
            counts=pd.Series([v["original_partition"] for v in records.values()]).value_counts()
            if counts.get("Jan_Jun",0)!=28 or counts.get("Jul_Dec",0)!=644:
                raise ValueError("2024 official UTC boundary not 7+161 hours per BA")
        original_labels=set()
        for key in sorted(expected):
            item=records[key]
            if item["raw_ba_net_mwh"] is None:
                raise ValueError("Missing original raw BA net generation")
            original_labels.update(item["fuels"])
            for label,value in item["fuels"].items():
                panels.append({"year":year,"utc_hour_start":item["utc_hour_start"],"ba":item["ba"],
                    "original_partition":item["original_partition"],
                    "original_fuel_category":label,"raw_net_generation_mwh":item["raw_ba_net_mwh"],
                    "reported_fuel_mwh":value,"fuel_value_reported":value is not None,
                    "reported_zero":value==0 if value is not None else False,
                    "source_ba_hour_present":True,"reported_category_not_necessarily_technology":True})
        audit.append({"year":year,"start_utc":YEARS[year],
            "source_ba_hours":len(records),"original_fuel_labels":len(original_labels),
            "full_source_grid_672_hours":True})
    detail=pd.DataFrame(panels)
    category=pd.DataFrame(categories)
    summary=detail.groupby(["year","ba","original_partition","original_fuel_category"],
                           as_index=False).agg(
        source_ba_hours=("source_ba_hour_present","sum"),
        reported_hours=("fuel_value_reported","sum"),
        reported_zero_hours=("reported_zero","sum"),
        reported_mwh_on_nonblank_hours=("reported_fuel_mwh",lambda x:x.sum(min_count=1)),
        observed_negative_fuel_hours=("reported_fuel_mwh",lambda x:int((x<0).sum())))
    summary["blank_hours"]=summary.source_ba_hours-summary.reported_hours
    summary["fully_reported_for_partition"]=summary.reported_hours.eq(summary.source_ba_hours)
    summary["full_partition_mwh_only_if_no_blank"]=summary.reported_mwh_on_nonblank_hours.where(
        summary.fully_reported_for_partition)
    summary["hourly_source_reporting_not_generator_availability"]=True
    metadata={"comparison_cohorts":audit,"original_source_partitions":categories,
              "year_2024_taxonomy_change_preserved":True,
              "2024_wind_hydro_solar_old_vs_new_not_assumed_equivalent":True,
              "blank_never_assumed_zero":True,"raw_categories_are_not_per_generator_dispatch":True,
              "net_generation_not_sum_of_partially_blank_fuel_fields":True,
              "source_ba_total_is_not_demand_or_EENS":True,
              "historical_hourly_available_mw_or_adequacy_calibrated":False}
    return detail,summary,metadata


def main():
    p=argparse.ArgumentParser()
    for key in ("source2023juldec","source2024janjun","source2024juldec","output"):
        p.add_argument("--"+key,required=True)
    a=p.parse_args()
    paths={(2023,"Jul_Dec"):a.source2023juldec,
           (2024,"Jan_Jun"):a.source2024janjun,
           (2024,"Jul_Dec"):a.source2024juldec}
    hourly,summary,scope=audit(paths)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    hourly.to_csv(out/"paperc_2023_2024_original_hourly_ba_fuel_labels.csv",index=False)
    summary.to_csv(out/"paperc_2023_2024_original_fuel_category_reporting.csv",index=False)
    (out/"paperc_2023_2024_original_fuel_reporting_scope.json").write_text(
        json.dumps(scope,indent=2)+"\n")
    print("SOURCE COHORT:",json.dumps(scope["comparison_cohorts"]))
    print("SOURCE CATEGORY COVERAGE:",summary.groupby(
        ["year","ba"]).agg(fuel_source_groups=("reported_hours","size"),
        blank_fuel_values=("blank_hours","sum"),
        fully_reported_groups=("fully_reported_for_partition","sum")).to_string())
    print(summary.loc[summary.original_fuel_category.str.contains(
        "Natural Gas|Wind|Solar|Hydro|Nuclear|Coal|Pumped|Battery",case=False)
        ].to_string(index=False))

if __name__=="__main__":main()
