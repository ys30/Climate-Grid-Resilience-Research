"""Extract genuine EIA-930 six-month CSV demand with hour-ending timestamps.

Convert hour-ending UTC to hour-starting PyPSA snapshots by subtracting 1h.
Only reported raw Demand (MW) is used; no imputed/adjusted substitution.
"""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path

BAS=("CISO","AZPS","BPAT","SRP")
FORMAT="%m/%d/%Y %I:%M:%S %p"

def extract(source,output,start="2024-02-01T00:00:00+00:00",hours=696):
    first=datetime.fromisoformat(start)
    if first.tzinfo is None or first.utcoffset()!=timedelta(0):
        raise ValueError("UTC-aware start required")
    expected={(first+timedelta(hours=h),ba) for h in range(hours) for ba in BAS}
    rows={}
    missing_raw=0
    with Path(source).open(newline="",encoding="utf-8-sig") as file:
        reader=csv.DictReader(file)
        required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Unexpected official six-month CSV headers")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            ending=datetime.strptime(row["UTC Time at End of Hour"].strip(),FORMAT).replace(tzinfo=timezone.utc)
            beginning=ending-timedelta(hours=1)
            key=(beginning,ba)
            if key not in expected:continue
            if key in rows:raise ValueError("Duplicate BA-hour in official CSV")
            raw=row["Demand (MW)"].strip()
            if not raw:
                missing_raw+=1
                continue
            value=float(raw)
            if not 0<=value<float("inf"):
                raise ValueError("Invalid demand MW")
            rows[key]=value
    if set(rows)!=expected:
        raise ValueError(f"Incomplete raw demand: {len(rows)}/{len(expected)}; blank raw cells={missing_raw}")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"hourly_ba_demand.csv").open("w",newline="") as file:
        writer=csv.writer(file);writer.writerow(("timestamp","ba","demand_mw"))
        for (t,ba),v in sorted(rows.items()):
            writer.writerow((t.isoformat(),ba,v))
    manifest={"rows":len(rows),"hours_per_ba":hours,"bas":list(BAS),
              "hour_ending_shift_hours":-1,"reported_raw_demand_only":True,
              "historical_calibration_certified":False}
    (out/"hourly_ba_demand_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(extract(a.csv,a.output),indent=2))
if __name__=="__main__":main()
