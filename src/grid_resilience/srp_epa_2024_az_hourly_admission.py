"""Source-provenanced 2024 Arizona CAMPD hourly emissions admission audit.

This audits *reported EPA hourly emissions / operations* at ORIS facility
level. It does NOT claim unit-gen linkage, measured EIA electrical net power,
outages or temperature derating. Unknown schemas fail closed and the data
source MD5 is checked against the independently published Zenodo record.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen
import pandas as pd

FACILITIES=("141","55129","147")
SNAPSHOT_URL=("https://zenodo.org/records/15059567/files/"
              "emissions-hourly-2024-az.csv?download=1")
EXPECTED_MD5="7123a5070f652890f46e819dcc890ec0"


def _column(columns,aliases,label):
    canon={str(s).casefold().replace("_","").replace(" ","").replace("-",""):s
           for s in columns}
    hits=[canon[a.casefold().replace("_","").replace(" ","").replace("-","")]
          for a in aliases
          if a.casefold().replace("_","").replace(" ","").replace("-","") in canon]
    hits=list(dict.fromkeys(hits))
    if len(hits)!=1:
        raise ValueError(f"Ambiguous or missing {label} CSV column: {list(columns)}")
    return hits[0]


def audit_csv(path):
    fields=pd.read_csv(path,nrows=0).columns
    facility=_column(fields,("facilityId","orisCode","orisplCode"),"facility identifier")
    unit=_column(fields,("unitId","unit_id"),"EPA unit identifier")
    date=_column(fields,("Date","operatingDate","date"),"operating date")
    hour=_column(fields,("Hour","operatingHour","hour"),"operating hour")
    columns=[facility,unit,date,hour]
    optional={}
    for name,aliases in {
        "gross_load":("Gross Load (MW)","grossLoad"),
        "heat_input":("Heat Input (mmBtu)","heatInput"),
        "operating_time":("Operating Time","operatingTime")
    }.items():
        try:
            optional[name]=_column(fields,aliases,name)
            columns.append(optional[name])
        except ValueError:
            pass
    rows=[]
    total_selected=0
    seen=set()
    for chunk in pd.read_csv(path,chunksize=120000,dtype="string",usecols=columns):
        idseries=chunk[facility].astype("string").str.strip().str.replace(
            r"^0+(?=[0-9])","",regex=True)
        selected=chunk.loc[idseries.isin(FACILITIES)].copy()
        if selected.empty:continue
        when=pd.to_datetime(selected[date],errors="coerce")
        if when.isna().any() or not when.dt.year.eq(2024).all():
            raise ValueError("Target facility snapshot contains invalid or non-2024 date")
        hours=pd.to_numeric(selected[hour],errors="coerce")
        if hours.isna().any() or not hours.between(0,23).all() or not hours.mod(1).eq(0).all():
            raise ValueError("Invalid EPA hourly source hour")
        if selected[unit].isna().any() or selected[unit].astype("string").str.strip().eq("").any():
            raise ValueError("Target EPA unit ID is missing")
        selected["normalized_oris"]=idseries.loc[selected.index]
        # Detect duplicate source unit/date/hour rows even across CSV chunks;
        # do not assume that 'Date' is UTC without source documentation.
        for fac,u,dt,h in zip(selected.normalized_oris,selected[unit],
                            when.dt.strftime("%Y-%m-%d"),hours.astype(int)):
            key=(str(fac),str(u).strip(),str(dt),int(h))
            if key in seen:
                raise ValueError("Duplicate EPA unit date/hour source observation")
            seen.add(key)
        total_selected+=len(selected)
        for fac,frame in selected.groupby("normalized_oris"):
            counts=frame[unit].value_counts(dropna=False)
            rows.extend({"oris":str(fac),"epa_unit_id":str(uid),
                         "report_rows":int(num)} for uid,num in counts.items())
    if rows:
        out=(pd.DataFrame(rows).groupby(["oris","epa_unit_id"],as_index=False)
             .report_rows.sum().sort_values(["oris","epa_unit_id"]))
    else:
        out=pd.DataFrame(columns=["oris","epa_unit_id","report_rows"])
    counts=out.groupby("oris",as_index=False).agg(
        distinct_epa_unit_ids=("epa_unit_id","size"),
        source_hourly_rows=("report_rows","sum"))
    population=pd.DataFrame({"oris":list(FACILITIES)})
    counts=population.merge(counts,on="oris",how="left")
    counts[["distinct_epa_unit_ids","source_hourly_rows"]]=counts[
        ["distinct_epa_unit_ids","source_hourly_rows"]].fillna(0).astype(int)
    meta={"source":"Zenodo v1 archived CAMPD 2024 Arizona hourly emissions",
          "source_url":SNAPSHOT_URL,"expected_md5":EXPECTED_MD5,
          "rows_at_target_facilities":total_selected,
          "target_facility_oris":list(FACILITIES),
          "recognized_source_columns":columns,
          "calendar_time_source_fields":[date,hour],
          "time_zone_verified":False,
          "unique_facility_unit_date_hour_verified":True,
          "gross_load_column_present":"gross_load" in optional,
          "heat_input_column_present":"heat_input" in optional,
          "record_is_source_emissions_or_operations_not_net_power":True,
          "target_eia860_gt_generators_automatically_matched":False,
          "unit_level_hourly_net_mw_verified":False,
          "weather_derating_calibrated":False,
          "missing_facility_emissions_is_not_outage":True}
    return out,counts,meta


def fetch(out):
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    path=root/"epacampd_2024_arizona_hourly_source.csv"
    digest=hashlib.md5()
    req=Request(SNAPSHOT_URL,headers={"User-Agent":"ClimateGridResilienceResearch/1.0"})
    with urlopen(req,timeout=150) as stream,path.open("wb") as dest:
        while True:
            block=stream.read(1024*1024)
            if not block:break
            digest.update(block)
            dest.write(block)
            if dest.tell()>250_000_000:
                raise ValueError("Unexpected oversized 2024 AZ archived dataset")
    if digest.hexdigest()!=EXPECTED_MD5:
        raise ValueError("Official-republished 2024 AZ snapshot checksum mismatch")
    units,summary,manifest=audit_csv(path)
    manifest["observed_md5"]=digest.hexdigest()
    manifest["downloaded_bytes"]=path.stat().st_size
    units.to_csv(root/"target_camd_2024_hourly_unit_ids.csv",index=False)
    summary.to_csv(root/"target_camd_2024_hourly_facility_coverage.csv",index=False)
    (root/"target_camd_2024_hourly_admission.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    path.unlink()
    print(summary.to_string(index=False))
    return manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    fetch(a.output)


if __name__=="__main__":
    main()
