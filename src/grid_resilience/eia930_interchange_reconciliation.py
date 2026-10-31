"""Compare EIA-930 net interchange against implied generation-minus-demand.

This is a diagnostic for reporting discrepancies, never a substitute for
observed transfers or calibrated link ratings.
"""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path

BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"

def audit(source,output,month="2024-02"):
    begin=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=begin.replace(year=begin.year+1,month=1) if begin.month==12 else begin.replace(month=begin.month+1)
    sums={ba:{"reported":0.0,"implied":0.0,"abs_discrepancy":0.0,"hours":0} for ba in BAS}
    with Path(source).open(newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        needed={"Balancing Authority","UTC Time at End of Hour","Demand (MW)","Net Generation (MW)","Total Interchange (MW)"}
        if not needed.issubset(r.fieldnames or []):raise ValueError("Missing EIA fields")
        seen=set()
        for row in r:
            ba=row["Balancing Authority"].strip()
            if ba not in sums:continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not begin<=t<end:continue
            if (ba,t) in seen:raise ValueError("Duplicate BA-hour")
            seen.add((ba,t))
            d,g,i=[float(row[x]) for x in ("Demand (MW)","Net Generation (MW)","Total Interchange (MW)")]
            if not all(-float("inf")<v<float("inf") for v in (d,g,i)):raise ValueError("Nonfinite")
            implied=g-d
            z=sums[ba];z["reported"]+=i;z["implied"]+=implied
            z["abs_discrepancy"]+=abs(implied-i);z["hours"]+=1
    expected=int((end-begin).total_seconds()/3600)
    if any(v["hours"]!=expected for v in sums.values()):raise ValueError("Incomplete coverage")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"interchange_reconciliation.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","period","reported_interchange_mwh","generation_minus_demand_mwh","discrepancy_mwh","absolute_hourly_discrepancy_mwh"])
        for ba,z in sums.items():
            w.writerow([ba,month,z["reported"],z["implied"],z["implied"]-z["reported"],z["abs_discrepancy"]])
    manifest={"period":month,"hours_per_ba":expected,"scope":"accounting reconciliation, not inferred physical transfers","historical_calibration_certified":False}
    (out/"interchange_reconciliation_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True)
    p.add_argument("--output",required=True);p.add_argument("--month",default="2024-02")
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output,a.month),indent=2))
if __name__=="__main__":main()
