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
    missing_fields={(ba,mode,col):0 for ba in BAS for mode,cols in sets.items() for col in cols}
    missing_field_rows=[]
    gate_rows=[]
    missing_field_times={(ba,mode,col):set() for ba in BAS for mode,cols in sets.items() for col in cols}
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
                    for col,value in zip(cols,values):
                        if not value:
                            missing_fields[ba,mode,col]+=1
                            missing_field_times[ba,mode,col].add(t)
                            missing_field_rows.append((ba,t.isoformat(),mode,col))
                    record["missing"]+=1
                    continue
                d,g,i=map(float,values)
                if not all(-float("inf")<v<float("inf") for v in (d,g,i)):raise ValueError("Nonfinite")
                residual=g-d-i
                threshold=max(1.0,0.01*abs(d))
                gate_rows.append((ba,t.isoformat(),mode,d,g,i,residual,threshold,abs(residual)<=threshold))
                record["valid"]+=1;record["residual_mwh"]+=residual
                record["absolute_residual_mwh"]+=abs(residual)
    expected=int((end-start).total_seconds()/3600)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    coverage={ba:{"present_hours":len(times[ba]),"expected_hours":expected,"missing_hours":expected-len(times[ba])} for ba in BAS}
    all_hours={start+timedelta(hours=h) for h in range(expected)}
    with (out/"eia930_missing_hours.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","utc_hour_start","missing_type","basis","field"])
        for ba in BAS:
            for t in sorted(all_hours-times[ba]):w.writerow([ba,t.isoformat(),"absent_row","",""])
        for ba,t,mode,col in missing_field_rows:w.writerow([ba,t,"empty_field",mode,col])
    # Compress contiguous UTC gaps to make source-file boundary and reporting
    # outages visible without treating them as observations.
    gaps=[]
    for ba in BAS:
        groups=[("absent_row","","",all_hours-times[ba])]
        groups += [("empty_field",mode,col,missing_field_times[ba,mode,col])
                   for mode,cols in sets.items() for col in cols]
        for kind,mode,col,missing in groups:
            begin=previous=None
            for t in sorted(missing):
                if previous is not None and t-previous!=timedelta(hours=1):
                    gaps.append([ba,kind,mode,col,begin.isoformat(),(previous+timedelta(hours=1)).isoformat(),int((previous-begin).total_seconds()/3600)+1])
                    begin=t
                if begin is None:begin=t
                previous=t
            if previous is not None:
                gaps.append([ba,kind,mode,col,begin.isoformat(),(previous+timedelta(hours=1)).isoformat(),int((previous-begin).total_seconds()/3600)+1])
    with (out/"eia930_missing_contiguous_intervals.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","missing_type","basis","field","utc_start_inclusive","utc_end_exclusive","hours"]);w.writerows(gaps)
    print("MISSING INTERVALS (UTC; boundary convention requires source verification):")
    for item in gaps:
        if item[0] in ("BPAT","CISO") and (item[1]=="absent_row" or (item[2]=="raw" and item[3]=="Total Interchange (MW)")):
            print(",".join(map(str,item)))
    coverage["field_missing_counts"]={ba:{mode:{col:missing_fields[ba,mode,col] for col in cols} for mode,cols in sets.items()} for ba in BAS}
    (out/"eia930_hour_coverage.json").write_text(json.dumps(coverage,indent=2)+"\n")
    if any(len(times[ba])!=expected for ba in BAS) and not allow_incomplete:
        raise ValueError(f"Missing BA hour: {coverage}")
    with (out/"eia930_hourly_calibration_gate.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["ba","utc_hour_start","basis","demand_mw","net_generation_mw",
                    "total_interchange_mw","balance_residual_mw","threshold_mw",
                    "arithmetic_closure_pass","historical_calibration_certified"])
        for item in gate_rows:w.writerow([*item,False])
    byba={}
    for ba in BAS:
        matching=[r for r in gate_rows if r[0]==ba and r[2]=="raw"]
        closed=sum(bool(r[-1]) for r in matching)
        byba[ba]={"expected_hours":expected,"complete_reported_triplets":len(matching),
                  "arithmetic_closing_hours":closed,
                  "all_hours_reported":len(matching)==expected,
                  "all_hours_arithmetic_close":len(matching)==expected and closed==expected,
                  "calibration_certified":False}
    (out/"eia930_ba_calibration_gate.json").write_text(json.dumps(byba,indent=2)+"\\n")
    print("FULL-MONTH BA CALIBRATION GATE (never equate arithmetic closure with calibration):")
    print(json.dumps(byba,indent=2))
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
    p.add_argument("--allow-incomplete",action="store_true",help="Output incomplete coverage diagnostics without claiming calibration")
    a=p.parse_args();print(json.dumps(audit(a.csv,a.output,a.month,allow_incomplete=a.allow_incomplete),indent=2))
if __name__=="__main__":main()
