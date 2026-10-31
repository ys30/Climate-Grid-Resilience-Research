"""Join independently extracted EIA-930 hourly bilateral totals to Balance totals."""
import argparse,json
from pathlib import Path
import pandas as pd

def reconcile(balance_csv,bilateral_csv,out):
    from datetime import datetime,timedelta,timezone
    records=[]
    import csv
    with open(balance_csv,newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ba=row["Balancing Authority"]
            if ba not in ("CISO","AZPS","BPAT","SRP"):continue
            t=datetime.strptime(row["UTC Time at End of Hour"],"%m/%d/%Y %I:%M:%S %p").replace(tzinfo=timezone.utc)-timedelta(hours=1)
            if not (datetime(2024,2,1,tzinfo=timezone.utc)<=t<datetime(2024,3,1,tzinfo=timezone.utc)):continue
            raw=row["Total Interchange (MW)"].strip()
            if not raw:raise ValueError("Missing raw balance interchange")
            records.append({"ba":ba,"timestamp":t.isoformat(),"balance_interchange_mw":float(raw)})
    balance=pd.DataFrame(records)
    bilateral=pd.read_csv(bilateral_csv,dtype={"ba":str,"timestamp":str})
    keys=["ba","timestamp"]
    if balance.duplicated(keys).any() or bilateral.duplicated(keys).any():raise ValueError("Duplicate BA hour")
    merged=balance.merge(bilateral,on=keys,how="outer",validate="one_to_one",indicator=True)
    if len(merged)!=2784 or not merged["_merge"].eq("both").all():raise ValueError("Incomplete matched hourly exchange")
    merged["difference_mw"]=merged.sum_bilateral_interchange_mw-merged.balance_interchange_mw
    if not merged.difference_mw.map(lambda x:-float("inf")<x<float("inf")).all():raise ValueError("Nonfinite difference")
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    merged.drop(columns="_merge").to_csv(output/"bilateral_vs_balance_hourly.csv",index=False)
    summary=merged.groupby("ba").agg(hours=("difference_mw","size"),
       signed_difference_mwh=("difference_mw","sum"),
       absolute_difference_mwh=("difference_mw",lambda x:x.abs().sum()),
       max_absolute_difference_mw=("difference_mw",lambda x:x.abs().max()),
       nonzero_hours=("difference_mw",lambda x:int((x.abs()>1).sum()))).reset_index()
    summary.to_csv(output/"bilateral_vs_balance_summary.csv",index=False)
    result={"rows":len(merged),"historical_calibration_certified":False,
            "definition":"sum directed bilateral interchange minus reported BA total interchange",
            "interpretation":"Reporting consistency only, not physical line capacities"}
    (output/"bilateral_vs_balance_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--balance",required=True);p.add_argument("--bilateral",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(reconcile(a.balance,a.bilateral,a.output),indent=2))
if __name__=="__main__":main()
