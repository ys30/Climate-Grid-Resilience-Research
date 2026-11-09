"""Independent CAISO historical 5min battery telemetry vs preliminary RTD LESR EN.

Download original local-date storage.csv and fuelsource.csv separately (handled
by workflow). Align CSV local PDT clock at 5min frequency to UTC; compare to
2023/24 pre-audited CAISO market RTD LESR EN at (hour+interval) keys. An
observed telemetry aggregate includes hybrids, unlike LESR market award; no
power equivalence, actual market error, battery energy/MWh or SOC asserted.
"""
import argparse
import csv
import json
import math
from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd

COHORT={2023:("2023-07-10T00:00:00Z","2023-07-17T00:00:00Z"),
        2024:("2024-07-01T00:00:00Z","2024-07-08T00:00:00Z")}
MARKET_KEY=("eia930_study_year","utc_5min_start")
STORAGE=("Time","Total batteries","Stand-alone batteries","Hybrid batteries")
FUEL_BATTERY=("Time","Batteries")


def _read_csv(path,required):
    with Path(path).open(newline="",encoding="utf-8-sig") as stream:
        reader=csv.DictReader(stream)
        if not set(required).issubset(reader.fieldnames or []):
            raise ValueError("Missing official CAISO telemetry CSV columns")
        data=list(reader)
    if not data:raise ValueError("Empty official historical CAISO CSV")
    return data


def telemetry(files):
    records=[]
    source_stats=[]
    for year,dated in sorted(files.items()):
        start,end=map(pd.Timestamp,COHORT[year])
        for localday,pair in sorted(dated.items()):
            batteries=_read_csv(pair["storage"],STORAGE)
            fuels=_read_csv(pair["fuelsource"],FUEL_BATTERY)
            bytime={}
            for record in fuels:
                key=record["Time"].strip()
                if key in bytime:raise ValueError("Duplicate fuel source time")
                try:bytime[key]=float(record["Batteries"])
                except ValueError:bytime[key]=None
            seen=set()
            for record in batteries:
                time=record["Time"].strip()
                if time in seen:raise ValueError("Duplicate battery local five minute time")
                seen.add(time)
                if time not in bytime:raise ValueError("No matching fuel-source battery timestamp")
                t=pd.Timestamp(localday+" "+time).tz_localize(
                    "America/Los_Angeles",ambiguous="raise",nonexistent="raise")
                utc=t.tz_convert("UTC")
                if not start<=utc<end:continue
                vals=[]
                for name in STORAGE[1:]:
                    raw=record[name].strip()
                    vals.append(float(raw) if raw else np.nan)
                if not all(math.isfinite(x) for x in vals):
                    raise ValueError("Missing nonfinite official storage five-minute values")
                other=bytime[time]
                if other is None or not math.isfinite(other):
                    raise ValueError("Missing source fuel batteries observation")
                records.append({"year":year,"utc_5min_start":utc.isoformat(),
                    "local_date":localday,"local_time":time,
                    "total_batteries_5min_mw":vals[0],
                    "standalone_batteries_5min_mw":vals[1],
                    "hybrid_batteries_5min_mw":vals[2],
                    "fuelsource_batteries_5min_mw":other,
                    "fuel_storage_same_source_reading":abs(other-vals[0])<1e-9,
                    "source_battery_includes_some_hybrid_resources":True,
                    "preliminary_market_rtd_en_not_same_measurement":True})
            source_stats.append({"year":year,"local_date":localday,
                                 "raw_storage_rows":len(batteries),
                                 "raw_fuelsource_rows":len(fuels),
                                 "kept_utc_cohort_rows":sum(
                                     x["year"]==year and x["local_date"]==localday
                                     for x in records)})
    frame=pd.DataFrame(records)
    if frame.empty or frame.duplicated(["year","utc_5min_start"]).any():
        raise ValueError("Missing telemetry or duplicate UTC key")
    for year,(start,end) in COHORT.items():
        group=frame[frame.year.eq(year)]
        exp=set(pd.date_range(start,periods=2016,freq="5min").astype(str))
        got=set(pd.to_datetime(group.utc_5min_start,utc=True).astype(str))
        if got!=exp:raise ValueError(f"CAISO historical telemetry five minute UTC cohort incomplete {year}: {len(got)}")
    return frame,pd.DataFrame(source_stats)


