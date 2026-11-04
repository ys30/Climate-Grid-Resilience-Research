"""Match 2024 EPA Part75 local-standard clock hours to actual UTC ERA5 site hours.

For Arizona plants 141/55129/147, EPA Part75 calendar Date/Hour is MST
(UTC-07, no daylight-time shift). A UTC July-only weather source covers
737 of the 744 local July clock-hours. Missing Aug 1 UTC weather stays NA.
EPA gross electrical source load is not EIA generator net load or derating.
"""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
import numpy as np

PLANTS=("141","55129","147")
UTC_OFFSET_HOURS=7
JULY_START="2024-07-01"
JULY_END="2024-07-31"


def align(epa_hourly,era5_hourly):
    required={"facility_id","unit_id","date_local_standard","hour_local_standard",
              "operating_time","gross_load_mw","heat_input_mmbtu"}
    weather_cols={"plant_id","technology","timestamp_utc","temperature_2m_c"}
    if not required.issubset(epa_hourly) or not weather_cols.issubset(era5_hourly):
        raise ValueError("Missing source EPA or ERA5 fields")
    a,b=epa_hourly.copy(),era5_hourly.copy()
    for df,col in ((a,"facility_id"),(b,"plant_id")):
        df[col]=df[col].astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
    a["unit_id"]=a.unit_id.astype("string").str.strip()
    if a[["facility_id","unit_id"]].isna().any().any():
        raise ValueError("Missing EPA identity")
    a=a.loc[a.facility_id.isin(PLANTS)].copy()
    if set(a.facility_id)!=set(PLANTS):
        raise ValueError("Not all three EPA source facilities present")
    day=pd.to_datetime(a.date_local_standard,errors="coerce")
    hour=pd.to_numeric(a.hour_local_standard,errors="coerce")
    if day.isna().any() or not day.dt.strftime("%Y-%m").eq("2024-07").all():
        raise ValueError("Non-July EPA local standard clock date")
    if hour.isna().any() or not hour.between(0,23).all() or not hour.mod(1).eq(0).all():
        raise ValueError("Invalid local standard source hour")
    a["epa_local_clock"]=day+pd.to_timedelta(hour,unit="h")
    a["timestamp_utc"]=(a.epa_local_clock+pd.Timedelta(hours=UTC_OFFSET_HOURS)).dt.tz_localize("UTC")
    if a.duplicated(["facility_id","unit_id","timestamp_utc"]).any():
        raise ValueError("Duplicate EPA unit UTC source hour")
    a["operating_time"]=pd.to_numeric(a.operating_time,errors="coerce")
    a["gross_load_mw"]=pd.to_numeric(a.gross_load_mw,errors="coerce")
    a["heat_input_mmbtu"]=pd.to_numeric(a.heat_input_mmbtu,errors="coerce")
    for col in ("operating_time","gross_load_mw","heat_input_mmbtu"):
        if not np.isfinite(a[col].dropna().to_numpy(float)).all():
            raise ValueError("Invalid EPA source metric")
    if not a.operating_time.dropna().between(0,1).all():
        raise ValueError("Invalid EPA source operating fraction")
    b=b.loc[b.plant_id.isin(PLANTS)&b.technology.eq("gas")].copy()
    b["timestamp_utc"]=pd.to_datetime(b.timestamp_utc,errors="raise",utc=True)
    b["temperature_2m_c"]=pd.to_numeric(b.temperature_2m_c,errors="coerce")
    if b.duplicated(["plant_id","timestamp_utc"]).any():
        raise ValueError("Duplicate ERA5 source plant UTC hour")
    if not np.isfinite(b.temperature_2m_c.to_numpy(float)).all():
        raise ValueError("Invalid ERA5 temperature")
    if set(b.plant_id)!=set(PLANTS):
        raise ValueError("ERA5 source missing one of target plants")
    for site,g in b.groupby("plant_id"):
        expected=pd.date_range("2024-07-01",periods=744,freq="h",tz="UTC")
        if not pd.DatetimeIndex(g.timestamp_utc.sort_values()).equals(expected):
            raise ValueError("Incomplete source UTC July weather")
    merged=a.merge(b[["plant_id","timestamp_utc","temperature_2m_c"]],
        left_on=["facility_id","timestamp_utc"],right_on=["plant_id","timestamp_utc"],
        how="left",validate="many_to_one",indicator=True)
    merged["era5_july_hour_matched"]=merged._merge.eq("both")
    merged=merged.drop(columns=["_merge","plant_id"])
    summary=merged.groupby(["facility_id","unit_id"],as_index=False).agg(
        epa_local_july_rows=("timestamp_utc","size"),
        matched_utc_july_weather_rows=("era5_july_hour_matched","sum"),
        operating_time_reported_rows=("operating_time","count"),
        positive_operating_fraction_rows=("operating_time",lambda s:int(s.gt(0).sum())),
        matched_hours_with_positive_operating_fraction=(
            "operating_time",lambda s:0), # replaced below from explicit intersection
        matched_with_positive_gross_load=("gross_load_mw",lambda s:0))
    computed=merged.groupby(["facility_id","unit_id"]).apply(
        lambda g:pd.Series({
            "matched_hours_with_positive_operating_fraction":int((
                g.era5_july_hour_matched & g.operating_time.gt(0)).sum()),
            "matched_with_positive_gross_load":int((
                g.era5_july_hour_matched & g.gross_load_mw.gt(0)).sum())
        }),include_groups=False).reset_index()
    summary=summary.drop(columns=[
        "matched_hours_with_positive_operating_fraction",
        "matched_with_positive_gross_load"]).merge(
        computed,on=["facility_id","unit_id"],validate="one_to_one")
    if not summary.epa_local_july_rows.eq(744).all():
        raise ValueError("Incomplete EPA local July unit calendar")
    if not summary.matched_utc_july_weather_rows.eq(737).all():
        raise ValueError("Expected 737/744 calendar hour intersection with UTC July source")
    outside=merged.loc[~merged.era5_july_hour_matched]
    if not outside.timestamp_utc.dt.strftime("%Y-%m-%d").eq("2024-08-01").all():
        raise ValueError("Unexpected source-weather unmatched times")
    if not outside.timestamp_utc.dt.hour.isin(range(7)).all():
        raise ValueError("Unexpected UTC boundary hours")
    if merged.loc[merged.era5_july_hour_matched,"temperature_2m_c"].isna().any():
        raise AssertionError("Source matched ERA5 temperature missing")
    manifest={
        "epa_source_clock":"EPA Part75 Local Standard Time",
        "site_time_basis":"Arizona Mountain Standard Time fixed UTC-07:00",
        "epa_hour_to_utc_hours_added":7,
        "dst_applied":False,
        "full_local_july_2024_hours_per_unit":744,
        "matched_utc_july_era5_hours_per_unit":737,
        "missing_weather_utc_hours_per_unit":7,
        "missing_weather_requires_august_source":True,
        "partial_month_hourly_join_not_observed_derating":True,
        "epa_unit_is_eia_generator":False,
        "gross_load_is_eia_net_mw":False,
        "dispatch_or_availability_controlled":False,
        "causal_weather_derating_calibrated":False}
    return merged,summary,manifest


