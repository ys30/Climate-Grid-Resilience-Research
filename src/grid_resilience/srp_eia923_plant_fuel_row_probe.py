"""Inspect an EIA-923 Page 1 plant's original fuel/consumption columns.

Preserves original worksheet headers and source-row observations without
assuming that net generation can be allocated to individual generators.
"""
import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

from openpyxl import load_workbook


def inspect(archive, *, plant="6177", ba="SRP", year=2024):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist()
               if "Schedules_2_3_4_5" in n and n.lower().endswith(".xlsx")]
        if len(names)!=1:
            raise ValueError("Expected one official EIA-923 schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            headers=next(ws.iter_rows(min_row=6,max_row=6,values_only=True))
            norm=lambda v:" ".join(str(v or "").split())
            expected={0:"Plant Id",13:"Reported Prime Mover",
                      14:"Reported Fuel Type Code",16:"Balancing Authority Code",
                      79:"Netgen January",96:"YEAR"}
            for idx,label in expected.items():
                if idx>=len(headers) or norm(headers[idx])!=label:
                    raise ValueError(f"Unexpected Page1 header at {idx}: {headers[idx] if idx<len(headers) else None}")
            fields=[(i,norm(h)) for i,h in enumerate(headers) if norm(h)
                    and (("fuel" in norm(h).lower()) or
                         ("consumption" in norm(h).lower()) or
                         ("quantity" in norm(h).lower()) or
                         ("heat content" in norm(h).lower()))]
            # Keep every named column through the reported monthly net generation
            # block so the original reporting layout can be reviewed directly.
            selected=[(i,norm(h)) for i,h in enumerate(headers[:91]) if norm(h)]
            output=[]
            for rownum,row in enumerate(ws.iter_rows(min_row=7,values_only=True),start=7):
                if not row or row[0] is None:continue
                pid=str(row[0]).strip().lstrip("0") or "0"
                if pid!=(str(plant).strip().lstrip("0") or "0"):continue
                if str(row[16] or "").strip()!=ba:continue
                if int(row[96])!=year:raise ValueError("Unexpected source year")
                output.append({
                    "source_sheet_row":rownum,
                    "plant_id":pid,
                    "prime_mover":str(row[13] or "").strip(),
                    "reported_fuel":str(row[14] or "").strip(),
                    "columns":[{"column_index_1based":i+1,"header":name,
                                "original_value":row[i] if i<len(row) else None}
                               for i,name in selected],
                })
        finally:
            wb.close()
    if not output:raise ValueError("No matching official plant BA records")
    return {"source_workbook":names[0],"sheet":"Page 1 Generation and Fuel Data",
            "plant_id":str(plant),"reported_ba":ba,"source_year":year,
            "fuel_or_consumption_header_fields":[{"column_index_1based":i+1,"name":name} for i,name in fields],
            "plant_source_rows":output,"source_row_count":len(output),
            "generator_allocation_certified":False,
            "fuel_consumption_interpretation_certified":False,
            "historical_calibration_certified":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--plant",default="6177")
    p.add_argument("--ba",default="SRP")
    args=p.parse_args()
    result=inspect(args.archive,plant=args.plant,ba=args.ba)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    (out/"eia923_selected_plant_full_source_rows.json").write_text(
        json.dumps(result,indent=2,default=str)+"\n")
    print(json.dumps({"plant":result["plant_id"],"source_rows":result["source_row_count"],
                      "source_fuel_consumption_fields":result["fuel_or_consumption_header_fields"],
                      "interpretation_certified":False},indent=2))


if __name__=="__main__":
    main()