def comparison(tele,market):
    mandatory={"eia930_study_year","market","resource_type","output_type",
               "utc_hour_start_from_local_trade_date","interval_index","original_market_value"}
    if not mandatory.issubset(market):
        raise ValueError("Original CAISO market record schema missing")
    d=market.loc[market.market.eq("RTD")&
                 market.resource_type.eq("LESR")&
                 market.output_type.eq("EN")].copy()
    d["utc_5min_start"]=(
        pd.to_datetime(d.utc_hour_start_from_local_trade_date,utc=True)+
        pd.to_timedelta((pd.to_numeric(d.interval_index)-1)*5,unit="min"))
    d=d.rename(columns={"eia930_study_year":"year",
                         "original_market_value":"rtd_lesr_en_preliminary_market_value"})
    if d.duplicated(["year","utc_5min_start"]).any():
        raise ValueError("Market RTD source has duplicate UTC five-minute interval")
    tele=tele.copy()
    tele["utc_5min_start"]=pd.to_datetime(tele.utc_5min_start,utc=True)
    pairs=tele.merge(d[["year","utc_5min_start",
                       "rtd_lesr_en_preliminary_market_value"]],
                    on=["year","utc_5min_start"],how="left",
                    validate="one_to_one",indicator=True)
    pairs["market_record_present"]=pairs["_merge"].eq("both")
    pairs=pairs.drop(columns="_merge")
    pairs["telemetry_minus_market_as_descriptive_gap_only"]=(
       pairs.total_batteries_5min_mw-pairs.rtd_lesr_en_preliminary_market_value)
    pairs["same_physical_resource_population_verified"]=False
    pairs["market_vs_telemetry_are_not_settlement_interchangeable"]=True
    rows=[]
    for year,g in pairs.groupby("year"):
        numeric=g.dropna(subset=["rtd_lesr_en_preliminary_market_value"])
        if numeric.empty:raise ValueError("No UTC matched telemetry vs RTD observations")
        bothcorr=(float(numeric.total_batteries_5min_mw.corr(
            numeric.rtd_lesr_en_preliminary_market_value))
                  if len(numeric)>=3 else None)
        rows.append({"year":year,"telemetry_expected_five_minute_keys":2016,
                     "telemetry_numeric_five_minute_keys":len(g),
                     "rtd_market_exact_utc_matched_intervals":len(numeric),
                     "rtd_market_missing_intervals":len(g)-len(numeric),
                     "matched_total_battery_vs_rtd_en_correlation":bothcorr,
                     "signed_difference_mw_mean_descriptive_only":
                         float(numeric.telemetry_minus_market_as_descriptive_gap_only.mean()),
                     "absolute_difference_mw_mean_descriptive_only":
                         float(numeric.telemetry_minus_market_as_descriptive_gap_only.abs().mean()),
                     "instrument_and_resource_population_identical":False,
                     "actual_metered_battery_generation_or_market_error_inferred":False})
    scope={"same_study_cohort_UTC":True,
           "storage_telemetry_frequency_minutes":5,
           "market_EN_is_preliminary_not_settlement_metering":True,
           "telemetry_total_batteries_includes_hybrid_scope":True,
           "rtd_lesr_is_market_resource_type_not_identical_scope":True,
           "no_imputed_2023_missing_rtd_market_intervals":True,
           "no_reliability_or_EENS_calibration":True}
    return pairs,pd.DataFrame(rows),scope


def main():
    a=argparse.ArgumentParser()
    for k in ("index","market","output"):a.add_argument("--"+k,required=True)
    p=a.parse_args()
    idx=json.loads(Path(p.index).read_text())
    files={}
    for item in idx:
        y=int(item["year"])
        files.setdefault(y,{})[item["local_date"]]={
           "storage":item["storage_csv"],"fuelsource":item["fuelsource_csv"]}
    t,s=telemetry(files)
    merged,c,scope=comparison(t,pd.read_csv(p.market))
    out=Path(p.output);out.mkdir(parents=True,exist_ok=True)
    for name,frame in (("ca_iso_original_battery_telemetry_5min",t),
                       ("ca_iso_telemetry_source_day_coverage",s),
                       ("ca_iso_telemetry_vs_preliminary_rtd_lesr_en",merged),
                       ("ca_iso_market_vs_telemetry_descriptive_summary",c)):
        frame.to_csv(out/(name+".csv"),index=False)
    (out/"ca_iso_telemetry_vs_rtd_scope.json").write_text(json.dumps(scope,indent=2)+"\n")
    print("CAISO FIVE MIN SOURCE VS RTD MARKET",c.to_string(index=False))
    print("OFFICIAL SOURCE SCOPE",s.to_string(index=False))


if __name__=="__main__":main()
