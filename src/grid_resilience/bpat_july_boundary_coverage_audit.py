"""Audit calendar-boundary gaps in BPAT EIA-930 observations without interpolation."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(observed,weather,output):
    o=pd.read_csv(observed);w=pd.read_csv(weather)
    ot=pd.to_datetime(o.timestamp,utc=True);wt=pd.to_datetime(w.timestamp,utc=True)
    if ot.duplicated().any() or wt.duplicated().any():raise ValueError("Duplicate UTC hours")
    if len(wt)!=744 or wt.min()!=pd.Timestamp("2024-07-01T00:00:00Z") or wt.max()!=pd.Timestamp("2024-07-31T23:00:00Z"):
        raise ValueError("Weather July UTC coverage incomplete")
    missing=sorted(set(wt)-set(ot))
    if set(ot)-set(wt):raise ValueError("Observation outside weather grid")
    gaps=[t.isoformat() for t in missing]
    first=wt.min()
    boundary=all(t==first+pd.Timedelta(hours=i) for i,t in enumerate(missing))
    summary={"expected_weather_hours":744,"matched_observed_hours":len(ot),"missing_hours":len(missing),
      "missing_timestamp_utc":gaps,"all_missing_at_start_of_month":bool(boundary),
      "first_observed_utc":ot.min().isoformat(),"last_observed_utc":ot.max().isoformat(),
      "missing_hours_interpolated":False,
      "archive_boundary_cause_confirmed":False,
      "interpretation":"Contiguous UTC month-start missing timestamps identified; attribution to archive boundary requires separate source cross-check."}
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"bpat_july_boundary_coverage_audit.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary
def main():
    p=argparse.ArgumentParser()
    for name in ("observed","weather","output"):p.add_argument("--"+name,required=True)
    a=p.parse_args();print(json.dumps(audit(a.observed,a.weather,a.output),indent=2))
if __name__=="__main__":main()
