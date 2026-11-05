"""Fetch and validate hourly EIA-930 demand through EIA API v2.

Source-scoped: one BA, one complete UTC calendar month; reject gaps/duplicates.
"""
import argparse, calendar, json, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd
from .eia930_hour_convention import hour_ending_to_start, api_hour_ending_bounds

def parse_records(records, ba, year, month):
    expected=pd.date_range(f"{year}-{month:02d}-01", periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    frame=pd.DataFrame(records)
    needed={"period","respondent","type","value"}
    if not needed.issubset(frame.columns):raise ValueError("Missing EIA-930 fields")
    frame=frame[(frame.respondent==ba)&(frame.type=="D")].copy()
    if frame.empty:raise ValueError(f"No EIA-930 demand for {ba}")
    frame["timestamp"]=hour_ending_to_start(frame.period)
    frame["demand_mw"]=pd.to_numeric(frame.value,errors="raise")
    if frame[["timestamp","demand_mw"]].isna().any().any() or frame.timestamp.duplicated().any():
        raise ValueError("Invalid/duplicate hourly EIA-930 demand")
    if (frame.demand_mw<0).any():raise ValueError("Negative demand")
    frame=frame.sort_values("timestamp")
    if not pd.DatetimeIndex(frame.timestamp).equals(expected):
        raise ValueError(f"Incomplete UTC calendar month: {len(frame)} rows, expected {len(expected)}")
    return pd.DataFrame({"timestamp":expected,"ba":ba,"demand_mw":frame.demand_mw.to_numpy()})

def fetch(ba,year,month):
    start_of_month=pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")
    start_label,end_label=api_hour_ending_bounds(
        start_of_month,start_of_month+pd.offsets.MonthBegin(1))
    start=start_label.strftime("%Y-%m-%dT%H")
    end=end_label.strftime("%Y-%m-%dT%H")
    params={"frequency":"hourly","data[0]":"value","facets[respondent][]":ba,
            "facets[type][]":"D","start":start,"end":end,"length":"5000",
            "sort[0][column]":"period","sort[0][direction]":"asc"}
    url="https://api.eia.gov/v2/electricity/rto/region-data/data/?"+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"climate-grid-resilience-research/0.1"}),timeout=120) as response:
        body=json.load(response)
    if "response" not in body or "data" not in body["response"]:raise ValueError("EIA API response missing data")
    data=body["response"]["data"]
    if int(body["response"].get("total",len(data)))!=len(data):raise ValueError("Pagination required; fail closed")
    return parse_records(data,ba,year,month),url


def from_official_balance_csv(csv_path,ba,year,month,*,permit_2024_jan_srp_first_seven_absent=False):
    """Fail-closed full UTC month from original EIA official hour-ending CSV."""
    fields={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
    source=pd.read_csv(csv_path,dtype="string")
    if not fields.issubset(source):
        raise ValueError("Official EIA930 balance CSV schema incomplete")
    g=source.loc[source["Balancing Authority"].str.strip().eq(ba),
                 ["UTC Time at End of Hour","Demand (MW)"]].copy()
    if g.empty:
        raise ValueError("No official balance CSV demand for requested BA")
    g["timestamp"]=hour_ending_to_start(pd.to_datetime(
        g["UTC Time at End of Hour"],
        format="%m/%d/%Y %I:%M:%S %p",utc=True,errors="raise"))
    g=g.loc[g.timestamp.dt.year.eq(year)&g.timestamp.dt.month.eq(month)].copy()
    g["demand_mw"]=pd.to_numeric(g["Demand (MW)"],errors="coerce")
    expected=pd.date_range(f"{year}-{month:02d}-01",
        periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    observed=pd.DatetimeIndex(g.timestamp.sort_values())
    missing=expected.difference(observed)
    extra=observed.difference(expected)
    boundary_exception=bool(
        permit_2024_jan_srp_first_seven_absent and
        ba=="SRP" and year==2024 and month==1 and
        len(g)==737 and observed.equals(expected[7:]) and
        missing.equals(expected[:7]) and len(extra)==0)
    if (g.timestamp.duplicated().any() or
        not (observed.equals(expected) or boundary_exception) or
        g.demand_mw.isna().any() or g.demand_mw.le(0).any()):
        raise ValueError(
            "Official original CSV lacks complete valid UTC model start-hours: "
            f"rows={len(g)}, expected={len(expected)}, "
            f"missing_hours={len(missing)}, extra_hours={len(extra)}, "
            f"missing_first={list(missing[:3])}, extra_first={list(extra[:3])}, "
            f"duplicate_hours={int(g.timestamp.duplicated().sum())}, "
            f"null_demand={int(g.demand_mw.isna().sum())}, "
            f"nonpositive_demand={int(g.demand_mw.le(0).sum())}")
    return g[["timestamp","demand_mw"]].assign(ba=ba)[
        ["timestamp","ba","demand_mw"]].sort_values("timestamp").reset_index(drop=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ba",required=True);p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True);p.add_argument("--output",required=True)
    p.add_argument("--official-csv",help="Original official EIA930 BALANCE six-month CSV; bypass API 403")
    p.add_argument("--permit-2024-jan-srp-first-seven-absent",action="store_true",
        help="Only for official SRP January 2024 CSV: admit 737 genuine UTC hours, never fill 7 missing boundary hours")
    a=p.parse_args()
    if a.official_csv:
        data=from_official_balance_csv(a.official_csv,a.ba,a.year,a.month,
            permit_2024_jan_srp_first_seven_absent=a.permit_2024_jan_srp_first_seven_absent)
        url="official EIA930 BALANCE CSV supplied and timestamp/checksum logged by source workflow"
    else:
        data,url=fetch(a.ba,a.year,a.month)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    data.to_csv(out/"hourly_eia930_demand.csv",index=False)
    (out/"demand_manifest.json").write_text(json.dumps({"source_url":url,"ba":a.ba,
      "year":a.year,"month":a.month,"hours":len(data),"source":"EIA-930 API region-data type D",
      "time_basis":"EIA period UTC hour-ending converted to model interval start",
      "complete_utc_month":len(data)==calendar.monthrange(a.year,a.month)[1]*24,
      "official_csv_2024_jan_srp_missing_first_7_utc_hours_admitted":bool(
          a.official_csv and a.permit_2024_jan_srp_first_seven_absent and len(data)==737),
      "unobserved_hours_imputed":False,
      "historical_calibration_certified":False},indent=2)+"\n")
    print(f"Validated {len(data)} UTC hourly demand rows for {a.ba}")
if __name__=="__main__":main()
