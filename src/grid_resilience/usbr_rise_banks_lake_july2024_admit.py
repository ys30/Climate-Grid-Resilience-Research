"""Admit source-observed USBR RISE Banks Lake July 2024 daily elevation and monthly PS upper pond.

RISE CSV begins with #LOCATION INFORMATION# comment rows. Actual data
columns are location, parameter, value, unit, frequency, statistic,
timestamp. Treat 2024-07-01 monthly stamp as END OF JULY per official
item 5226 metadata, not as one-day or 1 July observation. Do not
convert elevation differences into recoverable electric energy MWh.
"""
import argparse
import csv
import json
from pathlib import Path

import pandas as pd

EXPECTED={
 "banks_lake_daily_original_RISE_2024.csv":("Banks Lake and Dry Falls Dam (BNK)","Lake/Reservoir Elevation","daily"),
 "keys_iii_upper_pond_monthly_original_RISE_2024.csv":("Grand Coulee Pump Generating Plant","Upper Pond Elevation","monthly")
}

def rows_from_ise(path,location,parameter,frequency):
    rows=[]
    with open(path,encoding="utf-8-sig",newline="") as f:
        raw=list(csv.reader(f))
    for r in raw:
        if len(r)<7 or r[0].startswith("#") or r[0].strip()!=location:
            continue
        if r[1].strip()!=parameter or r[3].strip()!="ft" or r[4].strip()!=frequency or r[5].strip()!="instant":
            raise ValueError("RISE location data unexpected unit, frequency or parameter")
        try:
            d=pd.Timestamp(r[6].strip())
            v=float(r[2].strip())
        except Exception as e:
            raise ValueError("RISE source observation unreadable") from e
        if pd.isna(d) or pd.isna(v):
            raise ValueError("Unobserved value")
        rows.append({"source_record_timestamp":d,"elevation_ft":v,
                     "site":location,"frequency":frequency})
    if not rows:
        raise ValueError("No original RISE source observed elevation rows")
    return pd.DataFrame(rows)

def admit(daily_path,monthly_path):
    daily=rows_from_ise(daily_path,*EXPECTED["banks_lake_daily_original_RISE_2024.csv"])
    monthly=rows_from_ise(monthly_path,*EXPECTED["keys_iii_upper_pond_monthly_original_RISE_2024.csv"])
    d=daily.loc[daily.source_record_timestamp.dt.year.eq(2024)&
                daily.source_record_timestamp.dt.month.eq(7)].copy()
    expected=pd.date_range("2024-07-01",periods=31,freq="D")
    if len(d)!=31 or d.source_record_timestamp.dt.normalize().duplicated().any() or not pd.DatetimeIndex(
        d.source_record_timestamp.dt.normalize().sort_values()).equals(expected):
        raise ValueError(f"Banks Lake incomplete July 2024 source observed days: rows={len(d)}")
    if not d.elevation_ft.between(1000,2000).all():
        raise ValueError("Invalid Banks Lake original reservoir elevation feet")
    m=monthly.loc[monthly.source_record_timestamp.dt.year.eq(2024)&
                  monthly.source_record_timestamp.dt.month.eq(7)].copy()
    if len(m)!=1 or m.source_record_timestamp.iloc[0].day!=1 or not m.elevation_ft.between(1000,2000).all():
        raise ValueError("Grand Coulee monthly upper-pond July end-of-month observation not identified")
    d["date"]=d.source_record_timestamp.dt.strftime("%Y-%m-%d")
    result={
      "dataset_129466_Banks_Lake_observed_July_daily_records":31,
      "dataset_5226_upper_pond_July_source_records":1,
      "dataset_5226_first_of_month_timestamp_semantics":"July 1 source date represents July end-of-month instant per RISE catalog",
      "banks_2024_july_min_elevation_ft":float(d.elevation_ft.min()),
      "banks_2024_july_max_elevation_ft":float(d.elevation_ft.max()),
      "banks_2024_july_1_elevation_ft":float(d.loc[d.date.eq("2024-07-01"),"elevation_ft"].iloc[0]),
      "banks_2024_july_31_elevation_ft":float(d.loc[d.date.eq("2024-07-31"),"elevation_ft"].iloc[0]),
      "banks_2024_july_end_minus_start_elevation_ft":float(d.loc[d.date.eq("2024-07-31"),"elevation_ft"].iloc[0]-d.loc[d.date.eq("2024-07-01"),"elevation_ft"].iloc[0]),
      "grand_coulee_PG_2024_july_month_end_upper_pond_elevation_ft":float(m.elevation_ft.iloc[0]),
      "daily_vs_monthly_observation_time_and_site_identical":False,
      "roosevelt_lake_lower_level_source_included":False,
      "water_head_at_reversible_pump_generators_estimated":False,
      "water_duty_or_flow_2024_observed":False,
      "pumped_storage_usable_electric_MWh_verified":False,
      "pumped_storage_hourly_discharge_and_SOC_inferred":False,
      "original_2024_july_PyPSA_recalibrated":False
    }
    return d,m,result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",required=True);parser.add_argument("--output",required=True)
    a=parser.parse_args()
    src=Path(a.source_dir);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    d,m,r=admit(src/"banks_lake_daily_original_RISE_2024.csv",
                src/"keys_iii_upper_pond_monthly_original_RISE_2024.csv")
    d.to_csv(out/"banks_lake_2024_july_31_original_daily_elevation_ft.csv",index=False)
    m.to_csv(out/"keys_iii_2024_july_one_month_end_upper_pond_elevation_ft.csv",index=False)
    (out/"usbr_2024_july_banks_keys_hydrological_evidence_manifest.json").write_text(
        json.dumps(r,indent=2)+"\n")
    print("SOURCE-VERIFIED USBR BANKS LAKE JULY 2024 ACTUAL OBSERVED ELEVATION")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
