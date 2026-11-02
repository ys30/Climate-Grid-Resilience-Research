"""Fetch and validate hourly EIA-930 demand through EIA API v2.

Source-scoped: one BA, one complete UTC calendar month; reject gaps/duplicates.
"""
import argparse, calendar, json, urllib.parse, urllib.request
from pathlib import Path
import pandas as pd

def parse_records(records, ba, year, month):
    expected=pd.date_range(f"{year}-{month:02d}-01", periods=calendar.monthrange(year,month)[1]*24,freq="h",tz="UTC")
    frame=pd.DataFrame(records)
    needed={"period","respondent","type","value"}
    if not needed.issubset(frame.columns):raise ValueError("Missing EIA-930 fields")
    frame=frame[(frame.respondent==ba)&(frame.type=="D")].copy()
    if frame.empty:raise ValueError(f"No EIA-930 demand for {ba}")
    frame["timestamp"]=pd.to_datetime(frame.period,utc=True,errors="raise")
    frame["demand_mw"]=pd.to_numeric(frame.value,errors="raise")
    if frame[["timestamp","demand_mw"]].isna().any().any() or frame.timestamp.duplicated().any():
        raise ValueError("Invalid/duplicate hourly EIA-930 demand")
    if (frame.demand_mw<0).any():raise ValueError("Negative demand")
    frame=frame.sort_values("timestamp")
    if not pd.DatetimeIndex(frame.timestamp).equals(expected):
        raise ValueError(f"Incomplete UTC calendar month: {len(frame)} rows, expected {len(expected)}")
    return pd.DataFrame({"timestamp":expected,"ba":ba,"demand_mw":frame.demand_mw.to_numpy()})

def fetch(ba,year,month):
    start=f"{year}-{month:02d}-01T00"
    end=(pd.Timestamp(f"{year}-{month:02d}-01",tz="UTC")+pd.offsets.MonthBegin(1)).strftime("%Y-%m-%dT00")
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

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ba",required=True);p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    data,url=fetch(a.ba,a.year,a.month)
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    data.to_csv(out/"hourly_eia930_demand.csv",index=False)
    (out/"demand_manifest.json").write_text(json.dumps({"source_url":url,"ba":a.ba,
      "year":a.year,"month":a.month,"hours":len(data),"source":"EIA-930 API region-data type D",
      "historical_calibration_certified":False},indent=2)+"\n")
    print(f"Validated {len(data)} UTC hourly demand rows for {a.ba}")
if __name__=="__main__":main()
