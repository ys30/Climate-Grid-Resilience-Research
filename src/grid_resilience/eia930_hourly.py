"""Download EIA-930 reported hourly BA demand for an explicitly bounded UTC event.

Requires EIA_API_KEY. No imputation; any incomplete BA-hour grid fails.
EIA-930 demand is observed reporting, not a calibrated generation/flow series.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import pandas as pd

ENDPOINT="https://api.eia.gov/v2/electricity/rto/region-data/data/"

def normalize(rows,bas,start,end):
    frame=pd.DataFrame(rows)
    required={"period","respondent","value"}
    if not required.issubset(frame.columns):raise ValueError("EIA-930 fields missing")
    frame=frame.rename(columns={"respondent":"ba","value":"demand_mw","period":"timestamp"})
    frame=frame[["timestamp","ba","demand_mw"]]
    frame["timestamp"]=pd.to_datetime(frame.timestamp,utc=True,errors="raise")
    frame["demand_mw"]=pd.to_numeric(frame.demand_mw,errors="coerce")
    if frame.duplicated(["ba","timestamp"]).any():raise ValueError("Duplicate EIA BA-hour")
    expected_hours=pd.date_range(start,end,freq="h",inclusive="left",tz="UTC")
    if not len(expected_hours):raise ValueError("Empty time interval")
    expected=pd.MultiIndex.from_product([expected_hours,list(bas)],names=["timestamp","ba"])
    observed=pd.MultiIndex.from_frame(frame[["timestamp","ba"]])
    if len(frame)!=len(expected) or set(observed)!=set(expected):
        raise ValueError(f"Incomplete BA-hour demand: expected {len(expected)}, got {len(frame)}")
    if frame.demand_mw.isna().any() or frame.demand_mw.le(0).any():
        raise ValueError("Null/nonpositive reported demand: no imputation")
    return frame.sort_values(["timestamp","ba"]).reset_index(drop=True)

def fetch(bas,start,end,api_key,length=5000,data_type='D'):
    if not api_key:raise ValueError("EIA_API_KEY is required")
    if data_type not in ('D','NG','TI'):raise ValueError('Unsupported EIA-930 region-data type')
    if not bas or len(set(bas))!=len(bas):raise ValueError("Unique BA identifiers required")
    st=pd.Timestamp(start);en=pd.Timestamp(end)
    if st.tzinfo is None or en.tzinfo is None:raise ValueError("Use timezone-aware UTC bounds")
    st=st.tz_convert("UTC");en=en.tz_convert("UTC")
    if en<=st:raise ValueError("End must follow start")
    # EIA API upper bound inclusive: use last requested hour.
    last=en-pd.Timedelta(hours=1)
    if last.minute or last.second or st.minute or st.second:
        raise ValueError("Whole UTC hours only")
    params=[("api_key",api_key),("frequency","hourly"),("data[0]","value"),
            ("facets[type][]",data_type),("start",st.strftime("%Y-%m-%dT%H")),
            ("end",last.strftime("%Y-%m-%dT%H")),("length",str(length)),
            ("sort[0][column]","period"),("sort[0][direction]","asc"),
            ("sort[1][column]","respondent"),("sort[1][direction]","asc")]
    params += [("facets[respondent][]",ba) for ba in bas]
    rows=[];offset=0;total=None
    while total is None or offset<total:
        url=ENDPOINT+"?"+urlencode(params+[("offset",str(offset))])
        with urlopen(Request(url,headers={"User-Agent":"climate-grid-resilience-research/0.1"}),timeout=90) as response:
            payload=json.load(response)
        data=payload.get("response",{}).get("data")
        if not isinstance(data,list):raise ValueError("EIA response lacks data array")
        total=int(payload["response"].get("total",0))
        if not data:break
        rows.extend(data);offset+=len(data)
    return normalize(rows,bas,st,en),{"response_rows":len(rows),"reported_total":total}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bas",nargs="+",required=True)
    p.add_argument("--start",required=True,help="UTC e.g. 2024-07-01T00:00:00Z")
    p.add_argument("--end",required=True,help="UTC exclusive bound")
    p.add_argument("--output",required=True)
    a=p.parse_args()
    frame,meta=fetch(a.bas,a.start,a.end,os.environ.get("EIA_API_KEY"))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out,index=False)
    manifest={"source":"EIA-930 API reported BA demand, type D",
              "type":"observed hourly demand, not historical generation or transmission capacity",
              "bas":a.bas,"start":a.start,"end_exclusive":a.end,
              "observations":len(frame),**meta,"imputation":"none"}
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
