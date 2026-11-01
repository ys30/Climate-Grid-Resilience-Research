"""Extract Page 1 Energy Storage pumped-storage net monthly MWh.

Source: official EIA-923 2024 Schedules 2/3/4/5, "Page 1 Energy Storage".
Do not merge this plant/fuel/mover series with Page 4 generator observations.
"""
import argparse
import csv
import io
import json
import math
import zipfile
from collections import Counter
from pathlib import Path
from openpyxl import load_workbook

BAS = {"AZPS", "BPAT", "CISO", "SRP"}
MONTHS = ("January","February","March","April","May","June","July",
          "August","September","October","November","December")
MISSING = {"", ".", "NA", "NM"}

def extract(archive, output):
    with zipfile.ZipFile(archive) as z:
        members = [name for name in z.namelist()
                   if "Schedules_2_3_4_5" in name and name.endswith(".xlsx")]
        if len(members) != 1:
            raise ValueError("Expected one official schedules workbook")
        wb = load_workbook(io.BytesIO(z.read(members[0])),
                           read_only=True, data_only=True)
        try:
            ws = wb["Page 1 Energy Storage"]
            head = list(next(ws.iter_rows(min_row=6,max_row=6,values_only=True)))
            normalized = [" ".join(str(v or "").split()) for v in head]
            required = {0:"Plant Id",12:"Reported Prime Mover",15:"Balancing Authority Code"}
            for idx, label in required.items():
                if normalized[idx] != label:
                    raise ValueError(f"Unexpected source header at {idx+1}: {normalized[idx]!r}")
            for n,month in enumerate(MONTHS):
                if normalized[54+n] != f"Netgen {month}":
                    raise ValueError(f"Unexpected Netgen header at column {55+n}")
            rows = []
            missing = Counter()
            source_rows = Counter()
            for source_row, row in enumerate(ws.iter_rows(min_row=7,values_only=True),start=7):
                if not row or row[0] is None:
                    continue
                ba = str(row[15] or "").strip()
                code = str(row[12] or "").strip()
                if ba not in BAS or code != "PS":
                    continue
                plant_id = str(row[0]).strip()
                if not plant_id:
                    raise ValueError(f"Missing plant ID on worksheet row {source_row}")
                source_rows[ba] += 1
                for month_idx in range(12):
                    period=f"2024-{month_idx+1:02d}"
                    value=row[54+month_idx] if len(row)>54+month_idx else None
                    if value is None or str(value).strip().upper() in MISSING:
                        missing[ba] += 1
                        continue
                    try:
                        mwh=float(value)
                    except (TypeError,ValueError) as exc:
                        raise ValueError(f"Unrecognized PS net generation on row {source_row}, {period}: {value!r}") from exc
                    if not math.isfinite(mwh):
                        raise ValueError("Nonfinite PS net generation")
                    rows.append((plant_id,ba,"PS",period,mwh,source_row))
        finally:
            wb.close()
    if len(rows) != len(set((r[0],r[1],r[2],r[3]) for r in rows)):
        raise ValueError("Duplicate plant/BA/prime-mover/month: reconcile before aggregation")
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    with (out/"eia923_page1_ps_plant_month_net_mwh.csv").open("w",newline="") as file:
        writer=csv.writer(file)
        writer.writerow(["plant_id","reported_ba","prime_mover","period",
                         "net_generation_mwh","source_sheet_row"])
        writer.writerows(rows)
    manifest={
        "source_sheet":"Page 1 Energy Storage",
        "measurement":"Reported monthly Netgen (MWh), plant and prime-mover level",
        "observed_ps_plant_month_rows":len(rows),
        "source_ps_rows_by_ba":dict(sorted(source_rows.items())),
        "missing_netgen_cells_by_ba":dict(sorted(missing.items())),
        "negative_net_generation_rows":sum(r[4]<0 for r in rows),
        "zero_net_generation_rows":sum(r[4]==0 for r in rows),
        "historical_calibration_certified":False,
        "caution":"Not an hourly storage dispatch series; Page 1 does not independently validate plant-to-BA historical assignment, pumping energy, state of charge or fleet completeness."
    }
    (out/"eia923_page1_ps_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    print(json.dumps(extract(args.archive,args.output),indent=2))

if __name__=="__main__":
    main()
