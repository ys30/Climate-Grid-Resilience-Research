"""Hourly EIA-930 reported net generation versus sum of its fuel columns."""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"
FUELS=("Coal","Natural Gas","Nuclear","All Petroleum Products",
       "Hydropower and Pumped Storage","Solar","Wind","Other Fuel Sources","Unknown Fuel Sources")
def audit(path,out,month="2024-02"):
    first=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    last=first.replace(year=first.year+1,month=1) if first.month==12 else first.replace(month=first.month+1)
    sums={b:{"hours":0,"hours_with_any_blank_fuel":0,"signed_delta_mwh":0.0,
             "abs_delta_mwh":0.0,"max_abs_delta_mw":0.0} for b in BAS}
    seen=set()
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        fuelcols=["Net Generation (MW) from "+x for x in FUELS]
        needed=set(fuelcols+["Balancing Authority","UTC Time at End of Hour","Net Generation (MW)"])
        if not needed.issubset(reader.fieldnames or []):raise ValueError("Missing fuel columns")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in sums:continue
            hour=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not first<=hour<last:continue
            if (ba,hour) in seen:raise ValueError("Duplicate BA-hour")
            seen.add((ba,hour))
            raw=row["Net Generation (MW)"].strip()
            if not raw:raise ValueError("Missing net generation")
            source_values=[row[k].strip() for k in fuelcols]
            record=sums[ba];record["hours"]+=1
            if any(not x for x in source_values):
                record["hours_with_any_blank_fuel"]+=1
                # Incomplete fuel decomposition must not be treated as zeros.
                continue
            values=[float(raw)]+[float(x) for x in source_values]
            if not all(-float("inf")<v<float("inf") for v in values):
                raise ValueError("Nonfinite generation")
            delta=values[0]-sum(values[1:])
            record["signed_delta_mwh"]+=delta
            record["abs_delta_mwh"]+=abs(delta)
            record["max_abs_delta_mw"]=max(record["max_abs_delta_mw"],abs(delta))
    expected=int((last-first).total_seconds()/3600)
    if any(sums[b]["hours"]!=expected for b in BAS):raise ValueError("Incomplete BA-hour coverage")
    result={"month":month,"hours":expected,"by_ba":sums,
            "fuel_comparison_is_complete_only_when_no_blank_fuels":True,
            "historical_calibration_certified":False}
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    (output/"eia930_fuel_generation_decomposition.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output),indent=2))
if __name__=="__main__":main()
