"""Extract actual EIA-923 2024 Page 4 generator-month net MWh.

Uses verified workbook positional layout (header row 6; data start row 7).
Does NOT infer fuel technology from prime mover and does NOT claim BA
membership is independently verified beyond the EIA reported field.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path

BA_TARGETS = {"CISO", "AZPS", "BPAT", "SRP"}
MONTHS = tuple(f"2024-{month:02d}" for month in range(1, 13))

def extract(archive, output, *, target_bas=BA_TARGETS):
    from openpyxl import load_workbook
    from collections import Counter
    archive = Path(archive)
    with zipfile.ZipFile(archive) as z:
        names = [n for n in z.namelist() if "Schedules_2_3_4_5" in n and n.endswith(".xlsx")]
        if len(names) != 1:
            raise ValueError("Exactly one official schedules workbook required")
        wb = load_workbook(io.BytesIO(z.read(names[0])), read_only=True, data_only=True)
        try:
            ws = wb["Page 4 Generator Data"]
            headers = list(next(ws.iter_rows(min_row=6, max_row=6, values_only=True)))
            if str(headers[0]).strip() != "Plant Id":
                raise ValueError("Unexpected Page 4 header position")
            # The month block is identified by official row-5 grouping at column 15.
            group = list(next(ws.iter_rows(min_row=5, max_row=5, values_only=True)))
            if "Net Generation" not in str(group[14]):
                raise ValueError("Expected net generation at column 15")
            rows = []
            counts = Counter()
            excluded = Counter()
            for row in ws.iter_rows(min_row=7, values_only=True):
                if not row or row[0] is None:
                    continue
                ba = str(row[27]).strip() if len(row) > 27 and row[27] is not None else ""
                if ba not in target_bas:
                    continue
                plant, gen, pm = row[0], row[11], row[12]
                year = row[28] if len(row) > 28 else None
                if year is None or int(year) != 2024:
                    raise ValueError("Unexpected reporting year")
                if plant is None or gen is None or pm is None:
                    raise ValueError("Missing plant, generator or prime mover")
                for index, period in enumerate(MONTHS):
                    value = row[14 + index]
                    if value is None or str(value).strip() in ("", ".", "NA", "NM"):
                        excluded["unreported_monthly_value"] += 1
                        continue
                    try:
                        v = float(value)
                    except (ValueError, TypeError) as exc:
                        raise ValueError(f"Unexpected generation value {value!r}") from exc
                    if not (-float("inf") < v < float("inf")):
                        raise ValueError("Nonfinite generation")
                    rows.append((str(plant).strip(), str(gen).strip(), str(pm).strip(), ba, period, v))
                    counts[ba] += 1
        finally:
            wb.close()
    import csv
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "eia923_generator_month_net_mwh.csv").open("w", newline="") as f:
        w=csv.writer(f)
        w.writerow(("plant_id", "generator_id", "prime_mover", "reported_ba",
                    "period", "generation_mwh"))
        w.writerows(rows)
    manifest = {
        "classification": "official_sheet_extracted_not_fleet_calibrated",
        "requested_bas": sorted(target_bas),
        "monthly_records_by_ba": dict(sorted(counts.items())),
        "excluded_missing_month_cells": excluded["unreported_monthly_value"],
        "total_records": len(rows),
        "fuel_technology_inferred": False,
        "historical_calibration_certified": False,
        "note": "Generator-level net MWh, negative values retained. Missing is not zero. BA reported by the source is not a verified historical topology crosswalk."
    }
    (out / "generator_extraction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output", required=True)
    args=p.parse_args()
    print(json.dumps(extract(args.archive, args.output), indent=2))

if __name__=="__main__":
    main()
