"""Source-certified Grand Coulee reservoir elevation July 2024 (USGS + USBR).

USGS NWIS daily-values RDB file includes meta-comments, header and
column-width specification row. 62614 reservoir water surface elevation
has datum NGVD29. USBR POMTS monthly forebay is a different observation
frequency and may not share identical vertical datum.
"""
from pathlib import Path
import argparse,csv,io,json,re
import pandas as pd

def usgs_daily(path):
    raw=Path(path).read_text(encoding="utf-8-sig")
    lines=[x for x in raw.splitlines() if x.strip() and not x.startswith("#")]
    if len(lines)<3:raise ValueError("USGS NWIS source no observed daily records")
    header=lines[0].split("\t")
    if "site_no" not in header or "datetime" not in header:
        raise ValueError(f"USGS NWIS RDB source header absent: {header}")
    numeric=[k for k in header if re.search(r"62614_32400$",k)]
    if len(numeric)!=1:
        raise ValueError(f"USGS daily 2400-hour observation 62614 not uniquely present: {header}")
    if lines[1].split("\t")[0].endswith("s") is False:
        raise ValueError("USGS RDB type specification row absent")
    data="\n".join([lines[0]]+lines[2:])+"\n"
    x=pd.read_csv(io.StringIO(data),sep="\t",dtype="string")
    if "site_no" not in x or not x.site_no.eq("12436000").all():
        raise ValueError("USGS station identity not 12436000")
    x["date"]=pd.to_datetime(x["datetime"],errors="raise")
    x["lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"]=pd.to_numeric(
        x[numeric[0]],errors="coerce")
    q=x.loc[x.date.dt.strftime("%Y-%m").eq("2024-07")].copy()
    expected=pd.date_range("2024-07-01",periods=31,freq="D")
    if len(q)!=31 or q.date.duplicated().any() or not pd.DatetimeIndex(q.date.sort_values()).equals(expected):
        raise ValueError(f"USGS source missing July 31-day mean elevations, n={len(q)}")
    if q.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29.isna().any():
        raise ValueError("USGS daily 2400-hour observation lake levels missing, not imputed")
    if not q.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29.between(1200,1320).all():
        raise ValueError("USGS lake levels outside physically plausible original feet range")
    keep=["date","lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29"]
    q=q[keep].sort_values("date")
    return q

def usbr_month(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.reader(f))
    section=False;measure=[]
    for r in rows:
        if r and r[0].strip()=="#SERIES DATA#":
            section=True;continue
        if not section or len(r)<7 or r[0].strip()!="Grand Coulee Power Plant":
            continue
        if (r[1].strip()!="End of Month Forebay Elevation" or
            r[3].strip()!="ft" or r[4].strip()!="monthly" or
            r[5].strip()!="instant"):
            raise ValueError("Invalid USBR POMTS forebay source unit/frequency")
        dt=pd.Timestamp(r[6]);v=float(r[2])
        if dt.year==2024 and dt.month==7:
            if dt.day!=1:raise ValueError("Expected RISE first-of-month encoding")
            if len(r)<8 or "end of month" not in r[7].lower():
                raise ValueError("RISE original footnote does not certify month-end semantics")
            measure.append(v)
    if not measure or max(measure)-min(measure)>1e-8:
        raise ValueError("USBR monthly July forebay missing or duplicate conflicting")
    return float(measure[0]),len(measure)

def admit(usgs,usbr):
    df=usgs_daily(usgs)
    monthly,raw_rows=usbr_month(usbr)
    m={
      "USGS_12436000_2024_07_daily_2400_observed_observations":len(df),
      "USGS_daily_elevation_datum":"NGVD29",\n      "USGS_statistic_code":"32400",\n      "USGS_statistic_interpretation":"OBSERVATION AT 2400, not daily mean",
      "USGS_2024_07_daily_2400_observed_min_ft":float(df.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29.min()),
      "USGS_2024_07_daily_2400_observed_max_ft":float(df.lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29.max()),
      "USGS_2024_07_01_daily_2400_observed_ft":float(df.iloc[0].lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29),
      "USGS_2024_07_31_daily_2400_observed_ft":float(df.iloc[-1].lake_roosevelt_daily_2400_observed_elevation_ft_ngvd29),
      "USBR_5253_2024_07_monthly_Grand_Coulee_forebay_ft":monthly,
      "USBR_monthly_july_raw_duplicate_row_count":raw_rows,
      "USBR_5253_first_day_timestamp_means_month_end":True,
      "USGS_daily_2400_observed_is_same_as_USBR_month_end_instant":False,
      "USGS_and_USBR_vertical_datum_interoperability_verified":False,
      "direct_bank_lake_minus_roosevelt_daily_head_m_permitted":False,
      "pump_station_effective_net_head_verified":False,
      "pumped_storage_electric_energy_MWh_verified":False,
      "original_PyPSA_storage_hours_recalibrated":False
    }
    return df,m

def main():
    p=argparse.ArgumentParser()
    for a in ("usgs-daily","usbr-monthly","output"):p.add_argument("--"+a,required=True)
    a=p.parse_args()
    x,m=admit(a.usgs_daily,a.usbr_monthly)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    x.to_csv(out/"lake_roosevelt_usgs_2024_july_31_daily_2400_observed_ngvd29_elevation.csv",index=False)
    (out/"lake_roosevelt_july2024_forebay_elevation_source_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("ORIGINAL USGS 12436000 ROOSEVELT 2024 JULY DAILY SOURCE VERIFIED")
    print(json.dumps(m,indent=2))
if __name__=="__main__":main()
