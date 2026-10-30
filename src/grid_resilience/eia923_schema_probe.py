"""Inspect selected official EIA-923 worksheets without guessing header rows.

Operates directly on original ZIP. Exports a small, reviewable JSON schema
sample, but does not export actual plant generation records or claim calibration.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path

SHEETS = ("Page 4 Generator Data", "Page 1 Generation and Fuel Data",
          "Page 1 Energy Storage", "Page 7 File Layout")

def inspect(archive, output):
    from openpyxl import load_workbook
    result = []
    with zipfile.ZipFile(archive) as z:
        matches = [name for name in z.namelist()
                   if "Schedules_2_3_4_5" in name and name.lower().endswith(".xlsx")]
        if len(matches) != 1:
            raise ValueError("Expected exactly one EIA923 Schedules 2/3/4/5 workbook")
        wb = load_workbook(io.BytesIO(z.read(matches[0])), read_only=True, data_only=True)
        try:
            for name in SHEETS:
                if name not in wb.sheetnames:
                    raise ValueError(f"Required worksheet absent: {name}")
                ws = wb[name]
                samples = []
                for row in ws.iter_rows(min_row=1, max_row=12, values_only=True):
                    samples.append([str(v)[:100] if v is not None else None for v in row[:70]])
                result.append({"sheet": name, "first_12_rows_first_70_columns": samples})
        finally:
            wb.close()
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    for sheet in inspect(args.archive, args.output):
        print("SHEET:", sheet["sheet"])
        for i, row in enumerate(sheet["first_12_rows_first_70_columns"], start=1):
            nonempty = [f"{j+1}:{v}" for j, v in enumerate(row) if v is not None]
            print(f"ROW {i}: " + " | ".join(nonempty)[:7000])

if __name__ == "__main__":
    main()
