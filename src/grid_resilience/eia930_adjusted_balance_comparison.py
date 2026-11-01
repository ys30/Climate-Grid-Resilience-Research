"""Compare EIA-930 raw versus adjusted BA balance; preserve provenance."""
import argparse,csv,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"
def audit(source,output,month="2024-02",allow_incomplete=False):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    sets={"raw":("Demand (MW)","Net Generation (MW)","Total Interchange (MW)"),
          "adjusted":("Demand (MW) (Adjusted)","Net Generation (MW) (Adjusted)","Total Interchange (MW) (Adjusted)")}
    totals={(ba,mode):{"valid":0,"missing":0,"residual_mwh":0.0,"absolute_residual_mwh":0.0}
            for ba in BAS for mode in sets}
    times={ba:set() for ba in BAS}
    with Path(source).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not set(sum((list(x) for x in sets.values()),[])+["UTC Time at End of Hour","Balancing Authority"]).issubset(reader.fieldnames or []):
            raise ValueError("Missing comparison columns")
        for row in reader:
            ba=row["Balancing Authority"].strip()
            if ba not in BAS:continue
            t=datetime.strptime(row["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=t<end:continue
            if t in times[ba]:raise ValueError("Duplicate BA hour")
            times[ba].add(t)
            for mode,cols in sets.items():
                record=totals[ba,mode]
                values=[row[c].strip() for c in cols]
                if not all(values):
                    record["missing"]+=1
                    continue
                d,g,i=map(float,values)
                if not all(-float("inf")<v<float("inf") for v in (d,g,i)):raise ValueError("Nonfinite")
                residual=g-d-i
                record["valid"]+=1;record["residual_mwh"]+=residual
                record["absolute_residual_mwh"]+=abs(residual)
    expected=int((end-start).total_seconds()/3600)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    coverage={ba:{"present_hours":len(times[ba]),"expected_hours":expected,"missing_hours":expected-len(times[ba])} for ba in BAS}
    (out/"eia930_hour_coverage.json").write_text(json.dumps(coverage,indent=2)+"\\n")
    if any(len(times[ba])!=expected for ba in BAS) and not allow_incomplete:
        raise ValueError(f"Missing BA hour: {coverage}")
    with (out/"eia930_raw_vs_adjusted_balance.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","basis","valid_hours","missing_hours","signed_residual_mwh","absolute_residual_mwh"])
        for ba in BAS:
            for mode in sets:
                a=totals[ba,mode]
                w.writerow([ba,mode,a["valid"],a["missing"],a["residual_mwh"],a["absolute_residual_mwh"]])
    result={"period":month,"hours_per_ba":expected,"coverage":coverage,
            "complete_ba_hour_coverage":all(len(times[ba])==expected for ba in BAS),
            "incomplete_comparison_not_calibrated":True,"raw_adjusted_arithmetic_only":True,
            "adjusted_not_assumed_to_be_verified_physical_flows":True,
            "historical_calibration_certified":False}
    (out/"eia930_raw_vs_adjusted_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True)
    p.add_argument("--output",required=True);p.add_argument("--month",default="2024-02")
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output,a.month),indent=2))
if __name__=="__main__":main()
