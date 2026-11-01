"""Extract conventional hydro monthly net generation from verified EIA-923 Page 1.

Plant/prime-mover/fuel monthly MWh; keep missing distinct from zero.
"""
import argparse, csv, io, json, math, zipfile
from collections import Counter
from pathlib import Path
from openpyxl import load_workbook

BAS = ("AZPS", "BPAT", "CISO", "SRP")
MONTHS = ("January","February","March","April","May","June",
          "July","August","September","October","November","December")
MISSING = {"", ".", "NA", "NM"}

def extract(archive, output):
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names)!=1: raise ValueError("Expected exactly one schedules workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Page 1 Generation and Fuel Data"]
            head=[" ".join(str(x or "").split()) for x in next(ws.iter_rows(min_row=6,max_row=6,values_only=True))]
            for i,v in {0:"Plant Id",13:"Reported Prime Mover",14:"Reported Fuel Type Code",16:"Balancing Authority Code"}.items():
                if head[i]!=v: raise ValueError(f"Unexpected header at column {i+1}: {head[i]}")
            for i,month in enumerate(MONTHS):
                if head[79+i]!=f"Netgen {month}":
                    raise ValueError(f"Unexpected Netgen header at column {80+i}")
            rows=[];counts=Counter();missing=Counter()
            for source_row,row in enumerate(ws.iter_rows(min_row=7,values_only=True),start=7):
                if not row or row[0] is None:continue
                ba=str(row[16] or "").strip()
                pm=str(row[13] or "").strip()
                if ba not in BAS or pm!="HY":continue
                fuel=str(row[14] or "").strip()
                if fuel!="WAT": raise ValueError(f"HY unexpected fuel on source row {source_row}: {fuel}")
                plant=str(row[0]).strip()
                if not plant:raise ValueError("Missing HY plant ID")
                counts[ba]+=1
                for i in range(12):
                    value=row[79+i] if len(row)>79+i else None
                    if value is None or str(value).strip().upper() in MISSING:
                        missing[ba]+=1;continue
                    try: mwh=float(value)
                    except (TypeError, ValueError) as exc:
                        raise ValueError(f"Invalid HY net MWh row {source_row} month {i+1}: {value!r}") from exc
                    if not math.isfinite(mwh): raise ValueError("Nonfinite HY net generation")
                    rows.append((plant,ba,"HY","WAT",f"2024-{i+1:02d}",mwh,source_row))
        finally:wb.close()
    if len(rows)!=len({(r[0],r[1],r[4]) for r in rows}):
        raise ValueError("Duplicate HY plant/BA/month: source reporting requires reconciliation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"page1_hy_plant_month_net_mwh.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["plant_id","reported_ba","prime_mover","fuel","period","net_generation_mwh","source_sheet_row"])
        w.writerows(rows)
    manifest={"source_sheet":"Page 1 Generation and Fuel Data",
              "measurement":"HY WAT reported monthly Netgen MWh",
              "source_hy_rows_by_ba":dict(sorted(counts.items())),
              "observed_plant_month_rows":len(rows),
              "missing_month_cells_by_ba":dict(sorted(missing.items())),
              "negative_month_rows":sum(r[5]<0 for r in rows),
              "zero_month_rows":sum(r[5]==0 for r in rows),
              "historical_calibration_certified":False,
              "warning":"Observed plant-month Netgen is not hourly hydro availability or independent fleet/topology validation."}
    (out/"page1_hy_netgen_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(extract(a.archive,a.output),indent=2))
if __name__=="__main__":main()
