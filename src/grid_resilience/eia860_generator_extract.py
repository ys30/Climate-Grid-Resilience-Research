"""Extract reviewed EIA-860 2024 Operable generator inventory from official ZIP.

Uses verified EIA-860 Schedule 3 Operable column header labels. Records all
fuel codes, not only the predominant code; never asserts multi-fuel calibration.
"""
import argparse
import csv
import io
import json
import zipfile
from pathlib import Path

HEADERS={"Nameplate Capacity (MW)":"nameplate_capacity_mw",
         "Summer Capacity (MW)":"summer_capacity_mw",
         "Winter Capacity (MW)":"winter_capacity_mw",
         "Plant Code":"plant_id","Generator ID":"generator_id",
         "Energy Source 1":"energy_source_1","Prime Mover":"prime_mover",
         "Energy Source 2":"energy_source_2","Multiple Fuels?":"multiple_fuels",
         "Technology":"reported_technology","Status":"status"}

def extract(archive, output):
    from openpyxl import load_workbook
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "3_1_Generator" in n and n.lower().endswith(".xlsx")]
        if len(names)!=1:
            raise ValueError("Expected exactly one 3_1_Generator workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        try:
            ws=wb["Operable"]
            rows=ws.iter_rows(values_only=True)
            next(rows)
            headers=[str(x).strip() if x is not None else "" for x in next(rows)]
            indexes={}
            for key in HEADERS:
                if headers.count(key)!=1:
                    raise ValueError(f"Missing or ambiguous official column: {key}")
                indexes[key]=headers.index(key)
            records=[]
            for row in rows:
                if not row or row[indexes["Plant Code"]] is None:
                    continue
                record={}
                for key,dest in HEADERS.items():
                    v=row[indexes[key]] if indexes[key]<len(row) else None
                    record[dest]=str(v).strip() if v is not None else ""
                if not record["plant_id"] or not record["generator_id"]:
                    raise ValueError("Missing generator join identifier")
                records.append(record)
        finally:
            wb.close()
    keys=[(r["plant_id"],r["generator_id"]) for r in records]
    if len(keys)!=len(set(keys)):
        raise ValueError("Duplicate official EIA-860 Operable generator IDs")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    with (out/"eia860_2024_operable_generators.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(HEADERS.values()))
        w.writeheader();w.writerows(records)
    result={"operable_generator_rows":len(records),"unique_keys":len(set(keys)),
            "source_workbook":names[0],"technology_classification_certified":False,
            "notes":"Only Operable rows; excluded proposed/retired. Multi-fuel and storage need explicit treatment."}
    (out/"eia860_extraction_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(extract(a.archive,a.output),indent=2))

if __name__=="__main__":
    main()