def original_july_rows(csv_path):
    heads=pd.read_csv(csv_path,nrows=0).columns
    required={"Facility ID","Unit ID","Date","Hour",
              "Operating Time","Gross Load (MW)","Heat Input (mmBtu)"}
    if not required.issubset(heads):
        raise ValueError("Unexpected original EPA hourly csv schema")
    use=list(required)
    parts=[]
    for chunk in pd.read_csv(csv_path,usecols=use,dtype="string",chunksize=150000):
        sites=chunk["Facility ID"].str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        part=chunk.loc[sites.isin(PLANTS)&
                       chunk["Date"].str.contains("2024",na=False)].copy()
        if not part.empty:
            part["Facility ID"]=sites.loc[part.index]
            # Parse date by source string rather than infer a UTC timezone.
            parsed=pd.to_datetime(part["Date"],errors="coerce")
            if parsed.isna().any():
                raise ValueError("Invalid source EPA date")
            part=part.loc[parsed.dt.strftime("%Y-%m").eq("2024-07")]
            if not part.empty:parts.append(part)
    if not parts:raise ValueError("No EPA source rows for July targets")
    raw=pd.concat(parts,ignore_index=True)
    return raw.rename(columns={
       "Facility ID":"facility_id","Unit ID":"unit_id",
       "Date":"date_local_standard","Hour":"hour_local_standard",
       "Operating Time":"operating_time",
       "Gross Load (MW)":"gross_load_mw",
       "Heat Input (mmBtu)":"heat_input_mmbtu"})


def main():
    p=argparse.ArgumentParser()
    for field in ("epa-source","era5","output"):
        p.add_argument("--"+field,required=True)
    args=p.parse_args()
    source=original_july_rows(args.epa_source)
    hourly,summary,manifest=align(source,pd.read_csv(args.era5,dtype={"plant_id":"string"}))
    root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
    hourly.to_csv(root/"epa_source_july_lstd_era5_utc_hourly.csv",index=False)
    summary.to_csv(root/"epa_era5_july_hourly_alignment_summary.csv",index=False)
    (root/"epa_era5_july_alignment_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
