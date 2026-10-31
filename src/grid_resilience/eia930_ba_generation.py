"""Audit whether EIA-930 hourly BA generation is suitable as observed monthly totals.

EIA-930 reports BA-level net generation; this is not interchangeable with a
partial-fleet EIA-923 generator inventory. Hour-ending times become hour starts.
"""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"
def aggregate(path, output, month="2024-02"):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=(start.replace(year=start.year+1,month=1) if start.month==12
         else start.replace(month=start.month+1))
    total={ba:0.0 for ba in BAS};counts={ba:0 for ba in BAS}
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        required={"Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"}
        if not required.issubset(reader.fieldnames or []):raise ValueError("Missing official EIA-930 columns")
        seen=set()
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            key=(ba,t)
            if key in seen:raise ValueError("Duplicate BA hourly generation")
            seen.add(key)
            raw=row["Net Generation (MW)"].strip()
            if not raw:raise ValueError(f"Missing raw BA generation: {ba} {t}")
            value=float(raw)
            if not -float("inf")<value<float("inf"):raise ValueError("Nonfinite generation")
            total[ba]+=value
            counts[ba]+=1
    expected=int((end-start).total_seconds()/3600)
    if any(counts[ba]!=expected for ba in BAS):
        raise ValueError(f"Incomplete hourly generation: {counts}, expected {expected}")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"eia930_monthly_ba_generation.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","period","net_generation_mwh"])
        for ba in BAS:w.writerow([ba,month,round(total[ba],6)])
    result={"month":month,"hours_per_ba":expected,"rows":sum(counts.values()),
            "measurement":"EIA-930 raw BA-level net generation, not EIA-923 partial-fleet generator totals",
            "historical_calibration_certified":False}
    (out/"eia930_ba_generation_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True)
    p.add_argument("--output",required=True);p.add_argument("--month",default="2024-02")
    a=p.parse_args();print(json.dumps(aggregate(a.csv,a.output,a.month),indent=2))
if __name__=="__main__":main()
