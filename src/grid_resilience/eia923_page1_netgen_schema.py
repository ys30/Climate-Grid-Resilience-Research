"""Probe the *entire* official Page 1 header for monthly HY Netgen fields.

A diagnostic only: never infer MWh from fuel quantity or gross generation.
"""
import argparse, io, json, zipfile
from pathlib import Path
from openpyxl import load_workbook

MONTHS=("January","February","March","April","May","June","July","August","September","October","November","December")
def probe(archive,output):
    with zipfile.ZipFile(archive) as z:
        members=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(members)!=1: raise ValueError("Expected one schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(members[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            headings=list(next(ws.iter_rows(min_row=6,max_row=6,values_only=True)))
        finally: wb.close()
    norm=[" ".join(str(v or "").split()).lower() for v in headings]
    fields=[{"column_1based":i+1,"header":str(value)} for i,value in enumerate(headings)
            if value is not None and any(w in norm[i] for w in ("netgen","net generation","grossgen","gross generation","balancing authority","prime mover"))]
    net=[]
    for month in MONTHS:
        hits=[i for i,v in enumerate(norm) if v in (f"netgen {month.lower()}",f"net generation {month.lower()}",f"net generation (mwh) {month.lower()}")]
        if len(hits)!=1:
            net.append({"month":month,"status":"missing_or_ambiguous","matching_columns":[i+1 for i in hits]})
        else:
            net.append({"month":month,"status":"verified_header","column_1based":hits[0]+1})
    report={"sheet":"Page 1 Generation and Fuel Data","total_columns":len(headings),
            "generation_and_key_fields":fields,"monthly_net_generation_columns":net,
            "twelve_month_netgen_headers_verified":all(x["status"]=="verified_header" for x in net),
            "actual_hy_mwh_extracted":False,"historical_calibration_certified":False}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(probe(a.archive,a.output),indent=2))
if __name__=="__main__":main()
