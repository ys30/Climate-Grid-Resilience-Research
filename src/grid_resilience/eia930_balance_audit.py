"""Audit reported EIA-930 BA energy accounting using raw hourly measures.

Definition used for this diagnostic: reported net generation minus demand minus
total interchange. Interchange sign conventions and adjustments require
independent confirmation; residual is NOT automatically a grid loss.
"""
import argparse,csv,json
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"
def audit(source,output,month="2024-02"):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)","Net Generation (MW)","Total Interchange (MW)"}
    values=defaultdict(lambda:{"demand":0.0,"generation":0.0,"interchange":0.0,"residual":0.0,"hours":0})
    seen=set()
    with Path(source).open(newline="",encoding="utf-8-sig") as file:
        reader=csv.DictReader(file)
        if not required.issubset(reader.fieldnames or []):raise ValueError("EIA-930 schema incomplete")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            key=(ba,t)
            if key in seen:raise ValueError("Duplicate BA-hour")
            seen.add(key)
            fields=[row[x].strip() for x in ("Demand (MW)","Net Generation (MW)","Total Interchange (MW)")]
            if not all(fields):raise ValueError(f"Missing raw measurement {ba} {t}")
            d,g,i=map(float,fields)
            if not all(-float("inf")<v<float("inf") for v in (d,g,i)):raise ValueError("Nonfinite value")
            if d<0:raise ValueError("Negative demand")
            item=values[ba]
            item["demand"]+=d;item["generation"]+=g;item["interchange"]+=i
            item["residual"]+=g-d-i;item["hours"]+=1
    expected=int((end-start).total_seconds()/3600)
    if any(values[ba]["hours"]!=expected for ba in BAS):
        raise ValueError("Incomplete BA hourly balance coverage")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"eia930_raw_balance_diagnostic.csv").open("w",newline="") as file:
        w=csv.writer(file)
        w.writerow(["ba","period","hours","demand_mwh","generation_mwh","total_interchange_mwh","generation_minus_demand_minus_interchange_mwh"])
        for ba in BAS:
            v=values[ba];w.writerow([ba,month,v["hours"],v["demand"],v["generation"],v["interchange"],v["residual"]])
    meta={"month":month,"hours_per_ba":expected,"comparison":"raw generation - raw demand - raw total interchange",
          "interpretation":"Diagnostic arithmetic only; sign conventions, balancing adjustments and data revisions require audit.",
          "historical_calibration_certified":False}
    (out/"eia930_raw_balance_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    p.add_argument("--month",default="2024-02")
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output,a.month),indent=2))
if __name__=="__main__":main()
