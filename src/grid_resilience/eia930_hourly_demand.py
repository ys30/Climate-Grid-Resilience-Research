"""Normalize EIA-930 hourly BA demand data to PyPSA inputs.

Consumes EIA API v2 region-data JSON already downloaded independently.
No absent/invalid demand point is imputed and no local-hourly DST coercion is
allowed. Official API values are hourly MWh, numerically MW for one-hour bins.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

BAS=("CISO","AZPS","BPAT","SRP")

def normalize(api_json, output, start, end, bas=BAS):
    doc=json.loads(Path(api_json).read_text())
    response=doc.get("response",{})
    rows=response.get("data")
    if not isinstance(rows,list) or not rows:
        raise ValueError("No EIA-930 API records")
    total=int(response.get("total",len(rows)))
    if total!=len(rows):
        raise ValueError(f"Paginated EIA response incomplete: {len(rows)} of {total}")
    frame=pd.DataFrame(rows)
    needed={"period","respondent","type","value"}
    if not needed.issubset(frame):
        raise ValueError("Missing EIA region-data fields")
    if not frame.type.astype(str).eq("D").all():
        raise ValueError("Only actual demand type D permitted")
    if frame[list(needed)].isna().any().any():
        raise ValueError("Null official demand record")
    if not set(frame.respondent).issubset(set(bas)):
        raise ValueError("Unexpected BA respondent")
    frame["timestamp"]=pd.to_datetime(frame.period,utc=True,errors="raise")
    frame["demand_mw"]=pd.to_numeric(frame.value,errors="raise")
    if not frame.demand_mw.map(lambda v:0<=float(v)<float("inf")).all():
        raise ValueError("Nonfinite/negative reported demand")
    if frame.duplicated(["timestamp","respondent"]).any():
        raise ValueError("Duplicate BA-hour demand")
    expected_times=pd.date_range(start=start,end=end,freq="h",tz="UTC")
    expected=pd.MultiIndex.from_product([expected_times,list(bas)],names=["timestamp","respondent"])
    actual=pd.MultiIndex.from_frame(frame[["timestamp","respondent"]])
    if len(expected_times)<1 or set(actual)!=set(expected):
        raise ValueError(f"Incomplete BA-hour coverage: observed {len(actual)}, expected {len(expected)}")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    normalized=frame.rename(columns={"respondent":"ba"})[["timestamp","ba","demand_mw"]]
    normalized.sort_values(["timestamp","ba"]).to_csv(out/"hourly_ba_demand.csv",index=False)
    manifest={"status":"schema_and_coverage_verified_not_source_authenticated",
              "bas":list(bas),"hours_per_ba":len(expected_times),
              "records":len(normalized),"original_api_rows":len(rows),
              "historical_calibration_certified":False,
              "limitations":"UTC hourly labels must be verified against EIA's interval conventions; independently verify source URL/revision and applicability to modeled BA boundaries."}
    (out/"hourly_ba_demand_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--start",required=True)
    p.add_argument("--end",required=True)
    a=p.parse_args()
    print(json.dumps(normalize(a.json,a.output,a.start,a.end),indent=2))
if __name__=="__main__":main()
