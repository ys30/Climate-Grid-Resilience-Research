"""Reconcile EIA-930 bilateral counterparties with raw BA total interchange.

Aggregation preserves reporting-direction conventions and does not assume
reciprocity or treat interchange as line thermal ratings.
"""
import argparse,csv,json
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
BAS=("CISO","AZPS","BPAT","SRP")
FMT="%m/%d/%Y %I:%M:%S %p"
def run(path,output,month="2024-02"):
    start=datetime.strptime(month,"%Y-%m").replace(tzinfo=timezone.utc)
    end=start.replace(year=start.year+1,month=1) if start.month==12 else start.replace(month=start.month+1)
    aggregate=defaultdict(float);counterparts=defaultdict(set);count=defaultdict(int)
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        r=csv.DictReader(f)
        required={"Balancing Authority","Directly Interconnected Balancing Authority","Interchange (MW)","UTC Time at End of Hour"}
        if not required.issubset(r.fieldnames or []):raise ValueError("Missing interchange columns")
        for record in r:
            ba=record["Balancing Authority"].strip()
            if ba not in BAS:continue
            hour=datetime.strptime(record["UTC Time at End of Hour"],FMT).replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not start<=hour<end:continue
            partner=record["Directly Interconnected Balancing Authority"].strip()
            if not partner:raise ValueError("Empty counterparty")
            raw=record["Interchange (MW)"].strip()
            if not raw:raise ValueError("Missing hourly interchange")
            v=float(raw)
            if not -float("inf")<v<float("inf"):raise ValueError("Nonfinite interchange")
            key=(ba,hour)
            if partner in counterparts[key]:raise ValueError("Repeated counterpart for BA/hour")
            counterparts[key].add(partner);aggregate[key]+=v;count[ba]+=1
    expected=int((end-start).total_seconds()/3600)
    hours={ba:sum(k[0]==ba for k in aggregate) for ba in BAS}
    if any(hours[ba]!=expected for ba in BAS):raise ValueError(f"Missing bilateral BA-hours: {hours}")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"bilateral_hourly_totals.csv").open("w",newline="") as f:
        w=csv.writer(f);w.writerow(["ba","timestamp","sum_bilateral_interchange_mw","counterparty_count"])
        for (ba,hour),v in sorted(aggregate.items()):
            w.writerow((ba,hour.isoformat(),v,len(counterparts[ba,hour])))
    report={"month":month,"hours_by_ba":hours,"records_by_ba":dict(count),
            "interpretation":"Reported directed bilateral interchange; not independently validated transmission capacity.",
            "historical_calibration_certified":False}
    (out/"bilateral_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--csv",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(run(a.csv,a.output),indent=2))
if __name__=="__main__":main()
