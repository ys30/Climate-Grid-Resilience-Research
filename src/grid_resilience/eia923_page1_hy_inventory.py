"""Inventory conventional hydro plant/source rows from EIA-923 Page 1.

The fuel/physical-quantity fields are NOT converted to electricity MWh.
"""
import argparse
import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from openpyxl import load_workbook

BAS=("AZPS","BPAT","CISO","SRP")
def inventory(archive, output):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names)!=1: raise ValueError("Expected exactly one official schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            head=[" ".join(str(v or "").split()) for v in next(ws.iter_rows(min_row=6,max_row=6,values_only=True))]
            for i,expected in {0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",16:"Balancing Authority Code"}.items():
                if head[i]!=expected:raise ValueError(f"Unexpected Page 1 header {i+1}: {head[i]!r}")
            rows=[]
            for i,row in enumerate(ws.iter_rows(min_row=7,values_only=True),start=7):
                if not row or row[0] is None:continue
                code=str(row[13] or "").strip()
                ba=str(row[16] or "").strip()
                if code!="HY" or ba not in BAS:continue
                plant_id=str(row[0]).strip()
                fuel=str(row[14] or "").strip()
                if not plant_id or not fuel:raise ValueError(f"Missing plant/fuel on row {i}")
                rows.append((plant_id,ba,code,fuel,i))
        finally:wb.close()
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"page1_hy_source_rows_2024.csv").open("w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["plant_id","reported_ba","reported_prime_mover","reported_fuel","source_sheet_row"])
        writer.writerows(rows)
    by_ba=Counter(r[1] for r in rows)
    fuel=Counter(r[3] for r in rows)
    keys=Counter((r[0],r[1]) for r in rows)
    conflict_plants=sorted({r[0] for r in rows if len({x[1] for x in rows if x[0]==r[0]})>1})
    report={"sheet":"Page 1 Generation and Fuel Data",
            "hydro_source_rows":len(rows),
            "by_reported_ba":{ba:by_ba[ba] for ba in BAS},
            "fuel_codes":dict(sorted(fuel.items())),
            "distinct_plant_ba_pairs":len(keys),
            "multiple_source_rows_same_plant_ba":sum(n>1 for n in keys.values()),
            "plants_with_multiple_reported_bas":conflict_plants,
            "monthly_net_generation_extracted":False,
            "historical_calibration_certified":False,
            "caution":"Plant/fuel/mover source rows, not generation MWh or distinct generator units. Do not sum rows as power; independent EIA-923 generation source and historic BA crosswalk are required."}
    (out/"page1_hy_source_inventory_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(inventory(a.archive,a.output),indent=2))
if __name__=="__main__":main()
