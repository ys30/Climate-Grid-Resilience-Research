"""Audit all official EIA-860 2024 Operable Energy Source N columns.

This is a source-field coverage probe; generator fuels and reported EIA-923
generation fuel are not necessarily identical, even when a code matches.
"""
import argparse
import io
import json
import re
import zipfile
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook


def probe(archive, page1, *, plant_id="6177", reported_fuel="DFO", ba="SRP", period="2024-01"):
    with zipfile.ZipFile(archive) as z:
        members = [n for n in z.namelist() if "3_1_Generator" in n and n.lower().endswith(".xlsx")]
        if len(members) != 1:
            raise ValueError("Expected one official EIA-860 3_1_Generator workbook")
        wb = load_workbook(io.BytesIO(z.read(members[0])), read_only=True, data_only=True)
        try:
            ws = wb["Operable"]
            rows = ws.iter_rows(values_only=True)
            next(rows)
            headers = [str(v).strip() if v is not None else "" for v in next(rows)]
            fuel_fields = [(i, h) for i, h in enumerate(headers)
                           if re.fullmatch(r"Energy Source\s+[1-9]\d*", h)]
            if not fuel_fields:
                raise ValueError("No official EIA-860 Energy Source N fields found")
            required = ("Plant Code", "Generator ID", "Prime Mover")
            index = {}
            for h in required:
                if headers.count(h) != 1:
                    raise ValueError("Missing or duplicate official generator field: " + h)
                index[h] = headers.index(h)
            out = []
            for row in rows:
                if not row or row[index["Plant Code"]] is None:
                    continue
                pid = str(row[index["Plant Code"]]).strip().lstrip("0") or "0"
                if pid != str(plant_id).strip().lstrip("0"):
                    continue
                item = {"plant_id": pid,
                        "generator_id": str(row[index["Generator ID"]]).strip(),
                        "prime_mover": str(row[index["Prime Mover"]]).strip()}
                for i, label in fuel_fields:
                    item[label] = (str(row[i]).strip() if i < len(row) and row[i] is not None else "")
                out.append(item)
        finally:
            wb.close()
    if not out:
        raise ValueError("No operable EIA-860 generators for selected plant")
    p = page1.copy()
    for col in ("plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"):
        if col not in p.columns:
            raise ValueError("Missing EIA-923 Page1 column: " + col)
    p["plant_id"] = p.plant_id.astype("string").str.strip().str.lstrip("0").replace("", "0")
    target = p.loc[p.plant_id.eq(str(plant_id).strip().lstrip("0")) &
                   p.reported_ba.astype("string").str.strip().eq(ba) &
                   p.period.astype("string").str.strip().eq(period) &
                   p.reported_fuel.astype("string").str.strip().eq(reported_fuel)].copy()
    if target.empty:
        raise ValueError("No selected EIA-923 fuel records")
    generators = pd.DataFrame(out)
    fields = [x[1] for x in fuel_fields]
    match = generators.loc[generators[fields].eq(reported_fuel).any(axis=1)]
    detail = target[["plant_id","reported_ba","period","prime_mover","reported_fuel","net_generation_mwh"]].copy()
    manifest = {
        "eia860_source_workbook": members[0],
        "source_fuel_fields": fields,
        "plant_id": str(plant_id),
        "eia923_reported_fuel": reported_fuel,
        "eia923_source_rows": len(detail),
        "eia923_signed_net_mwh": float(pd.to_numeric(detail.net_generation_mwh,errors="raise").sum()),
        "operable_plant_generators": len(generators),
        "generators_with_fuel_in_any_source_field": len(match),
        "matching_generator_ids": sorted(match.generator_id.astype(str).tolist()),
        "generator_fuel_identity_certified": False,
        "historical_calibration_certified": False,
        "caution": "EIA-860 energy codes describe generator attributes; absence of a code does not disprove EIA-923 reported startup/supplemental fuel."
    }
    return generators, detail, manifest


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",required=True)
    ap.add_argument("--page1",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--plant",default="6177")
    ap.add_argument("--fuel",default="DFO")
    args=ap.parse_args()
    generators,reported,manifest=probe(
        args.archive,pd.read_csv(args.page1,dtype={"plant_id":"string"}),
        plant_id=args.plant,reported_fuel=args.fuel)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    generators.to_csv(out/"eia860_full_source_fields_plant.csv",index=False)
    reported.to_csv(out/"eia923_selected_plant_fuel_rows.csv",index=False)
    (out/"eia860_full_fuel_field_probe.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))


if __name__=="__main__":
    main()
