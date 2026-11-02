"""Inspect unmatched EIA-923 keys across all official EIA-860 generator worksheets.

Provides evidence of worksheet presence, NOT proof of historical operating
status or automatic generator aliases. No fuzzy join is performed.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path
import pandas as pd

def compare_status_sheets(archive, unmatched):
    from openpyxl import load_workbook
    required={"plant_id","generator_id","reported_ba","period"}
    if not required.issubset(unmatched.columns):
        raise ValueError(f"Missing unmatched fields: {sorted(required-set(unmatched.columns))}")
    if unmatched.empty or unmatched[list(required)].isna().any().any():
        raise ValueError("Empty or null unmatched keys")
    def norm(v):
        s=str(v).strip()
        if not s:return ""
        if s.isdigit():return str(int(s))
        return s
    unique=unmatched[["plant_id","generator_id","reported_ba"]].copy()
    unique["plant_id"]=unique.plant_id.map(norm)
    unique["generator_id"]=unique.generator_id.astype(str).str.strip()
    if unique[["plant_id","generator_id"]].eq("").any().any():
        raise ValueError("Blank keys")
    unique=unique.drop_duplicates()
    with zipfile.ZipFile(archive) as z:
        names=[n for n in z.namelist() if "3_1_Generator" in n and n.lower().endswith(".xlsx")]
        if len(names)!=1:raise ValueError("Require exactly one official generator workbook")
        wb=load_workbook(io.BytesIO(z.read(names[0])),read_only=True,data_only=True)
        inventory=[]
        try:
            for ws in wb:
                iterator=ws.iter_rows(values_only=True)
                next(iterator,None)
                headers=[str(v).strip() if v is not None else "" for v in (next(iterator,None) or [])]
                if "Plant Code" not in headers or "Generator ID" not in headers:
                    continue
                pi=headers.index("Plant Code")
                gi=headers.index("Generator ID")
                status_i=headers.index("Status") if "Status" in headers else None
                for row in iterator:
                    if not row or len(row)<=max(pi,gi) or row[pi] is None or row[gi] is None:
                        continue
                    inventory.append({"plant_id":norm(row[pi]),"generator_id":str(row[gi]).strip(),
                                      "sheet":ws.title,
                                      "reported_status":str(row[status_i]).strip() if status_i is not None and len(row)>status_i and row[status_i] is not None else ""})
        finally:
            wb.close()
    if not inventory:raise ValueError("No recognized generator inventory rows")
    inv=pd.DataFrame(inventory)
    if inv.duplicated(["sheet","plant_id","generator_id"]).any():
        raise ValueError("Duplicate identifiers within EIA-860 worksheet")
    result=[]
    for row in unique.itertuples(index=False):
        exact=inv[(inv.plant_id==row.plant_id)&(inv.generator_id==row.generator_id)]
        same=inv[inv.plant_id==row.plant_id]
        result.append({"reported_ba":row.reported_ba,"plant_id":row.plant_id,
            "generator_id":row.generator_id,"exact_sheet_matches":";".join(sorted(set(exact.sheet))),
            "exact_reported_statuses":";".join(sorted(set(x for x in exact.reported_status if x))),
            "other_ids_at_plant":";".join(sorted(set(same.generator_id)-{row.generator_id})),
            "status_resolution":"exact_key_found_in_source" if not exact.empty else
                ("plant_only_found" if not same.empty else "plant_not_in_generator_workbook"),
            "retirement_or_rename_certified":False})
    return pd.DataFrame(result).sort_values(["reported_ba","plant_id","generator_id"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True);p.add_argument("--unmatched",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=compare_status_sheets(a.archive,pd.read_csv(a.unmatched,dtype="string"))
    path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(path,index=False)
    print(json.dumps({"distinct_unmatched_keys":len(result),
      "statuses":result.status_resolution.value_counts().to_dict(),
      "retirement_or_rename_certified":False},indent=2))

if __name__=="__main__":main()
