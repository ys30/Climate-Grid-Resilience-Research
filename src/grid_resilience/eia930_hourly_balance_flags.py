"""Hourly EIA-930 balance diagnostics; flags only, no inferred physical losses."""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS={"CISO","AZPS","BPAT","SRP"}
FMT="%m/%d/%Y %I:%M:%S %p"
def audit(source,output,month="2024-02"):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    records=[];seen=set()
    with Path(source).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        cols=("Demand (MW)","Net Generation (MW)","Total Interchange (MW)")
        if not set(cols+("UTC Time at End of Hour","Balancing Authority")).issubset(reader.fieldnames or []):
            raise ValueError("Missing EIA-930 columns")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(row["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            key=(ba,t)
            if key in seen:raise ValueError("Duplicate BA-hour")
            seen.add(key)
            if any(not row[x].strip() for x in cols):raise ValueError("Missing raw hourly datum")
            d,g,i=map(lambda x:float(row[x]),cols)
            if any(not -float("inf")<v<float("inf") for v in (d,g,i)):raise ValueError("Nonfinite")
            residual=g-d-i
            records.append((ba,t.isoformat(),d,g,i,residual,abs(residual),int(abs(residual)>max(1,0.01*d))))
    expected=int((end-start).total_seconds()/3600)
    if len(records)!=expected*len(BAS):raise ValueError("Incomplete hourly BA coverage")
    with (out/"eia930_hourly_balance_flags.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","utc_hour_start","demand_mw","generation_mw","interchange_mw","residual_mw","absolute_residual_mw","over_1pct_demand_or_1mw"])
        w.writerows(sorted(records))
    stats={}
    for ba in sorted(BAS):
        a=[r for r in records if r[0]==ba]
        stats[ba]={"nonclosing_hours_over_threshold":sum(r[7] for r in a),
                   "max_absolute_residual_mw":max(r[6] for r in a),
                   "sum_absolute_residual_mwh":sum(r[6] for r in a),
                   "signed_residual_mwh":sum(r[5] for r in a)}
    result={"month":month,"hours_per_ba":expected,"ba_diagnostics":stats,
            "criterion":"absolute residual > max(1 MW,1% of hourly demand)",
            "reported_interchange_is_not_verified_link_flow":True,
            "historical_calibration_certified":False}
    (out/"eia930_hourly_balance_flags.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True)
    p.add_argument("--output",required=True);p.add_argument("--month",default="2024-02")
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output,a.month),indent=2))
if __name__=="__main__":main()
