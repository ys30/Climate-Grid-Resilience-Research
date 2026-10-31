"""Audit per-category EIA-930 fuel reporting, without imputing blank cells."""
import argparse,csv,json
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
from .eia930_fuel_decomposition import BAS,FUELS,FMT
def profile(source,output,month="2024-02"):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    counts=defaultdict(lambda:{"reported_hours":0,"blank_hours":0,"reported_zero_hours":0,"signed_generation_mwh_reported_hours_only":0.0})
    seen=set()
    with Path(source).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        columns={fuel:"Net Generation (MW) from "+fuel for fuel in FUELS}
        if not set(columns.values()).issubset(reader.fieldnames or []):raise ValueError("Missing EIA fuel columns")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            time=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=time<end:continue
            if (ba,time) in seen:raise ValueError("Duplicate BA-hour")
            seen.add((ba,time))
            for fuel,col in columns.items():
                item=counts[ba,fuel]
                raw=row[col].strip()
                if not raw:
                    item["blank_hours"]+=1
                    continue
                value=float(raw)
                if not -float("inf")<value<float("inf"):raise ValueError("Nonfinite fuel generation")
                item["reported_hours"]+=1
                item["reported_zero_hours"]+=int(value==0)
                item["signed_generation_mwh_reported_hours_only"]+=value
    hours=int((end-start).total_seconds()/3600)
    if len(seen)!=hours*len(BAS):raise ValueError("Incomplete BA-hour matrix")
    rows=[]
    for ba in BAS:
        for fuel in FUELS:
            row={"ba":ba,"fuel":fuel,**counts[ba,fuel]}
            if row["reported_hours"]+row["blank_hours"]!=hours:raise AssertionError("Coverage mismatch")
            row["coverage_fraction"]=row["reported_hours"]/hours
            if row["reported_hours"]==0:row["signed_generation_mwh_reported_hours_only"]=None
            rows.append(row)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    import csv as csv_module
    with (out/"eia930_fuel_reporting_coverage.csv").open("w",newline="") as f:
        writer=csv_module.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    result={"month":month,"hours_per_ba":hours,"fuel_groups":len(rows),
            "fully_reported_groups":sum(r["reported_hours"]==hours for r in rows),
            "entirely_blank_groups":sum(r["reported_hours"]==0 for r in rows),
            "blank_is_not_zero":True,"historical_calibration_certified":False}
    (out/"eia930_fuel_reporting_coverage_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(profile(a.csv,a.output),indent=2))
if __name__=="__main__":main()
