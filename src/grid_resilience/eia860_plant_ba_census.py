"""Independent EIA-860 Plant BA -> Operable Generator coverage census.

The plant-reported BA assignment is distinct from EIA-923 Page4's reporting
population. This census is NOT observed hourly generation or a calibration.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import numpy as np


def read_plant_ba(archive):
    from openpyxl import load_workbook
    with zipfile.ZipFile(archive) as z:
        members=[m for m in z.namelist() if m.lower().endswith(".xlsx")
                 and "2___Plant" in m]
        if len(members)!=1:
            raise ValueError("Expected exactly one official EIA-860 Plant workbook")
        wb=load_workbook(io.BytesIO(z.read(members[0])),read_only=True,data_only=True)
        try:
            sheets=[wb[x] for x in wb.sheetnames if x.strip().lower()=="plant"]
            if len(sheets)!=1:
                raise ValueError("Expected a unique Plant sheet")
            ws=sheets[0]
            rows=ws.iter_rows(values_only=True)
            header=None
            for i,row in enumerate(rows):
                normalized=[str(x).strip() if x is not None else "" for x in row]
                if "Plant Code" in normalized and "Balancing Authority Code" in normalized:
                    header=normalized
                    break
                if i>=9:break
            if header is None:
                raise ValueError("Official Plant Code / BA Code header not found")
            if header.count("Plant Code")!=1 or header.count("Balancing Authority Code")!=1:
                raise ValueError("Ambiguous Plant / BA columns")
            key=header.index("Plant Code")
            val=header.index("Balancing Authority Code")
            records=[]
            for row in rows:
                if not row or key>=len(row) or row[key] is None:continue
                pid=str(row[key]).strip()
                ba=str(row[val]).strip() if val<len(row) and row[val] is not None else ""
                records.append({"plant_id":pid,"plant_reported_ba":ba})
        finally:
            wb.close()
    return pd.DataFrame(records)


def census(plant,operable,page4,*,ba="SRP"):
    def normalize(df,fields):
        d=df.copy()
        for k in fields:
            if k not in d:raise ValueError("Required field missing: "+k)
            d[k]=d[k].astype("string").str.strip()
            if d[k].isna().any() or d[k].eq("").any():
                raise ValueError("Empty generator or plant identity")
        d["plant_id"]=d.plant_id.str.replace(r"^0+(?=[0-9])","",regex=True)
        return d
    p=normalize(plant,["plant_id"])
    if "plant_reported_ba" not in p:raise ValueError("Missing official plant BA code")
    p["plant_reported_ba"]=p.plant_reported_ba.astype("string").str.strip()
    if p.plant_id.duplicated().any():raise ValueError("Duplicate EIA-860 plant IDs")
    g=normalize(operable,["plant_id","generator_id"])
    if g[["plant_id","generator_id"]].duplicated().any():
        raise ValueError("Duplicate EIA-860 operable generator IDs")
    if "nameplate_capacity_mw" not in g:raise ValueError("Missing generator capacity")
    f=normalize(page4,["plant_id","generator_id"])
    if "reported_ba" not in f or "period" not in f:
        raise ValueError("Missing EIA-923 source scope fields")
    f=f[f.reported_ba.eq(ba)&f.period.astype(str).eq("2024-01")].copy()
    if f[["plant_id","generator_id"]].duplicated().any():
        raise ValueError("Duplicate EIA-923 BA/month generator identities")
    all_g=g.merge(p[["plant_id","plant_reported_ba"]],on="plant_id",how="left",validate="many_to_one")
    nationwide_missing_plant=int(all_g.plant_reported_ba.isna().sum())
    # Do not let a missing/invalid *unrelated national* capacity block a
    # source-scoped SRP census. Retain a quality metric for missing plant joins.
    candidates=all_g[all_g.plant_reported_ba.eq(ba)].copy()
    if candidates.empty:
        raise ValueError("No EIA-860 operable generators assigned to target BA")
    candidates["nameplate_capacity_mw"]=pd.to_numeric(candidates.nameplate_capacity_mw,errors="coerce")
    bad=candidates.nameplate_capacity_mw.isna() | ~candidates.nameplate_capacity_mw.ge(0)
    if bad.any() or not np.isfinite(candidates.nameplate_capacity_mw.to_numpy(dtype=float)).all():
        raise ValueError("Missing, negative or nonfinite target BA generator nameplate")
    candidates["appears_in_page4_ba_month"]=candidates.set_index(["plant_id","generator_id"]).index.isin(
        f.set_index(["plant_id","generator_id"]).index)
    unseen=candidates.loc[~candidates.appears_in_page4_ba_month]
    # A second, reverse comparison is required: source-reported Page4 BA
    # can disagree with annual EIA-860 Plant BA assignment.
    candidate_keys=candidates[["plant_id","generator_id"]]
    page4_reverse=f[["plant_id","generator_id"]].merge(
        candidate_keys,on=["plant_id","generator_id"],how="left",
        indicator=True,validate="one_to_one"
    )
    page4_outside=page4_reverse.loc[page4_reverse["_merge"].eq("left_only")]
    report={
      "target_ba":ba,"source_year":2024,"month":"2024-01",
      "nationwide_operable_records_without_plant_join":nationwide_missing_plant,
      "eia860_plant_assigned_operable_generators":len(candidates),
      "eia860_plant_assigned_nameplate_mw":float(candidates.nameplate_capacity_mw.sum()),
      "of_those_appearing_in_eia923_page4_ba_month":int(candidates.appears_in_page4_ba_month.sum()),
      "plant_assigned_operable_not_in_page4_month":len(unseen),
      "plant_assigned_nameplate_not_in_page4_month_mw":float(unseen.nameplate_capacity_mw.sum()),
      "page4_reported_ba_generator_count":len(f),
      "page4_reported_ba_not_in_plant_assigned_roster_count":len(page4_outside),
      "ba_attribution_is_bidirectionally_identical":bool(len(page4_outside)==0 and len(unseen)==0),
      "page4_reported_ba_missing_plant_roster_identities":page4_outside[
          ["plant_id","generator_id"]].to_dict("records"),
      "note":"Plant BA association can differ from generator dispatch ownership and external supply. Not a full physical network capacity census.",
      "historical_calibration_certified":False
    }
    return candidates,report


def main():
    p=argparse.ArgumentParser()
    for k in ("archive","operable","page4","output"):p.add_argument("--"+k,required=True)
    p.add_argument("--ba",default="SRP")
    a=p.parse_args()
    plants=read_plant_ba(a.archive)
    identity_dtype={"plant_id":"string","generator_id":"string"}
    census_rows,report=census(plants,pd.read_csv(a.operable,dtype=identity_dtype),
                              pd.read_csv(a.page4,dtype=identity_dtype),ba=a.ba)
    o=Path(a.output);o.mkdir(parents=True,exist_ok=True)
    census_rows.to_csv(o/"plant_ba_operable_generator_census.csv",index=False)
    (o/"plant_ba_generator_census_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
